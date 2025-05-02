#!/usr/bin/env python3
# G3r4ki GPT4All integration

import os
import sys
import subprocess
import logging
import tempfile
import json
from pathlib import Path

logger = logging.getLogger('g3r4ki.llm.gpt4all')

class GPT4All:
    """Interface for GPT4All models"""
    
    def __init__(self, config):
        self.config = config
        self.gpt4all_dir = config['paths']['gpt4all_dir']
        self.models_dir = os.path.join(config['paths']['models_dir'], "gpt4all")
        
        # Check if GPT4All is installed
        if not os.path.exists(self.gpt4all_dir):
            logger.warning(f"GPT4All directory not found at {self.gpt4all_dir}")
            logger.info("You may need to run setup_llms.sh to install GPT4All")
    
    def is_available(self):
        """Check if GPT4All CLI is available"""
        cli_executable = os.path.join(self.gpt4all_dir, "gpt4all-cli")
        return os.path.exists(cli_executable) and os.access(cli_executable, os.X_OK)
    
    def list_models(self):
        """
        List available GPT4All models
        
        Returns:
            List of model filenames
        """
        if not os.path.exists(self.models_dir):
            logger.warning(f"Models directory not found: {self.models_dir}")
            return []
        
        models = []
        for file in os.listdir(self.models_dir):
            if file.endswith(('.bin')):
                models.append(file)
        
        return models
    
    def run_completion(self, prompt, model=None, max_tokens=256, temperature=0.7, top_p=0.95):
        """
        Run completion using GPT4All
        
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
            logger.error("GPT4All is not available. Run setup_llms.sh to install it.")
            return "Error: GPT4All is not installed or configured properly."
        
        # Use specified model or default from config
        if not model:
            model = self.config['llm']['default_model']['gpt4all']
        
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
            # Run GPT4All CLI
            cli_executable = os.path.join(self.gpt4all_dir, "gpt4all-cli")
            
            logger.info(f"Running GPT4All with model {model}")
            process = subprocess.run(
                [
                    cli_executable,
                    "--model", model_path,
                    "--prompt-file", prompt_file,
                    "--temp", str(temperature),
                    "--top-p", str(top_p),
                    "--n-predict", str(max_tokens),
                    "--n-ctx", str(self.config['llm'].get('context_length', 2048)),
                    "--color", "false"
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Parse output
            output = process.stdout.strip()
            
            # Extract just the generated text (after prompt)
            lines = output.split('\n')
            generated_text = []
            found_prompt = False
            
            for line in lines:
                # Skip other GPT4All output like loading messages
                if prompt in line:
                    found_prompt = True
                    # Get just the text after the prompt in this line
                    prompt_index = line.find(prompt)
                    if prompt_index != -1:
                        line_after_prompt = line[prompt_index + len(prompt):]
                        if line_after_prompt:
                            generated_text.append(line_after_prompt)
                elif found_prompt:
                    generated_text.append(line)
            
            return '\n'.join(generated_text).strip()
            
        except subprocess.CalledProcessError as e:
            logger.error(f"GPT4All execution failed: {e}")
            logger.error(f"STDERR: {e.stderr}")
            return f"Error: GPT4All execution failed: {e.stderr}"
        finally:
            # Clean up temp files
            if os.path.exists(prompt_file):
                os.unlink(prompt_file)
            if os.path.exists(output_file):
                os.unlink(output_file)
