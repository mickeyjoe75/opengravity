import os
from typing import AsyncIterator, Any
from openai import AsyncOpenAI
from opengravity.providers.configs import ProviderConfig

class ModelClient:
    """Unified LLM client using the OpenAI SDK with custom base_url."""
    
    def __init__(self, config: ProviderConfig, api_key: str | None = None, base_url: str | None = None):
        self.config = config
        
        # Resolve API key: explicit > env var > default
        resolved_api_key = api_key
        if not resolved_api_key and config.api_key_env:
            resolved_api_key = os.environ.get(config.api_key_env)
        if not resolved_api_key:
            resolved_api_key = config.api_key_default
            
        if not resolved_api_key:
            raise ValueError(f"API key for provider '{config.name}' is missing. "
                             f"Please set {config.api_key_env} or provide it explicitly.")
            
        # Resolve base URL: explicit > config
        resolved_base_url = base_url or config.base_url
        if not resolved_base_url:
            raise ValueError(f"Base URL for provider '{config.name}' is missing.")
            
        self._api_key = resolved_api_key
        self._base_url = resolved_base_url
        
        self.client = AsyncOpenAI(
            api_key=self._api_key,
            base_url=self._base_url,
        )
        self._current_model = config.default_model

    async def chat(
        self,
        messages: list[dict],
        model: str | None = None,
        tools: list[dict] | None = None,
        tool_choice: str | None = None,
        temperature: float = 0.0,
        stream: bool = True,
        max_tokens: int | None = None,
    ) -> AsyncIterator[Any] | Any:
        """Send a chat completion request with optional tool definitions."""
        self._current_model = model or self.config.default_model
        if not self._current_model:
            raise ValueError(f"No model specified and no default model found for provider '{self.config.name}'.")
            
        kwargs: dict[str, Any] = {
            "model": self._current_model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
            
        if tools and self.config.supports_tool_calling:
            kwargs["tools"] = tools
            if tool_choice:
                kwargs["tool_choice"] = tool_choice
                
        response = await self.client.chat.completions.create(**kwargs)
        return response

    @property
    def provider_name(self) -> str:
        return self.config.name
    
    @property 
    def model_name(self) -> str:
        return self._current_model or self.config.default_model or "unknown"
