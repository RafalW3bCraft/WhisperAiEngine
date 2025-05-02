"""
G3r4ki Offensive Framework - Modules

This package contains all offensive modules used by the G3r4ki Offensive Framework
for advanced penetration testing and red team operations.
"""

from typing import Dict, List, Any, Optional, Type
import os
import logging
import importlib
import inspect

logger = logging.getLogger(__name__)

# Module categories
MODULE_CATEGORIES = [
    'credential_harvesting',
    'session_management',
    'post_exploitation',
    'persistence',
    'evasion',
    'remote_execution',
    'data_exfiltration',
    'rat_deployment',
    'surveillance',
    'command_control',
    'exploit_execution',
    'lateral_movement',
    'shells'
]

def list_module_categories() -> List[str]:
    """
    List all available module categories
    
    Returns:
        List of module category names
    """
    return MODULE_CATEGORIES.copy()

def get_module_path(category: str, module_name: Optional[str] = None) -> str:
    """
    Get the file system path to a module or category
    
    Args:
        category: Module category
        module_name: Optional module name
        
    Returns:
        File system path
    """
    base_path = os.path.dirname(__file__)
    
    if category not in MODULE_CATEGORIES:
        raise ValueError(f"Unknown module category: {category}")
        
    category_path = os.path.join(base_path, category)
    
    if module_name:
        return os.path.join(category_path, f"{module_name}.py")
    else:
        return category_path

def load_module(category: str, module_name: str) -> Any:
    """
    Load a module by category and name
    
    Args:
        category: Module category
        module_name: Module name
        
    Returns:
        Loaded module
        
    Raises:
        ValueError: If module cannot be loaded
    """
    if category not in MODULE_CATEGORIES:
        raise ValueError(f"Unknown module category: {category}")
        
    # Construct import path
    module_path = f"src.offensive.modules.{category}.{module_name}"
    
    try:
        # Import module
        module = importlib.import_module(module_path)
        return module
    except Exception as e:
        logger.error(f"Failed to load module {category}/{module_name}: {e}")
        raise ValueError(f"Failed to load module {category}/{module_name}: {e}")