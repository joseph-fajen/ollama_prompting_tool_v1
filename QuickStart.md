# Ollama Prompt CLI - QuickStart

## Basic Usage

```bash
# Interactive menu
python ollama_prompt.py

# Bypass menu
python ollama_prompt.py --no-menu

# Specific model
python ollama_prompt.py --model llama3:8b

# Multiple models
python ollama_prompt.py --models llama3:8b mixtral:latest phi3:mini

# All models
python ollama_prompt.py --all-models
```

## Custom Prompts

```bash
# List available prompts
python ollama_prompt.py --list-prompts

# Use custom user prompt
python ollama_prompt.py --prompt-file user_prompts/mortgage_advice.md

# Add system prompt
python ollama_prompt.py --system-file system_prompts/expert_financial_advisor.md
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

# Reset configuration to defaults
python ollama_prompt.py --reset-config

# Set custom Ollama API URL
python ollama_prompt.py --base-url http://192.168.1.100:11434
```

See all options: `python ollama_prompt.py --help`