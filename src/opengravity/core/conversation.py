from opengravity.core.types import Message, Role, ToolCallInfo, ToolResult

class Conversation:
    """Manages conversation history and context."""
    
    def __init__(self, system_prompt: str | None = None, max_history: int = 100):
        self._messages: list[Message] = []
        self._system_prompt = system_prompt
        self._max_history = max_history
        if system_prompt:
            self._messages.append(Message(role=Role.SYSTEM, content=system_prompt))
    
    def add_user_message(self, content: str) -> None:
        """Adds a user message to the conversation."""
        self._messages.append(Message(role=Role.USER, content=content))
        self._prune()
        
    def add_assistant_message(self, content: str | None = None, tool_calls: list[ToolCallInfo] | None = None) -> None:
        """Adds an assistant message to the conversation, optionally with tool calls."""
        self._messages.append(Message(role=Role.ASSISTANT, content=content, tool_calls=tool_calls))
        self._prune()
        
    def add_tool_result(self, result: ToolResult) -> None:
        """Adds a tool execution result to the conversation."""
        self._messages.append(Message(
            role=Role.TOOL, 
            content=result.result, 
            tool_call_id=result.tool_call_id, 
            name=result.name
        ))
        self._prune()
        
    def get_messages(self) -> list[dict]:
        """Returns messages formatted for the OpenAI API."""
        out = []
        for m in self._messages:
            d = {"role": m.role.value}
            if m.content is not None:
                d["content"] = m.content
            if m.name is not None:
                d["name"] = m.name
            if m.tool_calls is not None:
                d["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": tc.arguments}
                    } 
                    for tc in m.tool_calls
                ]
            if m.tool_call_id is not None:
                d["tool_call_id"] = m.tool_call_id
            out.append(d)
        return out
        
    def clear(self) -> None:
        """Clears the conversation history, retaining only the system prompt."""
        self._messages.clear()
        if self._system_prompt:
            self._messages.append(Message(role=Role.SYSTEM, content=self._system_prompt))
            
    def _prune(self) -> None:
        """Ensures the conversation doesn't exceed the max history, keeping the system prompt."""
        if len(self._messages) <= self._max_history:
            return
            
        sys_msgs = []
        if self._messages and self._messages[0].role == Role.SYSTEM:
            sys_msgs = [self._messages[0]]
            
        keep_count = self._max_history - len(sys_msgs)
        if keep_count <= 0:
            self._messages = sys_msgs
        else:
            self._messages = sys_msgs + self._messages[-keep_count:]
            
    @property
    def message_count(self) -> int:
        """Returns the number of messages in the conversation."""
        return len(self._messages)
