import subprocess
from opengravity.tools.registry import tool

@tool(description="Execute a shell command and return stdout/stderr. Use for running scripts, installing packages, git operations, etc.")
def run_command(command: str, cwd: str = ".", timeout: int = 60) -> str:
    """Run a shell command."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = []
        if result.stdout:
            output.append(result.stdout)
        if result.stderr:
            output.append(result.stderr)
            
        if not output:
            return f"Command executed successfully with exit code {result.returncode} (no output)."
            
        return "\n".join(output)
        
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds."
    except Exception as e:
        return f"Error executing command: {e}"
