"""
G3r4ki Skill Base Module

This module defines the base Skill class and the skill registry that
tracks all available skills for agents.
"""

import inspect
import logging
import functools
from typing import Dict, List, Any, Callable, Optional, Type, Union, get_type_hints

# Setup logging
logger = logging.getLogger('g3r4ki.agents.skills')

class SkillMetadata:
    """
    Metadata for a skill
    
    Attributes:
        name: Skill name
        description: Skill description
        parameters: Parameter names and types
        return_type: Return type
        category: Skill category
        func: Function implementing the skill
    """
    
    def __init__(self, 
                 name: str, 
                 description: str, 
                 parameters: Dict[str, Type],
                 return_type: Type,
                 category: str,
                 func: Callable):
        """
        Initialize skill metadata
        
        Args:
            name: Skill name
            description: Skill description
            parameters: Parameter names and types
            return_type: Return type
            category: Skill category
            func: Function implementing the skill
        """
        self.name = name
        self.description = description
        self.parameters = parameters
        self.return_type = return_type
        self.category = category
        self.func = func
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary
        
        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                name: str(param_type) for name, param_type in self.parameters.items()
            },
            "return_type": str(self.return_type),
            "category": self.category
        }

class SkillRegistry:
    """
    Registry of all available skills
    
    This is a singleton class to track all skills registered via the @skill decorator.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SkillRegistry, cls).__new__(cls)
            cls._instance.skills = {}
        return cls._instance
    
    def register(self, 
                 func: Callable,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 category: str = "general") -> str:
        """
        Register a skill function
        
        Args:
            func: Function implementing the skill
            name: Optional name override (defaults to function name)
            description: Optional description (defaults to function docstring)
            category: Skill category
            
        Returns:
            Registered skill name
        """
        # Get function name and docstring
        skill_name = name or func.__name__
        skill_description = description or (func.__doc__ or "").strip()
        
        # Get parameter and return types
        try:
            type_hints = get_type_hints(func)
            return_type = type_hints.pop('return', Any)
            parameters = {
                param: type_hints.get(param, Any)
                for param in inspect.signature(func).parameters
                if param != 'self'  # Skip 'self' parameter for methods
            }
        except Exception as e:
            logger.warning(f"Error getting type hints for skill {skill_name}: {str(e)}")
            parameters = {}
            return_type = Any
        
        # Create metadata
        metadata = SkillMetadata(
            name=skill_name,
            description=skill_description,
            parameters=parameters,
            return_type=return_type,
            category=category,
            func=func
        )
        
        # Register skill
        self.skills[skill_name] = metadata
        logger.debug(f"Registered skill: {skill_name} in category {category}")
        
        return skill_name
    
    def get_skill(self, name: str) -> Optional[SkillMetadata]:
        """
        Get skill by name
        
        Args:
            name: Skill name
            
        Returns:
            Skill metadata or None if not found
        """
        return self.skills.get(name)
    
    def get_skills_by_category(self, category: str) -> List[SkillMetadata]:
        """
        Get skills by category
        
        Args:
            category: Skill category
            
        Returns:
            List of skill metadata
        """
        return [
            metadata for metadata in self.skills.values()
            if metadata.category == category
        ]
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """
        List all registered skills
        
        Returns:
            List of skill metadata dictionaries
        """
        return [metadata.to_dict() for metadata in self.skills.values()]
    
    def list_categories(self) -> List[str]:
        """
        List all skill categories
        
        Returns:
            List of category names
        """
        return list(set(metadata.category for metadata in self.skills.values()))

def skill(name: Optional[str] = None, 
         description: Optional[str] = None,
         category: str = "general"):
    """
    Decorator to register a function as a skill
    
    Args:
        name: Optional name override (defaults to function name)
        description: Optional description (defaults to function docstring)
        category: Skill category
        
    Returns:
        Decorated function
    """
    def decorator(func):
        # Register skill
        registry = SkillRegistry()
        registry.register(func, name, description, category)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator

class Skill:
    """
    Base class for skill collections
    
    Skills can either be implemented as decorated functions or as methods in
    a class that inherits from this base class.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize skill collection
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self._register_skills()
    
    def _register_skills(self) -> None:
        """
        Register all methods marked as skills
        
        This automatically registers all methods in the class that are decorated
        with @skill or that have the "_skill" suffix in their name.
        """
        registry = SkillRegistry()
        
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            # Skip private methods
            if name.startswith('_') and not name.endswith('_skill'):
                continue
                
            # Skip methods that are not skills
            is_explicit_skill = hasattr(method, '_is_skill')
            is_implicit_skill = name.endswith('_skill')
            
            if not (is_explicit_skill or is_implicit_skill):
                continue
                
            # Get skill metadata
            skill_name = getattr(method, '_skill_name', None) or name
            skill_description = getattr(method, '_skill_description', None) or (method.__doc__ or "").strip()
            skill_category = getattr(method, '_skill_category', "general")
            
            # Register skill
            registry.register(method, skill_name, skill_description, skill_category)