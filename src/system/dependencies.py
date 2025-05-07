"""
G3r4ki Dependency Management

This module provides functionality to check and install required dependencies
for the G3r4ki framework.
"""

import os
import sys
import logging
import subprocess
import importlib.util
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logger = logging.getLogger("g3r4ki.system.dependencies")

class DependencyManager:
    """Manager for checking and installing dependencies."""
    
    def __init__(self):
        """Initialize the dependency manager."""
        self.required_packages = {
            "core": [
                "sqlalchemy",
                "pyyaml",
                "requests",
                "flask",
                "flask-socketio",
                "python-dotenv",
                "psycopg2-binary"  # PostgreSQL driver
            ],
            "ai": [
                "openai",
                "anthropic",
                "transformers"
            ],
            "security": [
                "cryptography",
                "pyopenssl"
            ],
            "offline_ai": [
                "llama-cpp-python",
                "huggingface_hub"
            ],
            "offensive": [
                "paramiko",  # SSH library
                "pypsrp",    # PowerShell Remoting
                "impacket"   # Network protocols
            ]
        }
        
        self.installed_packages = self._get_installed_packages()
    
    def _get_installed_packages(self) -> List[str]:
        """
        Get list of installed Python packages.
        
        Returns:
            List of installed package names
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True
            )
            
            import json
            packages = json.loads(result.stdout)
            return [pkg["name"].lower() for pkg in packages]
        
        except Exception as e:
            logger.error(f"Error getting installed packages: {e}")
            return []
    
    def check_dependencies(self, category: Optional[str] = None) -> Dict[str, bool]:
        """
        Check if dependencies are installed.
        
        Args:
            category: Optional category to check
            
        Returns:
            Dictionary of package status (True if installed)
        """
        results = {}
        
        # Determine which packages to check
        if category and category in self.required_packages:
            packages_to_check = self.required_packages[category]
        else:
            # Check all if no category specified
            packages_to_check = []
            for pkgs in self.required_packages.values():
                packages_to_check.extend(pkgs)
        
        # Check each package
        for package in packages_to_check:
            # Normalize package name for comparison
            norm_package = package.lower().replace("-", "_")
            results[package] = any(
                norm_package == installed.lower().replace("-", "_")
                for installed in self.installed_packages
            )
        
        return results
    
    def install_dependencies(self, category: Optional[str] = None, 
                           missing_only: bool = True,
                           python_executable: Optional[str] = None) -> Dict[str, bool]:
        """
        Install dependencies.
        
        Args:
            category: Optional category to install
            missing_only: Only install missing packages if True
            python_executable: Python executable to use for pip install (default: sys.executable)
            
        Returns:
            Dictionary of installation results
        """
        if python_executable is None:
            python_executable = sys.executable

        results = {}
        
        # Determine which packages to install
        if category and category in self.required_packages:
            packages_to_install = self.required_packages[category]
        else:
            # Install all if no category specified
            packages_to_install = []
            for pkgs in self.required_packages.values():
                packages_to_install.extend(pkgs)
        
        # Filter to missing packages if requested
        if missing_only:
            dependency_status = self.check_dependencies(category)
            packages_to_install = [pkg for pkg in packages_to_install if not dependency_status.get(pkg, False)]
        
        # Install each package
        for package in packages_to_install:
            try:
                logger.info(f"Installing {package} using {python_executable}...")
                
                result = subprocess.run(
                    [python_executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode == 0:
                    logger.info(f"Successfully installed {package}")
                    results[package] = True
                else:
                    logger.error(f"Failed to install {package}: {result.stderr}")
                    results[package] = False
            
            except Exception as e:
                logger.error(f"Error installing {package}: {e}")
                results[package] = False
        
        # Update installed packages list
        self.installed_packages = self._get_installed_packages()
        
        return results
    
    def is_category_installed(self, category: str) -> bool:
        """
        Check if all packages in a category are installed.
        
        Args:
            category: Category to check
            
        Returns:
            True if all packages in the category are installed
        """
        if category not in self.required_packages:
            return False
        
        status = self.check_dependencies(category)
        return all(status.values())


# Create dependency manager instance
dependency_manager = DependencyManager()

def check_and_install_core_dependencies():
    """Check and install core dependencies on import."""
    # Avoid automatic installation if running outside virtual environment
    if not (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
        logger.warning("Not running inside a virtual environment; skipping automatic dependency installation.")
        return

    # Check if core dependencies are installed
    if not dependency_manager.is_category_installed("core"):
        logger.warning("Core dependencies missing, attempting to install...")
        dependency_manager.install_dependencies("core")
    
    # Make sure SQLAlchemy is available
    if not importlib.util.find_spec("sqlalchemy"):
        logger.warning("SQLAlchemy not found, attempting to install...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "sqlalchemy"],
                capture_output=True,
                check=False
            )
        except Exception as e:
            logger.error(f"Error installing SQLAlchemy: {e}")

# Call check function on import
check_and_install_core_dependencies()
