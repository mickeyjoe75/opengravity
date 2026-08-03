from typing import Callable, Any
from opengravity.core.types import AgentResult, StreamChunk
from opengravity.core.conversation import Conversation
from opengravity.core.planner import Planner

# Support runtime where registries haven't been implemented yet
try:
    from opengravity.providers.registry import ProviderRegistry
except ImportError:
    ProviderRegistry = Any

try:
    from opengravity.tools.registry import ToolRegistry
except ImportError:
    ToolRegistry = Any

DEFAULT_SYSTEM_PROMPT = """You are OpenGravity, a powerful AI coding assistant. You can use tools to help accomplish tasks.

When you need to perform actions, use the available tools. Be precise, efficient, and helpful.
Always explain what you're doing and why. If a tool call fails, try to recover gracefully."""

class Agent:
    """Model-agnostic agentic AI assistant.
    
    Supports any OpenAI-compatible LLM provider including Kimi K2, GLM-4,
    DeepSeek, Qwen, Mistral, Gemini, Llama, and more.
    
    Usage:
        agent = Agent(provider="kimi", model="kimi-k2")
        result = await agent.run("Create a Python hello world script")
        print(result.content)
    """
    
    def __init__(
        self,
        provider: str = "auto",
        model: str | None = None,
        system_prompt: str | None = None,
        tools: list | None = None,
        max_turns: int = 50,
        temperature: float = 0.0,
        api_key: str | None = None,
        base_url: str | None = None,
        enable_default_tools: bool = True,
    ):
        self._client = None
        if hasattr(ProviderRegistry, "resolve"):
            self._client = ProviderRegistry.resolve(
                provider=provider, model=model,
                api_key=api_key, base_url=base_url,
            )
        
        self._tool_registry = ToolRegistry() if callable(ToolRegistry) else None
        
        if self._tool_registry:
            if enable_default_tools and hasattr(self._tool_registry, "register_defaults"):
                self._tool_registry.register_defaults()
            if tools:
                for tool_fn in tools:
                    if hasattr(self._tool_registry, "register"):
                        self._tool_registry.register(tool_fn)
        
        self._conversation = Conversation(
            system_prompt=system_prompt or DEFAULT_SYSTEM_PROMPT
        )
        self._model = model or getattr(self._client, "model_name", "default-model")
        self._max_turns = max_turns
        self._temperature = temperature
        self._on_stream: Callable[[StreamChunk], None] | None = None
    
    def on_stream(self, callback: Callable[[StreamChunk], None]) -> None:
        """Set a callback for streaming output."""
        self._on_stream = callback
    
    async def run(self, task: str) -> AgentResult:
        """Run a one-shot task through the agentic loop."""
        planner = Planner(
            client=self._client,
            conversation=self._conversation,
            tool_registry=self._tool_registry,
            model=self._model,
            max_turns=self._max_turns,
            temperature=self._temperature,
            on_stream=self._on_stream,
        )
        return await planner.run(task)
    
    async def chat(self, message: str) -> AgentResult:
        """Send a message in an ongoing conversation."""
        return await self.run(message)
    
    def reset(self) -> None:
        """Reset conversation history."""
        self._conversation.clear()
    
    @property
    def provider(self) -> str:
        """Get the current provider name."""
        return getattr(self._client, "provider", "unknown")
    
    @property
    def model(self) -> str:
        """Get the current model name."""
        return self._model
    
    @property
    def tool_count(self) -> int:
        """Get the number of registered tools."""
        if self._tool_registry and hasattr(self._tool_registry, "get_tool_definitions"):
            return len(self._tool_registry.get_tool_definitions())
        return 0
