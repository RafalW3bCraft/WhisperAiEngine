#!/usr/bin/env python3
# Test script for the AI Proxy system

import os
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Ensure we're in the project directory
project_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_dir)

from src.config import setup_config
from src.ai.ai_proxy import init_ai_proxy

def main():
    """Test the AI Proxy system"""
    # Initialize configuration
    config = setup_config()
    
    # Initialize AI Proxy
    ai_proxy = init_ai_proxy(config)
    
    # Get available providers
    providers = ai_proxy.get_available_providers()
    
    print("\nAvailable AI Providers:")
    
    # Group by type
    cloud_providers = [p for p in providers if p['type'] == 'cloud']
    local_providers = [p for p in providers if p['type'] == 'local']
    
    if cloud_providers:
        print("\nCloud Providers:")
        for provider in cloud_providers:
            print(f"  - {provider['name']} (id: {provider['id']})")
    
    if local_providers:
        print("\nLocal Providers:")
        for provider in local_providers:
            model_count = provider.get('model_count', 0)
            print(f"  - {provider['name']} (id: {provider['id']}) - {model_count} models")
    
    # Show recommended provider
    recommended = ai_proxy.get_recommended_provider()
    if recommended:
        print(f"\nRecommended provider: {recommended['name']} ({recommended['type']})")
    
    # Test query if providers are available
    if providers:
        test_query = "What are the 5 most common cybersecurity vulnerabilities in web applications?"
        
        print("\nTesting AI query with best provider...")
        result = ai_proxy.query_best(test_query)
        
        print(f"\nResponse from {result['provider_name']} (took {result['time_taken']}s):")
        print(result['response'])

if __name__ == "__main__":
    main()