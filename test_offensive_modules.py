#!/usr/bin/env python3
"""
Test script for G3r4ki's new offensive modules and elite framework
"""

import os
import sys
import logging
import argparse
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('g3r4ki.offensive')

def test_shell_generator(args):
    """Test the reverse shell generator"""
    from src.offensive.modules.shells.reverse_shell_generator import ReverseShellGenerator
    
    print("=" * 80)
    print("G3r4ki Offensive Framework - Reverse Shell Generator Test")
    print("=" * 80)
    
    # Initialize generator
    generator = ReverseShellGenerator({
        'obfuscate': args.obfuscate,
        'encode': args.encode,
        'platform_optimized': True
    })
    
    # List available shell types
    available_shells = generator.list_available_shells()
    print(f"\nAvailable shell types: {len(available_shells)}")
    for shell in available_shells:
        print(f"- {shell['type']}: {shell['description']}")
        
    # Generate shells
    if args.shell_type:
        shell_types = [args.shell_type]
    else:
        # Default to testing all shell types
        shell_types = [shell['type'] for shell in available_shells]
        
    host = args.host or '10.10.10.10'
    port = args.port or 4444
    platform = args.platform or 'linux'
    
    print(f"\nGenerating shells for host={host}, port={port}, platform={platform}")
    print(f"Options: obfuscate={args.obfuscate}, encode={args.encode}\n")
    
    for shell_type in shell_types:
        try:
            print(f"\n{'=' * 40}")
            print(f"Generating {shell_type} shell...")
            print(f"{'=' * 40}")
            
            shell = generator.generate_shell(shell_type, host, port, platform)
            print(shell)
            
            # Save to file if requested
            if args.output:
                output_dir = args.output
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    
                # Determine file extension
                if shell_type in ['bash', 'sh']:
                    ext = '.sh'
                elif shell_type in ['python', 'python3']:
                    ext = '.py'
                elif shell_type in ['powershell', 'pwsh']:
                    ext = '.ps1'
                elif shell_type == 'php':
                    ext = '.php'
                elif shell_type == 'perl':
                    ext = '.pl'
                elif shell_type == 'ruby':
                    ext = '.rb'
                elif shell_type == 'java':
                    ext = '.java'
                elif shell_type == 'jsp':
                    ext = '.jsp'
                elif shell_type == 'aspx':
                    ext = '.aspx'
                elif shell_type == 'golang':
                    ext = '.go'
                elif shell_type == 'nodejs':
                    ext = '.js'
                else:
                    ext = '.txt'
                    
                # Save to file
                filename = f"{shell_type}_shell{ext}"
                output_path = os.path.join(output_dir, filename)
                
                with open(output_path, 'w') as f:
                    f.write(shell)
                    
                print(f"Saved to {output_path}")
                
        except Exception as e:
            print(f"Error generating {shell_type} shell: {e}")
            
def test_module_loader(args):
    """Test the module loader system"""
    from src.offensive.module_loader import ModuleLoader
    
    print("=" * 80)
    print("G3r4ki Offensive Framework - Module Loader Test")
    print("=" * 80)
    
    # Initialize module loader
    loader = ModuleLoader()
    
    # Show available modules
    available_modules = loader.get_available_modules()
    print(f"\nAvailable modules: {len(available_modules)}")
    for module_id, metadata in available_modules.items():
        print(f"- {module_id}: {metadata.name} (v{metadata.version})")
        print(f"  Description: {metadata.description}")
        print(f"  Author: {metadata.author}")
        print(f"  Tags: {', '.join(metadata.tags)}")
        print(f"  Platforms: {', '.join(metadata.platforms)}")
        print(f"  Stealth level: {metadata.stealth_level}/10")
        print(f"  Effectiveness: {metadata.effectiveness}/10")
        print(f"  Supported missions: {', '.join(metadata.supported_mission_types)}")
        print()
        
    # If a specific module ID is specified, try to load and execute it
    if args.module_id:
        try:
            print(f"\nLoading module: {args.module_id}")
            module = loader.load_module(args.module_id)
            
            if hasattr(module, 'execute'):
                # Create context for module execution
                context = {
                    'target': args.target or 'localhost',
                    'options': {
                        # Generic options
                        'port': args.port or 4444,
                        'host': args.host or '10.10.10.10',
                        'platform': args.platform or 'linux',
                        'obfuscate': args.obfuscate,
                        'encode': args.encode,
                        
                        # Shell generator specific options
                        'shell_types': ['bash', 'python', 'powershell'],
                        
                        # Browser credential harvester specific options
                        'browsers': ['chrome', 'firefox', 'edge', 'brave'],
                    }
                }
                
                print(f"Executing module with context: {context}")
                results = module.execute(context)
                
                print("\nExecution results:")
                print(f"Status: {results.get('status', 'unknown')}")
                print(f"Message: {results.get('message', 'No message')}")
                
                # Print additional results depending on module type
                if args.module_id.endswith('reverse_shell_generator'):
                    if 'shells' in results:
                        print("\nGenerated shells:")
                        for shell_type, shell in results['shells'].items():
                            print(f"\n--- {shell_type} ---")
                            print(shell[:500] + "..." if len(shell) > 500 else shell)
                
                if args.module_id.endswith('browser_credentials'):
                    if 'data' in results:
                        print("\nHarvested credentials:")
                        for browser, browser_data in results['data'].items():
                            print(f"\n--- {browser} ---")
                            for data_type, items in browser_data.items():
                                print(f"  {data_type}: {len(items)} items")
                                if items and args.verbose:
                                    for i, item in enumerate(items[:5]):  # Show only first 5
                                        print(f"    {i+1}. {item}")
                                    if len(items) > 5:
                                        print(f"    ... and {len(items)-5} more")
                
            else:
                print(f"Module {args.module_id} has no execute function")
                
        except Exception as e:
            print(f"Error loading or executing module {args.module_id}: {e}")
            
