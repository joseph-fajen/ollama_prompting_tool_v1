# LLM Prompt Script Test Examples

This document provides example test cases that demonstrate the flexibility of the prompt script with different providers, system prompts, and user prompts. Each example shows how to run the script with specific combinations to illustrate various use cases.

## Example 1: Blockchain Education with Educator System Prompt

This example uses the blockchain educator system prompt with the smart contract explanation user prompt to generate specialized technical guidance.

```bash
python ollama_prompt.py --provider ollama --model llama3:8b --system-file system_prompts/blockchain_educator.md --prompt-file user_prompts/smart_contract_explanation.md
```

**What it demonstrates:** How a specialized system prompt (blockchain educator) enhances domain-specific responses when combined with a detailed query about smart contracts.

## Example 2: Same System Prompt, Different Main Prompts

This example keeps the blockchain educator system prompt but switches between different blockchain topics.

```bash
# First run with smart contract explanation
python ollama_prompt.py --model mixtral:latest --system-file system_prompts/blockchain_educator.md --prompt-file user_prompts/smart_contract_explanation.md

# Then run with consensus mechanism comparison
python ollama_prompt.py --model mixtral:latest --system-file system_prompts/blockchain_educator.md --prompt-file user_prompts/consensus_mechanism_comparison.md
```

**What it demonstrates:** How the same expert system prompt can be applied to different blockchain topics while maintaining consistent expertise and tone.

## Example 3: Different System Prompts, Same User Prompt

This example shows how different system prompts significantly change the output for the same user prompt.

```bash
# Run with blockchain educator system prompt
python ollama_prompt.py --model phi3:mini --system-file system_prompts/blockchain_educator.md --prompt-file user_prompts/smart_contract_explanation.md

# Then run with blockchain tech writer system prompt
python ollama_prompt.py --model phi3:mini --system-file system_prompts/blockchain_tech_writer.md --prompt-file user_prompts/smart_contract_explanation.md
```

**What it demonstrates:** How changing the system prompt transforms the depth, style, and expertise level in the response while keeping the same query.

## Example 4: Testing Multiple Models with Same Prompts

This example runs the same prompt combination across different models to compare responses.

```bash
python ollama_prompt.py --models llama3:8b mixtral:latest phi3:mini --system-file system_prompts/blockchain_educator.md --prompt-file user_prompts/wallet_setup_guide.md
```

**What it demonstrates:** How different models respond to the same prompt combination, allowing comparison of quality, expertise, and style between models.

## Example 5: Custom System Prompt for UX Writing

This example uses the blockchain UX writer system prompt:

```bash
python ollama_prompt.py --model codellama:7b-instruct --system-file system_prompts/blockchain_ux_writer.md --prompt-file user_prompts/wallet_setup_guide.md
```

**What it demonstrates:** How the system can be extended with specialized prompts for different writing styles and use cases.

## Example 6: Blockchain Education in Streaming Mode

This example demonstrates using the streaming mode to see responses as they're generated.

```bash
python ollama_prompt.py --model llama3:8b --system-file system_prompts/blockchain_educator.md --prompt-file user_prompts/consensus_mechanism_comparison.md --stream
```

**What it demonstrates:** How to use the streaming option to see responses as they are generated token by token.

## Example 7: Comparing All Available Models

This example runs a prompt across all available models to evaluate performance.

```bash
python ollama_prompt.py --all-models --system-file system_prompts/blockchain_educator.md --prompt-file user_prompts/smart_contract_explanation.md
```

**What it demonstrates:** How to easily benchmark all available models with the same prompt combination.

## Example 8: Using Multiple API Providers

This example demonstrates how to use different API providers with secure API key management.

```bash
# First, set up your API keys securely (one-time setup)
python ollama_prompt.py --setup-keys

# One-shot mode with OpenAI API
python ollama_prompt.py --provider openai --model gpt-3.5-turbo --system-file system_prompts/blockchain_educator.md --prompt-file user_prompts/smart_contract_explanation.md

# One-shot mode with Hugging Face model
python ollama_prompt.py --provider huggingface --model mistralai/Mistral-7B-Instruct-v0.1 --system-file system_prompts/blockchain_educator.md --prompt-file user_prompts/smart_contract_explanation.md
```

**Alternative API key methods:**

```bash
# Using environment variables (more secure than command line)
export OLLAMA_TOOL_OPENAI_API_KEY=your_key_here
python ollama_prompt.py --provider openai --model gpt-3.5-turbo

# Direct command line (least secure, not recommended for shared systems)
python ollama_prompt.py --provider openai --api-key your_key_here --model gpt-3.5-turbo
```

**What it demonstrates:** How to securely use multiple API providers with one-shot prompts while keeping your API keys safe.

## Example 9: Using Multiple API Providers with Chat Mode

This example demonstrates how to use different API providers in chat mode.

```bash
# First, set up your API keys securely (one-time setup)
python ollama_chat.py --setup-keys

# Chat using OpenAI API
python ollama_chat.py --provider openai --model gpt-3.5-turbo

# Chat using Hugging Face model
python ollama_chat.py --provider huggingface --model mistralai/Mistral-7B-Instruct-v0.1
```

**What it demonstrates:** How to use interactive chat mode with different API providers.

## Creating Your Own Test Cases

To create your own test cases:

1. Create new system prompts in the `system_prompts/` directory (plain text or markdown files)
2. Create new user prompts in the `user_prompts/` directory (plain text or markdown files)
3. Combine them using the command pattern shown in the examples above

The power of this approach is in the flexibility to mix and match different system prompts with different user prompts to achieve various response styles, expertise levels, and content types.