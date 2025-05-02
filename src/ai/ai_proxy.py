#!/usr/bin/env python3
"""
G3r4ki AI Proxy

This module provides a unified interface to both local and cloud AI providers.
It enables G3r4ki to work both online (with cloud AI services) and offline
(with local LLM models), allowing for seamless operation in various scenarios.
"""

import os
import sys
import logging
import time
import socket
from typing import Dict, List, Optional, Any, Union, Tuple

# Import AI providers
from src.web.ai_providers import ai_manager as cloud_ai_manager
from src.llm.manager import init_llm_manager

# Setup logging
logger = logging.getLogger("g3r4ki.ai.proxy")

class AIProxy:
    """
    AI Proxy that unifies local and cloud AI providers
    
    This class provides a unified interface to query both local LLMs
    and cloud AI services, with fallback capabilities.

    The proxy provides intelligent selection between:
    - Cloud providers (OpenAI, Anthropic, DeepSeek) when online
    - Local LLM models (llama.cpp, vLLM, GPT4All) when offline or preferred

    With self-improving capabilities that continuously enhance its performance
    and adapt to the user's needs.
    """
    
    def __init__(self, config):
        """
        Initialize the AI proxy
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.mode = config.get('ai', {}).get('mode', 'auto')
        
        # Initialize LLM manager for local models
        self.llm_manager = init_llm_manager(config)
        
        # Mode options:
        # - 'auto': Use cloud providers if available, fallback to local
        # - 'cloud': Use only cloud providers
        # - 'local': Use only local LLMs
        # - 'hybrid': Use a combination of cloud and local based on tasks
        
        # Keep track of local and cloud availability
        self.cloud_available = self._check_cloud_availability()
        self.local_available = self.llm_manager.is_local_available()
        
        logger.info(f"AI Proxy initialized in '{self.mode}' mode")
        logger.info(f"Cloud AI available: {self.cloud_available}")
        logger.info(f"Local AI available: {self.local_available}")
    
    def _check_cloud_availability(self) -> bool:
        """
        Check if cloud AI providers are available
        
        Returns:
            True if at least one cloud provider is available, False otherwise
        """
        providers = cloud_ai_manager.get_available_providers()
        return len(providers) > 0
    
    def get_available_providers(self) -> List[Dict[str, str]]:
        """
        Get a list of all available AI providers (both cloud and local)
        
        Returns:
            List of provider information dictionaries
        """
        providers = []
        
        # Add cloud providers if in auto or cloud mode
        if self.mode in ['auto', 'cloud'] and self.cloud_available:
            cloud_providers = cloud_ai_manager.get_available_providers()
            for provider in cloud_providers:
                provider['type'] = 'cloud'
                providers.append(provider)
        
        # Add local providers if in auto or local mode
        if self.mode in ['auto', 'local'] and self.local_available:
            engines = self.llm_manager.get_engines()
            for engine in engines:
                if engine['status'] == 'available':
                    model_count = engine.get('model_count', 0)
                    
                    # Only add if the engine has models available
                    if model_count > 0:
                        providers.append({
                            'id': f"local_{engine['id']}",
                            'name': f"Local {engine['name']}",
                            'type': 'local',
                            'model_count': model_count
                        })
        
        return providers
    
    def query(self, provider_id: str, prompt: str, system_prompt: str = "", 
              max_tokens: int = 512, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Query an AI provider
        
        Args:
            provider_id: Provider ID to use
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
        
        Returns:
            Dictionary with response and provider information
            
        Raises:
            Exception: If there's an error with the provider
        """
        start_time = time.time()
        
        # Check provider type
        if provider_id.startswith('local_'):
            # Local LLM
            engine = provider_id.replace('local_', '')
            response = self._query_local(engine, prompt, system_prompt, max_tokens, temperature)
            provider_name = f"Local {engine.capitalize()}"
            provider_type = 'local'
        else:
            # Cloud provider
            response = self._query_cloud(provider_id, prompt, system_prompt)
            provider_name = next((p['name'] for p in cloud_ai_manager.get_available_providers()
                                if p['id'] == provider_id), provider_id)
            provider_type = 'cloud'
        
        elapsed_time = time.time() - start_time
        
        return {
            'response': response,
            'provider': provider_id,
            'provider_name': provider_name,
            'provider_type': provider_type,
            'time_taken': round(elapsed_time, 2)
        }
    
    def _query_local(self, engine: str, prompt: str, system_prompt: str = "",
                     max_tokens: int = 512, temperature: float = 0.7) -> str:
        """
        Query a local LLM
        
        Args:
            engine: LLM engine (llama.cpp, vllm, gpt4all)
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            Generated text
        """
        try:
            # Combine system prompt and user prompt if both are provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Use the run_query method from LLMManager
            result = self.llm_manager.run_query(
                full_prompt, 
                engine, 
                None,  # Let the manager select the default model
                max_tokens, 
                temperature
            )
            
            # Return the response text
            if isinstance(result, dict) and 'response' in result:
                return result['response']
            elif isinstance(result, str):
                return result
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"Error querying local LLM: {e}")
            return f"Error: {str(e)}"
    
    def _query_cloud(self, provider_id: str, prompt: str, system_prompt: str = "") -> str:
        """
        Query a cloud AI provider
        
        Args:
            provider_id: Provider ID
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated text
        """
        return cloud_ai_manager.query(provider_id, prompt, system_prompt)
    
    def query_best(self, prompt: str, system_prompt: str = "", 
                   max_tokens: int = 512) -> Dict[str, Any]:
        """
        Query the best available AI provider
        
        This will intelligently select the best provider based on:
        1. Availability (cloud if available in auto mode)
        2. Capability (prefer more powerful models)
        3. Fallbacks (try local if cloud fails)
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dictionary with response and provider information
        """
        # Get available providers
        providers = self.get_available_providers()
        
        if not providers:
            return {
                'response': "Error: No AI providers available. Please ensure either internet connectivity for cloud AI or local LLMs are installed.",
                'provider': 'none',
                'provider_name': 'No Provider',
                'provider_type': 'none',
                'time_taken': 0
            }
        
        # Prioritize cloud in auto mode, otherwise use available providers
        if self.mode == 'auto' and self.cloud_available:
            # Prefer most capable cloud model in this order: OpenAI, Anthropic, DeepSeek
            preferred_order = ['openai', 'anthropic', 'deepseek']
            for provider_id in preferred_order:
                if any(p['id'] == provider_id for p in providers):
                    try:
                        return self.query(provider_id, prompt, system_prompt, max_tokens)
                    except Exception as e:
                        logger.warning(f"Error with {provider_id}: {str(e)}")
                        # Continue to next provider
        
        # If we get here, either we're in local mode or cloud providers failed
        if self.local_available:
            # Prefer most capable local model in this order: llama.cpp, vllm, gpt4all
            preferred_order = ['local_llama.cpp', 'local_vllm', 'local_gpt4all']
            for provider_id in preferred_order:
                if any(p['id'] == provider_id for p in providers):
                    try:
                        return self.query(provider_id, prompt, system_prompt, max_tokens)
                    except Exception as e:
                        logger.warning(f"Error with {provider_id}: {str(e)}")
                        # Continue to next provider
        
        # If all else fails, use first available provider
        try:
            return self.query(providers[0]['id'], prompt, system_prompt, max_tokens)
        except Exception as e:
            return {
                'response': f"Error: All AI providers failed. Last error: {str(e)}",
                'provider': 'error',
                'provider_name': 'Error',
                'provider_type': 'error',
                'time_taken': 0
            }
    
    def query_with_reasoning(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """
        Query with specific reasoning tasks to select the most appropriate model
        
        For complex reasoning tasks like cybersecurity analysis, 
        we'll select more powerful models.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Dictionary with response and provider information
        """
        # Keywords that suggest complex reasoning needs
        complex_keywords = [
            'analyze', 'exploit', 'vulnerability', 'security', 'hack', 
            'penetration', 'pentest', 'threat', 'attack', 'defend',
            'malware', 'ransomware', 'mitigation', 'risk', 'assessment'
        ]
        
        # Check if the prompt involves complex reasoning
        is_complex = any(keyword in prompt.lower() for keyword in complex_keywords)
        
        if is_complex:
            # For complex tasks, prefer powerful models
            logger.info("Detected complex reasoning task, selecting powerful model")
            providers = self.get_available_providers()
            
            # Prefer cloud models for complex tasks if available
            if self.mode in ['auto', 'cloud'] and self.cloud_available:
                preferred_order = ['openai', 'anthropic', 'deepseek']
                for provider_id in preferred_order:
                    if any(p['id'] == provider_id for p in providers):
                        try:
                            return self.query(provider_id, prompt, system_prompt)
                        except Exception as e:
                            logger.warning(f"Error with {provider_id}: {str(e)}")
            
            # If cloud isn't available, use most capable local model
            if self.local_available:
                # For complex tasks, prefer llama.cpp with larger models
                if any(p['id'] == 'local_llama.cpp' for p in providers):
                    try:
                        return self.query('local_llama.cpp', prompt, system_prompt)
                    except Exception as e:
                        logger.warning(f"Error with local_llama.cpp: {str(e)}")
        
        # For regular tasks or if preferred providers fail, use best available
        return self.query_best(prompt, system_prompt)
    
    def query_multi(self, provider_ids: List[str], prompt: str, 
                   system_prompt: str = "") -> Dict[str, Dict[str, Any]]:
        """
        Query multiple AI providers
        
        Args:
            provider_ids: List of provider IDs
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Dictionary mapping provider IDs to responses
        """
        results = {}
        errors = {}
        
        for provider_id in provider_ids:
            try:
                result = self.query(provider_id, prompt, system_prompt)
                results[provider_id] = result
            except Exception as e:
                errors[provider_id] = str(e)
        
        return {
            'results': results,
            'errors': errors
        }
    
    def is_provider_available(self, provider_id: str) -> bool:
        """
        Check if a provider is available
        
        Args:
            provider_id: Provider ID
            
        Returns:
            True if provider is available, False otherwise
        """
        providers = self.get_available_providers()
        return any(p['id'] == provider_id for p in providers)
    
    def get_recommended_provider(self) -> Optional[Dict[str, str]]:
        """
        Get the recommended AI provider for current tasks
        
        Returns:
            Provider information dictionary or None if no providers available
        """
        providers = self.get_available_providers()
        if not providers:
            return None
        
        # Prefer cloud in auto mode
        if self.mode == 'auto' and self.cloud_available:
            for provider_id in ['openai', 'anthropic', 'deepseek']:
                for p in providers:
                    if p['id'] == provider_id:
                        return p
        
        # Otherwise recommend first local provider
        for p in providers:
            if p['type'] == 'local':
                return p
        
        # Fall back to first available
        return providers[0]

# Create a singleton instance
ai_proxy = None

def init_ai_proxy(config):
    """
    Initialize the AI proxy
    
    Args:
        config: Configuration dictionary
    """
    global ai_proxy
    ai_proxy = AIProxy(config)
    return ai_proxy