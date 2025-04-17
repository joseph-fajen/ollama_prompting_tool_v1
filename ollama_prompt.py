import requests
import json
import time
import argparse
import os
import subprocess
import concurrent.futures
import glob
import sys
from datetime import datetime
from rich.console import Console
from rich.markdown import Markdown
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn

# Import configuration manager
import config_manager

class OllamaClient:
    def __init__(self, base_url=None):
        # Use configured base_url or fall back to default
        self.base_url = base_url or config_manager.get_config_value("base_url", "http://localhost:11434")
        self.console = Console()
        self.session = requests.Session()
        self._system_prompt = None
        
    def get_installed_models(self):
        """Get a list of all installed Ollama models, excluding embedding models"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            
            # Skip the header line
            if len(lines) > 1:
                models = []
                for line in lines[1:]:  # Skip header row
                    parts = line.split()
                    if len(parts) >= 1:
                        model_name = parts[0]
                        # Skip embedding models which cannot generate text
                        if "embed" not in model_name.lower():
                            models.append(model_name)  # Get just the model name
                return models
            return []
        except Exception as e:
            self.console.print(f"[bold red]Error getting models:[/bold red] {str(e)}")
            return []
    
    def generate_response(self, model, prompt, stream=False, save=True, timeout=300):
        """Generate a response from an Ollama model"""
        start_time = time.time()
        
        # Create API request
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        
        try:
            if stream:
                # Stream the response
                self.console.print(f"\n[bold green]Model:[/bold green] {model}")
                self.console.print("[bold green]Response:[/bold green]\n")
                
                response_text = ""
                with self.session.post(url, json=payload, stream=True, timeout=timeout) as r:
                    r.raise_for_status()
                    for line in r.iter_lines():
                        if line:
                            response_json = json.loads(line)
                            chunk = response_json.get("response", "")
                            response_text += chunk
                            self.console.print(chunk, end="")
                
                self.console.print("\n")
            else:
                # Get the full response at once
                self.console.print(f"\n[bold green]Model:[/bold green] {model}")
                self.console.print("[bold green]Response:[/bold green]\n")
                
                response = self.session.post(url, json=payload, timeout=timeout)
                response.raise_for_status()
                
                response_json = json.loads(response.text)
                response_text = response_json.get("response", "")
                
                # Print as formatted markdown
                self.console.print(Markdown(response_text))
            
            # Calculate and display timing
            elapsed_time = time.time() - start_time
            self.console.print(f"\n[bold blue]Response time:[/bold blue] {elapsed_time:.2f} seconds")
            
            # Save response if requested
            if save:
                filepath = self._save_response(model, prompt, response_text, elapsed_time)
                return response_text, filepath
            
            return response_text, None
            
        except requests.exceptions.RequestException as e:
            self.console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return None, None
    
    def _save_response(self, model, prompt, response, elapsed_time):
        """Save the response to a file in a timestamped batch folder"""
        # Create responses directory if it doesn't exist
        os.makedirs("ollama_responses", exist_ok=True)
        
        # Create a timestamped batch folder if it doesn't exist yet
        # We store this as a class attribute so all responses in one run use the same folder
        if not hasattr(self, '_batch_folder'):
            batch_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._batch_folder = f"ollama_responses/batch_{batch_timestamp}"
            os.makedirs(self._batch_folder, exist_ok=True)
        
        # Extract system prompt and user prompt if combined
        system_prompt = None
        main_prompt = prompt
        
        # Check if this is a combined prompt (system + user)
        if hasattr(self, '_system_prompt') and self._system_prompt:
            system_prompt = self._system_prompt
            # If the prompt starts with the system prompt, extract just the user prompt
            if prompt.startswith(system_prompt):
                main_prompt = prompt[len(system_prompt):].lstrip('\n')
        
        # Get prompt filenames if available (or 'direct_input' if not from file)
        system_filename = getattr(self, '_system_filename', 'no_system')
        user_filename = getattr(self, '_user_filename', 'direct_input') 
        
        # Create a filename based on the model and prompt filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self._batch_folder}/{model.replace(':', '_')}_sys-{system_filename}_usr-{user_filename}_{timestamp}.md"
        
        # Use context manager for file I/O
        try:
            with open(filename, "w") as f:
                f.write(f"# Ollama Response - {model}\n\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Model:** {model}\n")
                f.write(f"**System Prompt:** {system_filename}\n")
                f.write(f"**User Prompt:** {user_filename}\n")
                f.write(f"**Response Time:** {elapsed_time:.2f} seconds\n\n")
                
                # Add system prompt section if available
                if system_prompt:
                    f.write("## System Prompt\n\n")
                    f.write(f"```\n{system_prompt}\n```\n\n")
                
                # Add user prompt section
                f.write("## User Prompt\n\n")
                f.write(f"```\n{main_prompt}\n```\n\n")
                
                # Add response section
                f.write("## Response\n\n")
                f.write(response)
            
            print(f"\nResponse saved to {filename}")
            return filename
        except Exception as e:
            self.console.print(f"[bold red]Error saving response:[/bold red] {str(e)}")
            return None

    def _process_model(self, model, prompt, stream=False, save=True, timeout=600):
        """Process a single model (helper method for parallel execution)"""
        response, filepath = self.generate_response(model, prompt, stream=stream, save=save, timeout=timeout)
        if response:
            return {
                "model": model,
                "response": response,
                "filepath": filepath
            }
        return None
        
    def run_prompt_on_all_models(self, prompt, models=None, save=True, stream=False, max_workers=None, timeout=600):
        """Run a prompt on all installed models or a specific list of models in parallel"""
        if not models:
            models = self.get_installed_models()
            
        if not models:
            self.console.print("[bold red]No models found![/bold red]")
            return
            
        self.console.print(f"[bold]Running prompt on {len(models)} models:[/bold] {', '.join(models)}\n")
        
        results = []
        total_start_time = time.time()
        
        # If stream is True, we can't use parallel execution (would mix outputs)
        if stream:
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task("[green]Running models...", total=len(models))
                
                for model in models:
                    progress.update(task, description=f"[green]Running {model}...")
                    result = self._process_model(model, prompt, stream=stream, save=save)
                    if result:
                        results.append(result)
                    progress.update(task, advance=1)
        else:
            # Use parallel execution for non-streaming mode
            futures = []
            
            # Default to number of CPU cores if max_workers not specified
            if max_workers is None:
                # Use CPU count or 2, whichever is higher
                max_workers = max(2, os.cpu_count())
            
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task("[green]Running models in parallel...", total=len(models))
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Submit all jobs
                    for model in models:
                        future = executor.submit(self._process_model, model, prompt, stream, save, timeout)
                        futures.append((future, model))
                    
                    # Process as they complete
                    for future, model in futures:
                        progress.update(task, description=f"[green]Running {model}...")
                        result = future.result()
                        if result:
                            results.append(result)
                        progress.update(task, advance=1)
        
        total_time = time.time() - total_start_time
        
        # Print summary
        self.console.print(f"\n[bold]Finished running {len(models)} models in {total_time:.2f} seconds[/bold]")
        self.console.print("\n[bold]Summary of results:[/bold]")
        
        for result in results:
            self.console.print(f"[green]{result['model']}[/green]: Response saved to {result['filepath']}")
        
        return results


def get_available_files(directory, extensions=None):
    """Get available files in a directory with specific extensions"""
    if not os.path.exists(directory):
        return []
        
    if extensions is None:
        extensions = [".txt", ".md"]
        
    files = []
    for ext in extensions:
        files.extend(glob.glob(f"{directory}/*{ext}"))
    
    return sorted(files)

def get_prompt_content(file_path):
    """Read content from a user prompt file"""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return None

def display_interactive_cli_menu(client):
    """Display an interactive CLI menu for users to select options"""
    console = Console()
    console.print("\n[bold blue]===== Ollama Prompt CLI =====\n[/bold blue]")
    console.print("[yellow]Welcome to the Ollama Prompt CLI![/yellow]")
    console.print("This tool helps you run prompts on Ollama models.")
    
    # Show configuration status
    config = config_manager.load_config()
    if config.get("default_model") or config.get("default_models"):
        console.print("\n[bold magenta]CONFIG:[/bold magenta]")
        if config.get("default_model"):
            console.print(f"  • Default model: [green]{config['default_model']}[/green]")
        if config.get("default_models"):
            models_str = ", ".join(config["default_models"])
            console.print(f"  • Default models: [green]{models_str}[/green]")
        if config.get("default_system_prompt"):
            console.print(f"  • Default system: [green]{os.path.basename(config['default_system_prompt'])}[/green]")
        if config.get("default_user_prompt"):
            console.print(f"  • Default user: [green]{os.path.basename(config['default_user_prompt'])}[/green]")
        console.print("  • Use [bold]--show-config[/bold] to see all settings")
    
    console.print("\n[bold cyan]TIPS:[/bold cyan]")
    console.print("  • For advanced usage: [bold]python ollama_prompt.py --help[/bold]")
    console.print("  • Skip this menu: [bold]python ollama_prompt.py --no-menu[/bold]")
    console.print("  • Quick reference: [bold]cat QuickStart.md[/bold]")
    console.print("  • Save settings: [bold]python ollama_prompt.py --save-config[/bold]")
    console.print("\n[bold blue]==============================\n[/bold blue]")
    
    # Get available models
    available_models = client.get_installed_models()
    if not available_models:
        console.print("[bold red]No Ollama models found![/bold red]")
        console.print("Please install models with 'ollama pull <model>' and try again.")
        return None
    
    # Get available prompts
    system_files = get_available_files("system_prompts")
    user_prompt_files = get_available_files("user_prompts")
    
    # Display menu options
    console.print("\n[bold green]Please select from the following options:[/bold green]")
    
    # 1. Select model
    console.print("\n[bold]1. Select a model:[/bold]")
    for i, model in enumerate(available_models):
        console.print(f"  {i+1}. {model}")
    console.print(f"  {len(available_models)+1}. Run on all models")
    
    model_choice = input("\nEnter your model choice (number): ")
    try:
        model_idx = int(model_choice) - 1
        if model_idx == len(available_models):
            selected_models = available_models
            console.print(f"[green]Running on all models[/green]")
        elif 0 <= model_idx < len(available_models):
            selected_models = [available_models[model_idx]]
            console.print(f"[green]Selected model: {available_models[model_idx]}[/green]")
        else:
            console.print("[bold red]Invalid choice. Using default (all models).[/bold red]")
            selected_models = available_models
    except ValueError:
        console.print("[bold red]Invalid input. Using default (all models).[/bold red]")
        selected_models = available_models
    
    # 2. Select user prompt
    console.print("\n[bold]2. Select a user prompt:[/bold]")
    all_user_prompts = []
    if user_prompt_files:
        for file in user_prompt_files:
            all_user_prompts.append((os.path.basename(file), file))
    else:
        console.print("[yellow]No user prompts found in user_prompts/ directory[/yellow]")
    
    for i, (prompt_name, _) in enumerate(all_user_prompts):
        console.print(f"  {i+1}. {prompt_name}")
    
    # Only ask for input if user prompts are available
    selected_prompt = None
    if all_user_prompts:
        prompt_choice = input("\nEnter your user prompt choice (number): ")
        try:
            prompt_idx = int(prompt_choice) - 1
            if 0 <= prompt_idx < len(all_user_prompts):
                selected_prompt = all_user_prompts[prompt_idx][1]
                prompt_name = all_user_prompts[prompt_idx][0]
                # Store user prompt filename (for output naming)
                client._user_filename = os.path.splitext(os.path.basename(selected_prompt))[0]
                console.print(f"[green]Selected user prompt: {prompt_name}[/green]")
            else:
                console.print("[bold red]Invalid choice. No prompt selected. You will be asked to enter a prompt directly.[/bold red]")
                selected_prompt = None
                client._user_filename = "direct_input"
        except ValueError:
            console.print("[bold red]Invalid input. No prompt selected. You will be asked to enter a prompt directly.[/bold red]")
            selected_prompt = None
            client._user_filename = "direct_input"
    else:
        console.print("[bold yellow]No user prompts available. You will be asked to enter a prompt directly.[/bold yellow]")
        selected_prompt = None
        client._user_filename = "direct_input"
    
    # 3. Select system prompt (optional)
    system_prompt_options = [("None", None)]
    if system_files:
        for file in system_files:
            system_prompt_options.append((os.path.basename(file), file))
    
    console.print("\n[bold]3. Select a system prompt (optional):[/bold]")
    for i, (system_name, _) in enumerate(system_prompt_options):
        console.print(f"  {i+1}. {system_name}")
    
    system_choice = input("\nEnter your system prompt choice (number): ")
    try:
        system_idx = int(system_choice) - 1
        if 0 <= system_idx < len(system_prompt_options):
            selected_system = system_prompt_options[system_idx][1]
            system_name = system_prompt_options[system_idx][0]
            # Store system filename (for output naming) if a file was selected
            if selected_system:
                client._system_filename = os.path.splitext(system_name)[0]
            else:
                client._system_filename = "no_system"
            console.print(f"[green]Selected system prompt: {system_name}[/green]")
        else:
            console.print("[bold red]Invalid choice. Using no system prompt.[/bold red]")
            selected_system = None
            client._system_filename = "no_system"
    except ValueError:
        console.print("[bold red]Invalid input. Using no system prompt.[/bold red]")
        selected_system = None
        client._system_filename = "no_system"
    
    # 4. Stream output?
    console.print("\n[bold]4. Output mode:[/bold]")
    console.print("  1. Stream - show tokens as they're generated in real-time")
    console.print("  2. Complete - show the full formatted response when finished (default)")
    
    stream_choice = input("\nEnter your choice (number or press Enter for default): ")
    stream = stream_choice == "1"
    console.print(f"[green]Output mode: {'Streaming' if stream else 'Complete'}[/green]")
    
    # 5. Save as defaults?
    console.print("\n[bold]5. Save these settings as defaults?[/bold]")
    console.print("  1. Yes - save these selections as default configuration")
    console.print("  2. No - don't save (default)")
    
    save_config_choice = input("\nEnter your choice (number or press Enter for default): ")
    save_config = save_config_choice == "1"
    if save_config:
        console.print("[green]These settings will be saved as defaults.[/green]")
    
    console.print("\n[bold blue]Starting Ollama generation...[/bold blue]\n")
    
    return selected_models, selected_prompt, selected_system, stream, save_config

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run prompts with Ollama models")
    
    # Model selection arguments
    model_group = parser.add_argument_group("Model Selection")
    model_group.add_argument("--model", type=str,
                        help="Ollama model to use (default: use config or all models)")
    model_group.add_argument("--all-models", action="store_true",
                        help="Run the prompt on all installed models")
    model_group.add_argument("--models", type=str, nargs="+",
                        help="List of specific models to run the prompt on")
    
    # Prompt arguments
    prompt_group = parser.add_argument_group("Prompt Selection")
    prompt_group.add_argument("--prompt-file", type=str,
                        help="Path to file containing the user prompt")
    prompt_group.add_argument("--system-file", type=str,
                        help="Path to file containing the system prompt")
    prompt_group.add_argument("--list-prompts", action="store_true",
                        help="List available prompt files and exit")
    
    # Output arguments
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("--stream", action="store_true",
                        help="Stream the response token by token")
    output_group.add_argument("--no-save", dest="save", action="store_false",
                        help="Don't save the response to a file")
    output_group.add_argument("--max-workers", type=int,
                        help="Maximum number of worker threads for parallel execution")
    output_group.add_argument("--timeout", type=int,
                        help="Timeout in seconds for each model request (default from config)")
    output_group.add_argument("--no-menu", action="store_true",
                        help="Skip the interactive CLI menu")
    
    # Configuration arguments
    config_group = parser.add_argument_group("Configuration")
    config_group.add_argument("--show-config", action="store_true",
                        help="Display current configuration and exit")
    config_group.add_argument("--save-config", action="store_true",
                        help="Save current run settings as default configuration")
    config_group.add_argument("--reset-config", action="store_true",
                        help="Reset configuration to defaults")
    config_group.add_argument("--base-url", type=str,
                        help="Set Ollama API base URL (default: http://localhost:11434)")
    
    # Set defaults from configuration
    config = config_manager.load_config()
    parser.set_defaults(
        save=config["default_save"],
        stream=config["default_stream"],
        all_models=False,
        timeout=config["default_timeout"]
    )
    
    args = parser.parse_args()
    
    # Create necessary directories if they don't exist
    os.makedirs("system_prompts", exist_ok=True)
    os.makedirs("user_prompts", exist_ok=True)
    
    # Handle configuration commands
    if args.show_config:
        config_manager.display_config()
        return
    
    if args.reset_config:
        if config_manager.reset_config():
            console = Console()
            console.print("[bold green]Configuration reset to defaults.[/bold green]")
        return
        
    # Update base URL in configuration if specified
    if args.base_url:
        config_manager.update_config("base_url", args.base_url)
    
    # List available prompt files if requested
    if args.list_prompts:
        system_files = get_available_files("system_prompts")
        user_prompt_files = get_available_files("user_prompts")
        
        console = Console()
        console.print("\n[bold]Available System Prompts:[/bold]")
        if system_files:
            for file in system_files:
                console.print(f"  - {file}")
        else:
            console.print("  No system prompt files found in system_prompts/ directory")
            
        console.print("\n[bold]Available User Prompts:[/bold]")
        if user_prompt_files:
            for file in user_prompt_files:
                console.print(f"  - {file}")
        else:
            console.print("  No user prompt files found in user_prompts/ directory")
        
        return
    
    # Create Ollama client
    client = OllamaClient()
    
    # Check if any relevant command line arguments were provided
    # Only check for arguments that would affect model selection or prompt content
    relevant_arg_names = ['model', 'all_models', 'prompt_file', 'system_file', 'models']
    has_relevant_args = any(vars(args)[arg_name] for arg_name in relevant_arg_names)
    
    # Check if we should use menu based on config and args
    config_use_menu = config_manager.get_config_value("use_menu", True)
    use_menu = config_use_menu and not has_relevant_args and not args.no_menu
    
    if use_menu:
        # Use interactive CLI menu
        menu_results = display_interactive_cli_menu(client)
        if menu_results is None:
            return
        
        try:
            models_to_run, prompt_file, system_file, stream, save_config_from_menu = menu_results
        except Exception as e:
            # If there was an issue with menu results
            console = Console()
            console.print(f"[bold red]Error with menu selection: {str(e)}. Exiting.[/bold red]")
            return
        save = True  # Always save in interactive mode
        max_workers = None  # Use default
        timeout = config_manager.get_config_value("default_timeout", 1200)
        
        # If user chose to save settings from menu, set the save_config flag
        if save_config_from_menu:
            args.save_config = True
    else:
        # Use command line arguments and fall back to config values
        # Get system prompt if specified
        system_prompt = None
        if args.system_file:
            system_file = args.system_file
        else:
            system_file = config_manager.get_config_value("default_system_prompt")
            
        # Get user prompt file
        if args.prompt_file:
            prompt_file = args.prompt_file
        else:
            prompt_file = config_manager.get_config_value("default_user_prompt")
        
        # Determine which models to use
        if args.all_models:
            # Run on all installed models (excluding embedding models)
            models_to_run = client.get_installed_models()
        elif args.models:
            # Run on specified list of models, but filter out embedding models
            models_to_run = [model for model in args.models if "embed" not in model.lower()]
            if len(models_to_run) < len(args.models):
                client.console.print("[bold yellow]Warning:[/bold yellow] Skipped embedding models which cannot generate text")
        elif args.model:
            # Run on a single model, but check if it's an embedding model
            if "embed" not in args.model.lower():
                models_to_run = [args.model]
            else:
                client.console.print("[bold red]Error:[/bold red] Cannot run text generation on embedding model")
                return
        else:
            # Check config for default model or models
            default_model = config_manager.get_config_value("default_model")
            default_models = config_manager.get_config_value("default_models", [])
            
            if default_model and "embed" not in default_model.lower():
                models_to_run = [default_model]
            elif default_models:
                models_to_run = [model for model in default_models if "embed" not in model.lower()]
            else:
                models_to_run = client.get_installed_models()
            
        # Get output options
        stream = args.stream
        save = args.save
        
        # For max_workers and timeout, prefer command line args, then config, then default
        if args.max_workers is not None:
            max_workers = args.max_workers
        else:
            max_workers = config_manager.get_config_value("default_max_workers")
            
        if args.timeout is not None:
            timeout = args.timeout
        else:
            timeout = config_manager.get_config_value("default_timeout", 1200)
    
    # Get system prompt content if specified
    system_prompt = None
    if system_file:
        system_prompt = get_prompt_content(system_file)
        if system_prompt is None:
            return
        # Store system filename (basename without extension) for output naming
        client._system_filename = os.path.splitext(os.path.basename(system_file))[0]
    else:
        client._system_filename = "no_system"
    
    # Get user prompt content from file or ask for direct input
    if prompt_file:
        main_prompt = get_prompt_content(prompt_file)
        if main_prompt is None:
            return
        # Store user prompt filename (basename without extension) for output naming
        client._user_filename = os.path.splitext(os.path.basename(prompt_file))[0]
    else:
        # Ask user for direct input
        console = Console()
        console.print("\n[bold]No prompt file selected. Please enter your prompt directly:[/bold]")
        console.print("[dim]Type your prompt below. When finished, press Enter twice (leave a blank line).[/dim]")
        
        lines = []
        while True:
            line = input()
            if not line and lines and not lines[-1]:  # Two consecutive empty lines
                break
            lines.append(line)
        
        main_prompt = "\n".join(lines).strip()
        if not main_prompt:
            console.print("[bold red]No prompt provided. Exiting.[/bold red]")
            return
            
        client._user_filename = "direct_input"
    
    # Store the system prompt in the client object for access in save_response
    client._system_prompt = system_prompt
    
    # Combine system prompt and user prompt if system prompt is provided
    if system_prompt:
        prompt = f"{system_prompt}\n\n{main_prompt}"
    else:
        prompt = main_prompt
        
    # Generate responses
    if not models_to_run:
        console = Console()
        console.print("[bold red]No models specified or found![/bold red]")
        console.print("Try installing models with: [bold]ollama pull llama3:8b[/bold] (or another model)")
        return
        
    # Display a summary of what will run
    console = Console()
    model_str = models_to_run[0] if len(models_to_run) == 1 else f"{len(models_to_run)} models"
    prompt_str = os.path.basename(prompt_file) if prompt_file else "Direct user input"
    system_str = os.path.basename(system_file) if system_file else "None"
    
    console.print("\n[bold]Running with:[/bold]")
    console.print(f"  • Model(s): [green]{model_str}[/green]")
    console.print(f"  • User prompt: [green]{prompt_str}[/green]")
    console.print(f"  • System prompt: [green]{system_str}[/green]")
    console.print(f"  • Output mode: [green]{'Streaming' if stream else 'Complete'}[/green]")
    console.print(f"  • Save responses: [green]{'Yes' if save else 'No'}[/green]\n")
    
    # Run the model(s)
    if len(models_to_run) == 1:
        # Just run a single model normally
        client.generate_response(models_to_run[0], prompt, stream=stream, save=save, timeout=timeout)
    else:
        # Run on multiple models
        client.run_prompt_on_all_models(
            prompt, 
            models=models_to_run, 
            save=save, 
            stream=stream,
            max_workers=max_workers,
            timeout=timeout
        )
        
    # Save configuration if requested
    if args.save_config:
        # Create a config dictionary from the actual values used in this run
        # This way, even menu-selected options are saved correctly
        run_config = {
            "default_model": models_to_run[0] if len(models_to_run) == 1 else None,
            "default_models": models_to_run if len(models_to_run) > 1 else [],
            "default_system_prompt": system_file,
            "default_user_prompt": prompt_file,
            "default_stream": stream,
            "default_save": save,
            "default_max_workers": max_workers,
            "default_timeout": timeout,
            "use_menu": not args.no_menu if hasattr(args, 'no_menu') else True
        }
        
        # Load existing config and update with current run values
        config = config_manager.load_config()
        for key, value in run_config.items():
            if value is not None:  # Only update non-None values
                config[key] = value
                
        if config_manager.save_config(config):
            console = Console()
            console.print("\n[bold green]Current settings saved as default configuration.[/bold green]")
            console.print("[green]Future runs will use these settings unless overridden.[/green]")
        
if __name__ == "__main__":
    main()