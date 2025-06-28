# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenMCP is a **Flask-based implementation** that allows AI systems to discover and execute tools from OpenAPI specifications. This is a complete, working implementation that demonstrates the concept of using standard REST APIs as AI tools through OpenAPI extensions.

## Key Architecture

The project consists of:

1. **OpenMCP Core** (`openmcp/`) - Flask application with tool discovery and execution
2. **Example Calculator API** (`examples/calculator_api.py`) - Demonstrates AI-callable REST API
3. **Ollama Integration** (`openmcp/core/ollama_*`) - AI chat clients with tool support
4. **Docker Deployment** - Complete containerized setup

## Development Commands

### Docker Deployment (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Chat with AI
uv run python examples/docker_chat_client.py
```

### Local Development
```bash
# Install dependencies
uv sync

# Run OpenMCP server
uv run python -m openmcp.app

# Run example calculator API
uv run python examples/calculator_api.py

# Run simple chat client
uv run python examples/simple_chat.py
```

## Project Structure

- `openmcp/app.py` - Main Flask application entry point
- `openmcp/api/` - REST API endpoints (discovery, tools)
- `openmcp/core/openapi_parser.py` - Parses OpenAPI specs and extracts AI tools
- `openmcp/core/ollama_*.py` - Ollama integration for AI chat
- `examples/` - Working examples including calculator API and chat clients
- `specs/` - OpenAPI specifications with AI tool extensions
- `docs/` - Comprehensive documentation

## Core Concepts

### OpenAPI AI Tool Extensions
Tools are marked in OpenAPI specs using custom extensions:
```yaml
x-ai-tool: true
x-ai-description: "Description for AI context"
x-ai-category: "category"
```

### Tool Discovery Flow
1. Register OpenAPI spec via `/api/discovery/register`
2. Parser extracts endpoints marked with `x-ai-tool: true`
3. Tools become available via `/api/tools/list`
4. Execute tools via `/api/tools/execute`

### AI Integration
- Ollama provides local AI models with tool calling
- Chat clients demonstrate natural language to tool execution
- Conversation management with persistent history

## Key Features Implemented

- ✅ OpenAPI specification parsing
- ✅ Tool discovery and registration
- ✅ HTTP-based tool execution
- ✅ Ollama AI integration
- ✅ Docker containerization
- ✅ Rich terminal chat interface
- ✅ Example calculator API with 4 math operations

## Environment Configuration

### Docker (Production)
- OpenMCP runs on port 8000 (mapped from internal 5000)
- Calculator API runs on port 8001 (mapped from internal 5001)
- Services communicate via Docker network names

### Local Development
- OpenMCP typically runs on port 5005 (to avoid macOS AirPlay conflicts)
- Calculator API runs on port 5001
- Ollama runs on port 11434

## Common Development Tasks

### Adding New APIs
1. Create REST API with standard OpenAPI spec
2. Add `x-ai-tool: true` to endpoints you want AI-accessible
3. Register spec: `POST /api/discovery/register`
4. Tools automatically become available

### Debugging
- Check service health: `curl http://localhost:8000/health`
- View discovered tools: `curl http://localhost:8000/api/tools/list`
- Check container logs: `docker-compose logs -f`

### Testing
- Use `examples/docker_chat_client.py` for interactive testing
- Direct API testing via curl commands in documentation
- Calculator API provides working examples

## Dependencies

Key libraries:
- **Flask** - Web framework
- **Pydantic** - Data validation
- **PyYAML** - YAML parsing for OpenAPI specs
- **Requests** - HTTP client for tool execution
- **Ollama** - AI model integration
- **Rich** - Terminal UI for chat clients

## Next Development Steps

1. **Authentication** - Add OAuth/API key support for external APIs
2. **Rate Limiting** - Implement tool execution limits
3. **Caching** - Cache API responses for performance
4. **Testing** - Add comprehensive unit and integration tests
5. **More AI Integrations** - Support for other AI providers

## Docker vs Local Development

- **Docker**: Use for production-like testing, eliminates port conflicts
- **Local**: Use for active development, easier debugging and code changes

Both setups are fully functional and well-documented.

## Documentation

- `README.md` - Main project overview
- `docs/README_DOCKER.md` - Docker setup and deployment
- `docs/README_FLASK.md` - Flask implementation details  
- `docs/README_OLLAMA.md` - AI integration guide

The project is production-ready for demonstration and can serve as a foundation for enterprise AI tool integration.