import sys
import duckdb
import os
import argparse
from pathlib import Path
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich import box
from typing import Union
from importlib.metadata import version, PackageNotFoundError

from datatalk.config import (
    get_config_path,
    load_config,
    get_env_var,
    get_azure_config,
)


class TokenUsageTracker:
    """Track token usage across all API calls."""

    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_requests = 0

    def add_usage(self, usage):
        """Add usage from an API response."""
        if usage:
            self.input_tokens += getattr(usage, "prompt_tokens", 0)
            self.output_tokens += getattr(usage, "completion_tokens", 0)
            self.total_requests += 1

    def get_total_tokens(self) -> int:
        """Get total tokens used."""
        return self.input_tokens + self.output_tokens

    def print_statistics(self, console: Console) -> None:
        """Print usage statistics."""
        if self.total_requests == 0:
            console.print("[dim]No API calls were made.[/dim]")
            return

        console.print("\n[bold cyan]Token Usage Statistics[/bold cyan]")

        # Create a nice table for the statistics
        table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow", justify="right")

        table.add_row("API Requests", f"{self.total_requests:,}")
        table.add_row("Input Tokens", f"{self.input_tokens:,}")
        table.add_row("Output Tokens", f"{self.output_tokens:,}")
        table.add_row("Total Tokens", f"{self.get_total_tokens():,}")

        console.print(table)


# Global token tracker instance
token_tracker = TokenUsageTracker()


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
[dim]Ask questions about your CSV, Excel or Parquet data in natural language.[/dim]
"""
    console.print(logo)


def get_openai_config(config: dict[str, str], console: Console) -> tuple[str, str]:
    """Get OpenAI configuration."""
    api_key = get_env_var("OPENAI_API_KEY", config, console)
    model = get_env_var("OPENAI_MODEL", config, console)
    return api_key, model


def detect_provider(config: dict[str, str], console: Console) -> str:
    """Auto-detect provider based on available environment variables and config."""
    # Check environment variables first
    has_azure_env = bool(
        os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("AZURE_DEPLOYMENT_TARGET_URL")
    )
    has_openai_env = bool(os.getenv("OPENAI_API_KEY"))

    # Check saved config
    has_azure_config = bool(
        config.get("AZURE_OPENAI_API_KEY") or config.get("AZURE_DEPLOYMENT_TARGET_URL")
    )
    has_openai_config = bool(config.get("OPENAI_API_KEY") or config.get("OPENAI_MODEL"))

    # If both are available, prefer OpenAI (simpler setup)
    if (has_openai_env or has_openai_config) and (has_azure_env or has_azure_config):
        console.print("[yellow]Both Azure and OpenAI configurations detected.[/yellow]")
        console.print("[dim]Preferring OpenAI (simpler setup)[/dim]")
        return "openai"

    # If only one is available, use that
    if has_azure_env or has_azure_config:
        return "azure"

    if has_openai_env or has_openai_config:
        return "openai"

        # If neither is available, ask the user
    console.print("[yellow]No AI provider configuration detected.[/yellow]")
    console.print("Available providers:")
    console.print("  [bold]1[/bold] - Azure OpenAI (requires API key + target URL)")
    console.print("  [bold]2[/bold] - OpenAI (requires API key + model name)")

    while True:
        try:
            choice = Prompt.ask(
                "Choose provider", choices=["1", "2", "azure", "openai"], default="2"
            ).lower()
            if choice in ["1", "azure"]:
                return "azure"
            elif choice in ["2", "openai"]:
                return "openai"
            console.print("[red]Please choose '1' (Azure) or '2' (OpenAI)[/red]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]\n")
            sys.exit(0)


def setup_ai_client(
    provider: str, config: dict[str, str], console: Console
) -> tuple[Union[AzureOpenAI, OpenAI], str]:
    """Setup AI client based on provider."""
    if provider == "azure":
        api_key, endpoint, deployment_name, api_version = get_azure_config(
            config, console
        )
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
        )
        return client, deployment_name
    elif provider == "openai":
        api_key, model = get_openai_config(config, console)
        client = OpenAI(api_key=api_key)
        return client, model
    else:
        console.print(f"[red]Error:[/red] Unknown provider: {provider}")
        sys.exit(1)


def load_data_to_duckdb(path: str, con: duckdb.DuckDBPyConnection):
    """Load CSV, Parquet, or Excel file into DuckDB and create a table named 'events'."""
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
    elif file_extension in [".xlsx", ".xls"]:
        import pandas as pd
        df = pd.read_excel(path)
        con.execute("CREATE TABLE events AS SELECT * FROM df")
    else:
        raise ValueError(
            f"Unsupported file format: {file_extension}. "
            f"Supported formats: .csv, .parquet, .xlsx, .xls"
        )


def get_schema(con: duckdb.DuckDBPyConnection) -> str:
    """Return a simple schema description for the 'events' table."""
    rows = con.execute("PRAGMA table_info('events')").fetchall()
    schema_lines = []
    for row in rows:
        _, name, col_type, *_ = row
        schema_lines.append(f"{name} ({col_type})")
    return ", ".join(schema_lines)


def show_basic_stats(
    con: duckdb.DuckDBPyConnection, console: Console, show_schema: bool = True
) -> None:
    """Show basic statistics about the loaded data."""
    # Get row count
    result = con.execute("SELECT COUNT(*) FROM events").fetchone()
    row_count = result[0] if result else 0

    # Get column count and info
    columns = con.execute("PRAGMA table_info('events')").fetchall()
    col_count = len(columns)

    console.print("\n[bold green]Dataset Statistics[/bold green]")
    console.print(f"• Rows: [cyan]{row_count:,}[/cyan]")
    console.print(f"• Columns: [cyan]{col_count}[/cyan]")

    # Show column info in a table only if show_schema is True
    if show_schema and columns:
        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE,
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
    client: Union[AzureOpenAI, OpenAI], question: str, schema_info: str, model_name: str
) -> str:
    """Ask AI to translate a natural language question into SQL."""
    prompt = f"""
