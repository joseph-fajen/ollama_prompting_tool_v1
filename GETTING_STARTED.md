# Getting Started with Ollama Prompt CLI

## Installation

1. Ensure you have [Python 3.7+](https://www.python.org/downloads/) installed
2. Install [Ollama](https://ollama.ai/download) for your platform
3. Install required Python packages:

```bash
pip install -r requirements.txt
```

## Installing Ollama Models

Before running the script, you'll need at least one Ollama model installed:

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

Ensure the Ollama service is running before using this script:

```bash
ollama serve
```

This starts the Ollama API server on http://localhost:11434.

## Basic Usage

The simplest way to use the script is with the interactive menu:

```bash
python ollama_prompt.py
```

This will guide you through selecting:
1. A model (or all models)
2. A user prompt file (or use the default)
3. An optional system prompt file
4. Output display preferences

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
- Default model(s) to use
- Default system and user prompts
- Output preferences (streaming, saving)
- Performance settings (timeout, max workers)
- Custom Ollama API URL

## Next Steps

- Check [QuickStart.md](QuickStart.md) for common commands
- Explore [README.md](README.md) for advanced usage and examples
- See [test_examples.md](test_examples.md) for practical examples