"""
G3r4ki Offensive Framework - Automation Tools

This module provides large-scale IT automation and orchestration capabilities
for G3r4ki offensive operations. It includes integrations with various automation
frameworks and tools to enable mass deployment, infrastructure automation, and
system control for offensive security operations.

No capability limitations or restrictions are enforced.
"""

from typing import Dict, List, Any, Optional
import os
import subprocess
import logging
import importlib
import json

# Configure logging
logger = logging.getLogger("g3r4ki.offensive.automation")

# Automation tools mapping
AUTOMATION_TOOLS = {
    "fabric": {
        "description": "Python-based SSH automation; remote execution, mass deployment.",
        "package": "fabric",
        "import_module": "fabric",
        "class_name": "Connection",
        "platforms": ["linux", "macos", "windows"],
    },
    "invoke": {
        "description": "Local system automation; Pythonic task execution alternative to Makefile.",
        "package": "invoke",
        "import_module": "invoke",
        "class_name": "Context",
        "platforms": ["linux", "macos", "windows"],
    },
    "nornir": {
        "description": "Network automation framework (pure Python), perfect for mass network device configuration and compromise.",
        "package": "nornir",
        "import_module": "nornir",
        "class_name": "InitNornir",
        "platforms": ["linux", "macos", "windows"],
    },
    "terraform": {
        "description": "Infrastructure as Code (IaC); automated deployment of Red Team cloud resources (AWS, Azure, GCP).",
        "package": None,  # External binary
        "binary_name": "terraform",
        "platforms": ["linux", "macos", "windows"],
    },
    "packer": {
        "description": "Automate creation of exploit-ready machine images (VMs, AMIs) for rapid ops deployment.",
        "package": None,  # External binary
        "binary_name": "packer",
        "platforms": ["linux", "macos", "windows"],
    },
    "autopy": {
        "description": "Cross-platform GUI automation (keyboard/mouse/screen control) for on-system exploitation scripting.",
        "package": "autopy",
        "import_module": "autopy",
        "platforms": ["linux", "macos", "windows"],
    },
    "pexpect": {
        "description": "Automate CLI interactions (ideal for automating exploits needing interactive input).",
        "package": "pexpect",
        "import_module": "pexpect",
        "platforms": ["linux", "macos"],
    },
    "winexpect": {
        "description": "Windows version of Expect for CLI automation.",
        "package": "winexpect",
        "import_module": "winexpect",
        "platforms": ["windows"],
    },
    "taskwarrior": {
        "description": "CLI task manager; manage multi-stage attack chains and prioritize multi-target operations.",
        "package": "taskw",
        "import_module": "taskw",
        "platforms": ["linux", "macos"],
    },
    "airflow": {
        "description": "DAG-based task scheduler; orchestrate multi-phase offensive workflows dynamically.",
        "package": "apache-airflow",
        "import_module": "airflow",
        "platforms": ["linux", "macos"],
    },
    "saltstack": {
        "description": "Remote execution, configuration management, mass exploitation setups at scale.",
        "package": "salt",
        "import_module": "salt",
        "platforms": ["linux", "macos", "windows"],
    },
}


