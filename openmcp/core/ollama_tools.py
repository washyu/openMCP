"""
Enhanced Ollama integration with native tool calling support
"""

import ollama
import json
import requests
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class Tool:
    """Represents a tool that can be called by the AI"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Optional[Callable] = None
    
    def to_ollama_format(self) -> Dict[str, Any]:
        """Convert to Ollama's expected tool format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

class OllamaToolClient:
    """Enhanced Ollama client with tool calling support"""
    
    def __init__(self, model: str = "llama3.2", openmcp_base: str = "http://localhost:5005"):
        self.model = model
        self.openmcp_base = openmcp_base
        self.client = ollama.Client()
        self.tools: Dict[str, Tool] = {}
        self.conversation = []
        
    def discover_and_register_tools(self) -> List[Tool]:
        """Discover tools from OpenMCP and register them"""
        try:
            response = requests.get(f"{self.openmcp_base}/api/tools/list")
            if response.status_code == 200:
                data = response.json()
                
                for tool_data in data['tools']:
                    # Create tool wrapper
                    tool = Tool(
                        name=tool_data['name'],
                        description=tool_data.get('description', ''),
                        parameters=tool_data.get('parameters', {}),
                        function=self._create_tool_function(tool_data['name'])
                    )
                    self.tools[tool.name] = tool
                
                logger.info(f"Registered {len(self.tools)} tools")
                return list(self.tools.values())
            else:
                logger.error(f"Failed to discover tools: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error discovering tools: {e}")
            return []
    
    def _create_tool_function(self, tool_name: str) -> Callable:
        """Create a function that executes the tool via OpenMCP"""
        def execute(**kwargs):
            try:
                response = requests.post(
                    f"{self.openmcp_base}/api/tools/execute",
                    json={
                        "tool_name": tool_name,
                        "parameters": kwargs
                    }
                )
                result = response.json()
                
                if result.get('success'):
                    return result.get('data', {})
                else:
                    return {"error": result.get('error', 'Unknown error')}
            except Exception as e:
                return {"error": str(e)}
        
        return execute
    
    def chat_with_tools(self, user_input: str) -> str:
        """Chat with tool calling support"""
        # Add user message
        self.conversation.append({"role": "user", "content": user_input})
        
        # Prepare tools for Ollama
        tools_list = [tool.to_ollama_format() for tool in self.tools.values()]
        
        try:
            # Try to use native tool calling if available
            response = self._try_native_tools(tools_list)
            
            if response:
                return response
            else:
                # Fallback to prompt-based tool calling
                return self._fallback_tool_calling(user_input)
                
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _try_native_tools(self, tools_list: List[Dict]) -> Optional[str]:
        """Try to use Ollama's native tool calling if supported"""
        try:
            # Attempt native tool calling (works with newer Ollama versions)
            response = self.client.chat(
                model=self.model,
                messages=self.conversation,
                tools=tools_list,
                options={"temperature": 0.7}
            )
            
            message = response['message']
            
            # Check if the model wants to use a tool
            if 'tool_calls' in message:
                results = []
                for tool_call in message['tool_calls']:
                    tool_name = tool_call['function']['name']
                    tool_args = tool_call['function']['arguments']
                    
                    if tool_name in self.tools:
                        result = self.tools[tool_name].function(**tool_args)
                        results.append({
                            "tool": tool_name,
                            "result": result
                        })
                
                # Add tool results to conversation
                self.conversation.append({
                    "role": "assistant",
                    "content": message.get('content', ''),
                    "tool_calls": message['tool_calls']
                })
                
                self.conversation.append({
                    "role": "tool",
                    "content": json.dumps(results)
                })
                
                # Get final response
                final_response = self.client.chat(
                    model=self.model,
                    messages=self.conversation,
                    options={"temperature": 0.7}
                )
                
                final_content = final_response['message']['content']
                self.conversation.append({
                    "role": "assistant",
                    "content": final_content
                })
                
                return final_content
            else:
                # No tool use, regular response
                content = message['content']
                self.conversation.append({
                    "role": "assistant",
                    "content": content
                })
                return content
                
        except Exception as e:
            logger.info(f"Native tool calling not available: {e}")
            return None
    
    def _fallback_tool_calling(self, user_input: str) -> str:
        """Fallback to prompt-based tool calling"""
        # Build tool descriptions for the prompt
        tool_descriptions = []
        for tool in self.tools.values():
            params = tool.parameters.get('properties', {})
            param_str = ", ".join([f"{k}: {v.get('type', 'any')}" for k, v in params.items()])
            tool_descriptions.append(
                f"- {tool.name}({param_str}): {tool.description}"
            )
        
        system_prompt = f"""You are a helpful AI assistant with access to these tools:

{chr(10).join(tool_descriptions)}

To use a tool, respond with ONLY a JSON object in this format:
{{"tool": "tool_name", "parameters": {{"param1": value1, "param2": value2}}}}

After I provide the tool result, give a natural response to the user."""
        
        # Create messages with system prompt
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        response = self.client.chat(
            model=self.model,
            messages=messages,
            options={"temperature": 0.7}
        )
        
        content = response['message']['content']
        
        # Try to parse tool call
        tool_call = self._parse_tool_call(content)
        
        if tool_call and tool_call['tool'] in self.tools:
            # Execute tool
            tool = self.tools[tool_call['tool']]
            result = tool.function(**tool_call['parameters'])
            
            # Get final response with tool result
            messages.append({"role": "assistant", "content": content})
            messages.append({
                "role": "user", 
                "content": f"Tool result: {json.dumps(result)}"
            })
            
            final_response = self.client.chat(
                model=self.model,
                messages=messages,
                options={"temperature": 0.7}
            )
            
            return final_response['message']['content']
        else:
            # No tool use
            return content
    
    def _parse_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse tool call from text"""
        try:
            # Find JSON in the text
            start = text.find('{')
            end = text.rfind('}')
            
            if start != -1 and end != -1:
                json_str = text[start:end + 1]
                data = json.loads(json_str)
                
                if 'tool' in data and 'parameters' in data:
                    return data
        except:
            pass
        
        return None
    
    def reset(self):
        """Reset conversation history"""
        self.conversation = []