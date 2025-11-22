"""OpenAI LLM provider."""

import os

from openai import OpenAI

from datatalk.llm.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def to_sql(self, question: str, schema: str) -> str:
        """Convert natural language to SQL using OpenAI."""
        prompt = f"""
You are a data assistant.
The user asks questions about a table named 'events'.
Schema of events: {schema}

Return ONLY valid SQL for DuckDB, nothing else.
SQL should start with SELECT and must reference the 'events' table.

User question: {question}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=float(os.getenv("MODEL_TEMPERATURE", "0.1")),
            max_tokens=500,
        )

        content = response.choices[0].message.content
        if content is None:
            raise ValueError("No content returned from OpenAI")

        return self._clean_sql(content)

