"""DataTalk CLI - Natural language interface for data files."""

import os
import sys
import json
import argparse
from importlib.metadata import version, PackageNotFoundError
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt

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

        # Create printer (quiet in non-interactive mode)
        printer = Printer(console, quiet=args.prompt is not None)
        
        print_logo(printer)

        # Load .env file if it exists (but don't require it)
        load_dotenv()

        # Get LLM model from environment
        model = os.getenv("LLM_MODEL")
        if not model:
            print_configuration_help(printer)
            sys.exit(1)

        # Check if file is provided
        if not args.file:
            print_file_required_help(printer)
            sys.exit(1)

        # Create LLM provider
        provider = LiteLLMProvider(model)

        # Display version and model info
        try:
            app_version = version("datatalk-cli")
        except PackageNotFoundError:
            app_version = "unknown"
        
        version_text = f"DataTalk v{app_version} — powered by {model}"
        printer.decorative(version_text, highlight=False)

        # Create database connection and load data
        path = args.file
        con = database.create_connection()
        database.load_data(con, path)
        schema_info = database.get_schema(con)

        printer.decorative("\n[green]Data loaded successfully![/green]", highlight=False)
        
        # Get and display statistics
        stats = database.get_stats(con)
        print_stats(stats, printer, not args.no_schema)

        # Non-interactive mode
        if args.prompt:
            result = query.process_query(
                provider,
                args.prompt,
                schema_info,
                con,
                printer,
            )
            
            if result["error"]:
                if args.json:
                    output_json(result)
                elif args.csv:
                    sys.stderr.write(f"Error: {result['error']}\n")
                else:
                    printer.result(f"\n[red]Error:[/red] {result['error']}\n", highlight=False)
                sys.exit(1)
            
            # Machine-readable output (JSON/CSV)
            if args.json:
                output_json(result)
            elif args.csv:
                output_csv(result["dataframe"])
            # Human-readable output (non-interactive mode)
            else:
                # Show SQL if requested (--sql or --sql-only)
                if args.sql or args.sql_only:
                    printer.result(f"[cyan]SQL:[/cyan] [bold]{result['sql']}[/bold]", highlight=False)
                
                # Show data unless --sql-only is specified
                if not args.sql_only:
                    print_query_results(result["dataframe"], printer)
            
            return

        # Interactive mode
        printer.result(
            "Ask questions about your data. "
            "Type 'quit', 'exit', 'stop', or press Ctrl+C to exit.\n",
            highlight=False
        )

        while True:
            try:
                q = Prompt.ask("[bold blue]Question[/bold blue]")
            except EOFError:
                printer.result("\n[dim]Goodbye![/dim]\n", highlight=False)
                break

            if q.lower() in ["quit", "exit", "q", "stop", "bye", "goodbye"]:
                printer.result("[dim]Goodbye![/dim]\n", highlight=False)
                break
            if not q.strip():
                continue

            result = query.process_query(
                provider,
                q,
                schema_info,
                con,
                printer,
            )
            
            if result["error"]:
                printer.result(f"\n[red]Error:[/red] {result['error']}\n", highlight=False)
                sys.exit(1)
            else:
                if args.sql or args.sql_only:
                    printer.result(f"[cyan]SQL:[/cyan] [bold]{result['sql']}[/bold]", highlight=False)
                
                if not args.sql_only:
                    print_query_results(result["dataframe"], printer)

    except KeyboardInterrupt:
        console.print("\n[dim]Goodbye![/dim]\n", highlight=False)
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}", highlight=False)
        sys.exit(1)


if __name__ == "__main__":
    main()