def test_mission_chain(args):
    """Test creating a mission-based module chain"""
    from src.offensive.module_loader import ModuleLoader
    from src.offensive import MISSION_PROFILES
    
    print("=" * 80)
    print("G3r4ki Offensive Framework - Mission Chain Test")
    print("=" * 80)
    
    # Initialize module loader
    loader = ModuleLoader()
    
    # Show available mission profiles
    print("\nAvailable mission profiles:")
    for mission_type, profile in MISSION_PROFILES.items():
        print(f"- {mission_type}: {profile['description']}")
        print(f"  Priority modules: {', '.join(profile['priority_modules'])}")
        print(f"  Avoided modules: {', '.join(profile['avoid_modules'])}")
        print()
        
    # If a specific mission type is specified, create and show its module chain
    mission_type = args.mission_type or 'stealth'
    target_platform = args.platform or 'linux'
    
    try:
        print(f"\nCreating module chain for {mission_type} mission on {target_platform} platform")
        
        # Define available resources
        available_resources = {
            'cpu': 2,
            'memory': 512,
            'disk': 1024
        }
        
        # Create module chain
        module_chain = loader.create_chain(mission_type, target_platform, available_resources)
        
        print(f"\nGenerated module chain ({len(module_chain)} modules):")
        for i, module_id in enumerate(module_chain):
            if module_id in loader.available_modules:
                metadata = loader.available_modules[module_id]
                print(f"{i+1}. {module_id}: {metadata.name} (Stealth: {metadata.stealth_level}/10, Effectiveness: {metadata.effectiveness}/10)")
            else:
                print(f"{i+1}. {module_id} (Not available)")
                
        # Execute the chain if requested
        if args.execute_chain:
            print("\nExecuting module chain...")
            
            # Create context for execution
            context = {
                'target': args.target or 'localhost',
                'options': {
                    'port': args.port or 4444,
                    'host': args.host or '10.10.10.10',
                    'platform': target_platform,
                    'obfuscate': args.obfuscate,
                    'encode': args.encode,
                }
            }
            
            # Execute chain
            results = loader.execute_module_chain(module_chain, args.target, context['options'])
            
            print("\nExecution results:")
            for module_id, result in results.items():
                if isinstance(result, dict) and 'status' in result:
                    print(f"- {module_id}: {result['status']} - {result.get('message', '')}")
                else:
                    print(f"- {module_id}: {result}")
                    
    except Exception as e:
        print(f"Error creating or executing mission chain: {e}")

def main():
    """Main entry point for test script"""
    parser = argparse.ArgumentParser(description='Test G3r4ki Offensive Framework modules')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Shell generator test
    shell_parser = subparsers.add_parser('shells', help='Test reverse shell generator')
    shell_parser.add_argument('--shell-type', help='Specific shell type to generate')
    shell_parser.add_argument('--host', help='Listener host address')
    shell_parser.add_argument('--port', type=int, help='Listener port')
    shell_parser.add_argument('--platform', choices=['linux', 'windows', 'macos'], help='Target platform')
    shell_parser.add_argument('--obfuscate', action='store_true', help='Enable obfuscation')
    shell_parser.add_argument('--encode', action='store_true', help='Enable encoding')
    shell_parser.add_argument('--output', help='Output directory for generated shells')
    
    # Module loader test
    module_parser = subparsers.add_parser('module', help='Test module loader')
    module_parser.add_argument('--module-id', help='Specific module ID to load and execute')
    module_parser.add_argument('--target', help='Target for module execution')
    module_parser.add_argument('--host', help='Listener host address')
    module_parser.add_argument('--port', type=int, help='Listener port')
    module_parser.add_argument('--platform', choices=['linux', 'windows', 'macos'], help='Target platform')
    module_parser.add_argument('--obfuscate', action='store_true', help='Enable obfuscation')
    module_parser.add_argument('--encode', action='store_true', help='Enable encoding')
    module_parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    
    # Mission chain test
    mission_parser = subparsers.add_parser('mission', help='Test mission-based module chain')
    mission_parser.add_argument('--mission-type', choices=['stealth', 'loud', 'persistence', 'data_extraction'], help='Mission type')
    mission_parser.add_argument('--platform', choices=['linux', 'windows', 'macos'], help='Target platform')
    mission_parser.add_argument('--target', help='Target for module execution')
    mission_parser.add_argument('--host', help='Listener host address')
    mission_parser.add_argument('--port', type=int, help='Listener port')
    mission_parser.add_argument('--obfuscate', action='store_true', help='Enable obfuscation')
    mission_parser.add_argument('--encode', action='store_true', help='Enable encoding')
    mission_parser.add_argument('--execute-chain', action='store_true', help='Execute the generated module chain')
    
    args = parser.parse_args()
    
    if args.command == 'shells':
        test_shell_generator(args)
    elif args.command == 'module':
        test_module_loader(args)
    elif args.command == 'mission':
        test_mission_chain(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()