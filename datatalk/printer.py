"""Console output wrapper with quiet mode support."""

from typing import Any

import pandas as pd
from rich import box
from rich.console import Console
from rich.table import Table


class Printer:
    """Console output wrapper with quiet mode support."""
    
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


def print_logo(printer: Printer) -> None:
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
    printer.decorative(logo, highlight=False)


def print_configuration_help(printer: Printer) -> None:
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
    printer.result("📚 Full guide: [blue]https://github.com/vtsaplin/datatalk-cli#configuration[/blue]", highlight=False)


def print_file_required_help(printer: Printer) -> None:
    """Print helpful message when no data file is specified."""
    printer.result("\n[yellow]📄 Please specify a data file to analyze[/yellow]\n", highlight=False)
    printer.result("[bold]Usage:[/bold]", highlight=False)
    printer.result("  [cyan]dtalk[/cyan] [green]<file>[/green] [dim][question][/dim]\n", highlight=False)
    printer.result("[bold]Examples:[/bold]", highlight=False)
    printer.result("  [cyan]dtalk[/cyan] [green]data.csv[/green]", highlight=False)
    printer.result("  [cyan]dtalk[/cyan] [green]report.xlsx[/green] [dim]-p 'What are the top 5 products?'[/dim]", highlight=False)
    printer.result("  [cyan]dtalk[/cyan] [green]data.parquet[/green] [dim]-s[/dim]\n", highlight=False)
    printer.result("[bold]Supported formats:[/bold] CSV, Excel (.xlsx, .xls), Parquet", highlight=False)
    printer.result()


def print_stats(stats: dict[str, Any], printer: Printer, show_schema: bool = True) -> None:
    """Render dataset statistics."""
    row_count = stats["row_count"]
    col_count = stats["col_count"]
    columns = stats["columns"]

    printer.decorative("\n[bold green]Dataset Statistics[/bold green]", highlight=False)
    printer.decorative(f"• Rows: [cyan]{row_count:,}[/cyan]", highlight=False)
    printer.decorative(f"• Columns: [cyan]{col_count}[/cyan]", highlight=False)

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

        printer.decorative(table)

    printer.decorative()


def print_query_results(df: pd.DataFrame, printer: Printer, limit: int = 20) -> None:
    """Render query results as a table."""
    if len(df) == 0:
        printer.result("[yellow]No results found.[/yellow]", highlight=False)
        return

    table = Table(
        show_header=True,
        header_style="bold magenta",
        box=box.SIMPLE,
    )

    for col in df.columns:
        table.add_column(col)

    row_count = 0
    for _, row in df.iterrows():
        if row_count >= limit:
            ellipsis = ["..." for _ in range(len(df.columns) - 1)]
            table.add_row("...", *ellipsis)
            break
        table.add_row(*[str(val) for val in row])
        row_count += 1

    printer.result(table)

    if len(df) > limit:
        msg = f"[dim]Showing first {limit} of {len(df)} rows[/dim]"
        printer.result(msg, highlight=False)

