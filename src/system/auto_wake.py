"""
G3r4ki Auto-Wake System

This module provides functionality to automatically initialize AI components
when the G3r4ki application is launched, ensuring both online and offline
capabilities are available without manual activation.
"""

import os
import sys
import logging
import threading
import time
from typing import Dict, List, Any, Optional, Union, Callable

# Configure logging
logger = logging.getLogger("g3r4ki.system.auto_wake")

class AutoWakeManager:
    """Manager for automatically initializing AI components on launch."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the auto-wake manager.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {
            "enabled": True,
            "initialize_cloud_ai": True,
            "initialize_local_ai": True,
            "preload_models": True,
            "initialize_database": True,
            "startup_delay": 1.0  # Delay in seconds before initialization
        }
        
        self.initialized = False
        self.initialization_thread = None
        self.cloud_ai_available = False
        self.local_ai_available = False
        self.database_available = False
    
    def activate(self) -> None:
        """
        Activate the auto-wake system.
        
        This starts an initialization thread that will prepare all required components.
        """
        if not self.config["enabled"]:
            logger.info("Auto-wake system is disabled")
            return
        
        if self.initialized or (self.initialization_thread and self.initialization_thread.is_alive()):
            logger.info("Auto-wake initialization already in progress or completed")
            return
        
        logger.info("Activating auto-wake system")
        
        # Start initialization in a separate thread to avoid blocking
        self.initialization_thread = threading.Thread(target=self._initialize_components)
        self.initialization_thread.daemon = True
        self.initialization_thread.start()
    
    def _initialize_components(self) -> None:
        """Initialize system components."""
        # Add a small delay to allow other startup processes to complete
        time.sleep(self.config["startup_delay"])
        
        logger.info("Starting component initialization")
        
        # Initialize database
        if self.config["initialize_database"]:
            self._initialize_database()
        
        # Initialize cloud AI
        if self.config["initialize_cloud_ai"]:
            self._initialize_cloud_ai()
        
        # Initialize local AI
        if self.config["initialize_local_ai"]:
            self._initialize_local_ai()
        
        # Complete initialization
        self.initialized = True
        logger.info("Auto-wake initialization complete")
        
        # Log availability status
        logger.info(f"Cloud AI available: {self.cloud_ai_available}")
        logger.info(f"Local AI available: {self.local_ai_available}")
        logger.info(f"Database available: {self.database_available}")
    
    def _initialize_database(self) -> None:
        """Initialize database connection."""
        try:
            logger.info("Initializing database connection")
            
            # Import database module
            from ..database import init_db, create_tables
            
            # Initialize database
            if init_db():
                # Create tables
                if create_tables():
                    self.database_available = True
                    logger.info("Database initialization successful")
                else:
                    logger.warning("Failed to create database tables")
            else:
                logger.warning("Failed to initialize database connection")
        
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def _initialize_cloud_ai(self) -> None:
        """Initialize cloud AI providers."""
        try:
            logger.info("Initializing cloud AI providers")
            
            # Try to import AI proxy
            try:
                from ..ai.proxy import AIProxy
                
                # Initialize AI proxy
                ai_proxy = AIProxy(mode="cloud")
            except ImportError:
                # AI proxy not available yet
                logger.warning("AI proxy module not available")
                return
            
            # Check if cloud AI is available
            if ai_proxy.is_cloud_available():
                self.cloud_ai_available = True
                logger.info("Cloud AI initialization successful")
            else:
                logger.warning("Cloud AI providers not available")
                
                # Check if API keys are missing
                self._check_api_keys()
        
        except Exception as e:
            logger.error(f"Error initializing cloud AI: {e}")
    
    def _initialize_local_ai(self) -> None:
        """Initialize local AI models."""
        try:
            logger.info("Initializing local AI models")
            
            # Import local AI manager
            from ..llm.local_ai import LocalAIManager
            
            # Initialize local AI manager
            local_ai = LocalAIManager()
            
            # Check if local AI is available
            if local_ai.is_available():
                self.local_ai_available = True
                logger.info("Local AI initialization successful")
                
                # Preload models if configured
                if self.config["preload_models"]:
                    self._preload_models(local_ai)
            else:
                logger.warning("Local AI not available - no models found")
                
                # Try to download a fallback model
                self._download_fallback_model(local_ai)
        
        except ImportError:
            logger.warning("Local AI modules not installed")
        
        except Exception as e:
            logger.error(f"Error initializing local AI: {e}")
    
    def _check_api_keys(self) -> None:
        """Check if API keys are missing and log warnings."""
        api_keys = {
            "OPENAI_API_KEY": "OpenAI",
            "ANTHROPIC_API_KEY": "Anthropic",
            "DEEPSEEK_API_KEY": "DeepSeek"
        }
        
        missing_keys = []
        for key, provider in api_keys.items():
            if not os.environ.get(key):
                missing_keys.append(f"{provider} ({key})")
        
        if missing_keys:
            logger.warning(f"Missing API keys for: {', '.join(missing_keys)}")
            logger.warning("Set API keys in environment or .env file for cloud AI capabilities")
    
    def _preload_models(self, local_ai: Any) -> None:
        """
        Preload local AI models to speed up first inference.
        
        Args:
            local_ai: Local AI manager instance
        """
        try:
            # Get available models
            available_models = local_ai.list_available_models()
            
            if not available_models:
                logger.warning("No local models available for preloading")
                return
            
            # Try to preload at least one model per provider
            for provider, models in available_models.items():
                if models:
                    model_name = models[0]  # Use first available model
                    logger.info(f"Preloading {provider} model: {model_name}")
                    
                    # Preload by generating a simple completion
                    local_ai.get_completion(
                        "Hello, world!",
                        provider=provider,
                        model=model_name,
                        max_tokens=10
                    )
        
        except Exception as e:
            logger.error(f"Error preloading models: {e}")
    
    def _download_fallback_model(self, local_ai: Any) -> None:
        """
        Download a fallback model if no models are available.
        
        Args:
            local_ai: Local AI manager instance
        """
        try:
            # Check if any provider is enabled but has no models
            providers = local_ai.config["providers"]
            for provider_name, provider in providers.items():
                if provider["enabled"] and not provider["models"]:
                    # Try to download a small model for this provider
                    if provider_name == "llama.cpp":
                        logger.info("Downloading fallback llama.cpp model")
                        local_ai.download_model("llama.cpp", "llama2-7b")
                        break
                    elif provider_name == "gpt4all":
                        logger.info("Downloading fallback GPT4All model")
                        local_ai.download_model("gpt4all", "ggml-gpt4all-j-v1.3-groovy")
                        break
        
        except Exception as e:
            logger.error(f"Error downloading fallback model: {e}")
    
    def get_status(self) -> Dict[str, bool]:
        """
        Get the current status of the auto-wake system.
        
        Returns:
            Dictionary with status information
        """
        return {
            "initialized": self.initialized,
            "initializing": self.initialization_thread is not None and self.initialization_thread.is_alive(),
            "cloud_ai_available": self.cloud_ai_available,
            "local_ai_available": self.local_ai_available,
            "database_available": self.database_available
        }


# Initialize auto-wake manager on module import
auto_wake_manager = AutoWakeManager()

def initialize_on_import():
    """Initialize the auto-wake system when imported."""
    auto_wake_manager.activate()

# Call initialization function
initialize_on_import()