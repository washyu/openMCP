# OpenMCP - OpenAPI Model Context Protocol

A Flask-based implementation that allows AI systems to discover and execute tools from OpenAPI specifications, providing an enterprise-friendly alternative to traditional MCP implementations.

## 🎯 Project Overview

OpenMCP leverages existing OpenAPI (Swagger) specifications to create AI-callable tools. Instead of requiring custom protocols, companies can expose their existing REST APIs as AI tools by simply adding `x-ai-tool` extensions to their OpenAPI specs.

### Key Benefits

- **✅ Standards-Based**: Uses existing OpenAPI specifications
- **✅ Enterprise-Ready**: Leverages existing API infrastructure, security, and monitoring
- **✅ Zero Custom Protocols**: No stdio or custom communication needed
- **✅ Gradual Adoption**: Companies can expose specific endpoints incrementally
- **✅ Scalable**: Standard HTTP load balancing, caching, and rate limiting

## 🚀 Quick Start (Docker)

```bash
# Start all services
docker-compose up -d

# Chat with AI
uv run python examples/docker_chat_client.py
```

## 📁 Project Structure

```
├── openmcp/                 # Core OpenMCP library
│   ├── api/                 # REST API endpoints
│   ├── core/                # Core functionality (parsers, integrations)
│   └── utils/               # Utilities and helpers
├── examples/                # Example applications
│   ├── calculator_api.py    # Example API with AI tools
│   ├── docker_chat_client.py  # Docker-aware chat client
│   └── simple_chat.py       # Simple Ollama integration
├── specs/                   # OpenAPI specifications
│   ├── calculator-api.yaml  # Example calculator API spec
│   └── example-api.yaml     # Extended example spec
├── docs/                    # Documentation
│   ├── README_FLASK.md      # Flask implementation details
│   ├── README_DOCKER.md     # Docker setup guide
│   └── README_OLLAMA.md     # Ollama integration guide
├── docker-compose.yml       # Docker orchestration
└── CLAUDE.md               # Development guide
```

## 🛠 How It Works

1. **OpenAPI Extension**: Mark endpoints as AI-callable using `x-ai-tool: true`
2. **Tool Discovery**: OpenMCP scans OpenAPI specs and extracts AI tools
3. **Tool Execution**: AI systems call tools via standard HTTP requests
4. **Enterprise Integration**: Uses existing API infrastructure

### Example OpenAPI Extension

```yaml
paths:
  /calculate/add:
    post:
      summary: Add two numbers
      x-ai-tool: true
      x-ai-description: "Add two numbers together"
      x-ai-category: "math"
      # ... rest of standard OpenAPI spec
```

## 🤖 AI Integration

OpenMCP includes built-in support for:

- **Ollama**: Local AI models with tool calling
- **Rich Chat Interface**: Beautiful terminal-based chat client
- **Conversation Management**: Persistent chat history and context

### Example AI Conversation

```
You: What is 42 plus 17?
AI: I'll add those numbers for you.
    42 + 17 = 59
```

## 📚 Documentation

- **[Flask Implementation](docs/README_FLASK.md)** - Core API and architecture
- **[Docker Setup](docs/README_DOCKER.md)** - Containerized deployment
- **[Ollama Integration](docs/README_OLLAMA.md)** - AI chat client setup
- **[CLAUDE.md](CLAUDE.md)** - Development guide for Claude Code

## 🏃‍♂️ Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker and Docker Compose
- [Ollama](https://ollama.ai) (for AI chat features)

### Installation

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd openMCP
   uv sync
   ```

2. **Choose your deployment**:

   **Option A: Docker (Recommended)**
   ```bash
   docker-compose up -d
   uv run python examples/docker_chat_client.py
   ```

   **Option B: Local Development**
   ```bash
   # Terminal 1 - OpenMCP
   uv run python -m openmcp.app
   
   # Terminal 2 - Calculator API
   uv run python examples/calculator_api.py
   
   # Terminal 3 - Chat
   uv run python examples/simple_chat.py
   ```

## 🎮 Example: Calculator API

The project includes a complete example showing how to:

1. Create a REST API with math operations
2. Define OpenAPI spec with AI tool extensions
3. Register the API with OpenMCP
4. Use AI to perform calculations via natural language

Try asking: *"What is 156 divided by 12?"* or *"Calculate 25 times 4"*

## 🏗 Architecture

```
User Input → Ollama → OpenMCP → REST API
     ↓         ↓         ↓         ↓
AI Response ← Tool Call ← Discovery ← HTTP Response
```

- **OpenMCP**: Tool discovery and execution coordinator
- **Ollama**: Local AI model with tool calling capabilities
- **REST APIs**: Standard HTTP APIs with OpenAPI specifications
- **Chat Client**: Rich terminal interface for natural interaction

## 🔧 Development

### Adding New APIs

1. Create your REST API with OpenAPI spec
2. Add `x-ai-tool: true` to endpoints you want AI-accessible
3. Register with OpenMCP:
   ```bash
   curl -X POST http://localhost:8000/api/discovery/register \
     -H "Content-Type: application/json" \
     -d '{"spec_path": "./path/to/your/spec.yaml"}'
   ```

### Environment Variables

```bash
# OpenMCP Configuration
OPENMCP_PORT=8000
DEBUG=True
OPENAPI_SPECS_DIR=./specs

# Ollama Configuration  
OLLAMA_HOST=http://localhost:11434
```

## 📋 API Endpoints

- `GET /health` - Health check
- `POST /api/discovery/register` - Register OpenAPI specification
- `GET /api/discovery/tools` - List discovered tools
- `POST /api/tools/execute` - Execute a tool
- `GET /api/tools/list` - List registered tools

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new functionality
3. Update documentation
4. Ensure Docker setup works

## 📄 License

This project demonstrates the OpenMCP concept for integrating AI with existing REST APIs through OpenAPI specifications.

---

**OpenMCP** - Making enterprise APIs AI-ready through standards-based integration.