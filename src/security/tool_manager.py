"""
G3r4ki Tool Manager

This module handles the detection, installation, and configuration of security tools.
It checks if tools are pre-installed on the Linux system and sets them up if needed.
"""

import os
import sys
import logging
import subprocess
import shutil
import platform
import tempfile
import json
import requests
import tarfile
import zipfile
from pathlib import Path

# Setup logging
logger = logging.getLogger('g3r4ki.security.tool_manager')

class ToolManager:
    """
    Manager for security tools installation and configuration
    """
    
    # Tool categories and their components
    TOOL_CATEGORIES = {
        "recon": ["nmap", "amass", "subfinder", "whatweb", "ffuf", "masscan", "dnsrecon", "aquatone"],
        "remote_access": ["ssh", "paramiko"],
        "defensive": ["ufw", "suricata", "fail2ban"],
        "automation": ["make", "cmake", "ansible"],
        "offensive": ["metasploit", "sliver"],
        "data_analysis": ["pandas", "polars"],
        "linux_admin": ["systemd", "cron"],
        "threat_intel": ["misp-client", "threatfox"],
        "red_team": ["impacket", "bloodhound", "kerbrute"]
    }
    
    # Package names for different distributions
    PACKAGE_NAMES = {
        "debian": {  # For Debian/Ubuntu/Kali
            "nmap": "nmap",
            "amass": "amass",
            "subfinder": None,  # Not in standard repos
            "whatweb": "whatweb",
            "ffuf": None,  # Not in standard repos
            "masscan": "masscan",
            "dnsrecon": "dnsrecon",
            "aquatone": None,  # Not in standard repos
            "ssh": "openssh-client",
            "ufw": "ufw",
            "suricata": "suricata",
            "fail2ban": "fail2ban",
            "make": "make",
            "cmake": "cmake",
            "ansible": "ansible",
            "metasploit": "metasploit-framework",
            "cron": "cron"
        },
        "fedora": {  # For Fedora/RHEL/CentOS
            "nmap": "nmap",
            "amass": None,  # Not in standard repos
            "subfinder": None,  # Not in standard repos 
            "whatweb": None,  # Not in standard repos
            "ffuf": None,  # Not in standard repos
            "masscan": "masscan",
            "dnsrecon": None,  # Not in standard repos
            "aquatone": None,  # Not in standard repos
            "ssh": "openssh-clients",
            "ufw": "ufw",
            "suricata": "suricata",
            "fail2ban": "fail2ban",
            "make": "make",
            "cmake": "cmake",
            "ansible": "ansible",
            "metasploit": None,  # Not in standard repos
            "cron": "cronie"
        },
        "arch": {  # For Arch Linux
            "nmap": "nmap",
            "amass": "amass",
            "subfinder": None,  # Not in standard repos
            "whatweb": "whatweb",
            "ffuf": None,  # Not in standard repos
            "masscan": "masscan",
            "dnsrecon": "dnsrecon",
            "aquatone": None,  # Not in standard repos
            "ssh": "openssh",
            "ufw": "ufw",
            "suricata": "suricata",
            "fail2ban": "fail2ban",
            "make": "make",
            "cmake": "cmake",
            "ansible": "ansible",
            "metasploit": "metasploit",
            "cron": "cronie"
        }
    }
    
    # GitHub repositories for tools not in standard repos
    GITHUB_REPOS = {
        "subfinder": {
            "repo": "projectdiscovery/subfinder",
            "binary": "subfinder"
        },
        "ffuf": {
            "repo": "ffuf/ffuf",
            "binary": "ffuf"
        },
        "aquatone": {
            "repo": "michenriksen/aquatone",
            "binary": "aquatone"
        },
        "kerbrute": {
            "repo": "ropnop/kerbrute",
            "binary": "kerbrute"
        },
        "sliver": {
            "repo": "BishopFox/sliver",
            "binary": "sliver"
        }
    }
    
    # Python packages
    PYTHON_PACKAGES = {
        "impacket": "impacket",
        "bloodhound": "bloodhound",
        "pandas": "pandas",
        "polars": "polars",
        "paramiko": "paramiko"
    }
    
    def __init__(self, config):
        """
        Initialize tool manager
        
        Args:
            config: G3r4ki configuration
        """
        self.config = config
        
        # Determine Linux distribution
        self.distro = self._get_linux_distro()
        logger.info(f"Detected Linux distribution: {self.distro}")
        
        # Set tools directory
        self.tools_dir = os.path.expanduser("~/.local/share/g3r4ki/tools")
        os.makedirs(self.tools_dir, exist_ok=True)
        
        # Set bin directory for custom tool installations
        self.bin_dir = os.path.expanduser("~/.local/bin")
        os.makedirs(self.bin_dir, exist_ok=True)
        
        # Ensure bin directory is in PATH
        self._ensure_path()
    
    def _get_linux_distro(self):
        """
        Determine the Linux distribution
        
        Returns:
            String representing the distribution family
        """
        try:
            # Check for /etc/os-release
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    os_release = {}
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            os_release[key] = value.strip('"\'')
                
                # Check for specific distributions
                if 'ID' in os_release:
                    distro_id = os_release['ID'].lower()
                    
                    if distro_id in ['debian', 'ubuntu', 'kali', 'parrot']:
                        return 'debian'
                    elif distro_id in ['fedora', 'rhel', 'centos', 'rocky', 'alma']:
                        return 'fedora'
                    elif distro_id in ['arch', 'manjaro']:
                        return 'arch'
            
            # Fallback methods
            if os.path.exists('/etc/debian_version'):
                return 'debian'
            elif os.path.exists('/etc/fedora-release'):
                return 'fedora'
            elif os.path.exists('/etc/redhat-release'):
                return 'fedora'
            elif os.path.exists('/etc/arch-release'):
                return 'arch'
            
        except Exception as e:
            logger.error(f"Error determining Linux distribution: {e}")
        
        # Default to Debian if unable to determine
        logger.warning("Unable to determine Linux distribution, defaulting to Debian")
        return 'debian'
    
    def _ensure_path(self):
        """
        Ensure the local bin directory is in PATH
        """
        if self.bin_dir not in os.environ.get('PATH', '').split(':'):
            logger.info(f"Adding {self.bin_dir} to PATH")
            
            # Determine shell configuration file
            shell = os.environ.get('SHELL', '').split('/')[-1]
            if shell == 'bash':
                config_file = os.path.expanduser('~/.bashrc')
            elif shell == 'zsh':
                config_file = os.path.expanduser('~/.zshrc')
            else:
                config_file = os.path.expanduser('~/.profile')
            
            # Check if PATH is already set in config file
            try:
                with open(config_file, 'r') as f:
                    if f"PATH=\"$PATH:{self.bin_dir}\"" in f.read():
                        logger.info(f"{self.bin_dir} already in PATH configuration")
                        return
            except:
                pass
            
            # Add to PATH
            try:
                with open(config_file, 'a') as f:
                    f.write(f"\n# Added by G3r4ki Tool Manager\nexport PATH=\"$PATH:{self.bin_dir}\"\n")
                logger.info(f"Added {self.bin_dir} to {config_file}")
            except Exception as e:
                logger.error(f"Error updating PATH: {e}")
    
    def is_tool_installed(self, tool_name):
        """
        Check if a tool is installed and available
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            True if installed, False otherwise
        """
        # Check if installed via package manager
        if shutil.which(tool_name):
            logger.info(f"Tool {tool_name} found in system PATH")
            return True
        
        # Check if installed in local bin directory
        local_bin_path = os.path.join(self.bin_dir, tool_name)
        if os.path.exists(local_bin_path) and os.access(local_bin_path, os.X_OK):
            logger.info(f"Tool {tool_name} found in local bin directory")
            return True
        
        # Check Python packages for specific tools
        if tool_name in self.PYTHON_PACKAGES:
            try:
                __import__(self.PYTHON_PACKAGES[tool_name])
                logger.info(f"Python package {tool_name} is installed")
                return True
            except ImportError:
                logger.info(f"Python package {tool_name} is not installed")
        
        logger.info(f"Tool {tool_name} is not installed")
        return False
    
    def install_tool(self, tool_name, force=False):
        """
        Install a tool if not already installed
        
        Args:
            tool_name: Name of the tool
            force: Force reinstallation even if already installed
            
        Returns:
            True if installed successfully, False otherwise
        """
        if self.is_tool_installed(tool_name) and not force:
            logger.info(f"Tool {tool_name} is already installed")
            return True
        
        logger.info(f"Installing tool: {tool_name}")
        
        # Check if tool is a Python package
        if tool_name in self.PYTHON_PACKAGES:
            return self._install_python_package(self.PYTHON_PACKAGES[tool_name])
        
        # Check if tool is in package manager
        if self.distro in self.PACKAGE_NAMES:
            package_name = self.PACKAGE_NAMES[self.distro].get(tool_name)
            if package_name:
                return self._install_package(package_name)
        
        # Check if tool has a GitHub repo
        if tool_name in self.GITHUB_REPOS:
            return self._install_from_github(tool_name)
        
        logger.error(f"No installation method found for {tool_name}")
        return False
    
    def _install_package(self, package_name):
        """
        Install a package using the system package manager
        
        Args:
            package_name: Name of the package
            
        Returns:
            True if installed successfully, False otherwise
        """
        logger.info(f"Installing package {package_name} using system package manager")
        
        try:
            if self.distro == 'debian':
                # Check if root/sudo
                if os.geteuid() == 0:
                    cmd = ['apt-get', 'install', '-y', package_name]
                else:
                    cmd = ['sudo', 'apt-get', 'install', '-y', package_name]
            elif self.distro == 'fedora':
                if os.geteuid() == 0:
                    cmd = ['dnf', 'install', '-y', package_name]
                else:
                    cmd = ['sudo', 'dnf', 'install', '-y', package_name]
            elif self.distro == 'arch':
                if os.geteuid() == 0:
                    cmd = ['pacman', '-S', '--noconfirm', package_name]
                else:
                    cmd = ['sudo', 'pacman', '-S', '--noconfirm', package_name]
            else:
                logger.error(f"Unsupported distribution: {self.distro}")
                return False
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Error installing package {package_name}: {stderr}")
                return False
            
            logger.info(f"Successfully installed package {package_name}")
            return True
            
        except Exception as e:
            logger.error(f"Exception during package installation: {e}")
            return False
    
    def _install_python_package(self, package_name):
        """
        Install a Python package using pip
        
        Args:
            package_name: Name of the package
            
        Returns:
            True if installed successfully, False otherwise
        """
        logger.info(f"Installing Python package {package_name}")
        
        try:
            cmd = [sys.executable, '-m', 'pip', 'install', package_name]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Error installing Python package {package_name}: {stderr}")
                return False
            
            logger.info(f"Successfully installed Python package {package_name}")
            return True
            
        except Exception as e:
            logger.error(f"Exception during Python package installation: {e}")
            return False
    
    def _install_from_github(self, tool_name):
        """
        Install a tool from GitHub
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            True if installed successfully, False otherwise
        """
        if tool_name not in self.GITHUB_REPOS:
            logger.error(f"No GitHub repository configuration for {tool_name}")
            return False
        
        repo_info = self.GITHUB_REPOS[tool_name]
        repo = repo_info["repo"]
        binary = repo_info["binary"]
        
        logger.info(f"Installing {tool_name} from GitHub repository {repo}")
        
        try:
            # Get latest release info
            url = f"https://api.github.com/repos/{repo}/releases/latest"
            response = requests.get(url)
            
            if response.status_code != 200:
                logger.error(f"Error fetching release info: HTTP {response.status_code}")
                return False
            
            release_info = response.json()
            
            # Find asset for current platform
            system = platform.system().lower()
            machine = platform.machine().lower()
            
            # Map machine architecture to common naming
            if machine in ['x86_64', 'amd64']:
                arch = 'amd64'
            elif machine in ['arm64', 'aarch64']:
                arch = 'arm64'
            elif machine.startswith('arm'):
                arch = 'arm'
            else:
                arch = machine
            
            asset_url = None
            for asset in release_info['assets']:
                name = asset['name'].lower()
                if system in name and (arch in name or 'x64' in name or '64bit' in name or '64-bit' in name):
                    asset_url = asset['browser_download_url']
                    break
            
            if not asset_url:
                # Try to find any Linux asset
                for asset in release_info['assets']:
                    name = asset['name'].lower()
                    if 'linux' in name:
                        asset_url = asset['browser_download_url']
                        break
            
            if not asset_url:
                logger.error(f"No suitable release asset found for {system} {arch}")
                return False
            
            # Download asset
            download_path = os.path.join(tempfile.gettempdir(), os.path.basename(asset_url))
            logger.info(f"Downloading {asset_url} to {download_path}")
            
            response = requests.get(asset_url, stream=True)
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract if needed
            if download_path.endswith('.tar.gz') or download_path.endswith('.tgz'):
                extract_dir = os.path.join(tempfile.gettempdir(), tool_name)
                os.makedirs(extract_dir, exist_ok=True)
                
                with tarfile.open(download_path) as tar:
                    tar.extractall(path=extract_dir)
                
                # Find binary in extracted files
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        if file == binary or file.startswith(binary):
                            src_path = os.path.join(root, file)
                            dest_path = os.path.join(self.bin_dir, binary)
                            shutil.copy2(src_path, dest_path)
                            os.chmod(dest_path, 0o755)
                            logger.info(f"Installed {tool_name} to {dest_path}")
                            return True
            
            elif download_path.endswith('.zip'):
                extract_dir = os.path.join(tempfile.gettempdir(), tool_name)
                os.makedirs(extract_dir, exist_ok=True)
                
                with zipfile.ZipFile(download_path) as zip_file:
                    zip_file.extractall(path=extract_dir)
                
                # Find binary in extracted files
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        if file == binary or file.startswith(binary):
                            src_path = os.path.join(root, file)
                            dest_path = os.path.join(self.bin_dir, binary)
                            shutil.copy2(src_path, dest_path)
                            os.chmod(dest_path, 0o755)
                            logger.info(f"Installed {tool_name} to {dest_path}")
                            return True
            
            else:
                # Assume it's a direct binary
                dest_path = os.path.join(self.bin_dir, binary)
                shutil.copy2(download_path, dest_path)
                os.chmod(dest_path, 0o755)
                logger.info(f"Installed {tool_name} to {dest_path}")
                return True
            
            logger.error(f"Binary {binary} not found in downloaded package")
            return False
            
        except Exception as e:
            logger.error(f"Exception during GitHub installation: {e}")
            return False
    
    def scan_available_tools(self):
        """
        Scan system for all available tools
        
        Returns:
            Dictionary with availability status for each tool
        """
        logger.info("Scanning for available tools")
        
        results = {}
        
        for category, tools in self.TOOL_CATEGORIES.items():
            results[category] = {}
            for tool in tools:
                results[category][tool] = self.is_tool_installed(tool)
        
        return results
    
    def install_category(self, category):
        """
        Install all tools in a category
        
        Args:
            category: Category name
            
        Returns:
            Dictionary with installation status for each tool
        """
        if category not in self.TOOL_CATEGORIES:
            logger.error(f"Unknown category: {category}")
            return {"error": f"Unknown category: {category}"}
        
        logger.info(f"Installing tools for category: {category}")
        
        results = {}
        for tool in self.TOOL_CATEGORIES[category]:
            results[tool] = self.install_tool(tool)
        
        return results
    
    def get_tool_info(self, tool_name):
        """
        Get detailed information about a tool
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary with tool information
        """
        info = {
            "name": tool_name,
            "installed": self.is_tool_installed(tool_name),
            "path": shutil.which(tool_name),
            "package": None,
            "categories": []
        }
        
        # Find categories
        for category, tools in self.TOOL_CATEGORIES.items():
            if tool_name in tools:
                info["categories"].append(category)
        
        # Find package name
        if self.distro in self.PACKAGE_NAMES:
            info["package"] = self.PACKAGE_NAMES[self.distro].get(tool_name)
        
        # Check if it's a Python package
        if tool_name in self.PYTHON_PACKAGES:
            info["python_package"] = self.PYTHON_PACKAGES[tool_name]
        
        # Check if it's a GitHub tool
        if tool_name in self.GITHUB_REPOS:
            info["github_repo"] = self.GITHUB_REPOS[tool_name]["repo"]
        
        return info