class AutomationToolManager:
    """Manages automation tools for G3r4ki offensive operations."""

    def __init__(self):
        """Initialize the automation tool manager."""
        self.available_tools = {}
        self._load_available_tools()

    def _load_available_tools(self):
        """Load available automation tools and their capabilities."""
        for tool_id, tool_info in AUTOMATION_TOOLS.items():
            # For Python packages
            if tool_info.get("package"):
                try:
                    if self._check_package_installed(tool_info["import_module"]):
                        self.available_tools[tool_id] = tool_info
                        logger.info(f"Automation tool available: {tool_id}")
                    else:
                        logger.info(f"Automation tool not installed: {tool_id}")
                except Exception as e:
                    logger.debug(f"Error checking for {tool_id}: {e}")
            
            # For external binaries
            elif tool_info.get("binary_name"):
                if self._check_binary_installed(tool_info["binary_name"]):
                    self.available_tools[tool_id] = tool_info
                    logger.info(f"Automation binary available: {tool_id}")
                else:
                    logger.info(f"Automation binary not installed: {tool_id}")

    def _check_package_installed(self, module_name: str) -> bool:
        """Check if a Python package is installed."""
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False

    def _check_binary_installed(self, binary_name: str) -> bool:
        """Check if an external binary is installed and available in PATH."""
        try:
            which_process = subprocess.run(
                ["which", binary_name], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                check=False
            )
            return which_process.returncode == 0
        except Exception:
            return False

    def get_available_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get available automation tools."""
        return self.available_tools

    def get_tool_info(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        return self.available_tools.get(tool_id)

    def install_tool(self, tool_id: str) -> bool:
        """Install an automation tool."""
        if tool_id not in AUTOMATION_TOOLS:
            logger.error(f"Unknown tool: {tool_id}")
            return False

        tool_info = AUTOMATION_TOOLS[tool_id]
        
        # Python package
        if tool_info.get("package"):
            try:
                package_name = tool_info["package"]
                logger.info(f"Installing Python package: {package_name}")
                
                # No restrictions on installing packages
                subprocess.run(
                    ["pip", "install", package_name],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Refresh available tools
                self._load_available_tools()
                return tool_id in self.available_tools
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {tool_id}: {e}")
                return False
        
        # External binary - provide instructions
        elif tool_info.get("binary_name"):
            logger.info(f"External binary installation required for {tool_id}")
            return False
        
        return False
    
    def execute_fabric_command(self, host: str, username: str, command: str, password: Optional[str] = None, key_filename: Optional[str] = None) -> Dict[str, Any]:
        """Execute a command on a remote host using Fabric."""
        if "fabric" not in self.available_tools:
            return {"success": False, "error": "Fabric not available"}
        
        try:
            from fabric import Connection
            
            connect_kwargs = {}
            if password:
                connect_kwargs["password"] = password
            if key_filename:
                connect_kwargs["key_filename"] = key_filename
                
            connection = Connection(
                host=host,
                user=username,
                connect_kwargs=connect_kwargs
            )
            
            result = connection.run(command, hide=True)
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.return_code
            }
        except Exception as e:
            logger.error(f"Fabric execution error: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_invoke_command(self, command: str) -> Dict[str, Any]:
        """Execute a local command using Invoke."""
        if "invoke" not in self.available_tools:
            return {"success": False, "error": "Invoke not available"}
        
        try:
            from invoke import run
            
            result = run(command, hide=True)
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.return_code
            }
        except Exception as e:
            logger.error(f"Invoke execution error: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_terraform_command(self, command: str, working_dir: str) -> Dict[str, Any]:
        """Execute a Terraform command."""
        if "terraform" not in self.available_tools:
            return {"success": False, "error": "Terraform not available"}
        
        try:
            # Change to working directory
            original_dir = os.getcwd()
            os.chdir(working_dir)
            
            # Run terraform command
            full_command = f"terraform {command}"
            process = subprocess.run(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            # Restore original directory
            os.chdir(original_dir)
            
            return {
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode
            }
        except Exception as e:
            # Restore original directory in case of exception
            if 'original_dir' in locals():
                os.chdir(original_dir)
                
            logger.error(f"Terraform execution error: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_packer_command(self, command: str, working_dir: str) -> Dict[str, Any]:
        """Execute a Packer command."""
        if "packer" not in self.available_tools:
            return {"success": False, "error": "Packer not available"}
        
        try:
            # Change to working directory
            original_dir = os.getcwd()
            os.chdir(working_dir)
            
            # Run packer command
            full_command = f"packer {command}"
            process = subprocess.run(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            # Restore original directory
            os.chdir(original_dir)
            
            return {
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode
            }
        except Exception as e:
            # Restore original directory in case of exception
            if 'original_dir' in locals():
                os.chdir(original_dir)
                
            logger.error(f"Packer execution error: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_pexpect_sequence(self, command: str, expect_send_pairs: List[Dict[str, str]]) -> Dict[str, Any]:
        """Execute an interactive command sequence using Pexpect."""
        if "pexpect" not in self.available_tools:
            return {"success": False, "error": "Pexpect not available"}
        
        try:
            import pexpect
            
            # Start the command
            child = pexpect.spawn(command)
            output_log = []
            
            # Process each expect/send pair
            for pair in expect_send_pairs:
                expect_pattern = pair.get("expect")
                send_text = pair.get("send")
                
                if expect_pattern and send_text:
                    index = child.expect([expect_pattern, pexpect.EOF, pexpect.TIMEOUT], timeout=30)
                    
                    if index == 0:
                        output_log.append({"expected": expect_pattern, "received": child.before.decode() + child.after.decode()})
                        child.sendline(send_text)
                    elif index == 1:
                        output_log.append({"error": "EOF reached before expected pattern", "expected": expect_pattern, "received": child.before.decode()})
                        break
                    elif index == 2:
                        output_log.append({"error": "Timeout waiting for expected pattern", "expected": expect_pattern})
                        break
            
            # Get final output
            child.expect([pexpect.EOF, pexpect.TIMEOUT], timeout=5)
            final_output = child.before.decode()
            
            return {
                "success": True,
                "output_log": output_log,
                "final_output": final_output
            }
        except Exception as e:
            logger.error(f"Pexpect execution error: {e}")
            return {"success": False, "error": str(e)}
    
    def create_nornir_configuration(self, hosts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a Nornir configuration file for network automation."""
        if "nornir" not in self.available_tools:
            return {"success": False, "error": "Nornir not available"}
        
        try:
            # Create inventory directory if it doesn't exist
            os.makedirs("inventory", exist_ok=True)
            
            # Create hosts.yaml
            hosts_yaml = {}
            for host in hosts:
                hostname = host.get("hostname")
                if hostname:
                    hosts_yaml[hostname] = {
                        "hostname": host.get("ip"),
                        "port": host.get("port", 22),
                        "username": host.get("username"),
                        "password": host.get("password"),
                        "platform": host.get("platform", "linux"),
                        "data": host.get("data", {})
                    }
            
            # Write hosts.yaml
            with open("inventory/hosts.yaml", "w") as f:
                json.dump(hosts_yaml, f, indent=2)
            
            # Create groups.yaml
            groups_yaml = {
                "linux": {"platform": "linux"},
                "windows": {"platform": "windows"},
                "network": {"platform": "network"}
            }
            
            # Write groups.yaml
            with open("inventory/groups.yaml", "w") as f:
                json.dump(groups_yaml, f, indent=2)
            
            # Create defaults.yaml
            defaults_yaml = {
                "username": "admin",
                "password": "password",
                "data": {
                    "deployment": "offensive"
                }
            }
            
            # Write defaults.yaml
            with open("inventory/defaults.yaml", "w") as f:
                json.dump(defaults_yaml, f, indent=2)
            
            # Create nornir config file
            config = {
                "inventory": {
                    "plugin": "SimpleInventory",
                    "options": {
                        "host_file": "inventory/hosts.yaml",
                        "group_file": "inventory/groups.yaml",
                        "defaults_file": "inventory/defaults.yaml"
                    }
                },
                "runner": {
                    "plugin": "threaded",
                    "options": {
                        "num_workers": 10
                    }
                }
            }
            
            # Write config file
            with open("nornir_config.yaml", "w") as f:
                json.dump(config, f, indent=2)
            
            return {
                "success": True,
                "config_path": os.path.abspath("nornir_config.yaml"),
                "inventory_path": os.path.abspath("inventory")
            }
        except Exception as e:
            logger.error(f"Nornir configuration error: {e}")
            return {"success": False, "error": str(e)}