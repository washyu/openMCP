from flask import Blueprint, jsonify, request
import requests
from typing import Dict, Any
import json

bp = Blueprint('tools', __name__)

# In-memory storage for registered tools (in production, use a database)
registered_tools: Dict[str, Any] = {}

@bp.route('/execute', methods=['POST'])
def execute_tool():
    """Execute an AI tool by making the actual HTTP request"""
    data = request.json
    
    if not data or 'tool_name' not in data or 'parameters' not in data:
        return jsonify({'error': 'Missing tool_name or parameters'}), 400
    
    tool_name = data['tool_name']
    parameters = data['parameters']
    
    # Get tool definition
    tool = registered_tools.get(tool_name)
    if not tool:
        return jsonify({'error': f'Tool {tool_name} not found'}), 404
    
    try:
        # Build the request
        endpoint = tool['endpoint']
        url = endpoint['url']
        method = endpoint['method']
        
        # Separate path parameters from body/query parameters
        path_params = {}
        body_params = {}
        query_params = {}
        
        # Simple parameter routing (in production, use the OpenAPI spec for proper routing)
        for key, value in parameters.items():
            if f'{{{key}}}' in url:
                path_params[key] = value
            elif method in ['GET', 'DELETE']:
                query_params[key] = value
            else:
                body_params[key] = value
        
        # Replace path parameters in URL
        for key, value in path_params.items():
            url = url.replace(f'{{{key}}}', str(value))
        
        # Make the HTTP request
        headers = {'Content-Type': 'application/json'}
        
        if method == 'GET':
            response = requests.get(url, params=query_params, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=body_params, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=body_params, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, params=query_params, headers=headers)
        else:
            return jsonify({'error': f'Unsupported method: {method}'}), 400
        
        # Return the response
        return jsonify({
            'success': response.ok,
            'status_code': response.status_code,
            'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/list', methods=['GET'])
def list_tools():
    """List all registered AI tools"""
    tools_list = []
    for name, tool in registered_tools.items():
        tools_list.append({
            'name': name,
            'description': tool.get('description', ''),
            'parameters': tool.get('parameters', {}),
            'endpoint': tool.get('endpoint', {})
        })
    
    return jsonify({
        'tools': tools_list,
        'count': len(tools_list)
    })

@bp.route('/register', methods=['POST'])
def register_tool():
    """Register a tool (called internally by discovery service)"""
    tool_data = request.json
    
    if not tool_data or 'name' not in tool_data:
        return jsonify({'error': 'Missing tool name'}), 400
    
    tool_name = tool_data['name']
    registered_tools[tool_name] = tool_data
    
    return jsonify({
        'message': f'Tool {tool_name} registered successfully',
        'tool': tool_data
    }), 201