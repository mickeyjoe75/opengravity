import click
from rich.console import Console
from rich.table import Table
from opengravity.providers.registry import ProviderRegistry
from opengravity.providers.configs import PROVIDERS

console = Console()

@click.group("config")
def config_group():
    """Manage OpenGravity configuration."""
    pass

@config_group.command("providers")
def list_providers():
    """List all supported providers and their status."""
    table = Table(title="⚡ OpenGravity Providers", show_lines=True)
    table.add_column("Provider", style="cyan bold")
    table.add_column("Name", style="white")
    table.add_column("Default Model", style="green")
    table.add_column("Tool Calling", style="yellow")
    table.add_column("Status", style="bold")
    
    available = ProviderRegistry.list_available()
    for key, config, is_configured in available:
        status = "[green]✓ Ready[/]" if is_configured else "[dim]Not configured[/]"
        tool_support = "✅" if config.supports_tool_calling else "❌"
        table.add_row(key, config.name, config.default_model or "—", tool_support, status)
    
    console.print(table)

@config_group.command("models")
@click.option("--provider", "-p", required=True, help="Provider to list models for")
def list_models(provider):
    """List available models for a provider."""
    if provider not in PROVIDERS:
        console.print(f"[red]Unknown provider: {provider}[/]")
        console.print(f"Available: {', '.join(PROVIDERS.keys())}")
        return
    
    config = PROVIDERS[provider]
    console.print(f"\n[bold cyan]{config.name}[/] Models:\n")
    
    if not config.models:
        console.print("  [dim]Models are dynamically discovered for this provider.[/]")
    else:
        for model in config.models:
            marker = " [green](default)[/]" if model == config.default_model else ""
            console.print(f"  • {model}{marker}")
    
    if config.notes:
        console.print(f"\n  [dim]Note: {config.notes}[/]")
    console.print()
