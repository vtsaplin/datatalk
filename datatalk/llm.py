"""LLM provider abstraction with factory pattern."""

import os
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from openai import AzureOpenAI, OpenAI
from rich.console import Console

from datatalk.config import get_anthropic_config, get_azure_config, get_env_var


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


def detect_llm_provider(config: dict[str, str], console: Console) -> str:
    """Auto-detect LLM provider based on available environment variables and config."""
    # Check environment variables first
    has_anthropic_env = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_azure_env = bool(
        os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("AZURE_DEPLOYMENT_TARGET_URL")
    )
    has_openai_env = bool(os.getenv("OPENAI_API_KEY"))

    # Check saved config
    has_anthropic_config = bool(
        config.get("ANTHROPIC_API_KEY") or config.get("ANTHROPIC_MODEL")
    )
    has_azure_config = bool(
        config.get("AZURE_OPENAI_API_KEY") or config.get("AZURE_DEPLOYMENT_TARGET_URL")
    )
    has_openai_config = bool(config.get("OPENAI_API_KEY") or config.get("OPENAI_MODEL"))

    # Priority order: Anthropic > OpenAI > Azure
    if has_anthropic_env or has_anthropic_config:
        if (has_openai_env or has_openai_config) or (has_azure_env or has_azure_config):
            console.print("[yellow]Multiple AI provider configurations detected.[/yellow]")
            console.print("[dim]Preferring Anthropic[/dim]")
        return "anthropic"

    if has_openai_env or has_openai_config:
        if has_azure_env or has_azure_config:
            console.print("[yellow]Both Azure and OpenAI configurations detected.[/yellow]")
            console.print("[dim]Preferring OpenAI (simpler setup)[/dim]")
        return "openai"

    if has_azure_env or has_azure_config:
        return "azure"

    # If no provider is available, ask the user
    console.print("[yellow]No AI provider configuration detected.[/yellow]")
    console.print("Available providers:")
    console.print("  [bold]1[/bold] - OpenAI (requires API key + model name)")
    console.print("  [bold]2[/bold] - Azure OpenAI (requires API key + target URL)")
    console.print("  [bold]3[/bold] - Anthropic Claude (requires API key + model name)")

    from rich.prompt import Prompt
    import sys

    while True:
        try:
            choice = Prompt.ask(
                "Choose provider",
                choices=["1", "2", "3", "openai", "azure", "anthropic"],
                default="1",
            ).lower()
            if choice in ["1", "openai"]:
                return "openai"
            elif choice in ["2", "azure"]:
                return "azure"
            elif choice in ["3", "anthropic"]:
                return "anthropic"
            console.print("[red]Please choose '1' (OpenAI), '2' (Azure), or '3' (Anthropic)[/red]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]\n")
            sys.exit(0)


def get_openai_config(config: dict[str, str], console: Console) -> tuple[str, str]:
    """Get OpenAI configuration."""
    api_key = get_env_var("OPENAI_API_KEY", config, console)
    model = get_env_var("OPENAI_MODEL", config, console)
    return api_key, model


def create_provider(config: dict[str, str], console: Console) -> LLMProvider:
    """Factory function to create appropriate LLM provider."""
    provider_type = detect_llm_provider(config, console)

    if provider_type == "anthropic":
        api_key, model = get_anthropic_config(config, console)
        return AnthropicProvider(api_key, model)
    elif provider_type == "openai":
        api_key, model = get_openai_config(config, console)
        return OpenAIProvider(api_key, model)
    elif provider_type == "azure":
        api_key, endpoint, deployment_name, api_version = get_azure_config(config, console)
        return AzureProvider(api_key, endpoint, deployment_name, api_version)
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")

