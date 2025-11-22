"""Terminal output rendering using Rich."""

from typing import Any

import pandas as pd
from rich import box
from rich.console import Console
from rich.table import Table


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


def print_stats(stats: dict[str, Any], console: Console, show_schema: bool = True) -> None:
    """Render dataset statistics."""
    row_count = stats["row_count"]
    col_count = stats["col_count"]
    columns = stats["columns"]

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

        for col in columns:
            table.add_row(col["name"], col["type"], col["samples"])

        console.print(table)

    console.print()


def print_query_results(df: pd.DataFrame, console: Console, limit: int = 20) -> None:
    """Render query results as a table."""
    if len(df) == 0:
        console.print("[yellow]No results found.[/yellow]")
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
        console.print(msg)

