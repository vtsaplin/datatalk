"""LLM provider using LiteLLM for unified API access."""

import os
import re
import litellm

# Suppress litellm debug messages
litellm.suppress_debug_info = True


class LiteLLMProvider:
    """Unified LLM provider supporting 100+ models via LiteLLM."""
    
    def __init__(self, model: str):
        self.model = model
    
    def to_sql(self, question: str, schema: str) -> str:
        """Convert natural language to SQL using any LLM via LiteLLM."""
        prompt = f"""You are a SQL query generator. Convert the user's question into a valid DuckDB SQL query.

Table name: events
Schema: {schema}

CRITICAL RULES:
- Wrap the SQL query in markdown code blocks (```sql ... ```)
- No explanations, no apologies, no refusals
- If the question doesn't make sense, generate a simple SELECT * FROM events LIMIT 1
- Query must reference the 'events' table

User question: {question}

SQL query:"""
        
        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=float(os.getenv("MODEL_TEMPERATURE", "0.1")),
                max_tokens=500,
            )
        except Exception as e:
            # Clean up litellm error messages for user-friendly display
            cleaned_message = self._clean_litellm_error(str(e))
            raise ValueError(cleaned_message) from None
        
        content = response.choices[0].message.content
        if content is None:
            raise ValueError(f"No content returned from {self.model}")
        
        return self._clean_sql(content)
    
    def _clean_sql(self, sql: str) -> str:
        """Extract SQL from markdown code blocks."""
        if "```" in sql:
            parts = sql.split("```")
            if len(parts) >= 2:
                block = parts[1]
                # Skip language tag (first line) if present
                lines = block.strip().split("\n", 1)
                return lines[-1].strip() if len(lines) > 1 else lines[0].strip()
        return sql.strip()
    
    def _clean_litellm_error(self, error_message: str) -> str:
        """Clean up litellm error message for user-friendly display."""
        # Remove technical prefixes and noise from litellm errors
        # Example: "litellm.AuthenticationError: AuthenticationError: OpenAIException - The api_key..."
        # Result: "The api_key..."
        
        cleaned = error_message
        
        # Remove common technical prefixes
        prefixes_to_remove = [
            r"litellm\.\w+Error:\s*",  # litellm.AuthenticationError:, litellm.RateLimitError:, etc.
            r"\w+Error:\s*",  # AuthenticationError:, RateLimitError:, APIError:, etc.
            r"\w+Exception\s*-\s*",  # OpenAIException -, AnthropicException -, etc.
        ]
        
        for prefix in prefixes_to_remove:
            cleaned = re.sub(prefix, "", cleaned, flags=re.IGNORECASE)
        
        cleaned = cleaned.strip()
        
        # If we somehow ended up with an empty string, return the original
        if not cleaned:
            cleaned = error_message
        
        return cleaned


