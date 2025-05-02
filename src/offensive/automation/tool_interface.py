"""
G3r4ki Offensive Framework - Automation Tool Interface

This module provides a unified interface for automating operations using
various automation tools within the G3r4ki Offensive Framework.
"""

import os
import json
import logging
import importlib
from typing import Dict, List, Any, Optional, Union, Callable

from . import AutomationToolManager

# Configure logging
logger = logging.getLogger("g3r4ki.offensive.automation.interface")

class AutomationInterface:
    """Interface for integrating automation tools into the G3r4ki offensive framework."""
    
    def __init__(self):
        """Initialize the automation interface."""
        self.tool_manager = AutomationToolManager()
        self.available_tools = self.tool_manager.get_available_tools()
        
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """
        List available automation tools.
        
        Returns:
            List of available tools with metadata
        """
        tool_list = []
        for tool_id, tool_info in self.available_tools.items():
            tool_list.append({
                "id": tool_id,
                "name": tool_id.capitalize(),
                "description": tool_info.get("description", ""),
                "platforms": tool_info.get("platforms", []),
            })
        return tool_list
    
    def get_tool_details(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific tool.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            Tool details or None if not found
        """
        if tool_id in self.available_tools:
            tool_info = self.available_tools[tool_id]
            return {
                "id": tool_id,
                "name": tool_id.capitalize(),
                "description": tool_info.get("description", ""),
                "platforms": tool_info.get("platforms", []),
                "package": tool_info.get("package"),
                "binary": tool_info.get("binary_name"),
                "import_module": tool_info.get("import_module"),
                "class_name": tool_info.get("class_name"),
            }
        return None
    
    def install_tool(self, tool_id: str) -> Dict[str, Any]:
        """
        Install an automation tool.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            Dictionary with installation results
        """
        result = self.tool_manager.install_tool(tool_id)
        if result:
            # Refresh available tools
            self.available_tools = self.tool_manager.get_available_tools()
            return {"success": True, "message": f"Tool {tool_id} installed successfully"}
        else:
            return {"success": False, "message": f"Failed to install tool {tool_id}"}
    
    def execute_remote_command(self, tool_id: str, host: str, username: str, command: str,
                              password: Optional[str] = None, key_filename: Optional[str] = None,
                              options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a command on a remote host using the specified tool.
        
        Args:
            tool_id: Tool identifier
            host: Remote host address
            username: Remote username
            command: Command to execute
            password: Optional password for authentication
            key_filename: Optional private key file for authentication
            options: Additional tool-specific options
            
        Returns:
            Dictionary with execution results
        """
        if tool_id not in self.available_tools:
            return {"success": False, "error": f"Tool {tool_id} not available"}
        
        if tool_id == "fabric":
            return self.tool_manager.execute_fabric_command(
                host=host,
                username=username,
                command=command,
                password=password,
                key_filename=key_filename
            )
        elif tool_id == "saltstack":
            # Simplified SaltStack client implementation
            try:
                import salt.client
                
                local = salt.client.LocalClient()
                target = host if '@' not in host else host.split('@')[1]
                
                result = local.cmd(
                    target,
                    'cmd.run',
                    [command],
                    timeout=30
                )
                
                return {
                    "success": True,
                    "output": result,
                }
            except Exception as e:
                logger.error(f"SaltStack execution error: {e}")
                return {"success": False, "error": str(e)}
        else:
            return {"success": False, "error": f"Remote execution not supported for {tool_id}"}
    
    def execute_local_command(self, tool_id: str, command: str, 
                             options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a command locally using the specified tool.
        
        Args:
            tool_id: Tool identifier
            command: Command to execute
            options: Additional tool-specific options
            
        Returns:
            Dictionary with execution results
        """
        if tool_id not in self.available_tools:
            return {"success": False, "error": f"Tool {tool_id} not available"}
        
        if tool_id == "invoke":
            return self.tool_manager.execute_invoke_command(command)
        elif tool_id == "pexpect":
            if not options or "expect_send_pairs" not in options:
                return {"success": False, "error": "Expect/send pairs required for pexpect"}
                
            return self.tool_manager.execute_pexpect_sequence(
                command=command,
                expect_send_pairs=options["expect_send_pairs"]
            )
        else:
            return {"success": False, "error": f"Local execution not supported for {tool_id}"}
    
    def generate_infrastructure(self, tool_id: str, config_file: str, 
                               working_dir: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate infrastructure using IaC tools.
        
        Args:
            tool_id: Tool identifier
            config_file: Configuration file path
            working_dir: Working directory
            options: Additional tool-specific options
            
        Returns:
            Dictionary with execution results
        """
        if tool_id not in self.available_tools:
            return {"success": False, "error": f"Tool {tool_id} not available"}
        
        if tool_id == "terraform":
            # First initialize Terraform
            init_result = self.tool_manager.execute_terraform_command("init", working_dir)
            if not init_result.get("success", False):
                return {"success": False, "error": f"Terraform initialization failed: {init_result.get('stderr', '')}"}
            
            # Then apply the configuration
            apply_cmd = "apply -auto-approve"
            if options and options.get("vars"):
                for var_name, var_value in options["vars"].items():
                    apply_cmd += f" -var='{var_name}={var_value}'"
            
            return self.tool_manager.execute_terraform_command(apply_cmd, working_dir)
        elif tool_id == "packer":
            # Build the image
            build_cmd = f"build {config_file}"
            if options and options.get("vars"):
                for var_name, var_value in options["vars"].items():
                    build_cmd += f" -var '{var_name}={var_value}'"
            
            return self.tool_manager.execute_packer_command(build_cmd, working_dir)
        else:
            return {"success": False, "error": f"Infrastructure generation not supported for {tool_id}"}
    
    def create_network_automation_config(self, hosts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a network automation configuration.
        
        Args:
            hosts: List of host configurations
            
        Returns:
            Dictionary with configuration results
        """
        if "nornir" not in self.available_tools:
            return {"success": False, "error": "Nornir not available"}
        
        return self.tool_manager.create_nornir_configuration(hosts)
    
    def run_network_automation(self, script_path: str, config_path: str) -> Dict[str, Any]:
        """
        Run a network automation script using Nornir.
        
        Args:
            script_path: Path to the automation script
            config_path: Path to the Nornir configuration
            
        Returns:
            Dictionary with execution results
        """
        if "nornir" not in self.available_tools:
            return {"success": False, "error": "Nornir not available"}
        
        try:
            # We're using subprocess because Nornir requires a specific environment setup
            # which is difficult to manage within a Python process that's already running
            import subprocess
            
            # Set environment variable for Nornir config
            env = os.environ.copy()
            env["NORNIR_CONFIG"] = config_path
            
            # Run the script
            process = subprocess.run(
                ["python", script_path],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            return {
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode
            }
        except Exception as e:
            logger.error(f"Nornir execution error: {e}")
            return {"success": False, "error": str(e)}
    
    def run_automation_workflow(self, workflow_file: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run an automation workflow using Airflow.
        
        Args:
            workflow_file: Path to the workflow definition file
            parameters: Parameters for the workflow
            
        Returns:
            Dictionary with execution results
        """
        if "airflow" not in self.available_tools:
            return {"success": False, "error": "Airflow not available"}
        
        try:
            # Setup Airflow home
            airflow_home = os.path.abspath("airflow")
            os.makedirs(os.path.join(airflow_home, "dags"), exist_ok=True)
            
            # Set environment variable for Airflow
            env = os.environ.copy()
            env["AIRFLOW_HOME"] = airflow_home
            
            # Initialize Airflow database
            subprocess.run(
                ["airflow", "db", "init"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            
            # Copy workflow file to DAGs directory
            import shutil
            dag_file = os.path.join(airflow_home, "dags", os.path.basename(workflow_file))
            shutil.copy2(workflow_file, dag_file)
            
            # Get DAG ID from the file
            dag_id = None
            with open(workflow_file, "r") as f:
                for line in f:
                    if "DAG(" in line:
                        dag_id_match = line.split("DAG(")[1].split(",")[0].strip("'\"")
                        dag_id = dag_id_match
                        break
            
            if not dag_id:
                return {"success": False, "error": "Could not determine DAG ID from workflow file"}
            
            # Trigger the DAG
            params_json = json.dumps(parameters)
            trigger_cmd = ["airflow", "dags", "trigger", "-r", "manual_run", "--conf", params_json, dag_id]
            
            process = subprocess.run(
                trigger_cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            return {
                "success": process.returncode == 0,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "return_code": process.returncode,
                "dag_id": dag_id
            }
        except Exception as e:
            logger.error(f"Airflow execution error: {e}")
            return {"success": False, "error": str(e)}