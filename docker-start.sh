#!/bin/bash

echo "🐳 Starting OpenMCP with Docker"
echo "==============================="

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down

# Build and start services
echo "Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check service health
echo "Checking service health..."

# Check OpenMCP
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ OpenMCP is running on port 8000"
else
    echo "❌ OpenMCP failed to start"
    docker-compose logs openmcp
    exit 1
fi

# Check Calculator API
if curl -f http://localhost:8001/health >/dev/null 2>&1; then
    echo "✅ Calculator API is running on port 8001"
else
    echo "❌ Calculator API failed to start"
    docker-compose logs calculator
    exit 1
fi

# Register Calculator API with OpenMCP (Docker version)
echo "Registering Calculator API..."
sleep 2
curl -X POST http://localhost:8000/api/discovery/register \
  -H "Content-Type: application/json" \
  -d '{"spec_path": "./specs/calculator-api-docker.yaml"}' \
  >/dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Calculator API registered with OpenMCP"
else
    echo "⚠️  Calculator API registration may have failed (might already be registered)"
fi

# Show discovered tools
echo -e "\n📦 Discovered tools:"
curl -s http://localhost:8000/api/tools/list | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for tool in data['tools']:
        print(f'  - {tool[\"name\"]}: {tool.get(\"description\", \"No description\")[:50]}...')
except:
    print('  Error reading tools')
"

echo -e "\n==============================="
echo "🚀 Services are running!"
echo "  OpenMCP:        http://localhost:8000"
echo "  Calculator API: http://localhost:8001"
echo ""
echo "To chat with AI:"
echo "  uv run python examples/docker_chat_client.py"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo "==============================="