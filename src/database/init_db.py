#!/usr/bin/env python3
"""
G3r4ki Database Initialization Script

This script initializes the G3r4ki database and creates the necessary tables.
It can be run directly or imported as a module.
"""

import os
import sys
import logging
import argparse

# Add the parent directory to the path to allow importing database module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from database import init_db, create_tables
from database.operations import store_configuration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("g3r4ki.database.init_db")

def initialize_database(database_url: str = None):
    """
    Initialize the database and create tables.
    
    Args:
        database_url: Optional database URL override
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Initialize database connection
        if not init_db(database_url):
            logger.error("Failed to initialize database connection")
            return False
        
        # Create tables
        if not create_tables():
            logger.error("Failed to create database tables")
            return False
        
        # Initialize default configurations
        init_default_configurations()
        
        logger.info("Database initialization complete")
        return True
    
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

def init_default_configurations():
    """Initialize default configurations in the database."""
    try:
        # Offensive Framework configuration
        offensive_config = {
            "enabled_modules": [
                "rat",
                "keylogging",
                "c2",
                "credential_harvesting",
                "data_exfiltration",
                "evasion",
                "shells",
                "post_exploitation"
            ],
            "default_output_dir": "results",
            "default_c2_server": "localhost",
            "default_c2_port": 8443,
            "default_obfuscation_level": 3,
            "mission_profiles": {
                "stealth": {
                    "obfuscation_level": 5,
                    "evasion_level": 5,
                    "persistence": True,
                    "c2_interval": 300,
                    "modules": ["evasion", "rat", "c2"]
                },
                "loud": {
                    "obfuscation_level": 1,
                    "evasion_level": 1,
                    "persistence": False,
                    "c2_interval": 30,
                    "modules": ["shells", "credential_harvesting", "data_exfiltration"]
                },
                "persistence": {
                    "obfuscation_level": 4,
                    "evasion_level": 4,
                    "persistence": True,
                    "c2_interval": 180,
                    "modules": ["rat", "c2", "post_exploitation"]
                },
                "data_extraction": {
                    "obfuscation_level": 3,
                    "evasion_level": 3,
                    "persistence": True,
                    "c2_interval": 60,
                    "modules": ["credential_harvesting", "data_exfiltration", "keylogging"]
                }
            }
        }
        
        # AI configuration
        ai_config = {
            "default_mode": "auto",
            "cloud_providers": ["openai", "anthropic", "deepseek"],
            "local_providers": ["llama.cpp", "vllm", "gpt4all"],
            "default_model": {
                "openai": "gpt-4o",
                "anthropic": "claude-3-5-sonnet-20241022",
                "deepseek": "deepseek-coder",
                "llama.cpp": "llama3-8b",
                "vllm": "llama3-70b",
                "gpt4all": "gpt4all-j-v1.3-groovy"
            },
            "temperature": 0.7,
            "max_tokens": 4096,
            "fallback_order": ["openai", "anthropic", "deepseek", "llama.cpp", "vllm", "gpt4all"]
        }
        
        # Store configurations
        store_configuration("offensive", "app", offensive_config)
        store_configuration("ai", "app", ai_config)
        
        logger.info("Default configurations initialized")
        return True
    
    except Exception as e:
        logger.error(f"Error initializing default configurations: {e}")
        return False

def main():
    """Main function for direct script execution."""
    parser = argparse.ArgumentParser(description="G3r4ki Database Initialization")
    parser.add_argument("--db-url", help="Database URL override")
    args = parser.parse_args()
    
    if initialize_database(args.db_url):
        logger.info("Database initialization successful")
        return 0
    else:
        logger.error("Database initialization failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())