You are a data assistant.
The user asks questions about a table named 'events'.
Schema of events: {schema_info}

Return ONLY valid SQL for DuckDB, nothing else.
SQL should start with SELECT and must reference the 'events' table.

User question: {question}
"""

    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=float(os.getenv("MODEL_TEMPERATURE", "0.1")),
        max_tokens=500,
    )

    # Track token usage
    token_tracker.add_usage(response.usage)

    content = response.choices[0].message.content
    if content is None:
        raise ValueError("No content returned from AI")

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
    client: Union[AzureOpenAI, OpenAI],
    query: str,
    schema_info: str,
    con: duckdb.DuckDBPyConnection,
    show_sql: bool,
    console: Console,
    model_name: str,
    show_data: bool = True,
):
    """Process a single query and display results."""
    try:
        console.print("[dim]Analyzing your question...[/dim]")
        sql = llm_to_sql(client, query, schema_info, model_name)
        if show_sql:
            console.print(f"[cyan]SQL:[/cyan] [bold]{sql}[/bold]")

        console.print("[dim]Executing query...[/dim]")
        res = con.execute(sql).df()

        if len(res) == 0:
            console.print("[yellow]No results found.[/yellow]")
        else:
            # Only show raw data table if show_data flag is set
            if show_data:
                # Create a rich table for better formatting
                table = Table(
                    show_header=True,
                    header_style="bold magenta",
                    box=box.SIMPLE,
                )

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
                    msg = f"[dim]Showing first 20 of {len(res)} rows[/dim]"
                    console.print(msg)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


def main():
    console = Console()

    try:
        # Display logo
        print_logo(console)

        # Parse command line arguments
        epilog_text = """
examples:
  dtalk data.csv
  dtalk report.xlsx
  dtalk data.parquet --show-sql
  dtalk data.csv -p 'How many rows are there?'
  dtalk sales.xlsx -p 'What are the top 5 products?' --show-sql
