"""Core query processing logic - UI-agnostic orchestrator."""

from typing import Any, Optional

import duckdb
import pandas as pd
from rich.console import Console

from datatalk import database
from datatalk.llm import LLMProvider


def process_query(
    provider: LLMProvider,
    question: str,
    schema: str,
    con: duckdb.DuckDBPyConnection,
    console: Console,
) -> dict[str, Any]:
    """
    Process a natural language query and return results.

    Args:
        provider: LLM provider instance
        question: Natural language question
        schema: Database schema information
        con: DuckDB connection
        console: Console for status messages

    Returns:
        Dictionary with:
            - sql: Generated SQL query (or None if error)
            - dataframe: Query results (or None if error)
            - error: Error message (or None if success)
    """
    try:
        console.print("[dim]Analyzing your question...[/dim]")
        sql = provider.to_sql(question, schema)

        console.print("[dim]Executing query...[/dim]")
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

