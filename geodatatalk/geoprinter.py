"""Console output wrapper for geospatial data visualization."""

import json
from typing import Any, Dict

from rich import box
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree


class GeoPrinter:
    """Console output wrapper with quiet mode support for geospatial data."""

    def __init__(self, console: Console, quiet: bool = False):
        self.console = console
        self.quiet = quiet

    def decorative(self, *args, **kwargs) -> None:
        """Decorative output (banner, stats, progress) - suppressed in quiet mode."""
        if not self.quiet:
            self.console.print(*args, **kwargs)

    def result(self, *args, **kwargs) -> None:
        """Results output - always shown."""
        self.console.print(*args, **kwargs)


def print_logo(printer: GeoPrinter) -> None:
    """Print the GeoDataTalk ASCII logo."""
    logo = """
[bold cyan]
 ██████╗ ███████╗ ██████╗ ██████╗  █████╗ ████████╗ █████╗ ████████╗ █████╗ ██╗     ██╗  ██╗
██╔════╝ ██╔════╝██╔═══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗╚══██╔══╝██╔══██╗██║     ██║ ██╔╝
██║  ███╗█████╗  ██║   ██║██║  ██║███████║   ██║   ███████║   ██║   ███████║██║     █████╔╝
██║   ██║██╔══╝  ██║   ██║██║  ██║██╔══██║   ██║   ██╔══██║   ██║   ██╔══██║██║     ██╔═██╗
╚██████╔╝███████╗╚██████╔╝██████╔╝██║  ██║   ██║   ██║  ██║   ██║   ██║  ██║███████╗██║  ██╗
 ╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
[/bold cyan]
[dim]Ask questions about your geospatial data (vector & raster) in natural language.[/dim]
"""
    printer.decorative(logo, highlight=False)


def print_configuration_help(printer: GeoPrinter) -> None:
    """Print helpful configuration message when LLM_MODEL is not set."""
    printer.result("[yellow]⚠️  Please configure your LLM model first[/yellow]\n", highlight=False)
    printer.result("[bold]Quick setup:[/bold]", highlight=False)
    printer.result("  [cyan]export LLM_MODEL=gpt-4o[/cyan]", highlight=False)
    printer.result("  [cyan]export OPENAI_API_KEY=your-key[/cyan]\n", highlight=False)
    printer.result("[bold]Popular models:[/bold]", highlight=False)
    printer.result("  [green]•[/green] gpt-4o, gpt-4o-mini, gpt-3.5-turbo [dim](OpenAI)[/dim]", highlight=False)
    printer.result("  [green]•[/green] azure/gpt-4o [dim](Azure OpenAI)[/dim]", highlight=False)
    printer.result("  [green]•[/green] claude-3-5-sonnet-20241022 [dim](Anthropic)[/dim]", highlight=False)
    printer.result("  [green]•[/green] gemini-1.5-flash, gemini-1.5-pro [dim](Google)[/dim]", highlight=False)
    printer.result("  [green]•[/green] ollama/llama3.1, ollama/mistral [dim](Ollama - local)[/dim]\n", highlight=False)


def print_file_required_help(printer: GeoPrinter) -> None:
    """Print helpful message when no data file is specified."""
    printer.result("\n[yellow]📄 Please specify a geospatial data file to analyze[/yellow]\n", highlight=False)
    printer.result("[bold]Usage:[/bold]", highlight=False)
    printer.result("  [cyan]gdtalk[/cyan] [green]<file>[/green] [dim][question][/dim]\n", highlight=False)
    printer.result("[bold]Examples:[/bold]", highlight=False)
    printer.result("  [cyan]gdtalk[/cyan] [green]roads.shp[/green]", highlight=False)
    printer.result("  [cyan]gdtalk[/cyan] [green]buildings.geojson[/green] [dim]-p 'How many buildings?'[/dim]", highlight=False)
    printer.result("  [cyan]gdtalk[/cyan] [green]elevation.tif[/green] [dim]-p 'What is the max elevation?'[/dim]\n", highlight=False)
    printer.result("[bold]Supported formats:[/bold] Shapefile, GeoJSON, GeoPackage, KML, GeoTIFF, and more via GDAL/OGR", highlight=False)
    printer.result()


