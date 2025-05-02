"""
G3r4ki Offensive Framework - Module Loader

This module provides the core module loading system for G3r4ki's offensive capabilities.
It dynamically loads and chains modules based on mission parameters and available resources.
"""

import os
import sys
import logging
import importlib
import importlib.util
import inspect
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass

from src.offensive import MISSION_PROFILES

logger = logging.getLogger(__name__)

# Define module metadata structure
@dataclass
class ModuleMetadata:
    """Metadata for an offensive module"""
    id: str
    name: str
    description: str
    author: str
    version: str
    dependencies: List[str]
    tags: List[str]
    platforms: List[str]
    min_resources: Dict[str, int]  # cpu, memory, disk, etc.
    stealth_level: int  # 1-10, 10 being most stealthy
    effectiveness: int  # 1-10, 10 being most effective
    complexity: int  # 1-10, 10 being most complex
    supported_mission_types: List[str]

class ModuleLoader:
    """
    Dynamic module loader for G3r4ki offensive capabilities
    
    This class handles the discovery, validation, loading, and chaining of 
    offensive modules based on mission parameters and system resources.
    """
    
    def __init__(self, module_dir: Optional[str] = None):
        """
        Initialize the module loader
        
        Args:
            module_dir: Optional directory to look for modules
        """
        # Default module paths
        self.module_paths = [
            os.path.join(os.path.dirname(__file__), 'modules')
        ]
        
        # Add custom module path if provided
        if module_dir and os.path.exists(module_dir):
            self.module_paths.append(module_dir)
            
        # Module registry
        self.available_modules: Dict[str, ModuleMetadata] = {}
        self.loaded_modules: Dict[str, Any] = {}
        
        # Scan for available modules
        self._scan_modules()
    
    def _scan_modules(self) -> None:
        """Scan for available modules in module paths"""
        for module_path in self.module_paths:
            if not os.path.exists(module_path):
                logger.warning(f"Module path does not exist: {module_path}")
                continue
                
            logger.info(f"Scanning for modules in: {module_path}")
            
            # Walk module directories
            for root, dirs, files in os.walk(module_path):
                for filename in files:
                    if filename.endswith('.py') and not filename.startswith('_'):
                        module_file = os.path.join(root, filename)
                        module_id = self._get_module_id(module_file, module_path)
                        
                        try:
                            # Try to load module metadata
                            metadata = self._load_module_metadata(module_id, module_file)
                            if metadata:
                                self.available_modules[module_id] = metadata
                                logger.debug(f"Found module: {module_id} - {metadata.name}")
                        except Exception as e:
                            logger.warning(f"Failed to load module metadata for {module_id}: {e}")
    
    def _get_module_id(self, module_file: str, base_path: str) -> str:
        """
        Generate a module ID from file path
        
        Args:
            module_file: Path to module file
            base_path: Base module path
            
        Returns:
            Module ID string
        """
        rel_path = os.path.relpath(module_file, base_path)
        module_id = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
        return module_id
    
    def _load_module_metadata(self, module_id: str, module_file: str) -> Optional[ModuleMetadata]:
        """
        Load module metadata from file
        
        Args:
            module_id: Module identifier
            module_file: Path to module file
            
        Returns:
            Module metadata or None if invalid
        """
        try:
            # Convert file path to module path
            module_path = module_id.replace('/', '.').replace('\\', '.')
            
            # Load module
            spec = importlib.util.spec_from_file_location(module_path, module_file)
            if not spec or not spec.loader:
                return None
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Extract metadata
            if hasattr(module, 'METADATA'):
                metadata_dict = module.METADATA
                
                # Validate required fields
                required_fields = ['name', 'description', 'author', 'version']
                for field in required_fields:
                    if field not in metadata_dict:
                        logger.warning(f"Module {module_id} missing required metadata field: {field}")
                        return None
                
                # Create metadata object with defaults for optional fields
                return ModuleMetadata(
                    id=module_id,
                    name=metadata_dict['name'],
                    description=metadata_dict['description'],
                    author=metadata_dict['author'],
                    version=metadata_dict['version'],
                    dependencies=metadata_dict.get('dependencies', []),
                    tags=metadata_dict.get('tags', []),
                    platforms=metadata_dict.get('platforms', ['linux', 'windows', 'macos']),
                    min_resources=metadata_dict.get('min_resources', {'cpu': 1, 'memory': 64}),
                    stealth_level=metadata_dict.get('stealth_level', 5),
                    effectiveness=metadata_dict.get('effectiveness', 5),
                    complexity=metadata_dict.get('complexity', 5),
                    supported_mission_types=metadata_dict.get('supported_mission_types', ['stealth', 'loud', 'persistence', 'data_extraction'])
                )
                
            return None
            
        except Exception as e:
            logger.error(f"Error loading module metadata for {module_id}: {e}")
            return None
    
    def get_available_modules(self, mission_type: Optional[str] = None, platform: Optional[str] = None) -> Dict[str, ModuleMetadata]:
        """
        Get available modules with optional filtering
        
        Args:
            mission_type: Optional mission type to filter by
            platform: Optional platform to filter by
            
        Returns:
            Dict of module ID to metadata
        """
        if not mission_type and not platform:
            return self.available_modules.copy()
            
        filtered_modules = {}
        
        for module_id, metadata in self.available_modules.items():
            # Filter by mission type
            if mission_type and mission_type not in metadata.supported_mission_types:
                continue
                
            # Filter by platform
            if platform and platform not in metadata.platforms:
                continue
                
            filtered_modules[module_id] = metadata
            
        return filtered_modules
    
    def load_module(self, module_id: str) -> Any:
        """
        Load a module by ID
        
        Args:
            module_id: Module identifier
            
        Returns:
            Loaded module or None if not found
            
        Raises:
            ValueError: If module is not available or has dependency issues
        """
        # Check if already loaded
        if module_id in self.loaded_modules:
            return self.loaded_modules[module_id]
            
        # Check if module exists
        if module_id not in self.available_modules:
            raise ValueError(f"Module not found: {module_id}")
            
        metadata = self.available_modules[module_id]
        
        # Check dependencies
        for dep_id in metadata.dependencies:
            if dep_id not in self.loaded_modules:
                # Try to load dependency
                self.load_module(dep_id)
        
        # Load the module
        try:
            # Find module file
            module_file = None
            module_rel_path = module_id.replace('.', os.path.sep) + '.py'
            
            for base_path in self.module_paths:
                test_path = os.path.join(base_path, module_rel_path)
                if os.path.exists(test_path):
                    module_file = test_path
                    break
            
            if not module_file:
                raise ValueError(f"Module file not found for {module_id}")
                
            # Import module
            spec = importlib.util.spec_from_file_location(module_id, module_file)
            if not spec or not spec.loader:
                raise ValueError(f"Failed to create module spec for {module_id}")
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Cache loaded module
            self.loaded_modules[module_id] = module
            
            logger.info(f"Loaded module: {module_id}")
            return module
            
        except Exception as e:
            logger.error(f"Failed to load module {module_id}: {e}")
            raise ValueError(f"Failed to load module {module_id}: {e}")
    
    def create_chain(self, mission_type: str, target_platform: str, available_resources: Dict[str, int]) -> List[str]:
        """
        Create a module chain based on mission parameters
        
        Args:
            mission_type: Mission type ('stealth', 'loud', 'persistence', 'data_extraction')
            target_platform: Target platform ('linux', 'windows', 'macos')
            available_resources: Dict of available resources (cpu, memory, etc.)
            
        Returns:
            List of module IDs in execution order
        """
        if mission_type not in MISSION_PROFILES:
            raise ValueError(f"Unknown mission type: {mission_type}")
            
        mission_profile = MISSION_PROFILES[mission_type]
        
        # Get modules compatible with mission and platform
        available_modules = self.get_available_modules(mission_type, target_platform)
        
        # Start with priority modules for this mission type
        module_chain = []
        
        # Add priority modules if they exist and meet resource requirements
        for priority_module in mission_profile['priority_modules']:
            matching_modules = [
                module_id for module_id, metadata in available_modules.items()
                if any(tag == priority_module for tag in metadata.tags)
            ]
            
            if matching_modules:
                # Sort by effectiveness
                matching_modules.sort(
                    key=lambda m: available_modules[m].effectiveness, 
                    reverse=True
                )
                
                # Add first matching module that meets resource requirements
                for module_id in matching_modules:
                    metadata = available_modules[module_id]
                    
                    # Check resource requirements
                    meets_requirements = True
                    for resource, required in metadata.min_resources.items():
                        if resource in available_resources and available_resources[resource] < required:
                            meets_requirements = False
                            break
                    
                    if meets_requirements:
                        module_chain.append(module_id)
                        break
        
        # Check for dependencies and add them
        dependencies = set()
        for module_id in module_chain:
            dependencies.update(self._get_all_dependencies(module_id))
            
        # Add dependencies at the beginning of the chain
        for dep in dependencies:
            if dep not in module_chain:
                module_chain.insert(0, dep)
        
        # Filter out avoided modules
        avoid_modules = set(mission_profile.get('avoid_modules', []))
        module_chain = [
            module_id for module_id in module_chain
            if not any(tag in avoid_modules for tag in available_modules[module_id].tags)
        ]
        
        return module_chain
    
    def _get_all_dependencies(self, module_id: str, visited: Optional[Set[str]] = None) -> Set[str]:
        """
        Get all dependencies for a module recursively
        
        Args:
            module_id: Module identifier
            visited: Set of already visited modules
            
        Returns:
            Set of dependency module IDs
        """
        if visited is None:
            visited = set()
            
        if module_id in visited:
            return set()
            
        visited.add(module_id)
        
        if module_id not in self.available_modules:
            return set()
            
        metadata = self.available_modules[module_id]
        dependencies = set(metadata.dependencies)
        
        # Recursively get dependencies of dependencies
        for dep in list(dependencies):
            dependencies.update(self._get_all_dependencies(dep, visited))
            
        return dependencies
    
    def execute_module_chain(self, module_chain: List[str], target: Any, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a chain of modules
        
        Args:
            module_chain: List of module IDs to execute
            target: Target object to pass to modules
            options: Dict of options to pass to modules
            
        Returns:
            Dict containing results of execution
        """
        results = {}
        context = {
            'target': target,
            'options': options,
            'results': {},
        }
        
        for module_id in module_chain:
            try:
                module = self.load_module(module_id)
                
                # Check if module has the required entry point
                if not hasattr(module, 'execute'):
                    logger.warning(f"Module {module_id} has no execute function, skipping")
                    continue
                    
                # Execute module
                logger.info(f"Executing module: {module_id}")
                module_result = module.execute(context)
                
                # Store results
                results[module_id] = module_result
                context['results'][module_id] = module_result
                
            except Exception as e:
                logger.error(f"Error executing module {module_id}: {e}")
                results[module_id] = {'error': str(e)}
                
        return results