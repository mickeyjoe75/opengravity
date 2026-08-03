import click
import asyncio
from opengravity.utils.config import load_config

@click.group()
@click.version_option(version="0.1.0", prog_name="OpenGravity")
def cli():
    """OpenGravity — Model-agnostic agentic AI framework."""
    pass

@cli.command()
@click.option("--provider", "-p", default=None, help="LLM provider (e.g., kimi, glm, deepseek, ollama)")
@click.option("--model", "-m", default=None, help="Model identifier")
@click.option("--base-url", default=None, help="Custom API base URL")
@click.option("--api-key", default=None, help="API key (overrides env var)")
@click.option("--no-tools", is_flag=True, help="Disable built-in tools")
@click.option("--system-prompt", "-s", default=None, help="Custom system prompt")
def chat(provider, model, base_url, api_key, no_tools, system_prompt):
    """Start an interactive chat session."""
    from opengravity.cli.chat import run_chat
    config = load_config()
    asyncio.run(run_chat(
        provider=provider or config["default_provider"],
        model=model or config["default_model"],
        base_url=base_url,
        api_key=api_key,
        enable_tools=not no_tools,
        system_prompt=system_prompt,
        temperature=config["temperature"],
        max_turns=config["max_turns"],
    ))

@cli.command()
@click.argument("task")
@click.option("--provider", "-p", default=None, help="LLM provider")
@click.option("--model", "-m", default=None, help="Model identifier")
@click.option("--base-url", default=None, help="Custom API base URL")
@click.option("--api-key", default=None, help="API key")
@click.option("--no-tools", is_flag=True, help="Disable built-in tools")
def run(task, provider, model, base_url, api_key, no_tools):
    """Run a one-shot task."""
    from opengravity.cli.chat import run_task
    config = load_config()
    asyncio.run(run_task(
        task=task,
        provider=provider or config["default_provider"],
        model=model or config["default_model"],
        base_url=base_url,
        api_key=api_key,
        enable_tools=not no_tools,
        temperature=config["temperature"],
        max_turns=config["max_turns"],
    ))

@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", "-p", default=8000, type=int, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def serve(host, port, reload):
    """Start the OpenGravity API server."""
    import uvicorn
    from opengravity.utils.logging import print_header, console
    print_header()
    console.print(f"  Starting server at [bold cyan]http://{host}:{port}[/]")
    console.print(f"  WebSocket at [bold cyan]ws://{host}:{port}/ws/{{session_id}}[/]")
    console.print("─" * 60, style="dim")
    uvicorn.run(
        "opengravity.server.app:app",
        host=host,
        port=port,
        reload=reload,
    )

# Add the config subcommand group
from opengravity.cli.config import config_group
cli.add_command(config_group, "config")
