from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Calculator API'})

@app.route('/')
def index():
    return jsonify({
        'service': 'Calculator API',
        'version': '1.0.0',
        'endpoints': {
            'add': '/calculate/add',
            'subtract': '/calculate/subtract',
            'multiply': '/calculate/multiply',
            'divide': '/calculate/divide'
        }
    })

@app.route('/calculate/add', methods=['POST'])
def add():
    """Add two numbers"""
    data = request.json
    if not data or 'a' not in data or 'b' not in data:
        return jsonify({'error': 'Missing parameters a and b'}), 400
    
    try:
        a = float(data['a'])
        b = float(data['b'])
        result = a + b
        
        return jsonify({
            'operation': 'add',
            'a': a,
            'b': b,
            'result': result,
            'expression': f"{a} + {b} = {result}"
        })
    except (ValueError, TypeError):
        return jsonify({'error': 'Parameters a and b must be numbers'}), 400

@app.route('/calculate/subtract', methods=['POST'])
def subtract():
    """Subtract b from a"""
    data = request.json
    if not data or 'a' not in data or 'b' not in data:
        return jsonify({'error': 'Missing parameters a and b'}), 400
    
    try:
        a = float(data['a'])
        b = float(data['b'])
        result = a - b
        
        return jsonify({
            'operation': 'subtract',
            'a': a,
            'b': b,
            'result': result,
            'expression': f"{a} - {b} = {result}"
        })
    except (ValueError, TypeError):
        return jsonify({'error': 'Parameters a and b must be numbers'}), 400

@app.route('/calculate/multiply', methods=['POST'])
def multiply():
    """Multiply two numbers"""
    data = request.json
    if not data or 'a' not in data or 'b' not in data:
        return jsonify({'error': 'Missing parameters a and b'}), 400
    
    try:
        a = float(data['a'])
        b = float(data['b'])
        result = a * b
        
        return jsonify({
            'operation': 'multiply',
            'a': a,
            'b': b,
            'result': result,
            'expression': f"{a} × {b} = {result}"
        })
    except (ValueError, TypeError):
        return jsonify({'error': 'Parameters a and b must be numbers'}), 400

@app.route('/calculate/divide', methods=['POST'])
def divide():
    """Divide a by b"""
    data = request.json
    if not data or 'a' not in data or 'b' not in data:
        return jsonify({'error': 'Missing parameters a and b'}), 400
    
    try:
        a = float(data['a'])
        b = float(data['b'])
        
        if b == 0:
            return jsonify({'error': 'Division by zero is not allowed'}), 400
        
        result = a / b
        
        return jsonify({
            'operation': 'divide',
            'a': a,
            'b': b,
            'result': result,
            'expression': f"{a} ÷ {b} = {result}"
        })
    except (ValueError, TypeError):
        return jsonify({'error': 'Parameters a and b must be numbers'}), 400

if __name__ == '__main__':
    print("Starting Calculator API on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)