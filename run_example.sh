#!/bin/bash

echo "Starting OpenMCP Calculator Example"
echo "=================================="

# Function to cleanup on exit
cleanup() {
    echo -e "\n\nShutting down services..."
    kill $CALC_PID 2>/dev/null
    kill $OPENMCP_PID 2>/dev/null
    exit
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Start Calculator API
echo "1. Starting Calculator API on port 5001..."
uv run python examples/calculator_api.py &
CALC_PID=$!
sleep 2

# Start OpenMCP
echo -e "\n2. Starting OpenMCP on port 5005..."
uv run python -m openmcp.app &
OPENMCP_PID=$!
sleep 2

# Wait for services to be ready
echo -e "\n3. Waiting for services to start..."
sleep 3

# Register the calculator API with OpenMCP
echo -e "\n4. Registering Calculator API with OpenMCP..."
curl -X POST http://localhost:5005/api/discovery/register \
  -H "Content-Type: application/json" \
  -d '{"spec_path": "./specs/calculator-api.yaml"}' \
  | python -m json.tool

# Show discovered tools
echo -e "\n\n5. Listing discovered AI tools..."
curl http://localhost:5005/api/discovery/tools | python -m json.tool

# Example: Execute the add tool
echo -e "\n\n6. Example: Adding 42 + 17..."
curl -X POST http://localhost:5005/api/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "post_calculate_add",
    "parameters": {"a": 42, "b": 17}
  }' \
  | python -m json.tool

# Example: Execute the multiply tool
echo -e "\n\n7. Example: Multiplying 6 × 7..."
curl -X POST http://localhost:5005/api/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "post_calculate_multiply",
    "parameters": {"a": 6, "b": 7}
  }' \
  | python -m json.tool

echo -e "\n\n=================================="
echo "Services are running!"
echo "OpenMCP: http://localhost:5005"
echo "Calculator API: http://localhost:5001"
echo -e "\nPress Ctrl+C to stop all services"
echo "=================================="

# Keep script running
wait