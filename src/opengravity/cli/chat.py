import asyncio
from rich.console import Console
from rich.prompt import Prompt
from opengravity.core.agent import Agent
from opengravity.utils.streaming import StreamDisplay
from opengravity.utils.logging import print_header, print_provider_info, print_error, print_info, console

SLASH_COMMANDS = {
    "/help": "Show available commands",
    "/exit": "Exit the chat",
    "/quit": "Exit the chat",
    "/clear": "Clear conversation history",
    "/model": "Show current model info",
    "/tools": "List available tools",
    "/multi": "Start multi-line input (end with a line containing only '---')",
}

async def run_chat(
    provider: str,
    model: str | None,
    base_url: str | None = None,
    api_key: str | None = None,
    enable_tools: bool = True,
    system_prompt: str | None = None,
    temperature: float = 0.0,
    max_turns: int = 50,
):
    """Run the interactive chat REPL."""
    print_header()
    
    try:
        agent = Agent(
            provider=provider,
            model=model,
            system_prompt=system_prompt,
            api_key=api_key,
            base_url=base_url,
            enable_default_tools=enable_tools,
            temperature=temperature,
            max_turns=max_turns,
        )
    except Exception as e:
        print_error(str(e))
        return
    
    print_provider_info(agent.provider, agent.model, agent.tool_count)
    
    display = StreamDisplay(console)
    agent.on_stream(display.handle_chunk)
    
    while True:
        try:
            console.print()
            user_input = Prompt.ask("[bold white]You[/]")
            
            if not user_input.strip():
                continue
            
            # Handle slash commands
            cmd = user_input.strip().lower()
            if cmd in ("/exit", "/quit"):
                print_info("Goodbye! 👋")
                break
            elif cmd == "/help":
                console.print()
                for cmd_name, desc in SLASH_COMMANDS.items():
                    console.print(f"  [bold]{cmd_name}[/]  {desc}")
                continue
            elif cmd == "/clear":
                agent.reset()
                print_info("Conversation cleared.")
                continue
            elif cmd == "/model":
                print_info(f"Provider: {agent.provider} | Model: {agent.model} | Tools: {agent.tool_count}")
                continue
            elif cmd == "/tools":
                print_info(f"Tools: {', '.join(agent._tool_registry.tool_names)}")
                continue
            elif cmd == "/multi":
                lines = []
                console.print("  [dim]Enter multi-line input (end with '---'):[/]")
                while True:
                    line = input("  ... ")
                    if line.strip() == "---":
                        break
                    lines.append(line)
                user_input = "\n".join(lines)
                if not user_input.strip():
                    continue
            
            # Run the agent
            console.print()
            console.print("[bold magenta]OpenGravity[/] ", end="")
            
            result = await agent.chat(user_input)
            display.flush()
            
            # Show stats
            console.print(f"\n[dim]({result.turns} turn{'s' if result.turns != 1 else ''}, {result.tool_calls_made} tool call{'s' if result.tool_calls_made != 1 else ''}, {result.elapsed_seconds:.1f}s)[/]")
        
        except KeyboardInterrupt:
            console.print()
            print_info("Use /exit to quit.")
            continue
        except Exception as e:
            print_error(str(e))
            continue


async def run_task(
    task: str,
    provider: str,
    model: str | None,
    base_url: str | None = None,
    api_key: str | None = None,
    enable_tools: bool = True,
    temperature: float = 0.0,
    max_turns: int = 50,
):
    """Run a one-shot task."""
    try:
        agent = Agent(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
            enable_default_tools=enable_tools,
            temperature=temperature,
            max_turns=max_turns,
        )
    except Exception as e:
        print_error(str(e))
        return
    
    display = StreamDisplay(console)
    agent.on_stream(display.handle_chunk)
    
    console.print(f"[bold]⚡ Running task with {agent.provider}/{agent.model}...[/]\n")
    
    result = await agent.run(task)
    display.flush()
    
    console.print(f"\n[dim]Completed in {result.elapsed_seconds:.1f}s ({result.turns} turns, {result.tool_calls_made} tool calls)[/]")
