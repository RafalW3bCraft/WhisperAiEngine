#!/usr/bin/env python3
# Test if the help command includes the visualize command

import cmd
import re
import sys

# Import the CLI class directly to examine its commands
sys.path.append('.')
from src.cli import G3r4kiCLI

# Get an instance of the CLI
try:
    cli = G3r4kiCLI()
    
    # Get all command method names
    methods = [method for method in dir(cli) if method.startswith('do_')]
    
    # Print all command methods
    print("Commands defined in G3r4kiCLI:")
    for method in sorted(methods):
        command_name = method[3:]  # Remove 'do_' prefix
        doc = getattr(cli, method).__doc__ or 'No documentation'
        # Get first line of docstring
        doc_first_line = doc.strip().split('\n')[0]
        print(f"  - {command_name}: {doc_first_line}")
    
    # Check if visualize command exists
    if 'do_visualize' in methods:
        print("\nVisualize command IS defined!")
        vis_doc = cli.do_visualize.__doc__
        print(f"Documentation: {vis_doc}")
    else:
        print("\nVisualize command is NOT defined!")
    
except Exception as e:
    print(f"Error: {e}")