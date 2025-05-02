#!/usr/bin/env python3
# G3r4ki LLM Manager

import os
import time
import logging
from typing import Dict, List, Any, Optional, Union

from .llama_cpp import LlamaCpp
from .gpt4all import GPT4All
from .vllm_server import VLLMServer

logger = logging.getLogger('g3r4ki.llm.manager')

class LLMManager:
    """
    LLM Manager

    This class manages all local LLM engines, providing a unified interface
    for model loading, querying, and management across different backends.
    """

    def __init__(self, config):
        """
        Initialize LLM Manager

        Args:
            config: G3r4ki configuration
        """
        self.config = config
        self.models_dir = config['paths']['models_dir']
        
        # Initialize LLM engines
        self.llama_cpp = LlamaCpp(config)
        self.gpt4all = GPT4All(config)
        self.vllm = VLLMServer(config)
        
        # Store default model configuration
        self.default_model = config['llm'].get('default_model', {})
        
        # Cache for available models
        self._available_models = None
        
        logger.info("LLM Manager initialized")
    
    def get_engines(self) -> List[Dict[str, Any]]:
        """
        Get available LLM engines

        Returns:
            List of engine information dictionaries
        """
        engines = []
        
        # Check llama.cpp
        if self.llama_cpp.is_available():
            models = self.llama_cpp.list_models()
            engines.append({
                'id': 'llama.cpp',
                'name': 'llama.cpp',
                'type': 'local',
                'description': 'Efficient C++ implementation of LLM inference',
                'model_count': len(models),
                'status': 'available'
            })
        else:
            engines.append({
                'id': 'llama.cpp',
                'name': 'llama.cpp',
                'type': 'local',
                'description': 'Efficient C++ implementation of LLM inference',
                'model_count': 0,
                'status': 'not_installed'
            })
        
        # Check GPT4All
        if self.gpt4all.is_available():
            models = self.gpt4all.list_models()
            engines.append({
                'id': 'gpt4all',
                'name': 'GPT4All',
                'type': 'local',
                'description': 'Local inference with simplified models',
                'model_count': len(models),
                'status': 'available'
            })
        else:
            engines.append({
                'id': 'gpt4all',
                'name': 'GPT4All',
                'type': 'local',
                'description': 'Local inference with simplified models',
                'model_count': 0,
                'status': 'not_installed'
            })
        
        # Check vLLM
        if self.vllm.is_available():
            models = self.vllm.list_models()
            engines.append({
                'id': 'vllm',
                'name': 'vLLM',
                'type': 'local',
                'description': 'High-performance LLM inference with GPU acceleration',
                'model_count': len(models),
                'status': 'available' if self.vllm.is_running() else 'stopped'
            })
        else:
            engines.append({
                'id': 'vllm',
                'name': 'vLLM',
                'type': 'local',
                'description': 'High-performance LLM inference with GPU acceleration',
                'model_count': 0,
                'status': 'not_installed'
            })
        
        return engines
    
    def get_models(self, engine_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get available models for specified engine or all engines

        Args:
            engine_id: Engine ID (llama.cpp, gpt4all, vllm) or None for all

        Returns:
            List of model information dictionaries
        """
        all_models = []
        
        if engine_id == 'llama.cpp' or engine_id is None:
            if self.llama_cpp.is_available():
                models = self.llama_cpp.list_models()
                for model in models:
                    all_models.append({
                        'id': model,
                        'name': self._format_model_name(model),
                        'engine': 'llama.cpp',
                        'path': os.path.join(self.models_dir, 'llama', model),
                        'default': model == self.default_model.get('llama.cpp', '')
                    })
        
        if engine_id == 'gpt4all' or engine_id is None:
            if self.gpt4all.is_available():
                models = self.gpt4all.list_models()
                for model in models:
                    all_models.append({
                        'id': model,
                        'name': self._format_model_name(model),
                        'engine': 'gpt4all',
                        'path': os.path.join(self.models_dir, 'gpt4all', model),
                        'default': model == self.default_model.get('gpt4all', '')
                    })
        
        if engine_id == 'vllm' or engine_id is None:
            if self.vllm.is_available():
                models = self.vllm.list_models()
                for model in models:
                    all_models.append({
                        'id': model,
                        'name': self._format_model_name(model),
                        'engine': 'vllm',
                        'path': os.path.join(self.models_dir, 'vllm', model),
                        'default': model == self.default_model.get('vllm', '')
                    })
        
        return all_models
    
    def _format_model_name(self, filename: str) -> str:
        """
        Format model name for display

        Args:
            filename: Model filename

        Returns:
            Formatted model name
        """
        name = filename
        
        # Remove file extension
        if '.' in name:
            name = name.rsplit('.', 1)[0]
        
        # Replace underscores and hyphens with spaces
        name = name.replace('_', ' ').replace('-', ' ')
        
        # Handle GGUF models
        if 'gguf' in name.lower():
            # Extract model name before the quantization format
            parts = name.split('Q')
            if len(parts) > 1:
                name = parts[0].strip()
        
        # Capitalize first letter of each word
        name = ' '.join(word.capitalize() for word in name.split())
        
        return name
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get all available models across all engines

        Returns:
            List of model information dictionaries
        """
        if self._available_models is not None:
            return self._available_models
        
        self._available_models = self.get_models()
        return self._available_models
    
    def is_local_available(self) -> bool:
        """
        Check if any local LLM engine is available

        Returns:
            True if at least one local LLM engine is available, False otherwise
        """
        return self.llama_cpp.is_available() or self.gpt4all.is_available() or self.vllm.is_available()
    
    def run_query(self, prompt: str, engine: Optional[str] = None, model: Optional[str] = None,
                 max_tokens: int = 256, temperature: float = 0.7, top_p: float = 0.95) -> Dict[str, Any]:
        """
        Run a query on a local LLM

        Args:
            prompt: Text prompt
            engine: Engine name (llama.cpp, gpt4all, vllm) or None for auto-select
            model: Model name or None for default
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter

        Returns:
            Dictionary with response and metadata
        """
        # Auto-select engine if not specified
        if engine is None:
            engine = self._select_best_engine()
        
        # Get default model for the selected engine if not specified
        if model is None:
            model = self.default_model.get(engine, '')
        
        # Route to the appropriate engine
        if engine == 'llama.cpp':
            if not self.llama_cpp.is_available():
                return {
                    'response': "Error: llama.cpp is not available. Please install it first.",
                    'engine': 'llama.cpp',
                    'model': model,
                    'status': 'error'
                }
            
            start_time = time.time()
            response = self.llama_cpp.run_completion(prompt, model, max_tokens, temperature, top_p)
            elapsed_time = time.time() - start_time
            
            return {
                'response': response,
                'engine': 'llama.cpp',
                'model': model,
                'tokens': len(response.split()),  # Rough estimate
                'time_taken': elapsed_time,
                'status': 'error' if response.startswith('Error:') else 'success'
            }
            
        elif engine == 'gpt4all':
            if not self.gpt4all.is_available():
                return {
                    'response': "Error: GPT4All is not available. Please install it first.",
                    'engine': 'gpt4all',
                    'model': model,
                    'status': 'error'
                }
            
            start_time = time.time()
            response = self.gpt4all.run_completion(prompt, model, max_tokens, temperature, top_p)
            elapsed_time = time.time() - start_time
            
            return {
                'response': response,
                'engine': 'gpt4all',
                'model': model,
                'tokens': len(response.split()),  # Rough estimate
                'time_taken': elapsed_time,
                'status': 'error' if response.startswith('Error:') else 'success'
            }
            
        elif engine == 'vllm':
            if not self.vllm.is_available():
                return {
                    'response': "Error: vLLM is not available. Please install it first.",
                    'engine': 'vllm',
                    'model': model,
                    'status': 'error'
                }
            
            if not self.vllm.is_running():
                start_status = self.vllm.start_server(model)
                if not start_status['success']:
                    return {
                        'response': f"Error starting vLLM server: {start_status.get('error', 'Unknown error')}",
                        'engine': 'vllm',
                        'model': model,
                        'status': 'error'
                    }
            
            start_time = time.time()
            response = self.vllm.run_completion(prompt, model, max_tokens, temperature, top_p)
            elapsed_time = time.time() - start_time
            
            return {
                'response': response,
                'engine': 'vllm',
                'model': model,
                'tokens': len(response.split()),  # Rough estimate
                'time_taken': elapsed_time,
                'status': 'error' if response.startswith('Error:') else 'success'
            }
            
        else:
            return {
                'response': f"Error: Unknown engine '{engine}'",
                'engine': engine,
                'model': model,
                'status': 'error'
            }
    
    def _select_best_engine(self) -> str:
        """
        Select the best available LLM engine

        Returns:
            Engine ID (llama.cpp, gpt4all, vllm)
        """
        # Prefer vLLM if available (GPU acceleration)
        if self.vllm.is_available():
            return 'vllm'
        
        # Prefer llama.cpp as secondary option
        if self.llama_cpp.is_available():
            return 'llama.cpp'
        
        # Fall back to GPT4All
        if self.gpt4all.is_available():
            return 'gpt4all'
        
        # Default to llama.cpp (will show appropriate error)
        return 'llama.cpp'
    
    def setup_local_llm(self, engine: str, model_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Set up local LLM engine and download models if needed

        Args:
            engine: Engine name (llama.cpp, gpt4all, vllm)
            model_url: Optional URL to download model from

        Returns:
            Setup status
        """
        if engine == 'llama.cpp':
            # TODO: Implement llama.cpp setup
            return {
                'status': 'not_implemented',
                'message': 'llama.cpp setup not yet implemented. Please use setup_llms.sh script.'
            }
        elif engine == 'gpt4all':
            # TODO: Implement GPT4All setup
            return {
                'status': 'not_implemented',
                'message': 'GPT4All setup not yet implemented. Please use setup_llms.sh script.'
            }
        elif engine == 'vllm':
            # TODO: Implement vLLM setup
            return {
                'status': 'not_implemented',
                'message': 'vLLM setup not yet implemented. Please use setup_llms.sh script.'
            }
        else:
            return {
                'status': 'error',
                'message': f"Unknown engine: {engine}"
            }
    
    def download_model(self, engine: str, model_id: str, url: str) -> Dict[str, Any]:
        """
        Download a model for the specified engine

        Args:
            engine: Engine name (llama.cpp, gpt4all, vllm)
            model_id: Model identifier
            url: URL to download from

        Returns:
            Download status
        """
        # TODO: Implement model downloading
        return {
            'status': 'not_implemented',
            'message': 'Model downloading not yet implemented.'
        }
        
    def get_available_engines(self) -> List[str]:
        """
        Get list of available engines
        
        Returns:
            List of engine IDs that are available
        """
        engines = self.get_engines()
        return [engine['id'] for engine in engines if engine['status'] == 'available']
        
    def list_models(self) -> tuple:
        """
        List all available engines and models
        
        Returns:
            Tuple containing (engines, models)
        """
        engines = self.get_engines()
        models = self.get_available_models()
        return engines, models
        
    def query(self, prompt: str, engine: Optional[str] = None, model: Optional[str] = None) -> str:
        """
        Query an LLM with the given prompt
        
        Args:
            prompt: The text prompt to send to the LLM
            engine: Optional engine to use
            model: Optional model to use
            
        Returns:
            The LLM response
        """
        result = self.run_query(prompt, engine, model)
        return result.get('text', 'No response generated')



def init_llm_manager(config):
    """
    Initialize the LLM Manager

    Args:
        config: G3r4ki configuration

    Returns:
        LLMManager instance
    """
    return LLMManager(config)