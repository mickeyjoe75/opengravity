import tempfile
import subprocess
import os
from opengravity.tools.registry import tool

@tool(description="Execute Python code and return the output. Code runs in a subprocess for safety.")
def run_python(code: str, timeout: int = 30) -> str:
    """Execute Python code."""
    fd, temp_path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(code)
            
        result = subprocess.run(
            ["python3", temp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = []
        if result.stdout:
            output.append(result.stdout)
        if result.stderr:
            output.append(f"Errors:\n{result.stderr}")
            
        if not output:
            return f"Code executed successfully (exit code {result.returncode}) with no output."
            
        return "\n".join(output)
        
    except subprocess.TimeoutExpired:
        return f"Error: Code execution timed out after {timeout} seconds."
    except Exception as e:
        return f"Error executing Python code: {e}"
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass
