import time
from typing import AsyncIterator, Callable, Any
from opengravity.core.types import AgentResult, StreamChunk, ToolCallInfo, ToolResult
from opengravity.core.conversation import Conversation

# Support runtime where registry hasn't been implemented yet
try:
    from opengravity.tools.registry import ToolRegistry
except ImportError:
    ToolRegistry = Any

class Planner:
    """Executes the agentic loop: observe → think → act → reflect."""
    
    def __init__(
        self,
        client: Any,
        conversation: Conversation,
        tool_registry: ToolRegistry,
        model: str | None = None,
        max_turns: int = 50,
        temperature: float = 0.0,
        on_stream: Callable[[StreamChunk], None] | None = None,
    ):
        self._client = client
        self._conversation = conversation
        self._tool_registry = tool_registry
        self._model = model
        self._max_turns = max_turns
        self._temperature = temperature
        self._on_stream = on_stream
    
    async def run(self, user_message: str) -> AgentResult:
        """Execute the full agentic loop for a user message."""
        start_time = time.time()
        self._conversation.add_user_message(user_message)
        
        tool_calls_made = 0
        turns = 0
        final_content = ""
        
        while turns < self._max_turns:
            turns += 1
            messages = self._conversation.get_messages()
            
            tool_defs = []
            if hasattr(self._tool_registry, "get_tool_definitions"):
                tool_defs = self._tool_registry.get_tool_definitions()
            
            # Send to LLM
            response = await self._client.chat(
                messages=messages,
                model=self._model,
                tools=tool_defs if tool_defs else None,
                temperature=self._temperature,
                stream=True,
            )
            
            assistant_content = ""
            tool_call_accumulators: dict[int, dict] = {}
            
            async for chunk in response:
                choice = chunk.choices[0] if getattr(chunk, "choices", None) else None
                if not choice:
                    continue
                delta = choice.delta
                
                # Handle reasoning content
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                    if self._on_stream:
                        self._on_stream(StreamChunk(type="reasoning", content=delta.reasoning_content))
                
                # Handle text content
                if getattr(delta, "content", None):
                    assistant_content += delta.content
                    if self._on_stream:
                        self._on_stream(StreamChunk(type="text", content=delta.content))
                
                # Handle tool calls (accumulate by index)
                if getattr(delta, "tool_calls", None):
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in tool_call_accumulators:
                            tool_call_accumulators[idx] = {"id": "", "name": "", "arguments": ""}
                        
                        if getattr(tc, "id", None):
                            tool_call_accumulators[idx]["id"] = tc.id
                            
                        if getattr(tc, "function", None):
                            if getattr(tc.function, "name", None):
                                tool_call_accumulators[idx]["name"] += tc.function.name
                            if getattr(tc.function, "arguments", None):
                                tool_call_accumulators[idx]["arguments"] += tc.function.arguments
                
                # Check for finish
                if getattr(choice, "finish_reason", None):
                    break
            
            # Finalize tool calls
            tool_calls = []
            for _, tc_data in sorted(tool_call_accumulators.items()):
                tool_calls.append(ToolCallInfo(
                    id=tc_data["id"],
                    name=tc_data["name"],
                    arguments=tc_data["arguments"]
                ))
            
            # If tool calls were made, execute them and continue loop
            if tool_calls:
                self._conversation.add_assistant_message(content=assistant_content or None, tool_calls=tool_calls)
                
                for tc in tool_calls:
                    if self._on_stream:
                        self._on_stream(StreamChunk(type="tool_call", tool_call=tc))
                    
                    # Execute the tool
                    try:
                        result = await self._tool_registry.execute(tc.name, tc.arguments)
                        is_error = False
                    except Exception as e:
                        result = str(e)
                        is_error = True
                        
                    tool_result = ToolResult(
                        tool_call_id=tc.id,
                        name=tc.name,
                        result=result if isinstance(result, str) else str(result),
                        is_error=is_error,
                    )
                    self._conversation.add_tool_result(tool_result)
                    tool_calls_made += 1
                    
                    if self._on_stream:
                        self._on_stream(StreamChunk(type="tool_result", tool_result=tool_result))
                
                continue  # Go back to top of loop
            
            # No tool calls — we're done
            final_content = assistant_content
            self._conversation.add_assistant_message(content=final_content)
            break
        
        return AgentResult(
            content=final_content,
            messages=self._conversation._messages.copy(),
            tool_calls_made=tool_calls_made,
            turns=turns,
            elapsed_seconds=time.time() - start_time,
        )
