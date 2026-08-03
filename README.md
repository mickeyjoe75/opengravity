# OpenGravity

**An open-source, model-agnostic agentic AI framework supporting 12+ LLM providers.**

OpenGravity provides a unified interface for building powerful, tool-using AI agents powered by a wide variety of foundation models. Under the hood, OpenGravity standardizes everything through the OpenAI SDK, ensuring consistent tool calling, streaming, and conversation management across all supported platforms.

## Features

- 🔌 **Unified Interface:** One API to rule them all. Switch models and providers with a single parameter.
- 🛠️ **Seamless Tool Calling:** Expose Python functions to models natively using a simple `@tool` decorator.
- 💬 **Conversation Management:** Built-in agentic loop that manages conversation history and tool execution automatically.
- ⚡ **Asynchronous by Default:** Built with `asyncio` for high performance and streaming support.
- 📦 **Zero-Config CLI:** Ready-to-use CLI application for chatting, running agents, and managing configuration.

## Quick Start

### Installation

```bash
pip install opengravity
```

### Configuration

Set up your environment variables. You can copy the example `.env` file:

```bash
cp .env.example .env
```

Set your API keys for the providers you want to use, for example:

```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENGRAVITY_DEFAULT_PROVIDER="openai"
export OPENGRAVITY_DEFAULT_MODEL="gpt-4o"
```

### Usage

```python
import asyncio
from opengravity import Agent, tool

@tool
def get_weather(location: str) -> str:
    """Get the weather for a location."""
    return f"The weather in {location} is sunny."

async def main():
    agent = Agent(provider="openai", model="gpt-4o", tools=[get_weather])
    response = await agent.run("What is the weather like in San Francisco?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Supported Providers

| Provider | Default Model | Tool Calling |
| :--- | :--- | :--- |
| OpenAI | `gpt-4o` | ✅ |
| DeepSeek | `deepseek-chat` | ✅ |
| Moonshot (Kimi) | `moonshot-v1-8k` | ✅ |
| Zhipu (GLM) | `glm-4` | ✅ |
| Alibaba (Qwen) | `qwen-max` | ✅ |
| Mistral | `mistral-large-latest` | ✅ |
| Google Gemini | `gemini-1.5-pro` | ✅ |
| Groq | `llama3-70b-8192` | ✅ |
| Together AI | `meta-llama/Llama-3-70b-chat-hf` | ✅ |
| OpenRouter | `auto` | ✅ |

*Note: All providers are routed through the official `openai` Python SDK by dynamically customizing the `base_url`.*

## CLI Usage

OpenGravity comes with a powerful Command-Line Interface.

```bash
# Start an interactive chat session
opengravity chat --provider openai --model gpt-4o

# Run an agent on a specific prompt
opengravity run "Summarize this file" --file ./data.txt

# Configure settings
opengravity config set default_provider deepseek
```

## Custom Endpoints

You can also use OpenGravity with any OpenAI-compatible API endpoint:

```python
agent = Agent(
    provider="custom",
    model="local-model",
    base_url="http://localhost:8080/v1",
    api_key="not-needed"
)
```

## Architecture

OpenGravity operates on a simple, robust agentic loop:
1. **Send Message:** Dispatch user prompt and conversation history to the selected provider.
2. **Check for Tools:** If the model decides to call a tool, parse the JSON arguments using Pydantic.
3. **Execute Tools:** Run the Python function corresponding to the tool.
4. **Repeat:** Feed the tool output back into the model until a final answer is reached.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for more details on how to get started.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
