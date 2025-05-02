#!/usr/bin/env python3
# G3r4ki llama.cpp integration

import os
import sys
import subprocess
import logging
import tempfile
import json
from pathlib import Path

logger = logging.getLogger('g3r4ki.llm.llama_cpp')

class LlamaCpp:
    """Interface for llama.cpp models"""
    
    def __init__(self, config):
        self.config = config
        self.llama_dir = config['paths']['llama_cpp_dir']
        self.models_dir = os.path.join(config['paths']['models_dir'], "llama")
        
        # Check if llama.cpp is installed
        if not os.path.exists(self.llama_dir):
            logger.warning(f"llama.cpp directory not found at {self.llama_dir}")
            logger.info("You may need to run setup_llms.sh to install llama.cpp")
    
    def is_available(self):
        """Check if llama.cpp is available"""
        main_executable = os.path.join(self.llama_dir, "main")
        return os.path.exists(main_executable) and os.access(main_executable, os.X_OK)
    
    def list_models(self):
        """
        List available llama.cpp models
        
        Returns:
            List of model filenames
        """
        if not os.path.exists(self.models_dir):
            logger.warning(f"Models directory not found: {self.models_dir}")
            return []
        
        models = []
        for file in os.listdir(self.models_dir):
            if file.endswith(('.bin', '.gguf')):
                models.append(file)
        
        return models
    
    def run_completion(self, prompt, model=None, max_tokens=256, temperature=0.7, top_p=0.95):
        """
        Run completion using llama.cpp
        
        Args:
            prompt: Text prompt
            model: Model filename (without path) 
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling
            
        Returns:
            Generated text or error message
        """
        if not self.is_available():
            logger.error("llama.cpp is not available. Run setup_llms.sh to install it.")
            return "Error: llama.cpp is not installed or configured properly."
        
        # Use specified model or default from config
        if not model:
            model = self.config['llm']['default_model']['llama.cpp']
        
        model_path = os.path.join(self.models_dir, model)
        
        if not os.path.exists(model_path):
            logger.error(f"Model not found: {model_path}")
            available_models = self.list_models()
            if available_models:
                logger.info(f"Available models: {', '.join(available_models)}")
            return f"Error: Model not found: {model}"
        
        # Create temp file for prompt
        with tempfile.NamedTemporaryFile(mode='w', suffix=".txt", delete=False) as tmp:
            tmp.write(prompt)
            prompt_file = tmp.name
        
        # Create temp file for output
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            output_file = tmp.name
        
        try:
            # Run llama.cpp
            main_executable = os.path.join(self.llama_dir, "main")
            
            logger.info(f"Running llama.cpp with model {model}")
            process = subprocess.run(
                [
                    main_executable,
                    "-m", model_path,
                    "-f", prompt_file,
                    "--temp", str(temperature),
                    "--top_p", str(top_p),
                    "-n", str(max_tokens),
                    "-c", str(self.config['llm'].get('context_length', 2048))
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Parse output
            output = process.stdout.strip()
            
            # Remove prompt from output
            if output.startswith(prompt):
                output = output[len(prompt):]
            
            return output.strip()
            
        except subprocess.CalledProcessError as e:
            logger.error(f"llama.cpp execution failed: {e}")
            logger.error(f"STDERR: {e.stderr}")
            return f"Error: llama.cpp execution failed: {e.stderr}"
        finally:
            # Clean up temp files
            if os.path.exists(prompt_file):
                os.unlink(prompt_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
