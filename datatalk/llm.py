"""LLM provider using LiteLLM for unified API access."""

import os
import re
import litellm
from litellm.exceptions import AuthenticationError


class LiteLLMProvider:
    """Unified LLM provider supporting 100+ models via LiteLLM."""
    
    def __init__(self, model: str):
        self.model = model
    
    def to_sql(self, question: str, schema: str) -> str:
        """Convert natural language to SQL using any LLM via LiteLLM."""
        prompt = f"""You are a data assistant.
The user asks questions about a table named 'events'.
Schema of events: {schema}

Return ONLY valid SQL for DuckDB, nothing else.
SQL should start with SELECT and must reference the 'events' table.

User question: {question}"""
        
        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=float(os.getenv("MODEL_TEMPERATURE", "0.1")),
                max_tokens=500,
            )
        except AuthenticationError as e:
            # Clean up the error message for user-friendly display
            cleaned_message = self._clean_auth_error(str(e))
            raise ValueError(cleaned_message) from None
        
        content = response.choices[0].message.content
        if content is None:
            raise ValueError(f"No content returned from {self.model}")
        
        return self._clean_sql(content)
    
    def _clean_sql(self, sql: str) -> str:
        """Clean up SQL response (remove markdown code blocks)."""
        sql = sql.strip()
        if sql.startswith("```sql"):
            sql = sql[6:]
        elif sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        return sql.strip()
    
    def _clean_auth_error(self, error_message: str) -> str:
        """Clean up authentication error message for user-friendly display."""
        # Remove technical prefixes and noise from litellm error
        # Example: "litellm.AuthenticationError: AuthenticationError: OpenAIException - The api_key..."
        # We want to extract just the core message
        
        # Remove common prefixes
        cleaned = error_message
        prefixes_to_remove = [
            r"litellm\.AuthenticationError:\s*",
            r"AuthenticationError:\s*",
            r"OpenAIException\s*-\s*",
            r"AnthropicException\s*-\s*",
            r"GoogleException\s*-\s*",
            r"AzureException\s*-\s*",
        ]
        
        for prefix in prefixes_to_remove:
            cleaned = re.sub(prefix, "", cleaned, flags=re.IGNORECASE)
        
        cleaned = cleaned.strip()
        
        # Format the final message
        return (
            "⚠️  Authentication Error\n\n"
            f"{cleaned}\n\n"
            "For help setting up API keys, see:\n"
            "https://github.com/vtsaplin/datatalk-cli#configuration"
        )


