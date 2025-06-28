# OpenMCP Flask Implementation

A Flask-based implementation of OpenMCP (OpenAPI Model Context Protocol) that allows AI systems to discover and execute tools from OpenAPI specifications.

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd openMCP
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Copy the environment configuration:
```bash
cp .env.example .env
```

4. Run the application:
```bash
uv run python -m openmcp.app
```

The server will start at `http://localhost:5005`

## API Endpoints

### Health Check
- `GET /health` - Check if the service is running
- `GET /` - Get service information and available endpoints

### Discovery API
- `POST /api/discovery/register` - Register an OpenAPI specification
  ```json
  {
    "spec_path": "./specs/example-api.yaml"
  }
  ```
  or
  ```json
  {
    "spec_url": "https://api.example.com/openapi.json"
  }
  ```

- `GET /api/discovery/tools` - List all discovered AI tools
- `GET /api/discovery/specs` - List all loaded OpenAPI specifications
- `POST /api/discovery/scan` - Scan a directory for OpenAPI specs
  ```json
  {
    "directory": "./specs"
  }
  ```

### Tools API
- `GET /api/tools/list` - List all registered tools
- `POST /api/tools/execute` - Execute a tool
  ```json
  {
    "tool_name": "get_users_{userId}",
    "parameters": {
      "userId": "123"
    }
  }
  ```

## Project Structure

```
openmcp/
├── api/              # API endpoints
│   ├── discovery_api.py  # OpenAPI discovery endpoints
│   └── tools_api.py      # Tool execution endpoints
├── core/             # Core functionality
│   └── openapi_parser.py # OpenAPI parsing and tool extraction
├── utils/            # Utilities
│   └── logging.py        # Logging configuration
└── app.py            # Flask application entry point

specs/                # OpenAPI specifications
└── example-api.yaml  # Example OpenAPI spec with AI tools
```

## Example OpenAPI Specification

The project includes an example OpenAPI specification (`specs/example-api.yaml`) that demonstrates how to mark endpoints as AI tools using custom extensions:

```yaml
paths:
  /users/{userId}:
    get:
      summary: Get user by ID
      x-ai-tool: true
      x-ai-description: "Retrieve information about a specific user"
      x-ai-category: "user-management"
```

## Development

### Running in development mode

```bash
uv run python -m openmcp.app
```

### Adding new dependencies

```bash
uv add <package-name>
```

### Testing the API

1. Register the example specification:
```bash
curl -X POST http://localhost:5005/api/discovery/register \
  -H "Content-Type: application/json" \
  -d '{"spec_path": "./specs/example-api.yaml"}'
```

2. List discovered tools:
```bash
curl http://localhost:5005/api/discovery/tools
```

3. Execute a tool (example):
```bash
curl -X POST http://localhost:5005/api/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_users_{userId}",
    "parameters": {"userId": "123"}
  }'
```

## Example: Calculator API

The project includes a complete example of a calculator API that demonstrates the OpenMCP concept:

### Running the Example

```bash
# Start both services and run examples
./run_example.sh
```

This will:
1. Start the Calculator API on port 5001
2. Start OpenMCP on port 5005
3. Register the calculator's OpenAPI spec
4. Show discovered tools
5. Execute example calculations

### Interactive Testing

```bash
# Run the interactive test script
uv run python examples/test_calculator.py
```

### Calculator API Endpoints

The calculator API exposes four math operations as AI tools:
- **Add**: `POST /calculate/add` - Add two numbers
- **Subtract**: `POST /calculate/subtract` - Subtract b from a
- **Multiply**: `POST /calculate/multiply` - Multiply two numbers
- **Divide**: `POST /calculate/divide` - Divide a by b

Each endpoint is marked with `x-ai-tool: true` in the OpenAPI spec, making it discoverable by OpenMCP.

## Ollama Integration

OpenMCP includes integration with Ollama for AI-powered tool usage. See [README_OLLAMA.md](README_OLLAMA.md) for details.

### Quick Start with Ollama

1. Install Ollama and pull a model:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2
```

2. Run the example with chat:
```bash
./run_example.sh  # In one terminal
uv run python examples/simple_chat.py  # In another terminal
```

## Next Steps

1. Implement authentication for external API calls
2. Add support for OAuth and API key authentication
3. Create integration with AI systems (Ollama, Claude, etc.) ✓
4. Add caching for API responses
5. Implement rate limiting
6. Add comprehensive error handling
7. Create unit and integration tests