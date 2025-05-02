#!/usr/bin/env python3
# Simple script to display available commands in G3r4ki

import os
import sys
import subprocess
from time import sleep

# Run g3r4ki help command
print("Running 'help' command in G3r4ki interactive mode...")
p = subprocess.Popen(["python", "g3r4ki.py", "interactive"], 
                     stdin=subprocess.PIPE, 
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE, 
                     text=True)

# Wait a moment for the CLI to initialize
sleep(1)

# Send help command and wait for response
stdout, stderr = p.communicate(input="help\n")

# Print output
print("\nAvailable commands:")
print("=" * 50)
print(stdout)

# Check if visualize command exists
if "visualize" in stdout:
    print("\nVisualization command is available!")
else:
    print("\nVisualization command is NOT found in the available commands.")
    
print("\nDone.")