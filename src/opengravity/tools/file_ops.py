import os
import glob
from pathlib import Path
from opengravity.tools.registry import tool

@tool(description="Read the contents of a file at the given path")
def read_file(path: str, max_lines: int = 500) -> str:
    """Read a file."""
    try:
        if not os.path.exists(path):
            return f"Error: File not found: {path}"
            
        with open(path, 'r', encoding='utf-8') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    lines.append(f"... (truncated after {max_lines} lines)")
                    break
                lines.append(f"{i+1}: {line.rstrip()}")
                
        return "\n".join(lines)
    except Exception as e:
        return f"Error reading file {path}: {e}"

@tool(description="Write content to a file, creating directories if needed")
def write_file(path: str, content: str) -> str:
    """Write to a file."""
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing to file {path}: {e}"

@tool(description="List contents of a directory")
def list_directory(path: str = ".") -> str:
    """List directory contents."""
    try:
        if not os.path.exists(path):
            return f"Error: Directory not found: {path}"
        if not os.path.isdir(path):
            return f"Error: {path} is not a directory"
            
        items = os.listdir(path)
        if not items:
            return "Directory is empty."
            
        output = []
        for item in sorted(items):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                output.append(f"{item}/")
            else:
                size = os.path.getsize(full_path)
                output.append(f"{item} ({size} bytes)")
                
        return "\n".join(output)
    except Exception as e:
        return f"Error listing directory {path}: {e}"

@tool(description="Search for a pattern in files using recursive grep")
def search_files(pattern: str, path: str = ".", file_glob: str = "*") -> str:
    """Search files for a pattern."""
    try:
        search_path = Path(path)
        if not search_path.exists() or not search_path.is_dir():
            return f"Error: Directory not found: {path}"
            
        matches = []
        for root, _, files in os.walk(path):
            for filename in files:
                filepath = Path(root) / filename
                if filepath.match(file_glob):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            for i, line in enumerate(f):
                                if pattern in line:
                                    matches.append(f"{filepath}:{i+1}: {line.strip()}")
                                    if len(matches) >= 50:
                                        matches.append("... (limited to 50 results)")
                                        return "\n".join(matches)
                    except UnicodeDecodeError:
                        continue  # Skip binary files
                    except Exception:
                        continue
                        
        if not matches:
            return "No matches found."
            
        return "\n".join(matches)
    except Exception as e:
        return f"Error searching files: {e}"
