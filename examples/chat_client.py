#!/usr/bin/env python
"""
Interactive chat client using Ollama with OpenMCP tool support
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.table import Table
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
import requests
import time
from openmcp.core.ollama_integration import OllamaIntegration, OllamaConfig

console = Console()

def check_services():
    """Check if required services are running"""
    services_ok = True
    
    # Check OpenMCP
    try:
        r = requests.get("http://localhost:5005/health", timeout=2)
        if r.status_code == 200:
            console.print("✅ OpenMCP is running", style="green")
        else:
            console.print("❌ OpenMCP is not responding properly", style="red")
            services_ok = False
    except:
        console.print("❌ OpenMCP is not running on port 5005", style="red")
        services_ok = False
    
    # Check Calculator API
    try:
        r = requests.get("http://localhost:5001/health", timeout=2)
        if r.status_code == 200:
            console.print("✅ Calculator API is running", style="green")
        else:
            console.print("❌ Calculator API is not responding properly", style="red")
            services_ok = False
    except:
        console.print("❌ Calculator API is not running on port 5001", style="red")
        services_ok = False
    
    # Check Ollama
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        if r.status_code == 200:
            console.print("✅ Ollama is running", style="green")
        else:
            console.print("❌ Ollama is not responding properly", style="red")
            services_ok = False
    except:
        console.print("❌ Ollama is not running on port 11434", style="red")
        console.print("\nTo install and run Ollama:", style="yellow")
        console.print("1. Visit https://ollama.ai to download")
        console.print("2. Run: ollama pull llama3.2")
        console.print("3. Ollama runs automatically after installation")
        services_ok = False
    
    return services_ok

def display_tools(tools):
    """Display available tools in a nice table"""
    table = Table(title="Available AI Tools", show_header=True, header_style="bold magenta")
    table.add_column("Tool Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Parameters", style="green")
    
    for tool in tools:
        params = tool.get('parameters', {}).get('properties', {})
        params_str = ", ".join([f"{k}:{v.get('type', '?')}" for k, v in params.items()])
        table.add_row(
            tool['name'],
            tool.get('description', 'No description')[:60] + "...",
            params_str
        )
    
    console.print(table)

def main():
    console.print(Panel.fit(
        "[bold blue]OpenMCP Chat Client[/bold blue]\n"
        "Chat with AI that can use tools from OpenAPI specifications",
        border_style="blue"
    ))
    
    # Check services
    console.print("\n[bold]Checking services...[/bold]")
    if not check_services():
        console.print("\n[red]Please ensure all services are running:[/red]")
        console.print("1. Run ./run_example.sh to start OpenMCP and Calculator API")
        console.print("2. Install and run Ollama from https://ollama.ai")
        return
    
    # Register calculator API with OpenMCP
    console.print("\n[bold]Registering Calculator API...[/bold]")
    try:
        r = requests.post(
            "http://localhost:5005/api/discovery/register",
            json={"spec_path": "./specs/calculator-api.yaml"}
        )
        if r.status_code == 200:
            console.print("✅ Calculator API registered", style="green")
        else:
            console.print("⚠️  Calculator API may already be registered", style="yellow")
    except Exception as e:
        console.print(f"❌ Failed to register API: {e}", style="red")
    
    # Initialize Ollama integration
    config = OllamaConfig(
        model="llama3.2",  # You can change this to any model you have
        temperature=0.7,
        system_prompt="""You are a helpful AI assistant with access to calculation tools through OpenMCP.
When you need to perform calculations, use the available tools by responding with:
{"tool": "tool_name", "parameters": {"param1": value1, "param2": value2}}

Be conversational and explain what you're doing when using tools."""
    )
    
    ollama_client = OllamaIntegration(config)
    
    # Discover tools
    console.print("\n[bold]Discovering available tools...[/bold]")
    tools = ollama_client.discover_tools()
    if tools:
        console.print(f"✅ Found {len(tools)} tools", style="green")
        display_tools(tools)
    else:
        console.print("❌ No tools found", style="red")
        return
    
    # Chat interface
    console.print("\n[bold green]Chat started![/bold green] Type 'exit' or 'quit' to end.\n")
    console.print("[dim]Example: 'What is 42 plus 17?' or 'Calculate 6 times 7'[/dim]\n")
    
    history = FileHistory('.chat_history')
    
    while True:
        try:
            # Get user input
            user_input = prompt(
                "You: ",
                history=history,
                auto_suggest=AutoSuggestFromHistory(),
                multiline=False
            )
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                console.print("\n[bold blue]Goodbye![/bold blue]")
                break
            
            if user_input.lower() == 'clear':
                ollama_client.reset_conversation()
                console.clear()
                console.print("[bold green]Conversation cleared![/bold green]\n")
                continue
            
            # Show thinking indicator
            with console.status("[bold green]Thinking...", spinner="dots"):
                response = ollama_client.chat(user_input)
            
            # Display response
            console.print("\n[bold cyan]Assistant:[/bold cyan]")
            console.print(Panel(Markdown(response), border_style="cyan"))
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n\n[bold blue]Goodbye![/bold blue]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]\n")

if __name__ == "__main__":
    main()