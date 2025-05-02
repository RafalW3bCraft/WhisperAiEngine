"""
G3r4ki Offensive Framework - Shells Module

This module provides utilities for generating and managing various types of shells for
penetration testing and offensive security operations.
"""

from typing import Dict, List, Any, Optional
from src.offensive.modules.shells.reverse_shell_generator import ReverseShellGenerator

__all__ = [
    'ReverseShellGenerator',
    'get_shell_generator'
]

def get_shell_generator(options: Optional[Dict[str, Any]] = None) -> ReverseShellGenerator:
    """
    Get a shell generator instance
    
    Args:
        options: Optional configuration options
        
    Returns:
        Configured shell generator instance
    """
    return ReverseShellGenerator(options)