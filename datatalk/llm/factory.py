"""Factory for creating LLM providers."""

import os
import sys

from rich.console import Console
from rich.prompt import Prompt

from datatalk.config import (
    get_anthropic_config,
    get_azure_config,
    get_env_var,
    get_gemini_config,
    get_ollama_config,
)
from datatalk.llm.base import LLMProvider
from datatalk.llm.providers import (
    AnthropicProvider,
    AzureProvider,
    GeminiProvider,
    OllamaProvider,
    OpenAIProvider,
)


def detect_llm_provider(config: dict[str, str], console: Console) -> str:
    """Auto-detect LLM provider based on available environment variables and config."""
    # Check environment variables first
    has_ollama_env = bool(os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_MODEL"))
    has_anthropic_env = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_gemini_env = bool(os.getenv("GEMINI_API_KEY"))
    has_azure_env = bool(
        os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("AZURE_DEPLOYMENT_TARGET_URL")
    )
    has_openai_env = bool(os.getenv("OPENAI_API_KEY"))

    # Check saved config
    has_ollama_config = bool(
        config.get("OLLAMA_BASE_URL") or config.get("OLLAMA_MODEL")
    )
    has_anthropic_config = bool(
        config.get("ANTHROPIC_API_KEY") or config.get("ANTHROPIC_MODEL")
    )
    has_gemini_config = bool(
        config.get("GEMINI_API_KEY") or config.get("GEMINI_MODEL")
    )
    has_azure_config = bool(
        config.get("AZURE_OPENAI_API_KEY") or config.get("AZURE_DEPLOYMENT_TARGET_URL")
    )
    has_openai_config = bool(config.get("OPENAI_API_KEY") or config.get("OPENAI_MODEL"))

    # Priority order: Ollama > Anthropic > Gemini > OpenAI > Azure
    if has_ollama_env or has_ollama_config:
        if any([has_anthropic_env, has_anthropic_config, has_gemini_env, 
                has_gemini_config, has_openai_env, has_openai_config, 
                has_azure_env, has_azure_config]):
            console.print("[yellow]Multiple AI provider configurations detected.[/yellow]")
            console.print("[dim]Preferring Ollama (local)[/dim]")
        return "ollama"

    if has_anthropic_env or has_anthropic_config:
        if any([has_gemini_env, has_gemini_config, has_openai_env, 
                has_openai_config, has_azure_env, has_azure_config]):
            console.print("[yellow]Multiple AI provider configurations detected.[/yellow]")
            console.print("[dim]Preferring Anthropic[/dim]")
        return "anthropic"

    if has_gemini_env or has_gemini_config:
        if (has_openai_env or has_openai_config) or (has_azure_env or has_azure_config):
            console.print("[yellow]Multiple AI provider configurations detected.[/yellow]")
            console.print("[dim]Preferring Gemini[/dim]")
        return "gemini"

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
    console.print("  [bold]4[/bold] - Ollama (local - requires base URL + model name)")
    console.print("  [bold]5[/bold] - Google Gemini (requires API key + model name)")

    while True:
        try:
            choice = Prompt.ask(
                "Choose provider",
                choices=["1", "2", "3", "4", "5", "openai", "azure", "anthropic", "ollama", "gemini"],
                default="1",
            ).lower()
            if choice in ["1", "openai"]:
                return "openai"
            elif choice in ["2", "azure"]:
                return "azure"
            elif choice in ["3", "anthropic"]:
                return "anthropic"
            elif choice in ["4", "ollama"]:
                return "ollama"
            elif choice in ["5", "gemini"]:
                return "gemini"
            console.print("[red]Please choose '1' (OpenAI), '2' (Azure), '3' (Anthropic), '4' (Ollama), or '5' (Gemini)[/red]")
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

    if provider_type == "ollama":
        base_url, model = get_ollama_config(config, console)
        return OllamaProvider(base_url, model)
    elif provider_type == "anthropic":
        api_key, model = get_anthropic_config(config, console)
        return AnthropicProvider(api_key, model)
    elif provider_type == "gemini":
        api_key, model = get_gemini_config(config, console)
        return GeminiProvider(api_key, model)
    elif provider_type == "openai":
        api_key, model = get_openai_config(config, console)
        return OpenAIProvider(api_key, model)
    elif provider_type == "azure":
        api_key, endpoint, deployment_name, api_version = get_azure_config(config, console)
        return AzureProvider(api_key, endpoint, deployment_name, api_version)
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")

