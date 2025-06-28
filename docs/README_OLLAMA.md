# OpenMCP + Ollama Integration

This guide shows how to use Ollama with OpenMCP to create AI assistants that can use tools from OpenAPI specifications.

## Prerequisites

1. **Install Ollama**
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Or download from https://ollama.ai
   ```

2. **Pull a model**
   ```bash
   ollama pull llama3.2
   ```

3. **Ensure Ollama is running**
   - Ollama runs automatically after installation
   - Check status: `curl http://localhost:11434/api/tags`

## Quick Start

1. **Start the services**
   ```bash
   ./run_example.sh
   ```
   This starts both OpenMCP and the Calculator API.

2. **Run the chat client**
   ```bash
   # Simple chat demo
   uv run python examples/simple_chat.py
   
   # Or the rich UI version
   uv run python examples/chat_client.py
   ```

## How It Works

1. **Tool Discovery**: The Ollama client discovers available tools from OpenMCP
2. **Tool Registration**: Tools are converted to a format Ollama can understand
3. **Natural Language**: You can ask questions naturally, like "What is 42 plus 17?"
4. **Tool Execution**: The AI recognizes when to use tools and calls them automatically
5. **Response**: The AI provides a natural language response with the results

## Example Interactions

```
You: What is 42 plus 17?
AI: I'll add those numbers for you. 42 + 17 = 59

You: Calculate 6 times 7
AI: Let me multiply those numbers. 6 × 7 = 42

You: What's 100 divided by 4?
AI: I'll divide 100 by 4 for you. The result is 25.
```

## Architecture

```
User → Ollama → OpenMCP → Calculator API
         ↓         ↓           ↓
    AI Response ← Tool Result ← HTTP Response
```

## Two Integration Approaches

### 1. Enhanced Tool Client (`ollama_tools.py`)
- Attempts to use Ollama's native tool calling (if available)
- Falls back to prompt-based tool calling
- More robust and future-proof

### 2. Basic Integration (`ollama_integration.py`)
- Uses prompt engineering for tool calling
- Works with any Ollama model
- Simpler implementation

## Customization

### Using Different Models

Edit the model in your script:
```python
client = OllamaToolClient(model="mistral")  # or any model you have
```

### Adding Custom Tools

1. Create an OpenAPI spec with `x-ai-tool` extensions
2. Register it with OpenMCP
3. The tools are automatically available to Ollama

## Troubleshooting

### "Ollama is not running"
- Install Ollama from https://ollama.ai
- It should start automatically after installation

### "Model not found"
- Pull the model first: `ollama pull llama3.2`
- Check available models: `ollama list`

### "Tools not working"
- Ensure OpenMCP is running: `curl http://localhost:5005/health`
- Check tool discovery: `curl http://localhost:5005/api/tools/list`
- Some models may not support tool calling well - try `llama3.2` or `mistral`

## Advanced Features

### Tool Calling Methods

1. **Native Tool Calling**: Newer Ollama versions support native tool calling
2. **JSON Response**: Models respond with JSON to indicate tool use
3. **Fallback Mode**: Prompt-based tool calling for compatibility

### Conversation Management

- Reset conversation: Type "clear" in the chat client
- Conversation history is maintained for context
- Each tool use is tracked in the conversation

## Next Steps

1. Add more APIs with OpenAPI specs
2. Implement authentication for external APIs
3. Add streaming responses
4. Create specialized agents for different domains
5. Implement multi-tool workflows