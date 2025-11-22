"""Database operations with DuckDB."""

from pathlib import Path
from typing import Any

import duckdb
import pandas as pd


def create_connection() -> duckdb.DuckDBPyConnection:
    """Create and return a DuckDB connection."""
    return duckdb.connect()


def load_data(con: duckdb.DuckDBPyConnection, path: str) -> None:
    """Load CSV, Parquet, or Excel file into DuckDB and create a table named 'events'."""
    file_path = Path(path)
    file_extension = file_path.suffix.lower()

    con.execute("DROP TABLE IF EXISTS events;")

    if file_extension == ".parquet":
        con.execute(f"CREATE TABLE events AS SELECT * FROM read_parquet('{path}');")
    elif file_extension == ".csv":
        con.execute(
            f"CREATE TABLE events AS SELECT * FROM "
            f"read_csv_auto('{path}', HEADER=TRUE);"
        )
    elif file_extension in [".xlsx", ".xls"]:
        df = pd.read_excel(path)
        con.execute("CREATE TABLE events AS SELECT * FROM df")
    else:
        raise ValueError(
            f"Unsupported file format: {file_extension}. "
            f"Supported formats: .csv, .parquet, .xlsx, .xls"
        )


def get_schema(con: duckdb.DuckDBPyConnection) -> str:
    """Return a simple schema description for the 'events' table."""
    rows = con.execute("PRAGMA table_info('events')").fetchall()
    schema_lines = []
    for row in rows:
        _, name, col_type, *_ = row
        schema_lines.append(f"{name} ({col_type})")
    return ", ".join(schema_lines)


def execute_query(con: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    """Execute SQL query and return results as DataFrame."""
    return con.execute(sql).df()


def get_stats(con: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    """Get dataset statistics (row count, column information)."""
    # Get row count
    result = con.execute("SELECT COUNT(*) FROM events").fetchone()
    row_count = result[0] if result else 0

    # Get column info
    columns = con.execute("PRAGMA table_info('events')").fetchall()
    col_count = len(columns)

    # Get sample values for each column
    column_details = []
    for row in columns:
        _, name, col_type, *_ = row
        try:
            query = (
                f"SELECT DISTINCT {name} FROM events "
                f"WHERE {name} IS NOT NULL LIMIT 3"
            )
            samples = con.execute(query).fetchall()
            sample_values = []
            for sample in samples:
                value_str = str(sample[0])
                if len(value_str) > 20:
                    value_str = value_str[:20] + "..."
                sample_values.append(value_str)
            sample_str = ", ".join(sample_values) if sample_values else "[no data]"
        except Exception:
            sample_str = "[error reading]"

        column_details.append({
            "name": name,
            "type": col_type,
            "samples": sample_str,
        })

    return {
        "row_count": row_count,
        "col_count": col_count,
        "columns": column_details,
    }

