"""
G3r4ki AI Provider Manager

This module manages the connections to various AI providers for G3r4ki.
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Any, Union

import anthropic
from anthropic import Anthropic
import openai
from openai import OpenAI

# Setup logging
logger = logging.getLogger("g3r4ki.web.ai_providers")

class AiProviderException(Exception):
    """Exception for AI provider errors"""
    pass

class AiProviderManager:
    """
    Manager for AI providers
    
    This class handles the connections to various AI providers and routes
    queries to them.
    """
    
    def __init__(self):
        """Initialize the AI provider manager"""
        self.providers = {}
        self.available_providers = []
        
        # Initialize available providers
        self._init_openai()
        self._init_anthropic()
        self._init_deepseek()
    
    def _init_openai(self):
        """Initialize OpenAI provider"""
        logger.info("Initializing OpenAI provider")
        
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OpenAI API key not found")
            return
        
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            client = OpenAI(api_key=api_key)
            self.providers["openai"] = {
                "client": client,
                "model": "gpt-4o",
                "name": "OpenAI GPT-4o"
            }
            self.available_providers.append("openai")
            logger.info("OpenAI provider initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OpenAI provider: {str(e)}")
    
    def _init_anthropic(self):
        """Initialize Anthropic provider"""
        logger.info("Initializing Anthropic provider")
        
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            logger.warning("Anthropic API key not found")
            return
        
        try:
            # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
            client = Anthropic(api_key=api_key)
            self.providers["anthropic"] = {
                "client": client,
                "model": "claude-3-5-sonnet-20241022",
                "name": "Anthropic Claude 3.5 Sonnet"
            }
            self.available_providers.append("anthropic")
            logger.info("Anthropic provider initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Anthropic provider: {str(e)}")
    
    def _init_deepseek(self):
        """Initialize DeepSeek provider"""
        logger.info("Initializing DeepSeek provider")
        
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            logger.warning("DeepSeek API key not found")
            return
        
        try:
            # For DeepSeek, we'll use the OpenAI client with the DeepSeek base URL
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1",
            )
            
            self.providers["deepseek"] = {
                "client": client,
                "model": "deepseek-chat",
                "name": "DeepSeek Chat"
            }
            self.available_providers.append("deepseek")
            logger.info("DeepSeek provider initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing DeepSeek provider: {str(e)}")
    
    def get_available_providers(self) -> List[Dict[str, str]]:
        """
        Get a list of available providers
        
        Returns:
            List of provider information dictionaries
        """
        return [
            {"id": provider_id, "name": self.providers[provider_id]["name"]}
            for provider_id in self.available_providers
        ]
    
    def query_openai(self, prompt: str, system_prompt: str = "") -> str:
        """
        Query OpenAI
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
        
        Returns:
            Response text
        
        Raises:
            AiProviderException: If there's an error with the provider
        """
        if "openai" not in self.providers:
            raise AiProviderException("OpenAI provider not available")
        
        provider = self.providers["openai"]
        client = provider["client"]
        model = provider["model"]
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Check if JSON format is requested in the system prompt
            use_json_format = "JSON" in system_prompt or "json" in system_prompt
            
            # Create the response, with JSON format if applicable
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"} if use_json_format else None
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error querying OpenAI: {str(e)}")
            raise AiProviderException(f"Error querying OpenAI: {str(e)}")
    
    def query_anthropic(self, prompt: str, system_prompt: str = "") -> str:
        """
        Query Anthropic
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
        
        Returns:
            Response text
        
        Raises:
            AiProviderException: If there's an error with the provider
        """
        if "anthropic" not in self.providers:
            raise AiProviderException("Anthropic provider not available")
        
        provider = self.providers["anthropic"]
        client = provider["client"]
        model = provider["model"]
        
        try:
            message = client.messages.create(
                model=model,
                max_tokens=2000,
                system=system_prompt if system_prompt else None,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
        except Exception as e:
            logger.error(f"Error querying Anthropic: {str(e)}")
            raise AiProviderException(f"Error querying Anthropic: {str(e)}")
    
    def query_deepseek(self, prompt: str, system_prompt: str = "") -> str:
        """
        Query DeepSeek
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
        
        Returns:
            Response text
        
        Raises:
            AiProviderException: If there's an error with the provider
        """
        if "deepseek" not in self.providers:
            raise AiProviderException("DeepSeek provider not available")
        
        provider = self.providers["deepseek"]
        client = provider["client"]
        model = provider["model"]
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error querying DeepSeek: {str(e)}")
            raise AiProviderException(f"Error querying DeepSeek: {str(e)}")
    
    def query(self, provider_id: str, prompt: str, system_prompt: str = "") -> str:
        """
        Query a specific provider
        
        Args:
            provider_id: Provider ID
            prompt: User prompt
            system_prompt: Optional system prompt
        
        Returns:
            Response text
        
        Raises:
            AiProviderException: If the provider is unknown or there's an error
        """
        if provider_id == "openai":
            return self.query_openai(prompt, system_prompt)
        elif provider_id == "anthropic":
            return self.query_anthropic(prompt, system_prompt)
        elif provider_id == "deepseek":
            return self.query_deepseek(prompt, system_prompt)
        else:
            raise AiProviderException(f"Unknown provider: {provider_id}")
    
    def query_all(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """
        Query all available providers
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
        
        Returns:
            Dictionary mapping provider IDs to responses
        """
        results = {}
        errors = {}
        
        for provider_id in self.available_providers:
            try:
                response = self.query(provider_id, prompt, system_prompt)
                results[provider_id] = {
                    "response": response,
                    "provider_name": self.providers[provider_id]["name"]
                }
            except AiProviderException as e:
                errors[provider_id] = str(e)
        
        return {
            "results": results,
            "errors": errors
        }

# Create a singleton instance
ai_manager = AiProviderManager()