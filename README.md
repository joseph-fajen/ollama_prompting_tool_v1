# Ollama LLM Runner

A Python utility for running prompts on local Ollama LLM models with parallel execution support and interactive chat mode.

## Quick Start

See [QuickStart.md](QuickStart.md) for common commands and basic usage.
See [ChatMode.md](ChatMode.md) for using the new chat mode and API compatibility features.

## Features

- Interactive CLI menu for easy model and prompt selection
- Support for system prompts and user prompts from files
- Parallel model execution for faster multi-model processing
- Streaming or batch response modes
- Response saving to markdown files
- Progress tracking with rich console output
- Persistent configuration system to save default settings
- **New:** Interactive chat mode with conversation history
- **New:** Support for multiple LLM providers (Ollama, OpenAI, Hugging Face)
- **New:** Conversation management (save/load/list conversations)

## Prerequisites

- Python 3.6+
- [Ollama](https://ollama.ai/) installed locally
- Required packages: `pip install requests rich`

## Getting Started

Before running this script, ensure the Ollama service is running:

```bash
ollama serve
```

This starts the Ollama API server on http://localhost:11434.

## Common Issues

- **404 Not Found**: Ollama service not running or model name mismatch
- **400 Bad Request**: Trying to use an embedding model for text generation

## Prompt Organization

The script uses two directories for managing prompts:

- `system_prompts/`: Contains AI role or persona definitions
- `user_prompts/`: Contains specific tasks or questions

List available prompts with: `python ollama_prompt.py --list-prompts`

## Response Files

- Responses are saved in timestamped batch folders in `ollama_responses/`
- Files include model info, timing, original prompt, and complete response
- Batch organization makes comparing results across models easy

## Examples

### Run with interactive menu
```bash
python ollama_prompt.py
```

### Run a specific model with system and user prompts
```bash
python ollama_prompt.py --model llama3:8b --system-file system_prompts/blockchain_educator.md --prompt-file user_prompts/smart_contract_explanation.md
```

### Run on multiple models in parallel
```bash
python ollama_prompt.py --models llama3:8b mixtral:latest phi3:mini --max-workers 4
```

For more examples, see [test_examples.md](test_examples.md).

## Chat Mode

The new chat mode provides an interactive conversation experience:

```bash
# Start a chat session
python ollama_chat.py

# With streaming (recommended for chat)
python ollama_chat.py --stream
```

Features include:
- Conversation history tracking
- Save/load conversations
- Interactive commands during chat (use `/help` to see options)
- System prompts that persist across the conversation

See [ChatMode.md](ChatMode.md) for complete documentation.

## API Compatibility

Support for multiple LLM providers through an adapter pattern:

```bash
# Set up API keys securely (recommended)
python ollama_chat.py --setup-keys

# OpenAI-compatible API with stored key
python ollama_chat.py --provider openai

# Hugging Face models with stored key
python ollama_chat.py --provider huggingface
```

**Secure API Key Management:**
- System keyring integration (macOS Keychain, Windows Credential Manager, etc.)
- Environment variables: `OLLAMA_TOOL_OPENAI_API_KEY`, `OLLAMA_TOOL_HUGGINGFACE_API_KEY`
- Encrypted local configuration in `~/.ollama_tool/`
- Interactive setup wizard

All providers implement a common interface, making it easy to switch between them with minimal code changes.

## Configuration System

The script now includes a configuration system that persists your preferred settings:

- Configurations are stored in `config/ollama_config.yaml`
- Display current settings with `python ollama_prompt.py --show-config`
- Save current run settings as defaults with `python ollama_prompt.py --save-config`
- Reset configuration to defaults with `python ollama_prompt.py --reset-config`

You can configure default values for:
- Default model(s) to use
- Default system and user prompts
- Output preferences (streaming, saving responses)
- Performance options (max workers, timeout)
- Custom Ollama API URL
- API provider settings (provider type, API keys)

## Default Behavior

- If no options are specified, uses values from configuration
- If no configuration exists, falls back to these defaults:
  - If no prompt file is specified, uses default HELOC financial advice prompt
  - If no system prompt is specified, only the user prompt is used
  - If no model is specified, runs on all available models