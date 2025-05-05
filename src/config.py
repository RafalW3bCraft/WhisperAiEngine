#!/usr/bin/env python3
# G3r4ki configuration management

import os
import yaml
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('g3r4ki.config')

# Check if running in Replit
IS_REPLIT = 'REPL_ID' in os.environ

# Default configuration paths
if IS_REPLIT:
    # Replit paths - keep data in the project directory for persistence
    CONFIG_DIR = os.path.join(os.getcwd(), '.config/g3r4ki')
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")
    MODELS_DIR = os.path.join(os.getcwd(), '.local/share/g3r4ki/models')
    TEMP_DIR = os.path.join(os.getcwd(), '.cache/g3r4ki')
else:
    # Standard paths for normal installations
    CONFIG_DIR = os.path.expanduser("~/.config/g3r4ki")
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")
    MODELS_DIR = os.path.expanduser("~/.local/share/g3r4ki/models")
    TEMP_DIR = os.path.expanduser("~/.cache/g3r4ki")

def setup_config():
    """
    Create default configuration if it doesn't exist
    Returns the loaded config
    """
    # Create directories if they don't exist
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(os.path.join(MODELS_DIR, "llama"), exist_ok=True)
    os.makedirs(os.path.join(MODELS_DIR, "vllm"), exist_ok=True)
    os.makedirs(os.path.join(MODELS_DIR, "gpt4all"), exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Base directory for local AI components under current working directory
    PWD = os.getcwd()
    
    # Default configuration with paths based on environment
    if IS_REPLIT:
        # Replit-specific paths
        llm_paths = {
            "models_dir": MODELS_DIR,
            "temp_dir": TEMP_DIR,
            "llama_cpp_dir": os.path.join(PWD, 'vendor/llama.cpp'),
            "vllm_dir": os.path.join(PWD, 'vendor/vllm'),
            "gpt4all_dir": os.path.join(PWD, 'vendor/gpt4all'),
            "whisper_dir": os.path.join(PWD, 'vendor/whisper.cpp'),
            "piper_dir": os.path.join(PWD, 'vendor/piper'),
        }
    else:
        # Standard paths for normal installations, updated to PWD/vendor
        llm_paths = {
            "models_dir": MODELS_DIR,
            "temp_dir": TEMP_DIR,
            "llama_cpp_dir": os.path.join(PWD, 'vendor/llama.cpp'),
            "vllm_dir": os.path.join(PWD, 'vendor/vllm'),
            "gpt4all_dir": os.path.join(PWD, 'vendor/gpt4all'),
            "whisper_dir": os.path.join(PWD, 'vendor/whisper.cpp'),
            "piper_dir": os.path.join(PWD, 'vendor/piper'),
        }
    
    # Create the complete default config with updated default model filenames
    default_config = {
        "paths": llm_paths,
        "llm": {
            "default_engine": "llama.cpp",
            "default_model": {
                "llama.cpp": "tinyllama-1.1b-chat-v1.0.Q4_0.gguf",
                "vllm": "facebook/opt-1.3b",
                "gpt4all": "ggml-gpt4all-j-v1.3-groovy.bin"
            },
            "context_length": 2048,
            "use_gpu": True
        },
        "voice": {
            "whisper_model": "tiny.en",
            "piper_model": "en_US-amy-low",
            "audio_input_device": "default",
            "audio_output_device": "default",
            "voice_commands": {
                "enabled": True,
                "auto_start": False,
                "speak_responses": True,
                "listen_timeout": 5,
                "confidence_threshold": 0.6
            }
        },
        "nlp": {
            "enabled": True,
            "use_ai": True,
            "default_provider": "openai",
            "default_models": {
                "openai": "gpt-4o",
                "anthropic": "claude-3-5-sonnet-20241022",
                "deepseek": "deepseek-chat"
            },
            "confidence_threshold": 0.6,
            "max_history": 100,
            "log_commands": True
        },
        "security": {
            "nmap_args": "-sS -sV -p-",
            "max_recon_depth": 2,
            "vuln_scan_timeout": 300
        },
        "visualization": {
            "enabled": True,
            "host": "0.0.0.0",
            "port": 5000,
            "auto_start": False,
            "data_retention_days": 30,
            "results_dir": "results"
        },
        "debug": False
    }
    
    # Check if config file exists
    if not os.path.exists(CONFIG_FILE):
        logger.info(f"Creating default configuration at {CONFIG_FILE}")
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
    
    # Load and return config
    return load_config()

def load_config(config_file=None):
    """Load configuration from file"""
    if not config_file:
        config_file = CONFIG_FILE
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        logger.debug(f"Loaded configuration from {config_file}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        logger.info("Loading default configuration")
        return setup_config()

def save_config(config, config_file=None):
    """Save configuration to file"""
    if not config_file:
        config_file = CONFIG_FILE
    
    try:
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        logger.debug(f"Saved configuration to {config_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return False

def get_model_path(engine, model_name=None, config=None):
    """Get the path to a model file based on engine"""
    if not config:
        config = load_config()
    
    if not model_name:
        model_name = config['llm']['default_model'][engine]
    
    models_dir = config['paths']['models_dir']
    
    if engine == "llama.cpp":
        return os.path.join(models_dir, "llama", model_name)
    elif engine == "vllm":
        # vLLM can use HF model IDs directly
        if "/" in model_name:
            return model_name
        return os.path.join(models_dir, "vllm", model_name)
    elif engine == "gpt4all":
        return os.path.join(models_dir, "gpt4all", model_name)
    else:
        raise ValueError(f"Unknown engine: {engine}")
