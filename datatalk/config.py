"""Configuration management for DataTalk."""

import json
import os
import sys
from pathlib import Path
from typing import Dict

from rich.console import Console
from rich.prompt import Prompt


def get_config_path() -> Path:
    """Get the path to the configuration file."""
    config_dir = Path.home() / ".config" / "datatalk"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"


def load_config() -> Dict[str, str]:
    """Load configuration from file."""
    config_path = get_config_path()
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


def save_config(config: Dict[str, str]) -> None:
    """Save configuration to file."""
    config_path = get_config_path()
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def get_env_var(name: str, config: Dict[str, str], console: Console) -> str:
    """Get environment variable, prompting user if not available."""
    # First check environment variables
    value = os.getenv(name)
    if value:
        return value

    # Then check saved config
    if name in config:
        return config[name]

    # Prompt user for the value
    descriptions = {
        "AZURE_OPENAI_API_KEY": "Azure OpenAI API key",
        "AZURE_DEPLOYMENT_TARGET_URL": "Azure OpenAI deployment target URL",
        "OPENAI_API_KEY": "OpenAI API key",
        "OPENAI_MODEL": "OpenAI model name",
    }

    description = descriptions.get(name, name)
    console.print(f"[yellow]Missing configuration:[/yellow] {description}")

    try:
        if "API_KEY" in name:
            value = Prompt.ask(f"Enter {description}", console=console, password=True)
        elif name == "AZURE_DEPLOYMENT_TARGET_URL":
            value = Prompt.ask(f"Enter {description}", console=console, default=None)
            console.print(
                "[dim]Example: https://your-resource.openai.azure.com/openai/"
                "deployments/gpt-4o/chat/completions?"
                "api-version=2024-12-01-preview[/dim]"
            )
        elif name == "OPENAI_MODEL":
            value = Prompt.ask(
                f"Enter {description}", console=console, default="gpt-4o"
            )
            console.print("[dim]Example: gpt-4o, gpt-3.5-turbo[/dim]")
        else:
            # Unknown configuration variable
            console.print(f"[red]Error:[/red] Unknown configuration: {name}")
            sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]Operation cancelled. Goodbye![/dim]")
        sys.exit(0)

    if not value:
        console.print(f"[red]Error:[/red] {description} is required")
        sys.exit(1)

    # Save to config
    config[name] = value
    save_config(config)
    console.print(f"[green]✓[/green] Saved {description} to configuration")

    return value


def parse_target_url(target_url: str) -> tuple[str, str, str]:
    """Parse Azure deployment target URL to extract components."""
    # Example URL: https://your-resource.openai.azure.com/openai/
    # deployments/gpt-4o/chat/completions?api-version=2024-12-01-preview

    # Extract the base endpoint
    if "/openai/deployments/" not in target_url:
        raise ValueError("Invalid Azure deployment target URL format")

    endpoint = target_url.split("/openai/deployments/")[0] + "/"

    # Extract deployment name
    deployment_part = target_url.split("/openai/deployments/")[1]
    deployment_name = deployment_part.split("/")[0]

    # Extract API version from query parameters
    if "api-version=" not in target_url:
        raise ValueError("API version not found in target URL")

    api_version = target_url.split("api-version=")[1].split("&")[0]

    return endpoint, deployment_name, api_version


def get_azure_config(
    config: Dict[str, str], console: Console
) -> tuple[str, str, str, str]:
    """Get Azure OpenAI configuration using target URL approach only."""
    # Get the target URL and API key
    target_url = os.getenv("AZURE_DEPLOYMENT_TARGET_URL") or config.get(
        "AZURE_DEPLOYMENT_TARGET_URL"
    )

    if not target_url:
        target_url = get_env_var("AZURE_DEPLOYMENT_TARGET_URL", config, console)

    api_key = get_env_var("AZURE_OPENAI_API_KEY", config, console)

    try:
        endpoint, deployment_name, api_version = parse_target_url(target_url)
        console.print("[dim]Using Azure OpenAI[/dim]")
        return api_key, endpoint, deployment_name, api_version
    except ValueError as e:
        console.print(f"[red]Error parsing Azure target URL:[/red] {e}")
        sys.exit(1)
