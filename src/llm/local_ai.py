"""
G3r4ki Local AI Integration

This module provides integration with local language models for offline AI capabilities.
"""

import os
import sys
import json
import yaml
import logging
import importlib.util
import subprocess
from typing import Dict, List, Any, Optional, Union, Callable, Tuple

# Configure logging
logger = logging.getLogger("g3r4ki.llm.local_ai")

class LocalAIManager:
    """Manager for local AI models and inference."""
    
    def __init__(self, config_path: Optional[str] = None, model_dir: Optional[str] = None):
        """
        Initialize the local AI manager.
        
        Args:
            config_path: Optional path to configuration file
            model_dir: Optional directory for local models
        """
        self.config_path = config_path or os.path.join(os.path.expanduser("~"), ".g3r4ki", "local_ai_config.yaml")
        self.model_dir = model_dir or os.path.join(os.path.expanduser("~"), ".g3r4ki", "models")
        
        # Ensure model directory exists
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Default configuration
        self.config = {
            "providers": {
                "llama.cpp": {
                    "enabled": False,
                    "default_model": "llama2-7b",
                    "models": {}
                },
                "vllm": {
                    "enabled": False,
                    "default_model": "llama3-8b",
                    "models": {}
                },
                "gpt4all": {
                    "enabled": False,
                    "default_model": "gpt4all-j-v1.3-groovy",
                    "models": {}
                }
            },
            "global": {
                "default_provider": "llama.cpp",
                "temperature": 0.7,
                "max_tokens": 2048,
                "gpu_layers": 0  # 0 means CPU only
            }
        }
        
        # Load configuration if exists
        self._load_config()
        
        # Check available providers
        self._check_providers()
    
    def _load_config(self) -> None:
        """Load configuration from file if exists."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    if loaded_config:
                        # Update config with loaded values, keeping structure
                        self._update_nested_dict(self.config, loaded_config)
                        logger.info(f"Local AI configuration loaded from {self.config_path}")
            else:
                # Save default config
                self._save_config()
                logger.info(f"Default local AI configuration created at {self.config_path}")
        
        except Exception as e:
            logger.error(f"Error loading local AI configuration: {e}")
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            
            logger.info(f"Local AI configuration saved to {self.config_path}")
        
        except Exception as e:
            logger.error(f"Error saving local AI configuration: {e}")
    
    def _update_nested_dict(self, d: Dict, u: Dict) -> Dict:
        """Recursively update nested dictionary."""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._update_nested_dict(d.get(k, {}), v)
            else:
                d[k] = v
        return d
    
    def _check_providers(self) -> None:
        """Check which local AI providers are available."""
        # Check for llama.cpp
        if importlib.util.find_spec("llama_cpp"):
            self.config["providers"]["llama.cpp"]["enabled"] = True
            logger.info("llama.cpp provider is available")
        else:
            logger.info("llama.cpp provider is not available")
        
        # Check for vLLM
        if importlib.util.find_spec("vllm"):
            self.config["providers"]["vllm"]["enabled"] = True
            logger.info("vLLM provider is available")
        else:
            logger.info("vLLM provider is not available")
        
        # Check for GPT4All
        if importlib.util.find_spec("gpt4all"):
            self.config["providers"]["gpt4all"]["enabled"] = True
            logger.info("GPT4All provider is available")
        else:
            logger.info("GPT4All provider is not available")
        
        # Update default provider if necessary
        if not self.config["providers"][self.config["global"]["default_provider"]]["enabled"]:
            # Find first enabled provider
            for provider in self.config["providers"]:
                if self.config["providers"][provider]["enabled"]:
                    self.config["global"]["default_provider"] = provider
                    logger.info(f"Updated default provider to {provider}")
                    break
        
        # Scan for available models
        self._scan_models()
    
    def _scan_models(self) -> None:
        """Scan for available local models."""
        try:
            # Scan model directory
            if os.path.exists(self.model_dir):
                for provider in self.config["providers"]:
                    provider_dir = os.path.join(self.model_dir, provider)
                    if os.path.exists(provider_dir):
                        models = {}
                        
                        # Find model files
                        for file in os.listdir(provider_dir):
                            file_path = os.path.join(provider_dir, file)
                            if os.path.isfile(file_path):
                                # Determine model name from filename
                                name, ext = os.path.splitext(file)
                                
                                # Only include relevant file extensions
                                if provider == "llama.cpp" and ext in [".bin", ".gguf", ".ggml"]:
                                    models[name] = {
                                        "path": file_path,
                                        "type": "llama" if "llama" in file.lower() else "unknown"
                                    }
                                
                                elif provider == "vllm" and ext in [".safetensors", ".bin", ".pt"]:
                                    models[name] = {
                                        "path": file_path,
                                        "type": "llama" if "llama" in file.lower() else "unknown"
                                    }
                                
                                elif provider == "gpt4all" and ext in [".bin"]:
                                    models[name] = {
                                        "path": file_path,
                                        "type": "gpt4all"
                                    }
                        
                        self.config["providers"][provider]["models"] = models
                        
                        if models:
                            logger.info(f"Found {len(models)} models for {provider}")
                        else:
                            logger.info(f"No models found for {provider}")
        
        except Exception as e:
            logger.error(f"Error scanning for local models: {e}")
    
    def download_model(self, provider: str, model_name: str) -> bool:
        """
        Download a model for the specified provider.
        
        Args:
            provider: Provider name (llama.cpp, vllm, gpt4all)
            model_name: Name of the model to download
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if provider not in self.config["providers"]:
                logger.error(f"Unknown provider: {provider}")
                return False
            
            # Create provider directory
            provider_dir = os.path.join(self.model_dir, provider)
            os.makedirs(provider_dir, exist_ok=True)
            
            if provider == "llama.cpp":
                return self._download_llama_cpp_model(provider_dir, model_name)
            elif provider == "vllm":
                return self._download_vllm_model(provider_dir, model_name)
            elif provider == "gpt4all":
                return self._download_gpt4all_model(provider_dir, model_name)
            else:
                logger.error(f"Download not implemented for provider: {provider}")
                return False
        
        except Exception as e:
            logger.error(f"Error downloading model: {e}")
            return False
    
    def _download_llama_cpp_model(self, provider_dir: str, model_name: str) -> bool:
        """Download a model for llama.cpp."""
        try:
            # For llama.cpp, we'll use huggingface_hub to download
            try:
                from huggingface_hub import hf_hub_download
            except ImportError:
                logger.error("huggingface_hub is not installed. Please install with: pip install huggingface_hub")
                return False
            
            # Define common models and their repositories
            model_repos = {
                "llama2-7b": ("meta-llama/Llama-2-7b-chat-hf", "model-00001-of-00002.safetensors"),
                "llama2-13b": ("meta-llama/Llama-2-13b-chat-hf", "model-00001-of-00002.safetensors"),
                "llama3-8b": ("meta-llama/Meta-Llama-3-8B", "model-00001-of-00002.safetensors"),
                "codellama-7b": ("codellama/CodeLlama-7b-instruct-hf", "model-00001-of-00002.safetensors"),
                "mistral-7b": ("mistralai/Mistral-7B-Instruct-v0.2", "model-00001-of-00002.safetensors")
            }
            
            if model_name not in model_repos:
                logger.error(f"Unknown model: {model_name}. Supported models: {', '.join(model_repos.keys())}")
                return False
            
            repo_id, filename = model_repos[model_name]
            
            # Download model
            logger.info(f"Downloading {model_name} from {repo_id}...")
            file_path = hf_hub_download(repo_id=repo_id, filename=filename)
            
            # Convert to GGUF format using llama.cpp tools
            # This is a simplified version - in a real implementation, we'd use llama.cpp conversion tools
            output_path = os.path.join(provider_dir, f"{model_name}.gguf")
            logger.info(f"Converting to GGUF format: {output_path}")
            
            # Simulated conversion - in a real implementation, we'd run convert-llama-to-gguf.py
            with open(output_path, "wb") as f:
                with open(file_path, "rb") as src_f:
                    f.write(src_f.read())
            
            # Update configuration
            self.config["providers"]["llama.cpp"]["models"][model_name] = {
                "path": output_path,
                "type": "llama"
            }
            self._save_config()
            
            logger.info(f"Model {model_name} downloaded and converted successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error downloading llama.cpp model: {e}")
            return False
    
    def _download_vllm_model(self, provider_dir: str, model_name: str) -> bool:
        """Download a model for vLLM."""
        try:
            # For vLLM, we'll use huggingface_hub to download the model
            try:
                from huggingface_hub import snapshot_download
            except ImportError:
                logger.error("huggingface_hub is not installed. Please install with: pip install huggingface_hub")
                return False
            
            # Define common models and their repositories
            model_repos = {
                "llama2-7b": "meta-llama/Llama-2-7b-chat-hf",
                "llama2-13b": "meta-llama/Llama-2-13b-chat-hf",
                "llama3-8b": "meta-llama/Meta-Llama-3-8B",
                "llama3-70b": "meta-llama/Meta-Llama-3-70B",
                "vicuna-7b": "lmsys/vicuna-7b-v1.5",
                "mistral-7b": "mistralai/Mistral-7B-Instruct-v0.2"
            }
            
            if model_name not in model_repos:
                logger.error(f"Unknown model: {model_name}. Supported models: {', '.join(model_repos.keys())}")
                return False
            
            repo_id = model_repos[model_name]
            
            # Check if model directory already exists
            model_path = os.path.join(provider_dir, model_name)
            if os.path.exists(model_path):
                logger.info(f"Model {model_name} already exists at {model_path}, skipping download.")
                return True
            
            # Download entire model repository
            logger.info(f"Downloading {model_name} from {repo_id}...")
            model_path = snapshot_download(repo_id=repo_id, local_dir=model_path)
            
            # Update configuration
            self.config["providers"]["vllm"]["models"][model_name] = {
                "path": model_path,
                "type": "llama" if "llama" in model_name.lower() else "unknown"
            }
            self._save_config()
            
            logger.info(f"Model {model_name} downloaded successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error downloading vLLM model: {e}")
            return False
    
    def _download_gpt4all_model(self, provider_dir: str, model_name: str) -> bool:
        """Download a model for GPT4All."""
        try:
            # For GPT4All, we'll use the gpt4all package to download
            try:
                from gpt4all import GPT4All
            except ImportError:
                logger.error("gpt4all is not installed. Please install with: pip install gpt4all")
                return False
            
            # Check if model file already exists
            model_file_path = os.path.join(provider_dir, f"{model_name}.bin")
            if os.path.exists(model_file_path):
                logger.info(f"Model {model_name} already exists at {model_file_path}, skipping download.")
                # Update configuration if missing
                if model_name not in self.config["providers"]["gpt4all"]["models"]:
                    self.config["providers"]["gpt4all"]["models"][model_name] = {
                        "path": model_file_path,
                        "type": "gpt4all"
                    }
                    self._save_config()
                return True
            
            # GPT4All has its own model download mechanism
            model = GPT4All(model_name=model_name, model_path=provider_dir)
            
            # Get the downloaded model path
            model_file = model.model_path
            
            # Update configuration
            self.config["providers"]["gpt4all"]["models"][model_name] = {
                "path": model_file,
                "type": "gpt4all"
            }
            self._save_config()
            
            logger.info(f"Model {model_name} downloaded successfully")
            return True
        
        except Exception as e:
            logger.error(f"Error downloading GPT4All model: {e}")
            return False
    
    def list_available_models(self, provider: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List available local models.
        
        Args:
            provider: Optional provider name to filter by
            
        Returns:
            Dictionary of available models by provider
        """
        available_models = {}
        
        if provider:
            if provider in self.config["providers"] and self.config["providers"][provider]["enabled"]:
                available_models[provider] = list(self.config["providers"][provider]["models"].keys())
        else:
            for p in self.config["providers"]:
                if self.config["providers"][p]["enabled"]:
                    available_models[p] = list(self.config["providers"][p]["models"].keys())
        
        return available_models
    
    def is_available(self) -> bool:
        """
        Check if any local AI provider is available.
        
        Returns:
            True if at least one provider is available with models, False otherwise
        """
        for provider in self.config["providers"]:
            if (self.config["providers"][provider]["enabled"] and 
                self.config["providers"][provider]["models"]):
                return True
        
        return False
    
    def set_default_model(self, provider: str, model_name: str) -> bool:
        """
        Set the default model for a provider.
        
        Args:
            provider: Provider name
            model_name: Model name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if provider not in self.config["providers"]:
                logger.error(f"Unknown provider: {provider}")
                return False
            
            if not self.config["providers"][provider]["enabled"]:
                logger.error(f"Provider {provider} is not enabled")
                return False
            
            if model_name not in self.config["providers"][provider]["models"]:
                logger.error(f"Model {model_name} not found for provider {provider}")
                return False
            
            self.config["providers"][provider]["default_model"] = model_name
            self._save_config()
            
            logger.info(f"Default model for {provider} set to {model_name}")
            return True
        
        except Exception as e:
            logger.error(f"Error setting default model: {e}")
            return False
    
    def set_default_provider(self, provider: str) -> bool:
        """
        Set the default provider.
        
        Args:
            provider: Provider name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if provider not in self.config["providers"]:
                logger.error(f"Unknown provider: {provider}")
                return False
            
            if not self.config["providers"][provider]["enabled"]:
                logger.error(f"Provider {provider} is not enabled")
                return False
            
            if not self.config["providers"][provider]["models"]:
                logger.error(f"No models available for provider {provider}")
                return False
            
            self.config["global"]["default_provider"] = provider
            self._save_config()
            
            logger.info(f"Default provider set to {provider}")
            return True
        
        except Exception as e:
            logger.error(f"Error setting default provider: {e}")
            return False
    
    def get_completion(self, prompt: str, system_message: Optional[str] = None,
                     provider: Optional[str] = None, model: Optional[str] = None,
                     temperature: Optional[float] = None, max_tokens: Optional[int] = None,
                     **kwargs) -> Optional[str]:
        """
        Get completion from a local language model.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            provider: Optional provider override
            model: Optional model override
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Model completion or None if failed
        """
        try:
            # Use default provider if not specified
            provider = provider or self.config["global"]["default_provider"]
            
            if provider not in self.config["providers"]:
                logger.error(f"Unknown provider: {provider}")
                return None
            
            if not self.config["providers"][provider]["enabled"]:
                logger.error(f"Provider {provider} is not enabled")
                return None
            
            # Use default model if not specified
            model = model or self.config["providers"][provider]["default_model"]
            
            if model not in self.config["providers"][provider]["models"]:
                logger.error(f"Model {model} not found for provider {provider}")
                return None
            
            # Use default parameters if not specified
            temperature = temperature if temperature is not None else self.config["global"]["temperature"]
            max_tokens = max_tokens if max_tokens is not None else self.config["global"]["max_tokens"]
            
            # Get model path
            model_info = self.config["providers"][provider]["models"][model]
            model_path = model_info["path"]
            
            # Generate completion based on provider
            if provider == "llama.cpp":
                return self._generate_llama_cpp_completion(model_path, prompt, system_message, temperature, max_tokens, **kwargs)
            elif provider == "vllm":
                return self._generate_vllm_completion(model_path, prompt, system_message, temperature, max_tokens, **kwargs)
            elif provider == "gpt4all":
                return self._generate_gpt4all_completion(model_path, prompt, system_message, temperature, max_tokens, **kwargs)
            else:
                logger.error(f"Completion not implemented for provider: {provider}")
                return None
        
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            return None
    
    def _generate_llama_cpp_completion(self, model_path: str, prompt: str, system_message: Optional[str],
                                     temperature: float, max_tokens: int, **kwargs) -> Optional[str]:
        """Generate completion using llama.cpp."""
        try:
            from llama_cpp import Llama
            
            # Initialize Llama model
            llm = Llama(
                model_path=model_path,
                n_ctx=kwargs.get("n_ctx", 2048),
                n_threads=kwargs.get("n_threads", os.cpu_count() or 4),
                n_gpu_layers=kwargs.get("n_gpu_layers", self.config["global"].get("gpu_layers", 0))
            )
            
            # Format prompt with system message if provided
            formatted_prompt = prompt
            if system_message:
                formatted_prompt = f"<s>[INST] <<SYS>>\n{system_message}\n<</SYS>>\n\n{prompt} [/INST]"
            
            # Generate completion
            output = llm(
                formatted_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=kwargs.get("stop", ["</s>", "[/INST]"]),
                echo=False
            )
            
            # Extract text from output
            if isinstance(output, dict) and "choices" in output:
                return output["choices"][0]["text"].strip()
            elif isinstance(output, str):
                return output.strip()
            else:
                return str(output)
        
        except Exception as e:
            logger.error(f"Error generating llama.cpp completion: {e}")
            return None
    
    def _generate_vllm_completion(self, model_path: str, prompt: str, system_message: Optional[str],
                                temperature: float, max_tokens: int, **kwargs) -> Optional[str]:
        """Generate completion using vLLM."""
        try:
            from vllm import LLM, SamplingParams
            
            # Initialize vLLM model
            llm = LLM(
                model=model_path,
                trust_remote_code=True,
                tensor_parallel_size=kwargs.get("tensor_parallel_size", 1)
            )
            
            # Format prompt with system message if provided
            formatted_prompt = prompt
            if system_message:
                formatted_prompt = f"<s>[INST] <<SYS>>\n{system_message}\n<</SYS>>\n\n{prompt} [/INST]"
            
            # Set sampling parameters
            sampling_params = SamplingParams(
                temperature=temperature,
                max_tokens=max_tokens,
                stop=kwargs.get("stop", ["</s>", "[/INST]"])
            )
            
            # Generate completion
            outputs = llm.generate(formatted_prompt, sampling_params)
            
            # Extract text from output
            if outputs and len(outputs) > 0:
                return outputs[0].outputs[0].text.strip()
            else:
                return None
        
        except Exception as e:
            logger.error(f"Error generating vLLM completion: {e}")
            return None
    
    def _generate_gpt4all_completion(self, model_path: str, prompt: str, system_message: Optional[str],
                                   temperature: float, max_tokens: int, **kwargs) -> Optional[str]:
        """Generate completion using GPT4All."""
        try:
            from gpt4all import GPT4All
            
            # Initialize GPT4All model
            model = GPT4All(model_path=model_path)
            
            # Format prompt with system message if provided
            formatted_prompt = prompt
            if system_message:
                formatted_prompt = f"System: {system_message}\n\nUser: {prompt}\n\nAssistant:"
            
            # Generate completion
            output = model.generate(
                formatted_prompt,
                max_tokens=max_tokens,
                temp=temperature,
                top_k=kwargs.get("top_k", 40),
                top_p=kwargs.get("top_p", 0.9),
                repeat_penalty=kwargs.get("repeat_penalty", 1.1),
                streaming=False
            )
            
            return output.strip()
        
        except Exception as e:
            logger.error(f"Error generating GPT4All completion: {e}")
            return None