"""Anthropic (Claude) LLM provider."""

import os

from datatalk.llm.base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """Anthropic (Claude) LLM provider."""

    def __init__(self, api_key: str, model: str):
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. Install it with: pip install anthropic"
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def to_sql(self, question: str, schema: str) -> str:
        """Convert natural language to SQL using Anthropic Claude."""
        prompt = f"""You are a data assistant.
The user asks questions about a table named 'events'.
Schema of events: {schema}

Return ONLY valid SQL for DuckDB, nothing else.
SQL should start with SELECT and must reference the 'events' table.

User question: {question}"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=float(os.getenv("MODEL_TEMPERATURE", "0.1")),
            messages=[{"role": "user", "content": prompt}],
        )

        if not message.content or len(message.content) == 0:
            raise ValueError("No content returned from Anthropic")

        content = message.content[0].text
        return self._clean_sql(content)

