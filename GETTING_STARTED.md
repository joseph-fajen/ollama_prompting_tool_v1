# Getting Started with LLM Prompt CLI

## Installation

1. Ensure you have [Python 3.7+](https://www.python.org/downloads/) installed
2. Install required Python packages:

```bash
pip install -r requirements.txt
```

3. For Ollama provider (default):
   - Install [Ollama](https://ollama.ai/download) for your platform
   - Install at least one model (see below)
   - Start the Ollama service

4. For other providers (OpenAI, HuggingFace):
   - Set up API keys (see below)

## Installing Ollama Models (for Ollama provider)

Before using the Ollama provider, you'll need at least one model installed:

```bash
# Examples of models to install
ollama pull llama3:8b
ollama pull mixtral:latest
ollama pull phi3:mini
ollama pull codellama:7b-instruct

# List installed models
ollama list
```

## Running the Ollama Service

When using the Ollama provider, ensure the service is running:

```bash
ollama serve
```

This starts the Ollama API server on http://localhost:11434.

## Setting Up API Keys (for non-Ollama providers)

For OpenAI or HuggingFace providers, you'll need to set up API keys:

```bash
# Interactive API key setup (recommended)
python ollama_prompt.py --setup-keys
```

Alternatively, you can:
- Use environment variables: `OLLAMA_TOOL_OPENAI_API_KEY` or `OLLAMA_TOOL_HUGGINGFACE_API_KEY`
- Provide keys directly: `python ollama_prompt.py --provider openai --api-key your_key_here`

## Basic Usage

The simplest way to use the script is with the interactive menu:

```bash
python ollama_prompt.py
```

This will guide you through selecting:
1. A provider (Ollama, OpenAI, or HuggingFace)
2. A model (or all models for Ollama)
3. A user prompt file (or use the default)
4. An optional system prompt file
5. Output display preferences

## Using Prompt Files

The script organizes prompts into two directories:

- `system_prompts/`: Contains AI role definitions (e.g., "expert_financial_advisor.md")
- `user_prompts/`: Contains specific tasks or questions (e.g., "heloc_advice.md")

You can add your own prompt files to these directories.

## Output Files

All outputs are saved in the `ollama_responses/` directory, organized by batch:

- Each run creates a timestamped batch folder
- Each model response is saved as a markdown file
- Files include all details: system prompt, user prompt, and the complete response

## Configuration

The script now supports saving your preferred settings to avoid specifying the same options repeatedly:

```bash
# Display current configuration
python ollama_prompt.py --show-config

# Save your current settings as defaults
python ollama_prompt.py --model llama3:8b --stream --save-config

# Reset to factory defaults
python ollama_prompt.py --reset-config
```

Configuration values are stored in `config/ollama_config.yaml` and include:
- Default provider (Ollama, OpenAI, HuggingFace)
- Default model(s) to use
- Default system and user prompts
- Output preferences (streaming, saving)
- Performance settings (timeout, max workers)
- Custom API URLs for different providers
- API key handling preferences

## Chat Mode

The new `ollama_chat.py` script provides an interactive chat experience with conversation history:

```bash
# Start a chat session with the default model
python ollama_chat.py

# Chat with a specific model and stream tokens in real-time
python ollama_chat.py --model llama3:8b --stream

# Load a previous conversation
python ollama_chat.py --load-conversation <conversation_id>

# List all saved conversations
python ollama_chat.py --list-conversations
```

During a chat session, you can use commands like `/help`, `/new`, `/load`, `/show`, and `/model`.

## Multiple API Providers

The chat tool supports different LLM providers with secure API key management:

```bash
# Set up your API keys securely (recommended first step)
python ollama_chat.py --setup-keys

# Use OpenAI API with stored key
python ollama_chat.py --provider openai

# Use Hugging Face models with stored key
python ollama_chat.py --provider huggingface
```

### API Key Security

Your API keys are stored securely using one of these methods:

1. **System keyring** - Uses your OS's secure credential store (most secure)
2. **Local config** - Encrypted file in your home directory
3. **Environment variables** - For temporary usage:
   ```bash
   export OLLAMA_TOOL_OPENAI_API_KEY=your_key_here
   export OLLAMA_TOOL_HUGGINGFACE_API_KEY=your_key_here
   ```

## Next Steps

- Check [QuickStart.md](QuickStart.md) for common commands
- See [ChatMode.md](ChatMode.md) for detailed chat features and API compatibility
- Explore [README.md](README.md) for advanced usage and examples
- See [test_examples.md](test_examples.md) for practical examples