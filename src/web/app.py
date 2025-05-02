"""
G3r4ki Web Interface

This module provides a web interface for the G3r4ki system, allowing users
to interact with the system through a browser.
"""

import os
import json
import logging
import subprocess
from typing import Dict, Any, List, Optional
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit

from src.web.ai_providers import ai_manager, AiProviderException
# Agent manager import - use a simple mock for now
# from src.agents.manager import AgentManager

class MockAgentManager:
    """Simple mock agent manager for development"""
    
    def __init__(self):
        """Initialize the mock agent manager"""
        self.agents = {}
    
    def list_agents(self):
        """Return an empty list of agents"""
        return []
    
    def get_agent_types(self):
        """Return a list of agent types"""
        return ["pentest"]
    
    def create_agent(self, agent_type, name, description=None):
        """Create a mock agent"""
        agent_id = "mock-agent-" + name.lower().replace(" ", "-")
        agent = {
            "agent_id": agent_id,
            "name": name,
            "type": agent_type,
            "status": "IDLE"
        }
        self.agents[agent_id] = agent
        return agent

# Use the mock agent manager for now
agent_manager = MockAgentManager()
from src.pentest.shells import reverse_shells

# Setup logging
logger = logging.getLogger("g3r4ki.web")
logger.setLevel(logging.INFO)

# Create Flask app
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), "templates"),
            static_folder=os.path.join(os.path.dirname(__file__), "static"))
app.config['SECRET_KEY'] = os.urandom(24).hex()
socketio = SocketIO(app, cors_allowed_origins="*")

# Agent manager is already initialized above

# Security Headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
    return response

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', 
                           available_providers=ai_manager.get_available_providers())

@app.route('/api/ai/query', methods=['POST'])
def query_ai():
    """Query AI provider API endpoint"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    provider = data.get('provider')
    system_prompt = data.get('system_prompt', '')
    
    try:
        if provider and provider != 'all':
            response = ai_manager.query(provider, prompt, system_prompt)
            return jsonify({"response": response, "provider": provider})
        else:
            responses = ai_manager.query_all(prompt, system_prompt)
            return jsonify({"responses": responses})
    except AiProviderException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pentest/shells', methods=['GET'])
def list_shells():
    """List available reverse shells"""
    shell_types = reverse_shells.list_shell_types()
    return jsonify({"shell_types": shell_types})

@app.route('/api/pentest/shells/<shell_type>', methods=['GET'])
def get_shell_variants(shell_type):
    """Get variants for a specific shell type"""
    variants = reverse_shells.list_variants(shell_type)
    return jsonify({"shell_type": shell_type, "variants": variants})

@app.route('/api/pentest/shells/generate', methods=['POST'])
def generate_shell():
    """Generate a reverse shell"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    shell_type = data.get('shell_type')
    variant = data.get('variant', 'basic')
    ip = data.get('ip')
    port = data.get('port', 4444)
    
    if not shell_type:
        return jsonify({"error": "No shell type provided"}), 400
    if not ip:
        ip = reverse_shells.get_local_ip()
    
    try:
        shell = reverse_shells.generate_shell(shell_type, variant, ip, port)
        return jsonify({
            "shell": shell,
            "shell_type": shell_type,
            "variant": variant,
            "ip": ip,
            "port": port
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/agents', methods=['GET'])
def list_agents():
    """List available agents"""
    agents = agent_manager.list_agents()
    return jsonify({"agents": agents})

@app.route('/api/agents/types', methods=['GET'])
def get_agent_types():
    """Get available agent types"""
    types = agent_manager.get_agent_types()
    return jsonify({"agent_types": types})

@app.route('/api/agents/create', methods=['POST'])
def create_agent():
    """Create a new agent"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    agent_type = data.get('agent_type')
    name = data.get('name')
    description = data.get('description', f"{agent_type.capitalize()} agent")
    
    if not agent_type or not name:
        return jsonify({"error": "Agent type and name are required"}), 400
    
    try:
        agent = agent_manager.create_agent(agent_type, name, description)
        
        # Use appropriate format based on agent type (mock vs real)
        if hasattr(agent, 'agent_id') and hasattr(agent, 'status'):
            # Real agent
            if 'target' in data and hasattr(agent, 'set_target'):
                agent.set_target(data['target'])
            
            return jsonify({
                "agent_id": agent.agent_id,
                "name": agent.name,
                "type": agent_type,
                "status": agent.status.value if hasattr(agent.status, 'value') else agent.status
            })
        else:
            # Mock agent
            return jsonify({
                "agent_id": agent.get("agent_id", "unknown-id"),
                "name": agent.get("name", name),
                "type": agent_type,
                "status": agent.get("status", "UNKNOWN")
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info("Client disconnected")

@socketio.on('execute_command')
def handle_execute_command(data):
    """Execute a command and stream the output"""
    command = data.get('command')
    if not command:
        emit('command_output', {'error': 'No command provided'})
        return
    
    try:
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
            bufsize=1, universal_newlines=True
        )
        
        for line in iter(process.stdout.readline, ''):
            emit('command_output', {'line': line})
        
        process.stdout.close()
        return_code = process.wait()
        
        emit('command_output', {
            'exit_code': return_code,
            'completed': True
        })
    except Exception as e:
        emit('command_output', {'error': str(e), 'completed': True})

def run_web_server(host="0.0.0.0", port=5000, debug=False):
    """
    Run the web server
    
    Args:
        host: Host to bind to
        port: Port to bind to
        debug: Enable debug mode
    """
    logger.info(f"Starting G3r4ki web server on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    run_web_server(debug=True)