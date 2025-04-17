# Ollama Prompt Script Test Examples

This document provides example test cases that demonstrate the flexibility of the Ollama prompt script with different system prompts and user prompts. Each example shows how to run the script with specific combinations to illustrate various use cases.

## Example 1: Financial Advice with Expert System Prompt

This example uses the expert financial advisor system prompt with the HELOC advice user prompt to generate specialized financial guidance.

```bash
python ollama_prompt.py --model llama3:8b --system-file system_prompts/expert_financial_advisor.md --prompt-file user_prompts/heloc_advice.md
```

**What it demonstrates:** How a specialized system prompt (financial advisor) enhances domain-specific responses when combined with a detailed query about HELOCs.

## Example 2: Same System Prompt, Different Main Prompts

This example keeps the expert financial advisor system prompt but switches between different financial topics.

```bash
# First run with HELOC advice
python ollama_prompt.py --model mixtral:latest --system-file system_prompts/expert_financial_advisor.md --prompt-file user_prompts/heloc_advice.md

# Then run with mortgage advice
python ollama_prompt.py --model mixtral:latest --system-file system_prompts/expert_financial_advisor.md --prompt-file user_prompts/mortgage_advice.md
```

**What it demonstrates:** How the same expert system prompt can be applied to different financial topics while maintaining consistent expertise and tone.

## Example 3: Different System Prompts, Same User Prompt

This example shows how different system prompts significantly change the output for the same user prompt.

```bash
# Run with expert financial advisor system prompt
python ollama_prompt.py --model phi3:mini --system-file system_prompts/expert_financial_advisor.md --prompt-file user_prompts/mortgage_advice.md

# Then run with general helpful assistant system prompt
python ollama_prompt.py --model phi3:mini --system-file system_prompts/helpful_assistant.md --prompt-file user_prompts/mortgage_advice.md
```

**What it demonstrates:** How changing the system prompt transforms the depth, style, and expertise level in the response while keeping the same query.

## Example 4: Testing Multiple Models with Same Prompts

This example runs the same prompt combination across different models to compare responses.

```bash
python ollama_prompt.py --models llama3:8b mixtral:latest phi3:mini --system-file system_prompts/expert_financial_advisor.md --prompt-file user_prompts/heloc_advice.md
```

**What it demonstrates:** How different models respond to the same prompt combination, allowing comparison of quality, expertise, and style between models.

## Example 5: Custom System Prompt for Creative Writing

Create a new system prompt for creative writing (save as `system_prompts/creative_writer.md`):

```
You are an accomplished creative writer with expertise in storytelling, character development, and narrative structure. You excel at crafting engaging narratives with rich descriptions and authentic dialogue. Your writing style is versatile and can be adapted to different genres and tones as needed.

When responding to prompts, focus on creative elements, literary techniques, and engaging storytelling. Provide imaginative, vivid content that demonstrates the principles of good creative writing.
```

Then create a story prompt (save as `user_prompts/story_starter.md`):

```
Write the opening paragraph of a short story that takes place in Portland, Oregon during a particularly rainy autumn day. The main character has just received unexpected news that will change their life. Establish the setting, introduce the character, and hint at the nature of the news without explicitly revealing it.
```

Run with:

```bash
python ollama_prompt.py --model codellama:7b-instruct --system-file system_prompts/creative_writer.md --prompt-file user_prompts/story_starter.md
```

**What it demonstrates:** How the system can be extended with custom prompts for entirely different use cases like creative writing.

## Example 6: Financial Advice in Streaming Mode

This example demonstrates using the streaming mode to see responses as they're generated.

```bash
python ollama_prompt.py --model llama3:8b --system-file system_prompts/expert_financial_advisor.md --prompt-file user_prompts/heloc_advice.md --stream
```

**What it demonstrates:** How to use the streaming option to see responses as they are generated token by token.

## Example 7: Comparing All Available Models

This example runs a prompt across all available models to evaluate performance.

```bash
python ollama_prompt.py --all-models --system-file system_prompts/expert_financial_advisor.md --prompt-file user_prompts/mortgage_advice.md
```

**What it demonstrates:** How to easily benchmark all available models with the same prompt combination.

## Example 8: Using Multiple API Providers with Chat Mode

This example demonstrates how to use different API providers with secure API key management.

```bash
# First, set up your API keys securely (one-time setup)
python ollama_chat.py --setup-keys

# Chat using OpenAI API
python ollama_chat.py --provider openai --model gpt-3.5-turbo

# Chat using Hugging Face model
python ollama_chat.py --provider huggingface --model mistralai/Mistral-7B-Instruct-v0.1
```

**Alternative API key methods:**

```bash
# Using environment variables (more secure than command line)
export OLLAMA_TOOL_OPENAI_API_KEY=your_key_here
python ollama_chat.py --provider openai

# Direct command line (least secure, not recommended for shared systems)
python ollama_chat.py --provider openai --api-key your_key_here
```

**What it demonstrates:** How to securely use multiple API providers while keeping your API keys safe.

## Creating Your Own Test Cases

To create your own test cases:

1. Create new system prompts in the `system_prompts/` directory (plain text or markdown files)
2. Create new user prompts in the `user_prompts/` directory (plain text or markdown files)
3. Combine them using the command pattern shown in the examples above

The power of this approach is in the flexibility to mix and match different system prompts with different user prompts to achieve various response styles, expertise levels, and content types.