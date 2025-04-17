# LLM Prompt CLI - QuickStart

## Basic Usage - One-Shot Mode

```bash
# Interactive menu
python ollama_prompt.py

# Bypass menu
python ollama_prompt.py --no-menu

# Specific model
python ollama_prompt.py --model llama3:8b

# Multiple models
python ollama_prompt.py --models llama3:8b mixtral:latest phi3:mini

# All models (Ollama provider only)
python ollama_prompt.py --all-models

# Using different providers
python ollama_prompt.py --provider huggingface --model mistralai/Mistral-7B-Instruct-v0.1
python ollama_prompt.py --provider openai --model gpt-3.5-turbo

# Set up API keys securely (for non-Ollama providers)
python ollama_prompt.py --setup-keys
```

## Chat Mode

```bash
# Start interactive chat (new!)
python ollama_chat.py

# Chat with specific model
python ollama_chat.py --model llama3:8b

# Chat with streaming (recommended)
python ollama_chat.py --stream

# Set up API keys securely (recommended)
python ollama_chat.py --setup-keys

# Use alternate provider with stored key
python ollama_chat.py --provider openai
```

See [ChatMode.md](ChatMode.md) for more chat features.

## Custom Prompts

```bash
# List available prompts
python ollama_prompt.py --list-prompts

# Use custom user prompt
python ollama_prompt.py --prompt-file user_prompts/smart_contract_explanation.md

# Add system prompt
python ollama_prompt.py --system-file system_prompts/blockchain_educator.md
```

## Output Options

```bash
# Stream tokens in real-time
python ollama_prompt.py --stream

# Don't save response to file
python ollama_prompt.py --no-save

# Parallel execution control
python ollama_prompt.py --max-workers 4

# Adjust timeout (in seconds)
python ollama_prompt.py --timeout 600
```

## Configuration Options

```bash
# Show current configuration
python ollama_prompt.py --show-config

# Save current run settings as default
python ollama_prompt.py --model llama3:8b --stream --save-config

# Save provider settings as default
python ollama_prompt.py --provider huggingface --model mistralai/Mistral-7B-Instruct-v0.1 --save-config

# Reset configuration to defaults
python ollama_prompt.py --reset-config

# Set custom Ollama API URL
python ollama_prompt.py --base-url http://192.168.1.100:11434

# Set custom OpenAI-compatible API URL
python ollama_prompt.py --provider openai --base-url http://localhost:8080 --api-key none
```

See all options: `python ollama_prompt.py --help`