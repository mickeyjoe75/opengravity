from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from opengravity.core.types import StreamChunk

class StreamDisplay:
    """Handles real-time display of streaming agent output."""
    
    def __init__(self, console: Console | None = None):
        self._console = console or Console()
        self._buffer = ""
        self._reasoning_buffer = ""
        self._in_reasoning = False
    
    def handle_chunk(self, chunk: StreamChunk) -> None:
        """Process a streaming chunk and display it."""
        match chunk.type:
            case "text":
                # Print text content as it streams
                self._console.print(chunk.content, end="", highlight=False)
                self._buffer += chunk.content
            case "reasoning":
                # Show reasoning in dim text
                if not self._in_reasoning:
                    self._console.print("\n💭 ", style="dim italic", end="")
                    self._in_reasoning = True
                self._console.print(chunk.content, style="dim italic", end="", highlight=False)
            case "tool_call":
                # Show tool call in a panel
                self._finish_reasoning()
                if chunk.tool_call:
                    self._console.print()
                    self._console.print(
                        Panel(
                            f"[bold cyan]{chunk.tool_call.name}[/]\n{chunk.tool_call.arguments}",
                            title="🔧 Tool Call",
                            border_style="cyan",
                            expand=False,
                        )
                    )
            case "tool_result":
                # Show tool result
                if chunk.tool_result:
                    style = "red" if chunk.tool_result.is_error else "green"
                    result_text = chunk.tool_result.result[:500]  # Truncate long results
                    if len(chunk.tool_result.result) > 500:
                        result_text += "\n... (truncated)"
                    self._console.print(
                        Panel(
                            result_text,
                            title=f"{'❌' if chunk.tool_result.is_error else '✅'} Result: {chunk.tool_result.name}",
                            border_style=style,
                            expand=False,
                        )
                    )
            case "error":
                self._console.print(f"\n[bold red]Error:[/] {chunk.content}")
            case "done":
                self._finish_reasoning()
                self._console.print()
    
    def _finish_reasoning(self):
        if self._in_reasoning:
            self._console.print()
            self._in_reasoning = False
    
    def flush(self):
        self._finish_reasoning()
        if self._buffer:
            self._console.print()
            self._buffer = ""
