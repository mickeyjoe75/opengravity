from rich.console import Console
from rich.theme import Theme

# Custom theme for OpenGravity
OG_THEME = Theme({
    "og.header": "bold magenta",
    "og.provider": "bold cyan",
    "og.model": "bold green",
    "og.tool": "bold yellow",
    "og.error": "bold red",
    "og.success": "bold green",
    "og.info": "dim",
    "og.prompt": "bold white",
})

console = Console(theme=OG_THEME)

def print_header():
    """Print the OpenGravity header."""
    console.print()
    console.print("  ⚡ [og.header]OpenGravity[/og.header] — Model-Agnostic AI Agent", highlight=False)
    console.print()

def print_provider_info(provider: str, model: str, tool_count: int):
    """Print provider and model info."""
    console.print(f"  Provider: [og.provider]{provider}[/]  Model: [og.model]{model}[/]  Tools: [og.tool]{tool_count}[/]")
    console.print("  Type [bold]/help[/] for commands, [bold]/exit[/] to quit")
    console.print("─" * 60, style="dim")

def print_error(message: str):
    console.print(f"[og.error]Error:[/] {message}")

def print_success(message: str):
    console.print(f"[og.success]✓[/] {message}")

def print_info(message: str):
    console.print(f"[og.info]{message}[/]")
