#!/usr/bin/env python3
"""
Test script to verify configuration functionality.
"""

import os
import sys
import yaml
import argparse
from rich.console import Console

# Import the config_manager module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config_manager

console = Console()

def print_config():
    """Print the current configuration contents"""
    config_file = config_manager.CONFIG_FILE
    
    console.print(f"\n[bold]Current Configuration File:[/bold] {config_file}")
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                
            console.print("\n[bold green]Configuration Contents:[/bold green]")
            for key, value in config.items():
                value_str = "null" if value is None else str(value)
                console.print(f"  {key}: {value_str}")
        except Exception as e:
            console.print(f"[bold red]Error reading config file:[/bold red] {str(e)}")
    else:
        console.print("[bold yellow]Configuration file does not exist yet.[/bold yellow]")

def test_write_config():
    """Test writing to the configuration file"""
    test_config = {
        "base_url": "http://localhost:11434",
        "default_model": "llama3:8b",
        "default_system_prompt": "system_prompts/expert_financial_advisor.md",
        "default_user_prompt": "user_prompts/heloc_advice.md",
        "default_stream": True,
        "default_save": True,
        "default_max_workers": 4,
        "default_timeout": 900,
        "use_menu": False,
        "default_models": ["llama3:8b", "mixtral:latest"],
        "config_version": "1.0" 
    }
    
    console.print("\n[bold]Testing configuration write...[/bold]")
    
    if config_manager.save_config(test_config):
        console.print("[bold green]Configuration written successfully.[/bold green]")
    else:
        console.print("[bold red]Failed to write configuration.[/bold red]")
        
    # Verify the file was written
    print_config()

def test_read_config():
    """Test reading from the configuration file"""
    console.print("\n[bold]Testing configuration read...[/bold]")
    
    config = config_manager.load_config()
    
    console.print("[bold green]Configuration loaded:[/bold green]")
    for key, value in config.items():
        value_str = "null" if value is None else str(value)
        console.print(f"  {key}: {value_str}")
    
    return config

def test_update_config():
    """Test updating specific configuration values"""
    console.print("\n[bold]Testing configuration update...[/bold]")
    
    # Update a specific value
    if config_manager.update_config("default_model", "mixtral:latest"):
        console.print("[bold green]Configuration updated successfully.[/bold green]")
    else:
        console.print("[bold red]Failed to update configuration.[/bold red]")
    
    # Verify the update
    print_config()

def test_args_to_config():
    """Test saving command line args to configuration"""
    console.print("\n[bold]Testing saving args to configuration...[/bold]")
    
    # Create a mock args object
    class MockArgs:
        def __init__(self):
            self.model = "phi3:mini"
            self.models = None
            self.system_file = "system_prompts/creative_writer.md"
            self.prompt_file = "user_prompts/story_starter.md"
            self.stream = True
            self.save = True
            self.max_workers = 2
            self.timeout = 600
    
    args = MockArgs()
    
    if config_manager.save_current_run(args):
        console.print("[bold green]Args saved to configuration successfully.[/bold green]")
    else:
        console.print("[bold red]Failed to save args to configuration.[/bold red]")
    
    # Verify the update
    print_config()

def test_reset_config():
    """Test resetting configuration to defaults"""
    console.print("\n[bold]Testing configuration reset...[/bold]")
    
    if config_manager.reset_config():
        console.print("[bold green]Configuration reset successfully.[/bold green]")
    else:
        console.print("[bold red]Failed to reset configuration.[/bold red]")
    
    # Verify the reset
    print_config()

def main():
    parser = argparse.ArgumentParser(description="Test Ollama configuration functionality")
    parser.add_argument("--test", choices=["write", "read", "update", "args", "reset", "all"], 
                      default="all", help="Test to run")
    
    args = parser.parse_args()
    
    # Show current config
    print_config()
    
    # Run selected test
    if args.test == "write" or args.test == "all":
        test_write_config()
        
    if args.test == "read" or args.test == "all":
        test_read_config()
        
    if args.test == "update" or args.test == "all":
        test_update_config()
        
    if args.test == "args" or args.test == "all":
        test_args_to_config()
        
    if args.test == "reset" or args.test == "all":
        test_reset_config()

if __name__ == "__main__":
    main()