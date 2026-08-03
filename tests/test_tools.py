import pytest
import asyncio
from opengravity.tools.registry import tool, ToolRegistry

@tool(description="A test tool that adds two numbers")
def add_numbers(a: int, b: int) -> str:
    return str(a + b)

@tool(description="A test tool with optional params")
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

def test_tool_decorator_creates_definition():
    assert hasattr(add_numbers, "_tool_definition")
    td = add_numbers._tool_definition
    assert td.name == "add_numbers"
    assert td.description == "A test tool that adds two numbers"

def test_tool_schema_types():
    td = add_numbers._tool_definition
    props = td.parameters["properties"]
    assert props["a"]["type"] == "integer"
    assert props["b"]["type"] == "integer"

def test_tool_required_params():
    td = add_numbers._tool_definition
    assert "a" in td.parameters["required"]
    assert "b" in td.parameters["required"]

def test_tool_optional_params():
    td = greet._tool_definition
    assert "name" in td.parameters["required"]
    assert "greeting" not in td.parameters.get("required", [])

def test_registry_register():
    registry = ToolRegistry()
    registry.register(add_numbers)
    assert "add_numbers" in registry.tool_names
    assert len(registry) == 1

def test_registry_definitions():
    registry = ToolRegistry()
    registry.register(add_numbers)
    defs = registry.get_tool_definitions()
    assert len(defs) == 1
    assert defs[0]["type"] == "function"
    assert defs[0]["function"]["name"] == "add_numbers"

@pytest.mark.asyncio
async def test_registry_execute():
    registry = ToolRegistry()
    registry.register(add_numbers)
    result = await registry.execute("add_numbers", '{"a": 3, "b": 4}')
    assert "7" in result

@pytest.mark.asyncio
async def test_registry_execute_unknown_tool():
    registry = ToolRegistry()
    result = await registry.execute("unknown_tool", '{}')
    assert "error" in result.lower() or "not found" in result.lower() or "unknown" in result.lower()
