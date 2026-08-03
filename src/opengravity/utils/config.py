import os
from pathlib import Path
from dotenv import load_dotenv

def load_config() -> dict:
    """Load configuration from environment variables and .env file."""
    # Load .env file from current directory and home directory
    load_dotenv()
    home_env = Path.home() / ".opengravity" / ".env"
    if home_env.exists():
        load_dotenv(home_env)
    
    return {
        "default_provider": os.getenv("OPENGRAVITY_DEFAULT_PROVIDER", "auto"),
        "default_model": os.getenv("OPENGRAVITY_DEFAULT_MODEL"),
        "max_turns": int(os.getenv("OPENGRAVITY_MAX_TURNS", "50")),
        "temperature": float(os.getenv("OPENGRAVITY_TEMPERATURE", "0.0")),
    }
