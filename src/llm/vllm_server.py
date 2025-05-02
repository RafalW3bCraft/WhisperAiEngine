#!/usr/bin/env python3
# G3r4ki vLLM Server integration

import os
import sys
import json
import time
import signal
import logging
import platform
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger('g3r4ki.llm.vllm_server')

class VLLMServer:
    """Interface for vLLM server for GPU-accelerated inference"""
    
    def __init__(self, config):
        """
        Initialize the vLLM server interface
        
        Args:
            config: G3r4ki configuration
        """
        self.config = config
        self.vllm_dir = config['paths'].get('vllm_dir', os.path.expanduser("~/.local/share/g3r4ki/vllm"))
        self.models_dir = os.path.join(config['paths']['models_dir'], "vllm")
        
        # Server settings
        self.server_port = config['llm'].get('vllm_port', 8000)
        self.server_host = config['llm'].get('vllm_host', '127.0.0.1')
        self.server_url = f"http://{self.server_host}:{self.server_port}"
        
        # For keeping track of server process
        self.server_process = None
        self.current_model = None
        
        # Create model directory if it doesn't exist
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Check if vLLM is installed
        if not os.path.exists(self.vllm_dir):
            logger.warning(f"vLLM directory not found at {self.vllm_dir}")
            logger.info("You may need to run setup_llms.sh to install vLLM")
    
    def is_available(self) -> bool:
        """
        Check if vLLM is available
        
        Returns:
            True if vLLM is installed and can be used, False otherwise
        """
        try:
            # First check if the vLLM Python package is installed
            import importlib.util
            vllm_spec = importlib.util.find_spec("vllm")
            
            if vllm_spec is None:
                return False
            
            # Check for CUDA availability
            import torch
            if not torch.cuda.is_available():
                logger.warning("CUDA is not available. vLLM requires a CUDA-compatible GPU.")
                return False
            
            return True
            
        except ImportError:
            return False
    
    def is_running(self) -> bool:
        """
        Check if vLLM server is running
        
        Returns:
            True if running, False otherwise
        """
        # Check if we have a server process
        if self.server_process is not None:
            # Check if process is still running
            if self.server_process.poll() is None:
                # Process is running, check if server responds
                try:
                    response = requests.get(f"{self.server_url}/health", timeout=2)
                    return response.status_code == 200
                except:
                    # Server doesn't respond
                    return False
            else:
                # Process has terminated
                self.server_process = None
                return False
        
        # Check if there's a vLLM server running on the specified port
        try:
            response = requests.get(f"{self.server_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[str]:
        """
        List available vLLM models
        
        Returns:
            List of model directory/file names
        """
        if not os.path.exists(self.models_dir):
            logger.warning(f"Models directory not found: {self.models_dir}")
            return []
        
        # Get directories/files directly under the models directory
        models = []
        for item in os.listdir(self.models_dir):
            item_path = os.path.join(self.models_dir, item)
            
            # Include directories (HF models) and .bin/.gguf files
            if os.path.isdir(item_path) or item.endswith(('.bin', '.gguf')):
                models.append(item)
        
        return models
    
    def start_server(self, model: str) -> Dict[str, Any]:
        """
        Start vLLM server with the specified model
        
        Args:
            model: Model name/directory or path
            
        Returns:
            Dictionary with status information
        """
        if not self.is_available():
            return {
                'success': False,
                'error': "vLLM is not properly installed or CUDA is not available"
            }
        
        # Check if server is already running
        if self.is_running():
            # If already running with the requested model, return success
            if self.current_model == model:
                return {
                    'success': True,
                    'message': f"vLLM server already running with model {model}",
                    'port': self.server_port
                }
            
            # Stop the server if it's running with a different model
            self.stop_server()
        
        # Resolve model path
        if os.path.exists(model):
            model_path = model
        else:
            model_path = os.path.join(self.models_dir, model)
            if not os.path.exists(model_path):
                return {
                    'success': False,
                    'error': f"Model not found: {model_path}"
                }
        
        try:
            # Start the vLLM server
            cmd = [
                sys.executable, "-m", "vllm.entrypoints.api_server",
                "--model", model_path,
                "--port", str(self.server_port),
                "--host", self.server_host
            ]
            
            # Add quantization if specified
            if self.config['llm'].get('vllm_quantization'):
                cmd.extend(["--quantization", self.config['llm']['vllm_quantization']])
            
            # Add tensor parallel size if specified
            if self.config['llm'].get('vllm_tensor_parallel_size'):
                cmd.extend(["--tensor-parallel-size", str(self.config['llm']['vllm_tensor_parallel_size'])])
            
            # Start the server process
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Store current model
            self.current_model = model
            
            # Wait for server to start (max 60 seconds)
            start_time = time.time()
            while time.time() - start_time < 60:
                if self.is_running():
                    return {
                        'success': True,
                        'message': f"vLLM server started with model {model}",
                        'port': self.server_port
                    }
                
                # Check if process has terminated
                if self.server_process.poll() is not None:
                    stderr = self.server_process.stderr.read()
                    self.server_process = None
                    return {
                        'success': False,
                        'error': f"vLLM server failed to start: {stderr}"
                    }
                
                time.sleep(1)
            
            # If we get here, server didn't start in time
            if self.server_process:
                self.server_process.terminate()
                self.server_process = None
            
            return {
                'success': False,
                'error': "vLLM server timed out while starting"
            }
            
        except Exception as e:
            logger.error(f"Error starting vLLM server: {e}")
            
            if self.server_process:
                self.server_process.terminate()
                self.server_process = None
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def stop_server(self) -> Dict[str, Any]:
        """
        Stop vLLM server if running
        
        Returns:
            Dictionary with status information
        """
        if not self.is_running():
            return {
                'success': True,
                'message': "vLLM server is not running"
            }
        
        try:
            if self.server_process:
                # Try graceful termination
                self.server_process.terminate()
                
                # Wait for process to terminate (max 10 seconds)
                start_time = time.time()
                while time.time() - start_time < 10:
                    if self.server_process.poll() is not None:
                        break
                    time.sleep(0.5)
                
                # Force kill if still running
                if self.server_process.poll() is None:
                    if platform.system() == 'Windows':
                        self.server_process.kill()
                    else:
                        os.killpg(os.getpgid(self.server_process.pid), signal.SIGKILL)
                
                self.server_process = None
                self.current_model = None
                
                return {
                    'success': True,
                    'message': "vLLM server stopped"
                }
            else:
                # Try to kill any vLLM server running on our port
                if platform.system() == 'Windows':
                    # Find and kill the process using the port on Windows
                    subprocess.run(
                        f"FOR /F \"tokens=5\" %P IN ('netstat -ano ^| findstr \":{self.server_port}\"') DO taskkill /F /PID %P",
                        shell=True
                    )
                else:
                    # Find and kill the process using the port on Unix-like systems
                    subprocess.run(
                        f"lsof -i :{self.server_port} | awk 'NR>1 {{print $2}}' | xargs -r kill -9",
                        shell=True
                    )
                
                self.current_model = None
                
                return {
                    'success': True,
                    'message': "vLLM server stopped (externally managed process)"
                }
            
        except Exception as e:
            logger.error(f"Error stopping vLLM server: {e}")
            
            # Reset internal state even if there was an error
            self.server_process = None
            self.current_model = None
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_completion(self, prompt: str, model: Optional[str] = None, max_tokens: int = 256, 
                      temperature: float = 0.7, top_p: float = 0.95) -> str:
        """
        Run completion using vLLM server
        
        Args:
            prompt: Text prompt
            model: Model name
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling
            
        Returns:
            Generated text or error message
        """
        if not self.is_available():
            return "Error: vLLM is not available. Please install vLLM and ensure CUDA is available."
        
        # Start server if not running or if a specific model is requested
        if not self.is_running() or (model is not None and self.current_model != model):
            # Use specified model or default
            model_to_use = model
            if model_to_use is None:
                model_to_use = self.config['llm']['default_model'].get('vllm', '')
            
            if not model_to_use:
                return "Error: No model specified and no default model configured."
            
            start_result = self.start_server(model_to_use)
            if not start_result['success']:
                return f"Error starting vLLM server: {start_result.get('error', 'Unknown error')}"
        
        try:
            # Prepare request
            request_data = {
                'prompt': prompt,
                'max_tokens': max_tokens,
                'temperature': temperature,
                'top_p': top_p,
                'stop': [],  # Optional stop sequences
            }
            
            # Send request to vLLM server
            response = requests.post(
                f"{self.server_url}/generate", 
                json=request_data,
                timeout=60
            )
            
            if response.status_code != 200:
                return f"Error: vLLM server returned status code {response.status_code}: {response.text}"
            
            # Parse response
            result = response.json()
            
            # Extract generated text
            if 'text' in result:
                return result['text']
            elif 'generations' in result and len(result['generations']) > 0:
                if isinstance(result['generations'][0], dict) and 'text' in result['generations'][0]:
                    return result['generations'][0]['text']
                else:
                    return str(result['generations'][0])
            else:
                return f"Error: Unexpected response format from vLLM server: {json.dumps(result)}"
            
        except requests.exceptions.Timeout:
            return "Error: Request to vLLM server timed out."
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to vLLM server."
        except Exception as e:
            logger.error(f"Error in vLLM completion: {e}")
            return f"Error: {str(e)}"