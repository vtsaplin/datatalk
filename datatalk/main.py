"""DataTalk CLI - Natural language interface for data files."""

import sys
import argparse
from importlib.metadata import version, PackageNotFoundError

from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt

from datatalk import database, query, renderer
from datatalk.config import get_config_path, load_config
from datatalk.llm import create_provider


def main():
    """Main CLI entry point."""
    console = Console()

    try:
        # Display logo
        renderer.print_logo(console)

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

        # Create LLM provider using factory pattern
        provider = create_provider(config, console)

        # Display version and provider info
        try:
            app_version = version("datatalk-cli")
        except PackageNotFoundError:
            app_version = "unknown"
        
        provider_name = provider.__class__.__name__.replace("Provider", "")
        version_text = f"DataTalk v{app_version} — powered by {provider_name}"
        console.print(version_text, highlight=False)

        # Create database connection and load data
        path = args.file
        con = database.create_connection()
        database.load_data(con, path)
        schema_info = database.get_schema(con)

        console.print("\n[green]Data loaded successfully![/green]")
        
        # Get and display statistics
        stats = database.get_stats(con)
        renderer.print_stats(stats, console, not args.hide_schema)

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
                console.print(f"[red]Error:[/red] {result['error']}")
            else:
                if args.show_sql:
                    console.print(f"[cyan]SQL:[/cyan] [bold]{result['sql']}[/bold]")
                
                if not args.hide_data:
                    renderer.print_query_results(result["dataframe"], console)
            
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
                break

            if q.lower() in ["quit", "exit", "q", "stop", "bye", "goodbye"]:
                console.print("[dim]Goodbye![/dim]\n")
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
                console.print(f"[red]Error:[/red] {result['error']}")
            else:
                if args.show_sql:
                    console.print(f"[cyan]SQL:[/cyan] [bold]{result['sql']}[/bold]")
                
                if not args.hide_data:
                    renderer.print_query_results(result["dataframe"], console)

    except KeyboardInterrupt:
        console.print("\n[dim]Goodbye![/dim]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