def print_dataset_info(data_info: Dict[str, Any], printer: GeoPrinter, show_details: bool = True) -> None:
    """Print geospatial dataset information."""
    data_type = data_info.get('data_type', 'Unknown')

    printer.decorative("\n[bold green]Dataset Information[/bold green]", highlight=False)
    printer.decorative(f"• Type: [cyan]{data_type.upper()}[/cyan]", highlight=False)

    if data_type == 'vector':
        _print_vector_info(data_info, printer, show_details)
    elif data_type == 'raster':
        _print_raster_info(data_info, printer, show_details)

    printer.decorative()


def _print_vector_info(data_info: Dict[str, Any], printer: GeoPrinter, show_details: bool) -> None:
    """Print vector dataset information."""
    printer.decorative(f"• Geometry: [cyan]{data_info.get('geometry_type', 'Unknown')}[/cyan]", highlight=False)
    printer.decorative(f"• Features: [cyan]{data_info.get('feature_count', 0):,}[/cyan]", highlight=False)
    printer.decorative(f"• Projection: [cyan]{data_info.get('projection', 'Unknown')}[/cyan]", highlight=False)

    if data_info.get('epsg'):
        printer.decorative(f"• EPSG: [cyan]{data_info['epsg']}[/cyan]", highlight=False)

    extent = data_info.get('extent', {})
    if extent:
        printer.decorative(
            f"• Extent: [cyan]({extent.get('min_x', 0):.2f}, {extent.get('min_y', 0):.2f}) to "
            f"({extent.get('max_x', 0):.2f}, {extent.get('max_y', 0):.2f})[/cyan]",
            highlight=False
        )

    # Show fields table
    if show_details and data_info.get('fields'):
        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE,
        )
        table.add_column("Field", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Sample Values", style="dim")

        for field in data_info['fields']:
            samples = field.get('samples', [])
            sample_str = ', '.join([str(s)[:20] for s in samples[:3]])
            if not sample_str:
                sample_str = '[no data]'
            table.add_row(field['name'], field['type'], sample_str)

        printer.decorative(table)


def _print_raster_info(data_info: Dict[str, Any], printer: GeoPrinter, show_details: bool) -> None:
    """Print raster dataset information."""
    printer.decorative(
        f"• Dimensions: [cyan]{data_info.get('width', 0):,} x {data_info.get('height', 0):,}[/cyan] pixels",
        highlight=False
    )
    printer.decorative(f"• Bands: [cyan]{data_info.get('band_count', 0)}[/cyan]", highlight=False)
    printer.decorative(f"• Projection: [cyan]{data_info.get('projection', 'Unknown')}[/cyan]", highlight=False)

    if data_info.get('epsg'):
        printer.decorative(f"• EPSG: [cyan]{data_info['epsg']}[/cyan]", highlight=False)

    pixel_size = data_info.get('pixel_size', {})
    if pixel_size:
        printer.decorative(
            f"• Pixel Size: [cyan]{pixel_size.get('x', 0):.6f} x {pixel_size.get('y', 0):.6f}[/cyan]",
            highlight=False
        )

    extent = data_info.get('extent', {})
    if extent:
        printer.decorative(
            f"• Extent: [cyan]({extent.get('min_x', 0):.2f}, {extent.get('min_y', 0):.2f}) to "
            f"({extent.get('max_x', 0):.2f}, {extent.get('max_y', 0):.2f})[/cyan]",
            highlight=False
        )

    # Show bands table
    if show_details and data_info.get('bands'):
        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.SIMPLE,
        )
        table.add_column("Band", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Interpretation", style="green")
        table.add_column("Min", style="dim")
        table.add_column("Max", style="dim")

        for band in data_info['bands']:
            table.add_row(
                str(band.get('number', '')),
                band.get('data_type', 'Unknown'),
                band.get('color_interpretation', 'Unknown'),
                f"{band.get('min', 'N/A'):.2f}" if isinstance(band.get('min'), (int, float)) else 'N/A',
                f"{band.get('max', 'N/A'):.2f}" if isinstance(band.get('max'), (int, float)) else 'N/A'
            )

        printer.decorative(table)


def print_query_results(result: Dict[str, Any], printer: GeoPrinter) -> None:
    """Print query results based on result type."""
    result_type = result.get('type', 'unknown')

    if result_type == 'description':
        data_info = result.get('data', {})
        print_dataset_info(data_info, printer, show_details=True)

    elif result_type == 'metadata':
        data_info = result.get('data', {})
        print_dataset_info(data_info, printer, show_details=True)

    elif result_type == 'features':
        _print_features(result, printer)

    elif result_type == 'count':
        count = result.get('count', 0)
        total = result.get('total', 0)
        printer.result(f"\n[bold green]Feature Count:[/bold green] [cyan]{count:,}[/cyan]", highlight=False)
        if total != count:
            printer.result(f"[dim](Total features in dataset: {total:,})[/dim]", highlight=False)

    elif result_type == 'statistics':
        _print_statistics(result, printer)

    elif result_type == 'band_statistics':
        _print_band_statistics(result, printer)

    elif result_type == 'pixel_value':
        _print_pixel_value(result, printer)

    else:
        printer.result(f"\n[yellow]Unknown result type: {result_type}[/yellow]", highlight=False)


def _print_features(result: Dict[str, Any], printer: GeoPrinter, limit: int = 20) -> None:
    """Print feature results as a table."""
    features = result.get('features', [])
    count = result.get('count', len(features))

    if not features:
        printer.result("[yellow]No features found.[/yellow]", highlight=False)
        return

    # Build table from features
    table = Table(
        show_header=True,
        header_style="bold magenta",
        box=box.SIMPLE,
        title=f"[bold]Features (showing {min(len(features), limit)} of {count})[/bold]"
    )

    # Get columns from first feature (excluding geometry)
    first_feature = features[0]
    columns = [k for k in first_feature.keys() if k not in ['geometry', 'geometry_type']]

    for col in columns:
        table.add_column(col)

    # Add rows
    for i, feature in enumerate(features[:limit]):
        row_data = []
        for col in columns:
            value = feature.get(col, '')
            value_str = str(value)
            if len(value_str) > 50:
                value_str = value_str[:50] + '...'
            row_data.append(value_str)
        table.add_row(*row_data)

    printer.result(table)

    if len(features) > limit:
        printer.result(f"[dim]Showing first {limit} of {len(features)} features[/dim]", highlight=False)


def _print_statistics(result: Dict[str, Any], printer: GeoPrinter) -> None:
    """Print field statistics."""
    data = result.get('data', {})

    if 'error' in data:
        printer.result(f"\n[yellow]{data['error']}[/yellow]", highlight=False)
        return

    field = data.get('field', 'Unknown')

    table = Table(
        show_header=False,
        box=box.SIMPLE,
        title=f"[bold]Statistics for field: {field}[/bold]"
    )
    table.add_column("Statistic", style="cyan")
    table.add_column("Value", style="yellow")

    table.add_row("Count", f"{data.get('count', 0):,}")
    table.add_row("Min", f"{data.get('min', 0):.2f}")
    table.add_row("Max", f"{data.get('max', 0):.2f}")
    table.add_row("Mean", f"{data.get('mean', 0):.2f}")
    table.add_row("Median", f"{data.get('median', 0):.2f}")

    printer.result(table)


def _print_band_statistics(result: Dict[str, Any], printer: GeoPrinter) -> None:
    """Print raster band statistics."""
    band = result.get('band', 1)
    data = result.get('data', {})

    table = Table(
        show_header=False,
        box=box.SIMPLE,
        title=f"[bold]Band {band} Statistics[/bold]"
    )
    table.add_column("Statistic", style="cyan")
    table.add_column("Value", style="yellow")

    table.add_row("Min", f"{data.get('min', 0):.4f}")
    table.add_row("Max", f"{data.get('max', 0):.4f}")
    table.add_row("Mean", f"{data.get('mean', 0):.4f}")
    table.add_row("Std Dev", f"{data.get('stddev', 0):.4f}")

    printer.result(table)


def _print_pixel_value(result: Dict[str, Any], printer: GeoPrinter) -> None:
    """Print pixel value result."""
    x = result.get('x', 0)
    y = result.get('y', 0)
    band = result.get('band', 1)
    value = result.get('value')

    if value is None:
        printer.result(
            f"\n[yellow]No pixel value at coordinates ({x}, {y}) - outside raster extent[/yellow]",
            highlight=False
        )
    else:
        printer.result(
            f"\n[bold green]Pixel Value:[/bold green] [cyan]{value:.4f}[/cyan]",
            highlight=False
        )
        printer.result(f"[dim]Band {band} at coordinates ({x}, {y})[/dim]", highlight=False)


def output_json(result: Dict[str, Any], operation: Dict[str, Any]) -> None:
    """Output query results as JSON."""
    output = {
        "operation": operation,
        "result": result,
        "error": None,
    }
    # Convert any non-serializable objects
    print(json.dumps(output, indent=2, default=str))
