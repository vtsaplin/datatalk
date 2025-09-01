import sys
import duckdb
import os
import argparse
import json
from pathlib import Path
from openai import AzureOpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt


def print_logo(console: Console) -> None:
    """Print the DataTalk ASCII logo."""
    logo = """
[bold cyan]
██████╗  █████╗ ████████╗ █████╗ ████████╗ █████╗ ██╗     ██╗  ██╗
██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗██║     ██║ ██╔╝
██║  ██║███████║   ██║   ███████║   ██║   ███████║██║     █████╔╝
██║  ██║██╔══██║   ██║   ██╔══██║   ██║   ██╔══██║██║     ██╔═██╗
██████╔╝██║  ██║   ██║   ██║  ██║   ██║   ██║  ██║███████╗██║  ██╗
╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
[/bold cyan]
[dim]Ask questions about your CSV/Parquet data using natural language[/dim]
"""
    console.print(logo)


def get_config_path() -> Path:
    """Get the path to the configuration file."""
    config_dir = Path.home() / ".config" / "datatalk"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"


def load_config() -> dict[str, str]:
    """Load configuration from file."""
    config_path = get_config_path()
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


def save_config(config: dict[str, str]) -> None:
    """Save configuration to file."""
    config_path = get_config_path()
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def get_env_var(name: str, config: dict[str, str], console: Console) -> str:
    """Get environment variable, prompting user if not available."""
    # First check environment variables
    value = os.getenv(name)
    if value:
        return value

    # Then check saved config
    if name in config:
        return config[name]

    # Prompt user for the value
    descriptions = {
        "AZURE_OPENAI_API_KEY": "Azure OpenAI API key",
        "AZURE_DEPLOYMENT_TARGET_URL": "Azure OpenAI deployment target URL",
    }

    description = descriptions.get(name, name)
    console.print(f"[yellow]Missing configuration:[/yellow] {description}")

    if name == "AZURE_OPENAI_API_KEY":
        value = Prompt.ask(f"Enter {description}", console=console, password=True)
    elif name == "AZURE_DEPLOYMENT_TARGET_URL":
        value = Prompt.ask(f"Enter {description}", console=console, default=None)
        console.print(
            "[dim]Example: https://your-resource.openai.azure.com/openai/"
            "deployments/gpt-4o/chat/completions?"
            "api-version=2024-12-01-preview[/dim]"
        )
    else:
        # Unknown configuration variable
        console.print(f"[red]Error:[/red] Unknown configuration: {name}")
        sys.exit(1)

    if not value:
        console.print(f"[red]Error:[/red] {description} is required")
        sys.exit(1)

    # Save to config
    config[name] = value
    save_config(config)
    console.print(f"[green]✓[/green] Saved {description} to configuration")

    return value


def parse_target_url(target_url: str) -> tuple[str, str, str]:
    """Parse Azure deployment target URL to extract components."""
    # Example URL: https://your-resource.openai.azure.com/openai/
    # deployments/gpt-4o/chat/completions?api-version=2024-12-01-preview

    # Extract the base endpoint
    if "/openai/deployments/" not in target_url:
        raise ValueError("Invalid Azure deployment target URL format")

    endpoint = target_url.split("/openai/deployments/")[0] + "/"

    # Extract deployment name
    deployment_part = target_url.split("/openai/deployments/")[1]
    deployment_name = deployment_part.split("/")[0]

    # Extract API version from query parameters
    if "api-version=" not in target_url:
        raise ValueError("API version not found in target URL")

    api_version = target_url.split("api-version=")[1].split("&")[0]

    return endpoint, deployment_name, api_version


