from pydantic import BaseModel, Field
from enum import Enum

class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class ToolCallInfo(BaseModel):
    """Info about a tool call from the model."""
    id: str
    name: str
    arguments: str  # JSON string

class Message(BaseModel):
    """A conversation message."""
    role: Role
    content: str | None = None
    name: str | None = None
    tool_calls: list[ToolCallInfo] | None = None
    tool_call_id: str | None = None

class ToolResult(BaseModel):
    """Result of executing a tool."""
    tool_call_id: str
    name: str
    result: str
    is_error: bool = False

class StreamChunk(BaseModel):
    """A chunk of streaming output."""
    type: str  # "text", "reasoning", "tool_call", "tool_result", "error", "done"
    content: str = ""
    tool_call: ToolCallInfo | None = None
    tool_result: ToolResult | None = None

class UsageStats(BaseModel):
    """Token usage statistics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class AgentResult(BaseModel):
    """Final result of an agent run."""
    content: str
    messages: list[Message] = []
    tool_calls_made: int = 0
    turns: int = 0
    usage: UsageStats = Field(default_factory=UsageStats)
    elapsed_seconds: float = 0.0
