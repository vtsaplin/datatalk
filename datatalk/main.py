import sys
import duckdb
import os
import argparse
from pathlib import Path
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich import box
from typing import Union

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
[dim]Ask questions about your CSV/Parquet data using natural language[/dim]
"""
    console.print(logo)


def get_openai_config(config: dict[str, str], console: Console) -> tuple[str, str]:
    """Get OpenAI configuration."""
    api_key = get_env_var("OPENAI_API_KEY", config, console)
    model = get_env_var("OPENAI_MODEL", config, console)

    console.print("[green]✓[/green] Using OpenAI configuration")
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
        console.print("[dim]Azure OpenAI configuration detected[/dim]")
        return "azure"

    if has_openai_env or has_openai_config:
        console.print("[dim]OpenAI configuration detected[/dim]")
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
            console.print("\n[dim]Operation cancelled. Goodbye![/dim]")
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


def generate_sample_queries(
    con: duckdb.DuckDBPyConnection,
    client: Union[AzureOpenAI, OpenAI],
    model_name: str,
    schema_info: str,
    last_query: str | None = None,
) -> list[str]:
    """Generate sample queries using AI analysis of the actual data."""
    try:
        # Get basic data info for LLM analysis
        result = con.execute("SELECT COUNT(*) FROM events").fetchone()
        row_count = result[0] if result else 0
        columns = con.execute("PRAGMA table_info('events')").fetchall()

        # Get sample data to help LLM understand the content
        sample_data = con.execute("SELECT * FROM events LIMIT 5").fetchall()
        column_names = [col[1] for col in columns]

        # Format sample data for LLM
        sample_rows = []
        for row in sample_data:
            row_dict = {}
            for i, value in enumerate(row):
                if i < len(column_names):
                    # Truncate long values
                    str_value = str(value)
                    if len(str_value) > 50:
                        str_value = str_value[:50] + "..."
                    row_dict[column_names[i]] = str_value
            sample_rows.append(row_dict)

        # Create prompt for LLM, adapting based on whether there's a last query
        if last_query:
            prompt = f"""
You are a data analyst. A user just asked: "{last_query}"

Based on this previous question and the dataset below, suggest 5 follow-up questions
that would naturally complement or build upon their previous query.

Dataset Info:
- Schema: {schema_info}
- Total rows: {row_count:,}
- Sample data (first 5 rows): {sample_rows}

Requirements:
1. Generate questions that logically follow from their previous question
2. Focus on deeper insights or related analysis
3. Questions should be in natural language
4. Return ONLY the questions, one per line
5. No numbering or bullet points

Example format:
What is the total number of pageviews?
Which device type has the highest bounce rate?
"""
        else:
            prompt = f"""
You are a data analyst. Given this dataset information, suggest 5 interesting
and practical starter questions that a user might want to ask about this data.

Dataset Info:
- Schema: {schema_info}
- Total rows: {row_count:,}
- Sample data (first 5 rows): {sample_rows}

Requirements:
1. Generate questions that are specific to this data
2. Focus on actionable insights and patterns
3. Mix simple and analytical questions
4. Questions should be in natural language
5. Return ONLY the questions, one per line
6. No numbering or bullet points

Example format:
What is the total number of pageviews?
Which device type has the highest bounce rate?
"""

        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )

        # Track token usage
        token_tracker.add_usage(response.usage)

        content = response.choices[0].message.content
        if content is None:
            raise ValueError("No content returned from AI")

        # Parse the response into individual queries
        queries = [q.strip() for q in content.strip().split("\n") if q.strip()]

        # Filter out any numbered or bulleted items
        clean_queries = []
        for query in queries:
            # Remove common prefixes
            query = query.lstrip("- •*").strip()
            if query and not query[0].isdigit():
                clean_queries.append(query)
            elif query and query[0].isdigit():
                # Remove number prefix like "1. "
                parts = query.split(".", 1)
                if len(parts) > 1:
                    clean_queries.append(parts[1].strip())

        return clean_queries[:5]  # Limit to 5 queries

    except Exception as e:
        # Fallback to basic queries if LLM fails
        fallback_msg = f"Warning: Could not generate LLM-based queries ({e})."
        print(f"{fallback_msg} Using fallback.")
        if last_query:
            return [
                "Show me more details about this data",
                "What are some related patterns?",
                "How does this compare to other segments?",
                "What trends can we identify?",
                "Are there any outliers or anomalies?",
            ]
        else:
            return [
                "How many rows are in the dataset?",
                "Show me the first 10 rows",
                "What are the column names?",
                "Show me some summary statistics",
                "What are the unique values in the first column?",
            ]


def interpret_results(
    client: Union[AzureOpenAI, OpenAI],
    question: str,
    sql_query: str,
    results_df,
    model_name: str,
) -> str:
    """Send query results to AI for interpretation and insights."""
    # Convert results to a readable format for the LLM
    if len(results_df) == 0:
        results_summary = "No data returned from the query."
    else:
        # Limit to first 10 rows and format nicely
        limited_df = results_df.head(10)
        results_summary = limited_df.to_string(index=False)

        if len(results_df) > 10:
            total_rows = len(results_df)
            note = f"\n\n[Note: Showing first 10 of {total_rows} total rows]"
            results_summary += note

    prompt = f"""