def get_azure_config(
    config: dict[str, str], console: Console
) -> tuple[str, str, str, str]:
    """Get Azure OpenAI configuration using target URL approach only."""
    # Get the target URL and API key
    target_url = os.getenv("AZURE_DEPLOYMENT_TARGET_URL") or config.get(
        "AZURE_DEPLOYMENT_TARGET_URL"
    )

    if not target_url:
        target_url = get_env_var("AZURE_DEPLOYMENT_TARGET_URL", config, console)

    api_key = get_env_var("AZURE_OPENAI_API_KEY", config, console)

    try:
        endpoint, deployment_name, api_version = parse_target_url(target_url)
        console.print(
            "[green]✓[/green] Using Azure deployment target URL configuration"
        )
        return api_key, endpoint, deployment_name, api_version
    except ValueError as e:
        console.print(f"[red]Error parsing target URL:[/red] {e}")
        console.print("[red]Please check your AZURE_DEPLOYMENT_TARGET_URL format[/red]")
        sys.exit(1)


def load_data_to_duckdb(path: str, con: duckdb.DuckDBPyConnection):
    """Load CSV or Parquet file into DuckDB and create a table named 'events'."""
    file_path = Path(path)
    file_extension = file_path.suffix.lower()

    con.execute("DROP TABLE IF EXISTS events;")

    if file_extension == ".parquet":
        con.execute(f"CREATE TABLE events AS SELECT * FROM read_parquet('{path}');")
    elif file_extension == ".csv":
        con.execute(
            f"CREATE TABLE events AS SELECT * FROM "
            f"read_csv_auto('{path}', HEADER=TRUE);"
        )
    else:
        raise ValueError(
            f"Unsupported file format: {file_extension}. "
            f"Supported formats: .csv, .parquet"
        )


def get_schema(con: duckdb.DuckDBPyConnection) -> str:
    """Return a simple schema description for the 'events' table."""
    rows = con.execute("PRAGMA table_info('events')").fetchall()
    schema_lines = []
    for row in rows:
        _, name, col_type, *_ = row
        schema_lines.append(f"{name} ({col_type})")
    return ", ".join(schema_lines)


def show_basic_stats(con: duckdb.DuckDBPyConnection, console: Console) -> None:
    """Show basic statistics about the loaded data."""
    # Get row count
    result = con.execute("SELECT COUNT(*) FROM events").fetchone()
    row_count = result[0] if result else 0

    # Get column count and info
    columns = con.execute("PRAGMA table_info('events')").fetchall()
    col_count = len(columns)

    console.print("\n[bold green]📊 Dataset Statistics[/bold green]")
    console.print(f"• Rows: [cyan]{row_count:,}[/cyan]")
    console.print(f"• Columns: [cyan]{col_count}[/cyan]")

    # Show column info in a table
    if columns:
        table = Table(
            show_header=True, header_style="bold magenta", title="Column Information"
        )
        table.add_column("Column", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Sample Values", style="dim")

        for row in columns:
            _, name, col_type, *_ = row
            # Get a few sample values for this column
            try:
                query = (
                    f"SELECT DISTINCT {name} FROM events "
                    f"WHERE {name} IS NOT NULL LIMIT 3"
                )
                samples = con.execute(query).fetchall()
                sample_values = []
                for sample in samples:
                    value_str = str(sample[0])
                    if len(value_str) > 20:
                        value_str = value_str[:20] + "..."
                    sample_values.append(value_str)
                sample_str = ", ".join(sample_values)
                if not sample_str:
                    sample_str = "[dim]no data[/dim]"
            except Exception:
                sample_str = "[dim]error reading[/dim]"

            table.add_row(name, col_type, sample_str)

        console.print(table)

    console.print()


def llm_to_sql(
    client: AzureOpenAI, question: str, schema_info: str, deployment_name: str
) -> str:
    """Ask Azure OpenAI to translate a natural language question into SQL."""
    prompt = f"""
You are a data assistant.
The user asks questions about a table named 'events'.
Schema of events: {schema_info}

Return ONLY valid SQL for DuckDB, nothing else.
SQL should start with SELECT and must reference the 'events' table.

User question: {question}
"""

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=float(os.getenv("MODEL_TEMPERATURE", "0.1")),
        max_tokens=500,
    )

    content = response.choices[0].message.content
    if content is None:
        raise ValueError("No content returned from Azure OpenAI")

    sql = content.strip()

    # Clean up markdown code blocks if present
    if sql.startswith("```sql"):
        sql = sql[6:]  # Remove ```sql
    elif sql.startswith("```"):
        sql = sql[3:]  # Remove ```

    if sql.endswith("```"):
        sql = sql[:-3]  # Remove trailing ```

    sql = sql.strip()
    return sql


