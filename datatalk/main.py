"""DataTalk CLI - Natural language interface for data files."""

import os
import sys
import json
import argparse
from importlib.metadata import version, PackageNotFoundError
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from rich import box
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from datatalk import database, query
from datatalk.llm import LiteLLMProvider


# ============================================================================
# Terminal Rendering Functions
# ============================================================================


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
    console.print(logo, highlight=False)


def print_configuration_help(console: Console) -> None:
    """Print helpful configuration message when LLM_MODEL is not set."""
    console.print("[yellow]⚠️  Please configure your LLM model first[/yellow]\n", highlight=False)
    console.print("[bold]Quick setup:[/bold]", highlight=False)
    console.print("  [cyan]export LLM_MODEL=gpt-4o[/cyan]", highlight=False)
    console.print("  [cyan]export OPENAI_API_KEY=your-key[/cyan]\n", highlight=False)
    console.print("[bold]Popular models:[/bold]", highlight=False)
    console.print("  [green]•[/green] gpt-4o, gpt-4o-mini, gpt-3.5-turbo [dim](OpenAI)[/dim]", highlight=False)
    console.print("  [green]•[/green] azure/gpt-4o [dim](Azure OpenAI)[/dim]", highlight=False)
    console.print("  [green]•[/green] claude-3-5-sonnet-20241022 [dim](Anthropic)[/dim]", highlight=False)
    console.print("  [green]•[/green] gemini-1.5-flash, gemini-1.5-pro [dim](Google)[/dim]", highlight=False)
    console.print("  [green]•[/green] ollama/llama3.1, ollama/mistral [dim](Ollama - local)[/dim]\n", highlight=False)
    console.print("📚 Full guide: [blue]https://github.com/vtsaplin/datatalk-cli#configuration[/blue]", highlight=False)


def print_file_required_help(console: Console) -> None:
    """Print helpful message when no data file is specified."""
    console.print("\n[yellow]📄 Please specify a data file to analyze[/yellow]\n", highlight=False)
    console.print("[bold]Usage:[/bold]", highlight=False)
    console.print("  [cyan]dtalk[/cyan] [green]<file>[/green] [dim][question][/dim]\n", highlight=False)
    console.print("[bold]Examples:[/bold]", highlight=False)
    console.print("  [cyan]dtalk[/cyan] [green]data.csv[/green]", highlight=False)
    console.print("  [cyan]dtalk[/cyan] [green]report.xlsx[/green] [dim]-p 'What are the top 5 products?'[/dim]", highlight=False)
    console.print("  [cyan]dtalk[/cyan] [green]data.parquet[/green] [dim]-s[/dim]\n", highlight=False)
    console.print("[bold]Supported formats:[/bold] CSV, Excel (.xlsx, .xls), Parquet", highlight=False)
    console.print()


def print_stats(stats: dict[str, Any], console: Console, show_schema: bool = True) -> None:
    """Render dataset statistics."""
    row_count = stats["row_count"]
    col_count = stats["col_count"]
    columns = stats["columns"]

    console.print("\n[bold green]Dataset Statistics[/bold green]", highlight=False)
    console.print(f"• Rows: [cyan]{row_count:,}[/cyan]", highlight=False)
    console.print(f"• Columns: [cyan]{col_count}[/cyan]", highlight=False)

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

        for col in columns:
            table.add_row(col["name"], col["type"], col["samples"])

        console.print(table)

    console.print()


def print_query_results(df: pd.DataFrame, console: Console, limit: int = 20) -> None:
    """Render query results as a table."""
    if len(df) == 0:
        console.print("[yellow]No results found.[/yellow]", highlight=False)
        return

    # Create a rich table for better formatting
    table = Table(
        show_header=True,
        header_style="bold magenta",
        box=box.SIMPLE,
    )

    # Add columns
    for col in df.columns:
        table.add_column(col)

    # Add rows (limit to first N for readability)
    row_count = 0
    for _, row in df.iterrows():
        if row_count >= limit:
            ellipsis = ["..." for _ in range(len(df.columns) - 1)]
            table.add_row("...", *ellipsis)
            break
        table.add_row(*[str(val) for val in row])
        row_count += 1

    console.print(table)

    if len(df) > limit:
        msg = f"[dim]Showing first {limit} of {len(df)} rows[/dim]"
        console.print(msg, highlight=False)


def output_json(result: dict[str, Any]) -> None:
    """Output query results as JSON."""
    output = {
        "sql": result["sql"],
        "data": result["dataframe"].to_dict(orient="records") if result["dataframe"] is not None else None,
        "error": result["error"],
    }
    print(json.dumps(output, indent=2, default=str))


def output_csv(df: pd.DataFrame) -> None:
    """Output query results as CSV."""
    if df is not None and len(df) > 0:
        print(df.to_csv(index=False, lineterminator="\n"), end="")


# ============================================================================
# Main CLI Entry Point
# ============================================================================


class CleanArgumentParser(argparse.ArgumentParser):
    """ArgumentParser with clean error messages (no program name prefix)."""
    
    def error(self, message):
        """Print error message without program name prefix."""
        self.print_usage(sys.stderr)
        # Only 'error:' prefix, no program name
        self.exit(2, f"error: {message}\n")


