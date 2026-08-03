import pytest
from opengravity.core.types import Role, Message, ToolCallInfo, ToolResult, StreamChunk, AgentResult, UsageStats
from opengravity.core.conversation import Conversation

def test_message_creation():
    msg = Message(role=Role.USER, content="Hello")
    assert msg.role == Role.USER
    assert msg.content == "Hello"

def test_conversation_init():
    conv = Conversation(system_prompt="You are helpful.")
    messages = conv.get_messages()
    assert len(messages) == 1
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are helpful."

def test_conversation_add_messages():
    conv = Conversation()
    conv.add_user_message("Hello")
    conv.add_assistant_message(content="Hi there!")
    messages = conv.get_messages()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"

def test_conversation_tool_calls():
    conv = Conversation()
    conv.add_user_message("list files")
    tc = ToolCallInfo(id="call_1", name="list_directory", arguments='{"path": "."}')
    conv.add_assistant_message(tool_calls=[tc])
    messages = conv.get_messages()
    assert messages[-1]["tool_calls"][0]["function"]["name"] == "list_directory"

def test_conversation_tool_result():
    conv = Conversation()
    conv.add_user_message("test")
    tc = ToolCallInfo(id="call_1", name="test", arguments='{}')
    conv.add_assistant_message(tool_calls=[tc])
    result = ToolResult(tool_call_id="call_1", name="test", result="done")
    conv.add_tool_result(result)
    messages = conv.get_messages()
    assert messages[-1]["role"] == "tool"
    assert messages[-1]["tool_call_id"] == "call_1"

def test_conversation_clear():
    conv = Conversation(system_prompt="test")
    conv.add_user_message("hello")
    assert conv.message_count == 2
    conv.clear()
    # After clear, system prompt should remain
    assert conv.message_count == 1

def test_agent_result():
    result = AgentResult(
        content="Done!",
        tool_calls_made=3,
        turns=2,
        elapsed_seconds=1.5,
    )
    assert result.content == "Done!"
    assert result.tool_calls_made == 3

def test_stream_chunk_text():
    chunk = StreamChunk(type="text", content="Hello")
    assert chunk.type == "text"
    assert chunk.content == "Hello"

def test_stream_chunk_tool_call():
    tc = ToolCallInfo(id="1", name="test", arguments='{}')
    chunk = StreamChunk(type="tool_call", tool_call=tc)
    assert chunk.tool_call.name == "test"
