from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

from openmcp.api import tools_api, discovery_api
from openmcp.core.openapi_parser import OpenAPIParser
from openmcp.utils.logging import setup_logging

load_dotenv()

def create_app(config_name='development'):
    app = Flask(__name__)
    CORS(app)
    
    # Configure app
    app.config['DEBUG'] = os.getenv('DEBUG', 'True').lower() == 'true'
    app.config['OPENAPI_SPECS_DIR'] = os.getenv('OPENAPI_SPECS_DIR', './specs')
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    app.register_blueprint(tools_api.bp, url_prefix='/api/tools')
    app.register_blueprint(discovery_api.bp, url_prefix='/api/discovery')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'OpenMCP',
            'version': '0.1.0'
        })
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'service': 'OpenMCP - OpenAPI Model Context Protocol',
            'endpoints': {
                'health': '/health',
                'discover_tools': '/api/discovery/tools',
                'register_spec': '/api/discovery/register',
                'execute_tool': '/api/tools/execute'
            }
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('API_PORT', os.getenv('OPENMCP_PORT', '5005')))
    app.run(host='0.0.0.0', port=port)