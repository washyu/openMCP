import yaml
import json
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from pathlib import Path

class AIToolExtension(BaseModel):
    enabled: bool = Field(default=True, alias='x-ai-tool')
    description: str = Field(alias='x-ai-description')
    category: Optional[str] = Field(default=None, alias='x-ai-category')
    
    class Config:
        populate_by_name = True

class ParsedEndpoint(BaseModel):
    path: str
    method: str
    summary: str
    description: Optional[str] = None
    ai_tool: Optional[AIToolExtension] = None
    parameters: List[Dict[str, Any]] = []
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Any] = {}

class OpenAPIParser:
    def __init__(self):
        self.specs: Dict[str, Dict[str, Any]] = {}
    
    def load_spec(self, spec_path: str) -> Dict[str, Any]:
        """Load OpenAPI specification from file (YAML or JSON)"""
        path = Path(spec_path)
        
        if not path.exists():
            raise FileNotFoundError(f"OpenAPI spec not found: {spec_path}")
        
        with open(spec_path, 'r') as f:
            if spec_path.endswith('.yaml') or spec_path.endswith('.yml'):
                spec = yaml.safe_load(f)
            else:
                spec = json.load(f)
        
        # Store spec by its title or filename
        spec_id = spec.get('info', {}).get('title', path.stem)
        self.specs[spec_id] = spec
        
        return spec
    
    def extract_ai_tools(self, spec: Dict[str, Any]) -> List[ParsedEndpoint]:
        """Extract endpoints marked as AI tools from OpenAPI spec"""
        ai_tools = []
        
        paths = spec.get('paths', {})
        servers = spec.get('servers', [])
        base_url = servers[0]['url'] if servers else ''
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    # Check if endpoint is marked as AI tool
                    if 'x-ai-tool' in operation:
                        endpoint = self._parse_endpoint(
                            path, method, operation, base_url
                        )
                        if endpoint:
                            ai_tools.append(endpoint)
        
        return ai_tools
    
    def _parse_endpoint(self, path: str, method: str, 
                       operation: Dict[str, Any], base_url: str) -> Optional[ParsedEndpoint]:
        """Parse a single endpoint operation"""
        try:
            # Extract AI tool extensions
            ai_tool = None
            if operation.get('x-ai-tool'):
                ai_tool = AIToolExtension(
                    **{k: v for k, v in operation.items() if k.startswith('x-ai-')}
                )
            
            # Extract parameters
            parameters = []
            for param in operation.get('parameters', []):
                parameters.append({
                    'name': param.get('name'),
                    'in': param.get('in'),
                    'required': param.get('required', False),
                    'description': param.get('description'),
                    'schema': param.get('schema', {})
                })
            
            # Extract request body
            request_body = None
            if 'requestBody' in operation:
                content = operation['requestBody'].get('content', {})
                if 'application/json' in content:
                    request_body = content['application/json'].get('schema')
            
            return ParsedEndpoint(
                path=f"{base_url}{path}",
                method=method.upper(),
                summary=operation.get('summary', ''),
                description=operation.get('description'),
                ai_tool=ai_tool,
                parameters=parameters,
                request_body=request_body,
                responses=operation.get('responses', {})
            )
        except Exception as e:
            print(f"Error parsing endpoint {method} {path}: {e}")
            return None
    
    def convert_to_ai_format(self, endpoint: ParsedEndpoint) -> Dict[str, Any]:
        """Convert parsed endpoint to AI tool format"""
        # Build parameters schema
        properties = {}
        required = []
        
        # Path and query parameters
        for param in endpoint.parameters:
            param_name = param['name']
            properties[param_name] = param['schema']
            if param['required']:
                required.append(param_name)
        
        # Request body parameters
        if endpoint.request_body:
            if endpoint.request_body.get('type') == 'object':
                body_props = endpoint.request_body.get('properties', {})
                properties.update(body_props)
                body_required = endpoint.request_body.get('required', [])
                required.extend(body_required)
        
        return {
            'name': f"{endpoint.method.lower()}_{endpoint.path.replace('/', '_').strip('_')}",
            'description': endpoint.ai_tool.description if endpoint.ai_tool else endpoint.description,
            'parameters': {
                'type': 'object',
                'properties': properties,
                'required': required
            },
            'endpoint': {
                'url': endpoint.path,
                'method': endpoint.method
            }
        }