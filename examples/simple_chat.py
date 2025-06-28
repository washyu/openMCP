#!/usr/bin/env python
"""
Simple chat demo showing Ollama + OpenMCP integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openmcp.core.ollama_tools import OllamaToolClient
import requests

def setup_services():
    """Ensure calculator API is registered"""
    try:
        # Register calculator API
        r = requests.post(
            "http://localhost:5005/api/discovery/register",
            json={"spec_path": "./specs/calculator-api.yaml"}
        )
        print("✅ Calculator API registered with OpenMCP")
    except:
        print("⚠️  Make sure to run ./run_example.sh first!")
        return False
    return True

def main():
    print("🤖 OpenMCP + Ollama Chat Demo")
    print("=" * 40)
    
    # Check if services are running
    if not setup_services():
        return
    
    # Initialize Ollama client with tool support
    client = OllamaToolClient(model="llama3.2")
    
    # Discover and register tools
    tools = client.discover_and_register_tools()
    print(f"\n📦 Discovered {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description[:50]}...")
    
    print("\n💬 Chat started! (type 'exit' to quit)")
    print("Try asking: 'What is 42 plus 17?'\n")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye! 👋")
                break
            
            if not user_input:
                continue
            
            print("\nAI: ", end="", flush=True)
            response = client.chat_with_tools(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()