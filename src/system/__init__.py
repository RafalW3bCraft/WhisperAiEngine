"""
G3r4ki System Module

This module provides core system functionality for the G3r4ki framework.
"""

# Import dependency manager first to ensure dependencies are available
from .dependencies import dependency_manager

# Import auto-wake system for automatic initialization
from .auto_wake import auto_wake_manager

def check_system_requirements():
    """
    Check if the system meets requirements for running G3r4ki.
    
    Returns:
        True if requirements are met, False otherwise
    """
    # Check core dependencies
    core_deps = dependency_manager.check_dependencies("core")
    missing_deps = [dep for dep, installed in core_deps.items() if not installed]
    
    if missing_deps:
        # Try to install missing dependencies
        dependency_manager.install_dependencies("core", missing_only=True)
        
        # Check again
        core_deps = dependency_manager.check_dependencies("core")
        missing_deps = [dep for dep, installed in core_deps.items() if not installed]
        
        if missing_deps:
            return False
    
    # All dependencies available
    return True

# Export public instances and functions
__all__ = ['auto_wake_manager', 'dependency_manager', 'check_system_requirements']