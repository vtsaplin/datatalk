"""Base classes and protocols for LLM providers."""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol for LLM providers - structural typing."""

    def to_sql(self, question: str, schema: str) -> str:
        """Convert natural language question to SQL query."""
        ...


class BaseLLMProvider(ABC):
    """Optional base class with shared helper methods."""

    def _clean_sql(self, sql: str) -> str:
        """Clean up SQL response from LLM (remove markdown code blocks)."""
        sql = sql.strip()

        # Remove markdown code blocks if present
        if sql.startswith("```sql"):
            sql = sql[6:]  # Remove ```sql
        elif sql.startswith("```"):
            sql = sql[3:]  # Remove ```

        if sql.endswith("```"):
            sql = sql[:-3]  # Remove trailing ```

        return sql.strip()

    @abstractmethod
    def to_sql(self, question: str, schema: str) -> str:
        """Convert natural language question to SQL query."""
        pass

