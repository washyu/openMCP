import ollama
import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class OllamaConfig:
    """Configuration for Ollama integration"""
    host: str = "http://localhost:11434"
    model: str = "llama3.2"
    temperature: float = 0.7
    system_prompt: str = """You are a helpful AI assistant with access to various tools through OpenMCP.
When you need to use a tool, respond with a JSON object in this format:
{"tool": "tool_name", "parameters": {...}}

Available tools will be listed at the start of our conversation."""

class OllamaIntegration:
    """Integrates Ollama with OpenMCP for tool-enabled chat"""
    
    def __init__(self, config: OllamaConfig, openmcp_base: str = "http://localhost:5005"):
        self.config = config
        self.openmcp_base = openmcp_base
        self.client = ollama.Client(host=config.host)
        self.available_tools = []
        self.conversation_history = []
        
    def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover available tools from OpenMCP"""
        try:
            response = requests.get(f"{self.openmcp_base}/api/tools/list")
            if response.status_code == 200:
                data = response.json()
                self.available_tools = data['tools']
                return self.available_tools
            else:
                logger.error(f"Failed to discover tools: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error discovering tools: {e}")
            return []
    
    def format_tools_for_prompt(self) -> str:
        """Format available tools for the system prompt"""
        if not self.available_tools:
            return "No tools are currently available."
        
        tools_desc = []
        for tool in self.available_tools:
            params = tool.get('parameters', {}).get('properties', {})
            params_str = ", ".join([f"{k}: {v.get('type', 'any')}" for k, v in params.items()])
            tools_desc.append(f"- {tool['name']}({params_str}): {tool.get('description', 'No description')}")
        
        return "Available tools:\n" + "\n".join(tools_desc)
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool through OpenMCP"""
        try:
            response = requests.post(
                f"{self.openmcp_base}/api/tools/execute",
                json={
                    "tool_name": tool_name,
                    "parameters": parameters
                }
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}
    
    def parse_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse tool call from model response"""
        try:
            # Look for JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx + 1]
                data = json.loads(json_str)
                
                if 'tool' in data and 'parameters' in data:
                    return data
        except json.JSONDecodeError:
            pass
        
        return None
    
    def chat(self, user_input: str) -> str:
        """Process a chat message, potentially using tools"""
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Build messages for Ollama
        messages = [
            {
                "role": "system",
                "content": f"{self.config.system_prompt}\n\n{self.format_tools_for_prompt()}"
            }
        ]
        messages.extend(self.conversation_history)
        
        try:
            # Get response from Ollama
            response = self.client.chat(
                model=self.config.model,
                messages=messages,
                options={
                    "temperature": self.config.temperature
                }
            )
            
            assistant_message = response['message']['content']
            
            # Check if the response contains a tool call
            tool_call = self.parse_tool_call(assistant_message)
            
            if tool_call:
                # Execute the tool
                tool_result = self.execute_tool(
                    tool_call['tool'],
                    tool_call['parameters']
                )
                
                # Add tool execution to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": f"I'll use the {tool_call['tool']} tool with parameters {tool_call['parameters']}"
                })
                
                # Format tool result
                if tool_result.get('success'):
                    result_data = tool_result.get('data', {})
                    if 'expression' in result_data:
                        result_message = f"Result: {result_data['expression']}"
                    else:
                        result_message = f"Result: {json.dumps(result_data, indent=2)}"
                else:
                    result_message = f"Error: {tool_result.get('error', 'Unknown error')}"
                
                self.conversation_history.append({
                    "role": "user",
                    "content": f"Tool result: {result_message}"
                })
                
                # Get final response from model
                messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                messages.append({
                    "role": "user",
                    "content": f"Tool result: {result_message}"
                })
                
                final_response = self.client.chat(
                    model=self.config.model,
                    messages=messages,
                    options={"temperature": self.config.temperature}
                )
                
                final_message = final_response['message']['content']
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_message
                })
                
                return final_message
            else:
                # Regular response without tool use
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                return assistant_message
                
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []