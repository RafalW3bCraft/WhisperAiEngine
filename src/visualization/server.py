"""
G3r4ki Visualization Server

This module provides a web server for the G3r4ki visualization capabilities.
"""

import os
import sys
import time
import threading
import logging
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import json
import datetime

# Setup logging
logger = logging.getLogger('g3r4ki.visualization.server')

class VisualizationServer:
    """
    Visualization server for G3r4ki using Flask and SocketIO
    
    Provides:
    - Web interface for visualizing scan results
    - Real-time updates using websockets
    - Network map visualization
    - Vulnerability dashboard
    """
    
    def __init__(self, config):
        """
        Initialize visualization server
        
        Args:
            config: G3r4ki configuration
        """
        self.config = config
        self.running = False
        self.server_thread = None
        self.app = None
        self.socketio = None
        self.results_dir = os.path.expanduser(
            config.get('visualization', {}).get('results_dir', 'results')
        )
        
        # Ensure results directory exists
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Create subdirectories for different result types
        os.makedirs(os.path.join(self.results_dir, 'scans'), exist_ok=True)
        os.makedirs(os.path.join(self.results_dir, 'recon'), exist_ok=True)
        os.makedirs(os.path.join(self.results_dir, 'vuln'), exist_ok=True)
    
    def is_available(self):
        """
        Check if Flask is available
        
        Returns:
            True if Flask is available, False otherwise
        """
        try:
            from flask import Flask
            from flask_socketio import SocketIO
            return True
        except ImportError:
            return False
    
    def _create_app(self):
        """
        Create Flask application
        
        Returns:
            Flask application object
        """
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'g3r4ki-visualization-secret'
        socketio = SocketIO(app)
        
        # Main dashboard route
        @app.route('/')
        def index():
            return render_template('index.html')
        
        # Network map route
        @app.route('/network-map')
        def network_map():
            return render_template('network_map.html')
        
        # Host details route
        @app.route('/host/<host>')
        def host_details(host):
            return render_template('host_details.html', host=host)
        
        # API routes
        @app.route('/api/scans')
        def api_scans():
            return jsonify(self._load_results('scans'))
        
        @app.route('/api/recon')
        def api_recon():
            return jsonify(self._load_results('recon'))
        
        @app.route('/api/vuln')
        def api_vuln():
            return jsonify(self._load_results('vuln'))
        
        # SocketIO events
        @socketio.on('connect')
        def handle_connect():
            logger.debug('Client connected')
        
        @socketio.on('disconnect')
        def handle_disconnect():
            logger.debug('Client disconnected')
        
        # Save app and socketio instances
        self.app = app
        self.socketio = socketio
        
        return app, socketio
    
    def _load_results(self, result_type):
        """
        Load results from disk
        
        Args:
            result_type: Type of results to load (scans, recon, vuln)
            
        Returns:
            Dictionary of results
        """
        results = {}
        results_path = os.path.join(self.results_dir, result_type)
        
        if not os.path.exists(results_path):
            return results
        
        for filename in os.listdir(results_path):
            if not filename.endswith('.json'):
                continue
            
            try:
                with open(os.path.join(results_path, filename), 'r') as f:
                    data = json.load(f)
                
                # Extract target from filename (remove .json extension)
                target = filename[:-5]
                results[target] = data
            except Exception as e:
                logger.error(f"Error loading {result_type} result {filename}: {e}")
        
        return results
    
    def _run_server(self, host, port, debug):
        """
        Run the Flask server in a separate thread
        
        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Whether to run in debug mode
        """
        app, socketio = self._create_app()
        
        try:
            socketio.run(app, host=host, port=port, debug=debug, use_reloader=False, log_output=True, allow_unsafe_werkzeug=True)
        except Exception as e:
            logger.error(f"Error running visualization server: {e}")
            self.running = False
    
    def start(self, debug=False):
        """
        Start the visualization server
        
        Args:
            debug: Whether to run in debug mode
            
        Returns:
            True if server started successfully, False otherwise
        """
        if self.running:
            logger.warning("Visualization server is already running")
            return True
        
        if not self.is_available():
            logger.error("Flask is not available")
            return False
        
        host = self.config.get('visualization', {}).get('host', '0.0.0.0')
        port = self.config.get('visualization', {}).get('port', 5000)
        
        # Create and start server thread
        self.server_thread = threading.Thread(
            target=self._run_server,
            args=(host, port, debug)
        )
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Mark as running
        self.running = True
        
        # Give the server a moment to start
        time.sleep(1)
        
        return True
    
    def stop(self):
        """
        Stop the visualization server
        
        Returns:
            True if server stopped successfully, False otherwise
        """
        if not self.running:
            logger.warning("Visualization server is not running")
            return True
        
        # There's no clean way to stop a Flask server running in a thread
        # We'll rely on the daemon thread property to have it killed when the main program exits
        self.running = False
        self.server_thread = None
        
        return True
    
    def save_scan_result(self, target, data, timestamp=None):
        """
        Save scan result to disk
        
        Args:
            target: Scan target (IP, hostname, or CIDR)
            data: Scan data
            timestamp: Timestamp of the scan (defaults to current time)
            
        Returns:
            True if result saved successfully, False otherwise
        """
        if not timestamp:
            timestamp = time.time()
        
        result = {
            'timestamp': timestamp,
            'data': data
        }
        
        # Save to disk
        filename = os.path.join(self.results_dir, 'scans', f"{target}.json")
        
        try:
            with open(filename, 'w') as f:
                json.dump(result, f)
            
            # Notify clients if server is running
            if self.running and self.socketio:
                self.socketio.emit('scan_update', {'target': target, 'timestamp': timestamp})
            
            return True
        except Exception as e:
            logger.error(f"Error saving scan result: {e}")
            return False
    
    def save_recon_result(self, target, data, timestamp=None):
        """
        Save reconnaissance result to disk
        
        Args:
            target: Reconnaissance target
            data: Reconnaissance data
            timestamp: Timestamp of the reconnaissance (defaults to current time)
            
        Returns:
            True if result saved successfully, False otherwise
        """
        if not timestamp:
            timestamp = time.time()
        
        result = {
            'timestamp': timestamp,
            'data': data
        }
        
        # Save to disk
        filename = os.path.join(self.results_dir, 'recon', f"{target}.json")
        
        try:
            with open(filename, 'w') as f:
                json.dump(result, f)
            
            # Notify clients if server is running
            if self.running and self.socketio:
                self.socketio.emit('recon_update', {'target': target, 'timestamp': timestamp})
            
            return True
        except Exception as e:
            logger.error(f"Error saving reconnaissance result: {e}")
            return False
    
    def save_vuln_result(self, target, data, timestamp=None):
        """
        Save vulnerability scan result to disk
        
        Args:
            target: Vulnerability scan target
            data: Vulnerability scan data
            timestamp: Timestamp of the vulnerability scan (defaults to current time)
            
        Returns:
            True if result saved successfully, False otherwise
        """
        if not timestamp:
            timestamp = time.time()
        
        result = {
            'timestamp': timestamp,
            'data': data
        }
        
        # Save to disk
        filename = os.path.join(self.results_dir, 'vuln', f"{target}.json")
        
        try:
            with open(filename, 'w') as f:
                json.dump(result, f)
            
            # Notify clients if server is running
            if self.running and self.socketio:
                self.socketio.emit('vuln_update', {'target': target, 'timestamp': timestamp})
            
            return True
        except Exception as e:
            logger.error(f"Error saving vulnerability scan result: {e}")
            return False
    
    def __del__(self):
        """
        Clean up resources on deletion
        """
        if self.running:
            self.stop()