"""
        parser = argparse.ArgumentParser(
            description="",
            epilog=epilog_text,
            add_help=True,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        parser.add_argument("file", nargs="?", help="CSV, Excel, or Parquet file to analyze")
        parser.add_argument(
            "-p", "--prompt", help="Run a single query in non-interactive mode"
        )
        parser.add_argument(
            "-c",
            "--config-info",
            action="store_true",
            help="Show configuration file location and exit",
        )
        parser.add_argument(
            "--reset-config",
            action="store_true",
            help="Reset (clear) all saved configuration and exit",
        )
        parser.add_argument(
            "-q", "--show-sql", action="store_true", help="Show generated SQL queries"
        )
        parser.add_argument(
            "--hide-data",
            action="store_true",
            help="Hide detailed dataset information and raw query results",
        )
        parser.add_argument(
            "--hide-schema",
            action="store_true",
            help="Hide detailed column information table",
        )
        parser.add_argument(
            "-t",
            "--show-tokens",
            action="store_true",
            help="Show token usage statistics",
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
                    console.print("[dim]Current configuration:[/dim]")
                    for key, value in config.items():
                        if "key" in key.lower() or "password" in key.lower():
                            # Mask sensitive values
                            masked = value[:8] + "..." if len(value) > 8 else "***"
                            console.print(f"  {key}: [dim]{masked}[/dim]")
                        else:
                            console.print(f"  {key}: [dim]{value}[/dim]")
                else:
                    console.print("[yellow]Configuration file is empty[/yellow]")
            else:
                console.print("[yellow]Configuration file does not exist[/yellow]")
            return

        # Handle config reset request
        if args.reset_config:
            config_path = get_config_path()
            if config_path.exists():
                config_path.unlink()
                console.print("[green]✓[/green] Configuration file deleted")
                console.print(f"[dim]Removed: {config_path}[/dim]")
            else:
                console.print("[yellow]No configuration file to delete[/yellow]")
            return

        if not args.file:
            console.print("[red]Error:[/red] CSV or Parquet file is required")
            console.print()
            parser.print_help()
            sys.exit(1)

        # Load .env file if it exists (but don't require it)
        load_dotenv()

        # Load saved configuration
        config = load_config()

        # Auto-detect provider
        provider = detect_provider(config, console)

        # Setup AI client based on provider
        client, model_name = setup_ai_client(provider, config, console)

        # Display version and provider
        try:
            app_version = version("datatalk-cli")
        except PackageNotFoundError:
            app_version = "unknown"
        
        provider_name = "Azure OpenAI" if provider == "azure" else "OpenAI"
        version_text = f"DataTalk v{app_version} — powered by {provider_name}"
        console.print(version_text, highlight=False)

        path = args.file
        con = duckdb.connect()
        load_data_to_duckdb(path, con)
        schema_info = get_schema(con)

        console.print("\n[green]Data loaded successfully![/green]")
        show_basic_stats(con, console, not args.hide_schema)

        # Non-interactive mode
        if args.prompt:
            process_query(
                client,
                args.prompt,
                schema_info,
                con,
                args.show_sql,
                console,
                model_name,
                not args.hide_data,
            )
            # Show token usage statistics before exiting
            if args.show_tokens:
                token_tracker.print_statistics(console)
            return

        # Interactive mode
        console.print(
            "Ask questions about your data. "
            "Type 'quit', 'exit', 'stop', or press Ctrl+C to exit.\n"
        )

        while True:
            try:
                # Get user input
                q = Prompt.ask("[bold blue]Question[/bold blue]")
            except EOFError:
                console.print("\n[dim]Goodbye![/dim]\n")
                # Show token usage statistics before exiting
                if args.show_tokens:
                    token_tracker.print_statistics(console)
                break

            if q.lower() in ["quit", "exit", "q", "stop", "bye", "goodbye"]:
                console.print("[dim]Goodbye![/dim]\n")
                # Show token usage statistics before exiting
                if args.show_tokens:
                    token_tracker.print_statistics(console)
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
                model_name,
                not args.hide_data,
            )

    except KeyboardInterrupt:
        console.print("\n[dim]Goodbye![/dim]\n")
        # Show token usage statistics before exiting
        if "args" in locals() and hasattr(args, "show_tokens") and args.show_tokens:
            token_tracker.print_statistics(console)
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        # Show token usage statistics before exiting
        if "args" in locals() and hasattr(args, "show_tokens") and args.show_tokens:
            token_tracker.print_statistics(console)
        sys.exit(1)


if __name__ == "__main__":
    main()
