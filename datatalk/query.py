"""Core query processing logic."""

from typing import Any

import duckdb

from datatalk import database
from datatalk.llm import LiteLLMProvider
from datatalk.printer import Printer


def process_query(
    provider: LiteLLMProvider,
    question: str,
    schema: str,
    con: duckdb.DuckDBPyConnection,
    printer: Printer,
) -> dict[str, Any]:
    """Process a natural language query and return results."""
    try:
        printer.decorative("[dim]Analyzing your question...[/dim]")
        sql = provider.to_sql(question, schema)

        printer.decorative("[dim]Executing query...[/dim]")
        df = database.execute_query(con, sql)

        return {
            "sql": sql,
            "dataframe": df,
            "error": None,
        }
    except Exception as e:
        return {
            "sql": None,
            "dataframe": None,
            "error": str(e),
        }

