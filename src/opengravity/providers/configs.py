from pydantic import BaseModel

class ProviderConfig(BaseModel):
    """Configuration for an LLM provider."""
    name: str                          # Human-readable name
    base_url: str | None = None        # API base URL
    api_key_env: str | None = None     # Environment variable for API key
    api_key_default: str | None = None # Default API key (for local models)
    models: list[str] = []             # Known model identifiers
    default_model: str | None = None   # Default model to use
    supports_tool_calling: bool = True
    supports_streaming: bool = True
    supports_reasoning: bool = False   # Supports reasoning_content field
    notes: str = ""                    # Provider-specific notes/quirks

PROVIDERS: dict[str, ProviderConfig] = {
    "openai": ProviderConfig(
        name="openai",
        base_url="https://api.openai.com/v1",
        api_key_env="OPENAI_API_KEY",
        models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1", "o1-mini"],
        default_model="gpt-4o",
    ),
    "kimi": ProviderConfig(
        name="kimi",
        base_url="https://api.moonshot.ai/v1",
        api_key_env="KIMI_API_KEY",
        models=["kimi-k2", "moonshot-v1-128k", "moonshot-v1-32k", "moonshot-v1-8k"],
        default_model="kimi-k2",
        notes="Strict temperature validation and JSON schema restrictions.",
    ),
    "glm": ProviderConfig(
        name="glm",
        base_url="https://open.bigmodel.cn/api/paas/v4",
        api_key_env="GLM_API_KEY",
        models=["glm-4-plus", "glm-4-flash", "glm-4-air", "glm-z1-flash"],
        default_model="glm-4-plus",
        notes="Base URL must end with /v4 and system message must be first.",
    ),
    "deepseek": ProviderConfig(
        name="deepseek",
        base_url="https://api.deepseek.com",
        api_key_env="DEEPSEEK_API_KEY",
        models=["deepseek-chat", "deepseek-reasoner"],
        default_model="deepseek-chat",
        supports_reasoning=True,
        notes="R1 does not support tool calling. Special handling for reasoning_content.",
    ),
    "qwen": ProviderConfig(
        name="qwen",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key_env="QWEN_API_KEY",
        models=["qwen-max", "qwen-plus", "qwen-turbo", "qwen3-235b-a22b", "qwen3-32b"],
        default_model="qwen-max",
        notes="Regional URL matching may be required.",
    ),
    "mistral": ProviderConfig(
        name="mistral",
        base_url="https://api.mistral.ai/v1",
        api_key_env="MISTRAL_API_KEY",
        models=["mistral-large-latest", "mistral-small-latest", "codestral-latest"],
        default_model="mistral-large-latest",
        notes="JSON mode requires 'json' in the prompt.",
    ),
    "gemini": ProviderConfig(
        name="gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key_env="GEMINI_API_KEY",
        models=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
        default_model="gemini-2.5-flash",
        notes="Do NOT append /v1 to the base_url.",
    ),
    "groq": ProviderConfig(
        name="groq",
        base_url="https://api.groq.com/openai/v1",
        api_key_env="GROQ_API_KEY",
        models=["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama3-70b-8192"],
        default_model="llama-3.3-70b-versatile",
    ),
    "together": ProviderConfig(
        name="together",
        base_url="https://api.together.xyz/v1",
        api_key_env="TOGETHER_API_KEY",
        models=["meta-llama/Llama-3.3-70B-Instruct-Turbo", "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"],
        default_model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    ),
    "ollama": ProviderConfig(
        name="ollama",
        base_url="http://localhost:11434/v1",
        api_key_default="ollama",
        models=[],
        default_model="llama3.1",
        notes="No API key needed. Models are dynamically discovered.",
    ),
    "openrouter": ProviderConfig(
        name="openrouter",
        base_url="https://openrouter.ai/api/v1",
        api_key_env="OPENROUTER_API_KEY",
        models=[],
        default_model="openai/gpt-4o",
    ),
    "custom": ProviderConfig(
        name="custom",
        base_url=None,
        api_key_env="CUSTOM_API_KEY",
        models=[],
        notes="User must provide base_url.",
    ),
}

def get_provider_config(name: str) -> ProviderConfig:
    """Get the configuration for a given provider name."""
    config = PROVIDERS.get(name)
    if not config:
        raise ValueError(f"Provider '{name}' not found.")
    return config

def list_providers() -> list[str]:
    """List all available provider names."""
    return list(PROVIDERS.keys())
