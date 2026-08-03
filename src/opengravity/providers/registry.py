import os
from opengravity.providers.configs import ProviderConfig, PROVIDERS, get_provider_config
from opengravity.providers.base import ModelClient

class ProviderRegistry:
    """Discovers and manages LLM providers."""
    
    @classmethod
    def resolve(cls, provider: str = "auto", model: str | None = None, 
                api_key: str | None = None, base_url: str | None = None) -> ModelClient:
        """Resolve a provider name to a configured ModelClient."""
        if provider == "auto":
            provider_name, config = cls.auto_detect()
        else:
            provider_name = provider
            config = get_provider_config(provider_name)
            
        if provider_name == "custom" and not base_url:
            raise ValueError("When using the 'custom' provider, a 'base_url' must be provided.")
            
        client = ModelClient(config=config, api_key=api_key, base_url=base_url)
        # Use provided model or config default
        if model:
            client._current_model = model
        return client
    
    @classmethod
    def auto_detect(cls) -> tuple[str, ProviderConfig]:
        """Auto-detect the best available provider from environment variables."""
        priority_order = [
            "openai", "deepseek", "kimi", "glm", "qwen", 
            "mistral", "gemini", "groq", "together", 
            "openrouter", "ollama"
        ]
        
        for name in priority_order:
            config = PROVIDERS.get(name)
            if not config:
                continue
                
            if config.api_key_env and os.environ.get(config.api_key_env):
                return name, config
                
            # Ollama is an exception since it typically doesn't need an API key
            if name == "ollama" and config.api_key_default:
                return name, config
                
        raise ValueError("No available providers detected from environment variables.")
    
    @classmethod
    def list_available(cls) -> list[tuple[str, ProviderConfig, bool]]:
        """List all providers and whether they're configured (have API key)."""
        available = []
        for name, config in PROVIDERS.items():
            is_configured = False
            if config.api_key_env and os.environ.get(config.api_key_env):
                is_configured = True
            elif config.api_key_default:
                is_configured = True
                
            available.append((name, config, is_configured))
            
        return available
