import inspect
import json
import functools
import types
from typing import Any, Callable, get_type_hints, Optional, Union
from pydantic import BaseModel, ConfigDict

class ToolDefinition(BaseModel):
    """Internal representation of a registered tool."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    description: str
    parameters: dict  # JSON Schema
    function: Any  # The actual callable (excluded from serialization)

def _map_type_to_schema(t: Any) -> dict:
    if t == str:
        return {"type": "string"}
    elif t == int:
        return {"type": "integer"}
    elif t == float:
        return {"type": "number"}
    elif t == bool:
        return {"type": "boolean"}
    elif t == list or getattr(t, "__origin__", None) == list:
        return {"type": "array"}
    elif t == dict or getattr(t, "__origin__", None) == dict:
        return {"type": "object"}
    
    # Handle Optional/Union[..., None]
    origin = getattr(t, "__origin__", None)
    if origin is Union:
        args = getattr(t, "__args__", [])
        if type(None) in args:
            non_none_args = [a for a in args if a is not type(None)]
            if len(non_none_args) == 1:
                return _map_type_to_schema(non_none_args[0])
    
    return {"type": "string"}  # Default fallback

def tool(description: str | None = None, name: str | None = None):
    """Decorator to register a function as a tool.
    
    Auto-generates OpenAI-compatible JSON schema from type hints and docstring.
    """
    def decorator(func: Callable) -> Callable:
        func_name = name or func.__name__
        func_desc = description or func.__doc__ or ""
        func_desc = func_desc.strip()
        
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param_name, param in sig.parameters.items():
            if param_name == "self" or param_name == "cls":
                continue
                
            param_type = type_hints.get(param_name, Any)
            param_schema = _map_type_to_schema(param_type)
            
            parameters["properties"][param_name] = param_schema
            
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)
                
        # Register the definition on the function
        func._tool_definition = ToolDefinition(
            name=func_name,
            description=func_desc,
            parameters=parameters,
            function=func
        )
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
            
        wrapper._tool_definition = func._tool_definition
        return wrapper
    return decorator


class ToolRegistry:
    """Manages tool registration and execution."""
    
    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}
    
    def register(self, func: Callable) -> None:
        """Register a @tool-decorated function."""
        if not hasattr(func, "_tool_definition"):
            raise ValueError(f"Function {func.__name__} is not decorated with @tool")
        
        td: ToolDefinition = getattr(func, "_tool_definition")
        self._tools[td.name] = td
    
    def register_defaults(self) -> None:
        """Register all built-in tools."""
        from opengravity.tools.shell import run_command
        from opengravity.tools.file_ops import read_file, write_file, list_directory, search_files
        from opengravity.tools.web_search import web_search
        from opengravity.tools.python_exec import run_python
        
        for fn in [run_command, read_file, write_file, list_directory, search_files, web_search, run_python]:
            self.register(fn)
    
    def get_tool_definitions(self) -> list[dict]:
        """Get OpenAI-compatible tool definitions for all registered tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": td.name,
                    "description": td.description,
                    "parameters": td.parameters,
                }
            }
            for td in self._tools.values()
        ]
    
    async def execute(self, name: str, arguments: str) -> str:
        """Execute a tool by name with JSON arguments."""
        if name not in self._tools:
            return f"Error: Tool '{name}' not found."
            
        try:
            kwargs = json.loads(arguments) if arguments else {}
        except json.JSONDecodeError as e:
            return f"Error parsing arguments: {e}"
            
        tool_def = self._tools[name]
        func = tool_def.function
        
        try:
            if inspect.iscoroutinefunction(func):
                result = await func(**kwargs)
            else:
                result = func(**kwargs)
                
            return str(result)
        except Exception as e:
            return f"Error executing tool '{name}': {e}"
            
    @property
    def tool_names(self) -> list[str]:
        return list(self._tools.keys())
        
    def __len__(self) -> int:
        return len(self._tools)
