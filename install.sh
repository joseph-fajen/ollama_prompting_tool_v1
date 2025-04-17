#!/bin/bash

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install required packages
echo "Installing required packages..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p ollama_responses
mkdir -p user_prompts
mkdir -p system_prompts
mkdir -p config

echo "Installation complete!"
echo "To use the script:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the script: python ollama_prompt.py"
echo "3. For more options, see QuickStart.md or README.md"