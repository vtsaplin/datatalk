"""Azure OpenAI LLM provider."""

import os

from openai import AzureOpenAI

from datatalk.llm.base import BaseLLMProvider


class AzureProvider(BaseLLMProvider):
    """Azure OpenAI LLM provider."""

    def __init__(self, api_key: str, endpoint: str, deployment_name: str, api_version: str):
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
        )
        self.deployment_name = deployment_name

    def to_sql(self, question: str, schema: str) -> str:
        """Convert natural language to SQL using Azure OpenAI."""
        prompt = f"""
You are a data assistant.
The user asks questions about a table named 'events'.
Schema of events: {schema}

Return ONLY valid SQL for DuckDB, nothing else.
SQL should start with SELECT and must reference the 'events' table.

User question: {question}
"""

        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=float(os.getenv("MODEL_TEMPERATURE", "0.1")),
            max_tokens=500,
        )

        content = response.choices[0].message.content
        if content is None:
            raise ValueError("No content returned from Azure OpenAI")

        return self._clean_sql(content)

