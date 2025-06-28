#!/usr/bin/env python
"""
Interactive test script for the Calculator API via OpenMCP
"""

import requests
import json
import time

OPENMCP_BASE = "http://localhost:5005"
CALC_API_BASE = "http://localhost:5001"

def check_services():
    """Check if both services are running"""
    try:
        # Check OpenMCP
        r = requests.get(f"{OPENMCP_BASE}/health")
        if r.status_code != 200:
            print("❌ OpenMCP is not running on port 5005")
            return False
        print("✅ OpenMCP is running")
        
        # Check Calculator API
        r = requests.get(f"{CALC_API_BASE}/health")
        if r.status_code != 200:
            print("❌ Calculator API is not running on port 5001")
            return False
        print("✅ Calculator API is running")
        
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Services are not running. Please run ./run_example.sh first")
        return False

def register_calculator_api():
    """Register the calculator API with OpenMCP"""
    print("\nRegistering Calculator API with OpenMCP...")
    
    response = requests.post(
        f"{OPENMCP_BASE}/api/discovery/register",
        json={"spec_path": "./specs/calculator-api.yaml"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Registered successfully!")
        print(f"   - Spec: {data['spec_title']}")
        print(f"   - Tools discovered: {data['tools_discovered']}")
        print(f"   - Tools registered: {data['tools_registered']}")
    else:
        print(f"❌ Registration failed: {response.text}")

def list_tools():
    """List all available tools"""
    print("\nAvailable AI Tools:")
    print("-" * 50)
    
    response = requests.get(f"{OPENMCP_BASE}/api/tools/list")
    data = response.json()
    
    for tool in data['tools']:
        print(f"\n📌 {tool['name']}")
        print(f"   Description: {tool['description']}")
        print(f"   Parameters: {json.dumps(tool['parameters']['properties'], indent=6)}")

def execute_tool(tool_name, parameters):
    """Execute a tool through OpenMCP"""
    response = requests.post(
        f"{OPENMCP_BASE}/api/tools/execute",
        json={
            "tool_name": tool_name,
            "parameters": parameters
        }
    )
    
    return response.json()

def interactive_calculator():
    """Interactive calculator using OpenMCP tools"""
    print("\n🧮 Interactive Calculator (using OpenMCP)")
    print("=" * 50)
    print("Commands: add, subtract, multiply, divide, quit")
    print("=" * 50)
    
    while True:
        command = input("\nEnter operation (or 'quit'): ").lower().strip()
        
        if command == 'quit':
            break
        
        if command not in ['add', 'subtract', 'multiply', 'divide']:
            print("Invalid operation. Try: add, subtract, multiply, divide")
            continue
        
        try:
            a = float(input("Enter first number: "))
            b = float(input("Enter second number: "))
            
            # Execute through OpenMCP
            tool_name = f"post_calculate_{command}"
            result = execute_tool(tool_name, {"a": a, "b": b})
            
            if result.get('success'):
                data = result['data']
                print(f"\n✅ Result: {data['expression']}")
            else:
                print(f"\n❌ Error: {result}")
                
        except ValueError:
            print("Please enter valid numbers")
        except Exception as e:
            print(f"Error: {e}")

def run_examples():
    """Run example calculations"""
    print("\n📊 Running Example Calculations")
    print("=" * 50)
    
    examples = [
        ("add", {"a": 100, "b": 23}, "Addition"),
        ("subtract", {"a": 100, "b": 23}, "Subtraction"),
        ("multiply", {"a": 12, "b": 8}, "Multiplication"),
        ("divide", {"a": 144, "b": 12}, "Division"),
        ("divide", {"a": 10, "b": 0}, "Division by zero (error expected)")
    ]
    
    for operation, params, description in examples:
        print(f"\n{description}: {params['a']} and {params['b']}")
        tool_name = f"post_calculate_{operation}"
        result = execute_tool(tool_name, params)
        
        if result.get('success'):
            print(f"✅ {result['data']['expression']}")
        else:
            print(f"❌ Error: {result.get('data', result)}")

def main():
    print("🚀 OpenMCP Calculator Test Script")
    print("=" * 50)
    
    # Check services
    if not check_services():
        print("\nPlease start the services first:")
        print("  ./run_example.sh")
        return
    
    # Register API
    register_calculator_api()
    time.sleep(1)
    
    # List tools
    list_tools()
    
    # Run examples
    run_examples()
    
    # Interactive mode
    interactive_calculator()
    
    print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()