def process_query(
    client: AzureOpenAI,
    query: str,
    schema_info: str,
    con: duckdb.DuckDBPyConnection,
    show_sql: bool,
    console: Console,
    deployment_name: str,
):
    """Process a single query and display results."""
    try:
        console.print("[dim]Analyzing your question...[/dim]")
        sql = llm_to_sql(client, query, schema_info, deployment_name)
        if show_sql:
            console.print(f"[cyan]SQL:[/cyan] [bold]{sql}[/bold]")

        console.print("[dim]Executing query...[/dim]")
        res = con.execute(sql).df()

        if len(res) == 0:
            console.print("[yellow]No results found.[/yellow]")
        else:
            # Create a rich table for better formatting
            table = Table(show_header=True, header_style="bold magenta")

            # Add columns
            for col in res.columns:
                table.add_column(col)

            # Add rows (limit to first 20 for readability)
            row_count = 0
            for _, row in res.iterrows():
                if row_count >= 20:
                    ellipsis = ["..." for _ in range(len(res.columns) - 1)]
                    table.add_row("...", *ellipsis)
                    break
                table.add_row(*[str(val) for val in row])
                row_count += 1

            console.print(table)

            if len(res) > 20:
                console.print(f"[dim]Showing first 20 of {len(res)} rows[/dim]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


def main():
    console = Console()

    # Display logo
    print_logo(console)

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Ask questions about CSV/Parquet data using natural language"
    )
    parser.add_argument("file", nargs="?", help="CSV or Parquet file to analyze")
    parser.add_argument(
        "--show-sql", action="store_true", help="Show generated SQL queries"
    )
    parser.add_argument("--prompt", help="Run a single query in non-interactive mode")
    parser.add_argument(
        "--config-info",
        action="store_true",
        help="Show configuration file location and exit",
    )

    args = parser.parse_args()

    # Handle config info request
    if args.config_info:
        config_path = get_config_path()
        console.print(f"Configuration file: [cyan]{config_path}[/cyan]")
        if config_path.exists():
            console.print("[green]✓[/green] Configuration file exists")
            config = load_config()
            if config:
                console.print("Stored settings:")
                for key in config:
                    if "API_KEY" in key:
                        console.print(f"  {key}: [dim]***[/dim]")
                    else:
                        console.print(f"  {key}: {config[key]}")
            else:
                console.print("[yellow]Configuration file is empty[/yellow]")
        else:
            console.print("[yellow]Configuration file does not exist[/yellow]")
        return

    # Check if file argument is provided when not using --config-info
    if not args.file:
        console.print("[red]Error:[/red] CSV or Parquet file is required")
        parser.print_help()
        sys.exit(1)

    # Load .env file if it exists (but don't require it)
    load_dotenv()

    # Load saved configuration
    config = load_config()

    # Get Azure OpenAI configuration
    api_key, endpoint, deployment_name, api_version = get_azure_config(config, console)

    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint,
    )

    path = args.file
    con = duckdb.connect()
    load_data_to_duckdb(path, con)
    schema_info = get_schema(con)

    console.print("[green]Data loaded successfully![/green] ✨")
    show_basic_stats(con, console)

    # Non-interactive mode
    if args.prompt:
        process_query(
            client,
            args.prompt,
            schema_info,
            con,
            args.show_sql,
            console,
            deployment_name,
        )
        return

    # Interactive mode
    console.print("[dim]Type your questions ([bold]q[/bold] to quit)[/dim]\n")

    while True:
        try:
            q = Prompt.ask("[bold blue]>[/bold blue]", console=console)
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye! 👋[/dim]")
            break
        if q.strip().lower() in ("q", "quit", "exit"):
            console.print("[dim]Goodbye! 👋[/dim]")
            break
        if not q.strip():
            continue

        process_query(
            client,
            q,
            schema_info,
            con,
            args.show_sql,
            console,
            deployment_name,
        )
        console.print()  # Add blank line for spacing


if __name__ == "__main__":
    main()