def main():
    """Main CLI entry point."""
    console = Console()

    try:
        # Display logo
        print_logo(console)

        # Parse command line arguments
        epilog_text = """
examples:
  # Interactive mode
  dtalk data.csv
  
  # Single query with different outputs
  dtalk data.csv -p 'How many rows?'
  dtalk data.csv -p 'Top 5 products' -s              # Show SQL
  dtalk data.csv -p 'Count products' --json          # JSON for scripts
  dtalk data.csv -p 'All products' --csv             # CSV for export
  
  # Other options
  dtalk data.csv --no-schema                         # Hide schema table
  dtalk data.csv -p 'query' --sql-only               # Only SQL
"""
        parser = CleanArgumentParser(
            prog="dtalk",
            description="",
            epilog=epilog_text,
            add_help=True,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        parser.add_argument("file", nargs="?", help="CSV, Excel, or Parquet file to analyze")
        
        # Query mode
        parser.add_argument(
            "-p", "--prompt", help="Run a single query in non-interactive mode"
        )
        
        # Output formats (only with -p)
        format_group = parser.add_mutually_exclusive_group()
        format_group.add_argument(
            "--json",
            action="store_true",
            help="Output results as JSON (requires -p, for scripting)",
        )
        format_group.add_argument(
            "--csv",
            action="store_true",
            help="Output results as CSV (requires -p, for export)",
        )
        
        # Display options
        parser.add_argument(
            "-s", "--sql", action="store_true", help="Show generated SQL queries"
        )
        parser.add_argument(
            "--no-schema",
            action="store_true",
            help="Don't show column details table when loading data",
        )
        parser.add_argument(
            "--sql-only",
            action="store_true",
            help="Show only SQL query without executing it",
        )

        args = parser.parse_args()
        
        # Validate format options require -p
        if (args.json or args.csv) and not args.prompt:
            parser.error("--json and --csv require -p/--prompt (non-interactive mode)")

        # Load .env file if it exists (but don't require it)
        load_dotenv()

        # Get LLM model from environment - check this FIRST as it's more fundamental
        model = os.getenv("LLM_MODEL")
        if not model:
            print_configuration_help(console)
            sys.exit(1)

        # Then check if file is provided
        if not args.file:
            print_file_required_help(console)
            sys.exit(1)

        # Create LLM provider
        provider = LiteLLMProvider(model)

        # Display version and model info
        try:
            app_version = version("datatalk-cli")
        except PackageNotFoundError:
            app_version = "unknown"
        
        version_text = f"DataTalk v{app_version} — powered by {model}"
        console.print(version_text, highlight=False)

        # Create database connection and load data
        path = args.file
        con = database.create_connection()
        database.load_data(con, path)
        schema_info = database.get_schema(con)

        console.print("\n[green]Data loaded successfully![/green]", highlight=False)
        
        # Get and display statistics
        stats = database.get_stats(con)
        print_stats(stats, console, not args.no_schema)

        # Non-interactive mode
        if args.prompt:
            result = query.process_query(
                provider,
                args.prompt,
                schema_info,
                con,
                console,
            )
            
            if result["error"]:
                if args.json:
                    output_json(result)
                else:
                    console.print(f"[red]Error:[/red] {result['error']}", highlight=False)
                sys.exit(1)
            
            # JSON output (machine-readable)
            if args.json:
                output_json(result)
            # CSV output (export format)
            elif args.csv:
                output_csv(result["dataframe"])
            # Standard output (human-readable)
            else:
                # Show SQL if requested (--sql or --sql-only)
                if args.sql or args.sql_only:
                    console.print(f"[cyan]SQL:[/cyan] [bold]{result['sql']}[/bold]", highlight=False)
                
                # Show data unless --sql-only is specified
                if not args.sql_only:
                    print_query_results(result["dataframe"], console)
            
            return

        # Interactive mode
        console.print(
            "Ask questions about your data. "
            "Type 'quit', 'exit', 'stop', or press Ctrl+C to exit.\n",
            highlight=False
        )

        while True:
            try:
                # Get user input
                q = Prompt.ask("[bold blue]Question[/bold blue]")
            except EOFError:
                console.print("\n[dim]Goodbye![/dim]\n", highlight=False)
                break

            if q.lower() in ["quit", "exit", "q", "stop", "bye", "goodbye"]:
                console.print("[dim]Goodbye![/dim]\n", highlight=False)
                break
            if not q.strip():
                continue

            result = query.process_query(
                provider,
                q,
                schema_info,
                con,
                console,
            )
            
            if result["error"]:
                console.print(f"[red]Error:[/red] {result['error']}", highlight=False)
            else:
                # Show SQL if requested (--sql or --sql-only)
                if args.sql or args.sql_only:
                    console.print(f"[cyan]SQL:[/cyan] [bold]{result['sql']}[/bold]", highlight=False)
                
                # Show data unless --sql-only is specified
                if not args.sql_only:
                    print_query_results(result["dataframe"], console)

    except KeyboardInterrupt:
        console.print("\n[dim]Goodbye![/dim]\n", highlight=False)
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}", highlight=False)
        sys.exit(1)


if __name__ == "__main__":
    main()
