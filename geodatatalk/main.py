"""GeoDataTalk CLI - Natural language interface for geospatial data files."""

import os
import sys
import argparse
from importlib.metadata import version, PackageNotFoundError

from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt

from geodatatalk.geodatabase import GeoDataSource
from geodatatalk import geoquery
from geodatatalk.geollm import GeoLLMProvider
from geodatatalk.geoprinter import (
    GeoPrinter,
    print_logo,
    print_configuration_help,
    print_file_required_help,
    print_dataset_info,
    print_query_results,
    output_json,
)


class CleanArgumentParser(argparse.ArgumentParser):
    """ArgumentParser with clean error messages (no program name prefix)."""

    def error(self, message):
        """Print error message without program name prefix."""
        self.print_usage(sys.stderr)
        self.exit(2, f"error: {message}\n")


def main():
    """Main CLI entry point."""
    console = Console()

    try:
        epilog_text = """
examples:
  # Interactive mode
  gdtalk roads.shp
  gdtalk elevation.tif

  # Single query with different outputs
  gdtalk buildings.geojson -p 'How many buildings?'
  gdtalk roads.shp -p 'Show roads longer than 1km'
  gdtalk elevation.tif -p 'What is the elevation range?' --json

  # Other options
  gdtalk data.gpkg --no-schema                         # Hide schema table
  gdtalk parcels.shp -p 'Count parcels' --operation    # Show operation details
"""
        parser = CleanArgumentParser(
            prog="gdtalk",
            description="",
            epilog=epilog_text,
            add_help=True,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        parser.add_argument("file", nargs="?", help="Geospatial file to analyze (vector or raster)")

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

        # Display options
        parser.add_argument(
            "--operation",
            action="store_true",
            help="Show generated operation details"
        )
        parser.add_argument(
            "--no-schema",
            action="store_true",
            help="Don't show field/band details table when loading data",
        )

        args = parser.parse_args()

        # Validate format options require -p
        if args.json and not args.prompt:
            parser.error("--json requires -p/--prompt (non-interactive mode)")

        # Create printer (quiet in non-interactive mode)
        printer = GeoPrinter(console, quiet=args.prompt is not None)

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
        provider = GeoLLMProvider(model)

        # Display version and model info
        try:
            app_version = version("geodatatalk-cli")
        except PackageNotFoundError:
            app_version = "0.1.0"

        version_text = f"GeoDataTalk v{app_version} — powered by {model} & GDAL"
        printer.decorative(version_text, highlight=False)

        # Load geospatial data
        path = args.file
        printer.decorative(f"\n[dim]Loading geospatial data from {path}...[/dim]", highlight=False)

        try:
            geo_source = GeoDataSource(path)
        except Exception as e:
            printer.result(f"\n[red]Error loading file:[/red] {e}", highlight=False)
            sys.exit(1)

        data_info = geo_source.get_info()

        printer.decorative("\n[green]Data loaded successfully![/green]", highlight=False)

        # Display dataset information
        print_dataset_info(data_info, printer, not args.no_schema)

        # Non-interactive mode
        if args.prompt:
            result = geoquery.process_query(
                provider,
                args.prompt,
                geo_source,
                data_info,
                printer,
            )

            if result["error"]:
                if args.json:
                    output_json(result["result"], result["operation"])
                else:
                    printer.result(f"\n[red]Error:[/red] {result['error']}\n", highlight=False)
                geo_source.close()
                sys.exit(1)

            # Machine-readable output (JSON)
            if args.json:
                output_json(result["result"], result["operation"])
            # Human-readable output (non-interactive mode)
            else:
                # Show operation if requested
                if args.operation:
                    printer.result(f"\n[cyan]Operation:[/cyan] {result['operation']}", highlight=False)

                # Show results
                print_query_results(result["result"], printer)

            geo_source.close()
            return

        # Interactive mode
        printer.result(
            "Ask questions about your geospatial data. "
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

            result = geoquery.process_query(
                provider,
                q,
                geo_source,
                data_info,
                printer,
            )

            if result["error"]:
                printer.result(f"\n[red]Error:[/red] {result['error']}\n", highlight=False)
            else:
                if args.operation:
                    printer.result(f"\n[cyan]Operation:[/cyan] {result['operation']}", highlight=False)

                print_query_results(result["result"], printer)

        geo_source.close()

    except KeyboardInterrupt:
        console.print("\n[dim]Goodbye![/dim]\n", highlight=False)
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}", highlight=False)
        sys.exit(1)


if __name__ == "__main__":
    main()
