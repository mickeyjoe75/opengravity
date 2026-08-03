import pytest
from opengravity.providers.configs import PROVIDERS, ProviderConfig, get_provider_config, list_providers

def test_all_providers_defined():
    """Verify all expected providers are in the registry."""
    expected = ["openai", "kimi", "glm", "deepseek", "qwen", "mistral", "gemini", "groq", "together", "ollama", "openrouter", "custom"]
    for name in expected:
        assert name in PROVIDERS, f"Provider '{name}' not found"

def test_provider_configs_valid():
    """Verify all provider configs have required fields."""
    for name, config in PROVIDERS.items():
        assert isinstance(config, ProviderConfig)
        assert config.name, f"{name} missing name"
        if name != "custom":
            assert config.base_url, f"{name} missing base_url"

def test_kimi_config():
    config = get_provider_config("kimi")
    assert "moonshot" in config.base_url
    assert "kimi-k2" in config.models
    assert config.supports_tool_calling

def test_glm_config():
    config = get_provider_config("glm")
    assert "bigmodel" in config.base_url
    assert config.base_url.endswith("/v4")

def test_deepseek_config():
    config = get_provider_config("deepseek")
    assert "deepseek-chat" in config.models
    assert config.supports_reasoning

def test_ollama_config():
    config = get_provider_config("ollama")
    assert "localhost" in config.base_url
    assert config.api_key_default == "ollama"

def test_list_providers():
    providers = list_providers()
    assert len(providers) >= 12
    assert "kimi" in providers
    assert "glm" in providers
