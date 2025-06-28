# OpenAPI for AI Tool Integration

## What is OpenAPI?

OpenAPI (formerly called Swagger) is a specification for describing REST APIs. It's a standardized way to document:

- What endpoints exist (`/users`, `/orders`, etc.)
- HTTP methods (GET, POST, PUT, DELETE)
- Request/response formats
- Parameters and their types
- Authentication requirements

## Example OpenAPI Specification

Here's a simple example of an OpenAPI spec:

```yaml
openapi: 3.0.0
info:
  title: User Management API
  version: 1.0.0
  description: API for managing users and orders

servers:
  - url: https://api.example.com/v1
    description: Production server

paths:
  /users/{userId}:
    get:
      summary: Get user by ID
      description: Retrieve a specific user's information
      parameters:
        - name: userId
          in: path
          required: true
          description: The unique identifier for the user
          schema:
            type: string
      responses:
        '200':
          description: User found successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                    description: User's unique identifier
                  name:
                    type: string
                    description: User's full name
                  email:
                    type: string
                    format: email
                    description: User's email address
        '404':
          description: User not found

  /orders:
    post:
      summary: Create new order
      description: Creates a new customer order
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - customerId
                - items
              properties:
                customerId:
                  type: string
                  description: ID of the customer placing the order
                items:
                  type: array
                  description: List of items to order
                  items:
                    type: object
                    properties:
                      productId:
                        type: string
                      quantity:
                        type: integer
                        minimum: 1
      responses:
        '201':
          description: Order created successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  orderId:
                    type: string
                  status:
                    type: string
                  total:
                    type: number
```

## How This Relates to AI Tool Integration

The key insight is that instead of using MCP's custom stdio protocol, you could leverage existing OpenAPI specifications that companies already maintain. Here's how:

### 1. Mark AI-Callable Endpoints

Companies could extend their existing OpenAPI specs with custom extensions to mark endpoints as AI-callable:

```yaml
paths:
  /orders:
    post:
      summary: Create new order
      description: Creates a new customer order
      x-ai-tool: true                    # Mark as AI-callable
      x-ai-description: "Use this tool to create orders for customers when they request to purchase items"
      x-ai-category: "commerce"          # Optional categorization
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required:
                - customerId
                - items
              properties:
                customerId:
                  type: string
                  description: ID of the customer placing the order
                items:
                  type: array
                  description: List of items to order
                  items:
                    type: object
                    properties:
                      productId:
                        type: string
                      quantity:
                        type: integer

  /users/{userId}/preferences:
    put:
      summary: Update user preferences
      x-ai-tool: true
      x-ai-description: "Update a user's account preferences and settings"
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                notifications:
                  type: boolean
                theme:
                  type: string
                  enum: ["light", "dark"]
```

### 2. Web Client Architecture

Your web client would then:

1. **Discover Tools**: Read OpenAPI specs and extract AI-callable endpoints
2. **Convert to AI Format**: Transform OpenAPI definitions into tool definitions that Ollama understands
3. **Execute Tools**: Handle HTTP calls when the AI wants to use those tools

```typescript
interface AITool {
  name: string;
  description: string;
  endpoint: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  parameters: OpenAPISchema;
  authentication?: AuthConfig;
}

class WebMCPClient {
  async discoverTools(apiSpecUrl: string): Promise<AITool[]> {
    // Fetch OpenAPI spec
    // Parse and find x-ai-tool marked endpoints
    // Convert to AITool format
  }
  
  async executeTool(tool: AITool, params: any): Promise<any> {
    // Make HTTP request to the actual API endpoint
    // Handle authentication, error handling, etc.
  }
  
  async registerWithOllama(tools: AITool[]): Promise<void> {
    // Convert AITool[] to Ollama's function calling format
    // Register with Ollama instance
  }
}
```

## Advantages Over stdio MCP

- **Scalability**: Standard HTTP load balancing, caching, rate limiting
- **Security**: OAuth, API keys, standard enterprise authentication
- **Monitoring**: Existing APM tools work out of the box  
- **Documentation**: Swagger UI for human developers too
- **Gradual Adoption**: Companies can expose specific endpoints to AI incrementally
- **Standards-Based**: Leverages existing OpenAPI ecosystem and tooling
- **Enterprise-Friendly**: Fits into existing API governance and security policies

## Implementation Flow

1. **Company maintains OpenAPI spec** (they probably already do this)
2. **Add `x-ai-tool` extensions** to mark AI-callable endpoints
3. **Web client discovers tools** from the OpenAPI spec
4. **Client registers tools with Ollama** using function calling
5. **AI makes tool requests** through standard HTTP calls
6. **Standard API infrastructure** handles scaling, auth, monitoring

This approach essentially turns any REST API into an AI tool provider with minimal additional work, while maintaining enterprise-grade reliability and security.
