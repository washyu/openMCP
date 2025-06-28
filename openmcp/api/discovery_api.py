from flask import Blueprint, jsonify, request, current_app
from pathlib import Path
import requests
from openmcp.core.openapi_parser import OpenAPIParser
from openmcp.api.tools_api import registered_tools

bp = Blueprint('discovery', __name__)
parser = OpenAPIParser()

@bp.route('/register', methods=['POST'])
def register_spec():
    """Register an OpenAPI specification and discover AI tools"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Support both file path and URL
    spec_source = data.get('spec_path') or data.get('spec_url')
    if not spec_source:
        return jsonify({'error': 'Missing spec_path or spec_url'}), 400
    
    try:
        # Load the spec
        if data.get('spec_url'):
            # Fetch spec from URL
            response = requests.get(spec_source)
            response.raise_for_status()
            spec = response.json()
        else:
            # Load from file
            spec = parser.load_spec(spec_source)
        
        # Extract AI tools
        ai_tools = parser.extract_ai_tools(spec)
        
        # Convert and register each tool
        registered_count = 0
        for endpoint in ai_tools:
            tool_def = parser.convert_to_ai_format(endpoint)
            # Register with tools service
            registered_tools[tool_def['name']] = tool_def
            registered_count += 1
        
        return jsonify({
            'message': 'OpenAPI spec processed successfully',
            'spec_title': spec.get('info', {}).get('title', 'Unknown'),
            'tools_discovered': len(ai_tools),
            'tools_registered': registered_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/tools', methods=['GET'])
def discover_tools():
    """Discover all available AI tools from registered specs"""
    all_tools = []
    
    # Get tools from all loaded specs
    for spec_id, spec in parser.specs.items():
        tools = parser.extract_ai_tools(spec)
        for tool in tools:
            tool_info = parser.convert_to_ai_format(tool)
            tool_info['spec_id'] = spec_id
            all_tools.append(tool_info)
    
    # Include already registered tools
    for name, tool in registered_tools.items():
        if not any(t['name'] == name for t in all_tools):
            all_tools.append(tool)
    
    return jsonify({
        'tools': all_tools,
        'total': len(all_tools),
        'specs_loaded': len(parser.specs)
    })

@bp.route('/specs', methods=['GET'])
def list_specs():
    """List all loaded OpenAPI specifications"""
    specs_info = []
    
    for spec_id, spec in parser.specs.items():
        info = spec.get('info', {})
        specs_info.append({
            'id': spec_id,
            'title': info.get('title', 'Unknown'),
            'version': info.get('version', '1.0.0'),
            'description': info.get('description', ''),
            'servers': spec.get('servers', [])
        })
    
    return jsonify({
        'specs': specs_info,
        'count': len(specs_info)
    })

@bp.route('/scan', methods=['POST'])
def scan_directory():
    """Scan a directory for OpenAPI specifications"""
    data = request.json
    directory = data.get('directory', current_app.config['OPENAPI_SPECS_DIR'])
    
    try:
        specs_dir = Path(directory)
        if not specs_dir.exists():
            return jsonify({'error': f'Directory not found: {directory}'}), 404
        
        discovered_specs = []
        
        # Look for YAML and JSON files
        for pattern in ['*.yaml', '*.yml', '*.json']:
            for spec_file in specs_dir.glob(pattern):
                try:
                    spec = parser.load_spec(str(spec_file))
                    ai_tools = parser.extract_ai_tools(spec)
                    
                    discovered_specs.append({
                        'file': str(spec_file),
                        'title': spec.get('info', {}).get('title', 'Unknown'),
                        'ai_tools_count': len(ai_tools)
                    })
                except Exception as e:
                    current_app.logger.warning(f"Failed to load {spec_file}: {e}")
        
        return jsonify({
            'directory': directory,
            'specs_discovered': discovered_specs,
            'total': len(discovered_specs)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500