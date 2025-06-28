# OpenMCP Docker Setup

This guide shows how to run OpenMCP and the Calculator API using Docker Compose to avoid port conflicts and simplify deployment.

## Quick Start

1. **Start all services with Docker**:
   ```bash
   ./docker-start.sh
   ```

2. **Chat with AI**:
   ```bash
   uv run python examples/docker_chat_client.py
   ```

3. **Stop services**:
   ```bash
   docker-compose down
   ```

## What Gets Deployed

The Docker setup includes:

- **OpenMCP Service**: Running on port 8000 (mapped from internal 5000)
- **Calculator API**: Running on port 8001 (mapped from internal 5001)
- **Shared Network**: Both services can communicate internally
- **Volume Mounts**: Specs and logs are accessible from host

## Port Mapping

| Service | Internal Port | External Port | URL |
|---------|---------------|---------------|-----|
| OpenMCP | 5000 | 8000 | http://localhost:8000 |
| Calculator API | 5001 | 8001 | http://localhost:8001 |

## Manual Docker Commands

### Build and start services:
```bash
docker-compose up -d --build
```

### View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f openmcp
docker-compose logs -f calculator
```

### Stop services:
```bash
docker-compose down
```

### Rebuild after code changes:
```bash
docker-compose up -d --build
```

## Testing the Docker Setup

### Health Checks
```bash
# OpenMCP
curl http://localhost:8000/health

# Calculator API
curl http://localhost:8001/health
```

### Register API and Test Tools
```bash
# Register Calculator API (Docker version)
curl -X POST http://localhost:8000/api/discovery/register \
  -H "Content-Type: application/json" \
  -d '{"spec_path": "./specs/calculator-api-docker.yaml"}'

# List discovered tools
curl http://localhost:8000/api/tools/list

# Execute a calculation (note the Docker tool naming)
curl -X POST http://localhost:8000/api/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "post_http:__calculator:5001_calculate_add",
    "parameters": {"a": 42, "b": 17}
  }'
```

## Ollama Integration with Docker

The setup assumes Ollama is running locally on your host machine. The Docker containers will connect to Ollama at `host.docker.internal:11434`.

### Install Ollama locally:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.2
```

### Optional: Run Ollama in Docker too
Uncomment the `ollama` service in `docker-compose.yml` to run everything containerized:

```yaml
ollama:
  image: ollama/ollama:latest
  container_name: ollama
  ports:
    - "11434:11434"
  volumes:
    - ollama-data:/root/.ollama
  networks:
    - openmcp-network
```

Then pull models inside the container:
```bash
docker-compose exec ollama ollama pull llama3.2
```

## File Structure

```
├── Dockerfile.openmcp      # OpenMCP service container
├── Dockerfile.calculator   # Calculator API container
├── docker-compose.yml      # Service orchestration
├── .env.docker            # Docker environment variables
├── docker-start.sh        # One-command startup script
└── examples/
    └── docker_chat_client.py  # Docker-aware chat client
```

## Development with Docker

### Code Changes
After making code changes, rebuild and restart:
```bash
docker-compose up -d --build
```

### Debugging
Access container shells:
```bash
# OpenMCP container
docker-compose exec openmcp bash

# Calculator container
docker-compose exec calculator bash
```

### Volume Mounts
- `./specs` → `/app/specs` (read-only)
- `./logs` → `/app/logs` (read-write)

## Advantages of Docker Setup

1. **No Port Conflicts**: Uses non-conflicting ports (8000, 8001)
2. **Isolated Environment**: Each service runs in its own container
3. **Easy Deployment**: One command starts everything
4. **Reproducible**: Same environment across different machines
5. **Scalable**: Easy to add more services or scale existing ones

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Check if ports are in use
lsof -i :8000
lsof -i :8001
```

### Can't connect to Ollama
- Ensure Ollama is running locally: `ollama list`
- Check if you're using the right host: `host.docker.internal` (macOS/Windows) or `172.17.0.1` (Linux)

### Calculator API registration fails
- Wait a few seconds after starting services
- Check OpenMCP logs: `docker-compose logs openmcp`
- Manually register: Use the curl commands above