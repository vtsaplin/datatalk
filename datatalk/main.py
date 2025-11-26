"""DataTalk CLI - Natural language interface for data files."""

import atexit
import os
import sys
import json
import argparse
import readline
import termios
from importlib.metadata import version, PackageNotFoundError
from typing import Any

import duckdb
import pandas as pd
from dotenv import load_dotenv
from rich.console import Console

from datatalk import database, query
from datatalk.llm import LiteLLMProvider
from datatalk.printer import (
    Printer,
    print_logo,
    print_configuration_help,
    print_file_required_help,
    print_stats,
    print_query_results,
)

HISTORY_FILE = os.path.expanduser("~/.datatalk_history")
EXIT_COMMANDS = {"quit", "exit", "q", "stop", "bye", "goodbye"}


class ArgumentParserWithShortErrors(argparse.ArgumentParser):
    """ArgumentParser that shows 'error: message' instead of 'prog: error: message'."""
    
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, f"error: {message}\n")


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser."""
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

    parser = ArgumentParserWithShortErrors(
        prog="dtalk",
        description="",
        epilog=epilog_text,
        add_help=True,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("file", nargs="?", help="CSV, Excel, or Parquet file to analyze")
    parser.add_argument("-p", "--prompt", help="Run a single query in non-interactive mode")
    
    format_group = parser.add_mutually_exclusive_group()
    format_group.add_argument("--json", action="store_true", help="Output results as JSON (requires -p)")
    format_group.add_argument("--csv", action="store_true", help="Output results as CSV (requires -p)")
    
    parser.add_argument("-s", "--sql", action="store_true", help="Show generated SQL queries")
    parser.add_argument("--no-schema", action="store_true", help="Don't show column details table")
    parser.add_argument("--sql-only", action="store_true", help="Show only SQL query without executing")

    return parser


def validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace, printer: Printer) -> None:
    """Validate argument combinations."""
    if (args.json or args.csv) and not args.prompt:
        parser.error("--json and --csv require -p/--prompt (non-interactive mode)")
    
    if not args.file:
        print_file_required_help(printer)
        sys.exit(1)


def setup_environment(args: argparse.Namespace, printer: Printer) -> LiteLLMProvider:
    """Load config and create LLM provider."""
    load_dotenv()

    model = os.getenv("LLM_MODEL")
    if not model:
        print_configuration_help(printer)
        sys.exit(1)

    try:
        app_version = version("datatalk-cli")
    except PackageNotFoundError:
        app_version = "unknown"
    
    printer.decorative(f"DataTalk v{app_version} — powered by {model}", highlight=False)
    
    return LiteLLMProvider(model)


def load_data(args: argparse.Namespace, printer: Printer) -> tuple[duckdb.DuckDBPyConnection, str]:
    """Load data file and return database connection with schema."""
    con = database.create_connection()
    database.load_data(con, args.file)
    schema_info = database.get_schema(con)

    printer.decorative("\n[green]Data loaded successfully![/green]", highlight=False)
    
    stats = database.get_stats(con)
    print_stats(stats, printer, not args.no_schema)
    
    return con, schema_info


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


def print_result(result: dict[str, Any], args: argparse.Namespace, printer: Printer) -> None:
    """Print query result based on output format."""
    if args.sql or args.sql_only:
        printer.result(f"[cyan]SQL:[/cyan] [bold]{result['sql']}[/bold]", highlight=False)
    
    if not args.sql_only:
        print_query_results(result["dataframe"], printer)


def run_single_query(
    args: argparse.Namespace,
    provider: LiteLLMProvider,
    schema_info: str,
    con: duckdb.DuckDBPyConnection,
    printer: Printer,
) -> None:
    """Execute a single query in non-interactive mode."""
    result = query.process_query(provider, args.prompt, schema_info, con, printer)
    
    if result["error"]:
        if args.json:
            output_json(result)
        elif args.csv:
            sys.stderr.write(f"Error: {result['error']}\n")
        else:
            printer.result(f"\n[red]Error:[/red] {result['error']}\n", highlight=False)
        sys.exit(1)
    
    if args.json:
        output_json(result)
    elif args.csv:
        output_csv(result["dataframe"])
    else:
        print_result(result, args, printer)


def setup_history() -> None:
    """Load command history and register save on exit."""
    if os.path.exists(HISTORY_FILE):
        readline.read_history_file(HISTORY_FILE)
    atexit.register(readline.write_history_file, HISTORY_FILE)


def disable_input_echo() -> list | None:
    """Disable terminal echo and return original settings."""
    if not sys.stdin.isatty():
        return None
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    new_settings = termios.tcgetattr(fd)
    new_settings[3] = new_settings[3] & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
    return old_settings


def restore_input_echo(old_settings: list | None) -> None:
    """Restore terminal settings and clear input buffer."""
    if old_settings is None:
        return
    fd = sys.stdin.fileno()
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    termios.tcflush(fd, termios.TCIFLUSH)


def run_interactive_mode(
    args: argparse.Namespace,
    provider: LiteLLMProvider,
    schema_info: str,
    con: duckdb.DuckDBPyConnection,
    printer: Printer,
) -> None:
    """Run the interactive question-answer loop."""
    setup_history()
    
    printer.result(
        "Ask questions about your data. Use ↑↓ for history. "
        "Type 'quit' or press Ctrl+C to exit.\n",
        highlight=False
    )

    while True:
        try:
            question = input(">>> ")
        except EOFError:
            printer.result("\n[dim]Goodbye![/dim]\n", highlight=False)
            break

        if question.lower() in EXIT_COMMANDS:
            printer.result("[dim]Goodbye![/dim]\n", highlight=False)
            break
        
        if not question.strip():
            continue

        old_settings = disable_input_echo()
        result = query.process_query(provider, question, schema_info, con, printer)
        restore_input_echo(old_settings)
        
        if result["error"]:
            printer.result(f"\n[red]Error:[/red] {result['error']}\n", highlight=False)
            continue
        
        print_result(result, args, printer)


def main():
    """Main CLI entry point."""
    console = Console()

    try:
        parser = create_argument_parser()
        args = parser.parse_args()
        
        printer = Printer(console, quiet=args.prompt is not None)
        print_logo(printer)
        
        validate_args(parser, args, printer)
        provider = setup_environment(args, printer)
        con, schema_info = load_data(args, printer)

        if args.prompt:
            run_single_query(args, provider, schema_info, con, printer)
        else:
            run_interactive_mode(args, provider, schema_info, con, printer)

    except KeyboardInterrupt:
        console.print("\n[dim]Goodbye![/dim]\n", highlight=False)
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}", highlight=False)
        sys.exit(1)


if __name__ == "__main__":
    main()