You are a data analyst assistant. A user asked a question about their data and
received the following results. Please provide a clear, concise summary.

User's Question: {question}
Query Results: {results_summary}

Provide a 2-3 sentence summary. ALWAYS format numbers and percentages in bold.

Example: "The average bounce rate is **65.5%**" or "There are **1,234**
total records"

Focus on:
- Direct answer with bold numbers
- What the data shows
- Any notable patterns

Maximum 100 words.
"""

    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=200,
    )

    # Track token usage
    token_tracker.add_usage(response.usage)

    content = response.choices[0].message.content
    if content is None:
        raise ValueError("No content returned from AI")

    return content.strip()


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

            # Send results to AI for summarization
            console.print("[dim]Getting summary from AI...[/dim]")
            try:
                interpretation = interpret_results(client, query, sql, res, model_name)
                console.print("\n[bold green]AI Summary:[/bold green]")
                # Render markdown for better formatting
                markdown = Markdown(interpretation)
                console.print(markdown)
            except Exception as e:
                msg = "[yellow]Note: Could not generate AI summary " "({e})[/yellow]"
                console.print(msg.format(e=e))

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


def main():
    console = Console()

    try:
        # Display logo
        print_logo(console)

        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description=("Ask questions about CSV/Parquet data using natural language")
        )
        parser.add_argument("file", nargs="?", help="CSV or Parquet file to analyze")
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

        # Check if file argument is provided when not using config options
        if not args.file:
            console.print("[red]Error:[/red] CSV or Parquet file is required")
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

        path = args.file
        con = duckdb.connect()
        load_data_to_duckdb(path, con)
        schema_info = get_schema(con)

        console.print("[green]Data loaded successfully![/green]")
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
        console.print("[bold green]AI Assistant Ready![/bold green]")
        console.print(
            "Ask questions about your data. "
            "Type 'quit', 'exit', or 'stop' to quit.\n"
        )

        # Initialize tracking variables
        last_query = None
        sample_queries = []

        # Function to refresh suggestions
        def refresh_suggestions():
            nonlocal sample_queries
            sample_queries = generate_sample_queries(
                con, client, model_name, schema_info, last_query
            )
            if sample_queries:
                if last_query:
                    console.print("[bold]New suggested questions:[/bold]")
                else:
                    console.print("[bold]Suggested questions to get started:[/bold]")
                for i, query in enumerate(sample_queries, 1):
                    console.print(f"  {i}. {query}")
                console.print()

        # Show initial suggestions
        refresh_suggestions()

        while True:
            try:
                # Get user input
                prompt_text = "[bold blue]Ask a question or choose 1-5[/bold blue]"
                q = Prompt.ask(prompt_text)
            except EOFError:
                console.print("\n[dim]Goodbye![/dim]")
                # Show token usage statistics before exiting
                if args.show_tokens:
                    token_tracker.print_statistics(console)
                break

            if q.lower() in ["quit", "exit", "q", "stop", "bye", "goodbye"]:
                console.print("[dim]Goodbye![/dim]")
                # Show token usage statistics before exiting
                if args.show_tokens:
                    token_tracker.print_statistics(console)
                break
            if not q.strip():
                continue

            # Check if user chose a suggestion number
            selected_query = None
            if q.strip().isdigit():
                choice_num = int(q.strip())
                if 1 <= choice_num <= len(sample_queries):
                    selected_query = sample_queries[choice_num - 1]
                    console.print(f"[dim]Selected: {selected_query}[/dim]")
                else:
                    console.print(f"[red]Please choose 1-{len(sample_queries)}[/red]")
                    continue

            # Use selected query or user's own question
            query_to_process = selected_query if selected_query else q

            process_query(
                client,
                query_to_process,
                schema_info,
                con,
                args.show_sql,
                console,
                model_name,
                not args.hide_data,
            )

            # Update last query and refresh suggestions
            last_query = query_to_process
            console.print()  # Add blank line for spacing
            refresh_suggestions()

    except KeyboardInterrupt:
        console.print("\n[dim]Operation cancelled. Goodbye![/dim]")
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
