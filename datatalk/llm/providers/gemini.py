"""Google Gemini LLM provider."""

import os

from datatalk.llm.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""

    def __init__(self, api_key: str, model: str):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "Google Generative AI package not installed. Install it with: pip install google-generativeai"
            )
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def to_sql(self, question: str, schema: str) -> str:
        """Convert natural language to SQL using Google Gemini."""
        prompt = f"""You are a data assistant.
The user asks questions about a table named 'events'.
Schema of events: {schema}

Return ONLY valid SQL for DuckDB, nothing else.
SQL should start with SELECT and must reference the 'events' table.

User question: {question}"""

        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": float(os.getenv("MODEL_TEMPERATURE", "0.1")),
                "max_output_tokens": 500,
            },
        )

        if not response.text:
            raise ValueError("No content returned from Gemini")

        return self._clean_sql(response.text)

