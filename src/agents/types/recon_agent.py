"""
G3r4ki Reconnaissance Agent

This module provides a specialized agent for conducting reconnaissance operations.
The ReconAgent can autonomously perform reconnaissance tasks such as domain enumeration,
port scanning, and service discovery.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union

from src.agents.core.base import Agent, AgentStatus
from src.agents.core.planner import AgentPlanner
from src.agents.skills.recon import ReconSkills
from src.agents.skills.network import NetworkSkills
from src.agents.skills.analysis import AnalysisSkills

# Setup logging
logger = logging.getLogger('g3r4ki.agents.recon')

class ReconAgent(Agent):
    """
    Reconnaissance agent for automated information gathering and analysis
    
    This agent specializes in reconnaissance operations, including:
    - Domain and subdomain enumeration
    - Network scanning
    - Service identification
    - Technology detection
    - Vulnerability scanning
    - Analysis and reporting
    """
    
    def __init__(self, 
                 name: str, 
                 description: str,
                 config: Dict[str, Any],
                 parent: Optional[Agent] = None):
        """
        Initialize reconnaissance agent
        
        Args:
            name: Agent name
            description: Agent description
            config: Configuration dictionary
            parent: Parent agent if this is a sub-agent
        """
        super().__init__(name, description, config, parent)
        
        # Initialize skills
        self.recon_skills = ReconSkills(config)
        self.network_skills = NetworkSkills(config)
        self.analysis_skills = AnalysisSkills(config)
        
        # Register all skills
        self._register_all_skills()
        
        # Initialize planner
        self.planner = AgentPlanner(config)
        
        logger.info(f"ReconAgent '{name}' initialized")
    
    def _register_all_skills(self) -> None:
        """Register all available skills"""
        # Register recon skills
        for name, method in vars(self.recon_skills.__class__).items():
            if callable(method) and not name.startswith('_'):
                self.register_skill(f"recon.{name}", getattr(self.recon_skills, name))
        
        # Register network skills
        for name, method in vars(self.network_skills.__class__).items():
            if callable(method) and not name.startswith('_'):
                self.register_skill(f"network.{name}", getattr(self.network_skills, name))
        
        # Register analysis skills
        for name, method in vars(self.analysis_skills.__class__).items():
            if callable(method) and not name.startswith('_'):
                self.register_skill(f"analysis.{name}", getattr(self.analysis_skills, name))
    
    def plan(self) -> Dict[str, Any]:
        """
        Generate a reconnaissance plan based on current state and objectives
        
        Returns:
            A plan dictionary with steps to execute
        """
        # Get target from state
        target = self.state.get("target")
        
        if not target:
            logger.error("Cannot create plan: target not set in agent state")
            return {
                "plan_id": "error",
                "objective": "Error: target not set",
                "steps": []
            }
        
        # Create context for planning
        context = {
            "target": target,
            "target_type": self.state.get("target_type", "unknown"),
            "scope": self.state.get("scope", "standard"),
            "previous_results": self.state.get("results", {})
        }
        
        # List of skills available to the agent
        available_skills = list(self.skills.keys())
        
        # Generate constraints based on scope
        constraints = [
            "The plan must adhere to the specified scope",
            "The plan should prioritize passive reconnaissance before active scanning"
        ]
        
        if context["scope"] == "passive":
            constraints.append("Only passive reconnaissance techniques are allowed")
        
        # Generate objective based on target type and scope
        if context["target_type"] == "domain":
            objective = f"Perform comprehensive reconnaissance on the domain {target}"
        elif context["target_type"] == "ip":
            objective = f"Perform comprehensive reconnaissance on the IP address {target}"
        else:
            objective = f"Perform comprehensive reconnaissance on {target}"
        
        # Create plan using planner
        plan = self.planner.create_plan(
            objective=objective,
            context=context,
            available_skills=available_skills,
            constraints=constraints
        )
        
        # Evaluate and refine plan if needed
        is_valid, issues = self.planner.evaluate_plan(plan)
        
        if not is_valid:
            logger.warning(f"Initial plan has issues: {issues}")
            plan = self.planner.refine_plan(plan, issues, available_skills)
        
        return plan
    
    def execute_plan(self, plan: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute a reconnaissance plan
        
        Args:
            plan: Plan dictionary to execute
            
        Returns:
            Tuple of (success, results)
        """
        results = {
            "plan_id": plan.get("plan_id", "unknown"),
            "target": self.state.get("target", "unknown"),
            "steps_completed": 0,
            "steps_failed": 0,
            "steps_results": {},
            "combined_results": {}
        }
        
        steps = plan.get("steps", [])
        
        if not steps:
            logger.warning("Plan has no steps to execute")
            return False, results
        
        logger.info(f"Executing plan with {len(steps)} steps")
        
        for step in steps:
            step_id = step.get("id")
            step_name = step.get("name", f"Step {step_id}")
            skill_name = step.get("skill")
            parameters = step.get("parameters", {})
            
            logger.info(f"Executing step {step_id}: {step_name} using skill {skill_name}")
            
            # Check if we have the required skill
            if not self.has_skill(skill_name):
                logger.error(f"Missing required skill: {skill_name}")
                results["steps_failed"] += 1
                continue
            
            try:
                # Execute the skill
                step_result = self.use_skill(skill_name, **parameters)
                
                # Record result
                results["steps_completed"] += 1
                results["steps_results"][step_id] = step_result
                
                # Add to combined results based on result type
                self._update_combined_results(results["combined_results"], step_result)
                
                # Update agent state with latest results
                self.state["results"] = results["combined_results"]
                
                logger.info(f"Step {step_id} completed successfully")
                
            except Exception as e:
                logger.error(f"Error executing step {step_id}: {str(e)}")
                results["steps_failed"] += 1
                
                # Try fallback if available
                fallback = step.get("fallback")
                if fallback and fallback.get("skill"):
                    fallback_skill = fallback.get("skill")
                    fallback_params = fallback.get("parameters", {})
                    
                    logger.info(f"Attempting fallback for step {step_id} using {fallback_skill}")
                    
                    try:
                        # Execute fallback skill
                        fallback_result = self.use_skill(fallback_skill, **fallback_params)
                        
                        # Record result
                        results["steps_completed"] += 1
                        results["steps_results"][f"{step_id}_fallback"] = fallback_result
                        
                        # Add to combined results
                        self._update_combined_results(results["combined_results"], fallback_result)
                        
                    except Exception as fallback_error:
                        logger.error(f"Fallback for step {step_id} also failed: {str(fallback_error)}")
        
        # Save final results to file
        self._save_results(results)
        
        # Determine overall success
        success = results["steps_completed"] > 0 and results["steps_failed"] < len(steps) / 2
        
        logger.info(f"Plan execution completed: {results['steps_completed']} steps succeeded, {results['steps_failed']} steps failed")
        
        return success, results
    
    def _update_combined_results(self, combined_results: Dict[str, Any], step_result: Any) -> None:
        """
        Update combined results with step result
        
        Args:
            combined_results: Combined results dictionary to update
            step_result: Result from a step execution
        """
        # Handle different types of results based on content
        if isinstance(step_result, dict):
            # Extract key information based on content
            
            # Handle subdomains
            if "subdomains" in step_result:
                if "subdomains" not in combined_results:
                    combined_results["subdomains"] = []
                
                for subdomain in step_result["subdomains"]:
                    if subdomain not in combined_results["subdomains"]:
                        combined_results["subdomains"].append(subdomain)
            
            # Handle port scan results
            if "hosts" in step_result:
                if "hosts" not in combined_results:
                    combined_results["hosts"] = []
                
                # Merge hosts data
                for host in step_result["hosts"]:
                    host_ip = host.get("ip")
                    
                    # Check if we already have this host
                    existing_host = next((h for h in combined_results["hosts"] if h.get("ip") == host_ip), None)
                    
                    if existing_host:
                        # Merge port information
                        existing_ports = {(p["port"], p["protocol"]): p for p in existing_host["ports"]}
                        
                        for port in host.get("ports", []):
                            port_key = (port["port"], port["protocol"])
                            if port_key not in existing_ports:
                                existing_host["ports"].append(port)
                    else:
                        # Add new host
                        combined_results["hosts"].append(host)
            
            # Handle open ports directly
            if "open_ports" in step_result:
                if "open_ports" not in combined_results:
                    combined_results["open_ports"] = []
                
                for port in step_result["open_ports"]:
                    if port not in combined_results["open_ports"]:
                        combined_results["open_ports"].append(port)
            
            # Handle web technologies
            if "technologies" in step_result:
                if "technologies" not in combined_results:
                    combined_results["technologies"] = []
                
                for tech in step_result["technologies"]:
                    if tech not in combined_results["technologies"]:
                        combined_results["technologies"].append(tech)
            
            # Handle domain info
            if "domain_info" in step_result and step_result["domain_info"]:
                combined_results["domain_info"] = step_result["domain_info"]
            
            # Handle security issues
            if "security_issues" in step_result:
                if "security_issues" not in combined_results:
                    combined_results["security_issues"] = []
                
                for issue in step_result["security_issues"]:
                    if issue not in combined_results["security_issues"]:
                        combined_results["security_issues"].append(issue)
            
            # Handle vulnerabilities
            if "vulnerabilities" in step_result:
                if "vulnerabilities" not in combined_results:
                    combined_results["vulnerabilities"] = []
                
                for vuln in step_result["vulnerabilities"]:
                    if vuln not in combined_results["vulnerabilities"]:
                        combined_results["vulnerabilities"].append(vuln)
    
    def _save_results(self, results: Dict[str, Any]) -> None:
        """
        Save results to file
        
        Args:
            results: Results dictionary to save
        """
        import os
        import json
        from datetime import datetime
        
        # Create results directory if it doesn't exist
        results_dir = os.path.join(os.getcwd(), 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = self.state.get("target", "unknown")
        safe_target = target.replace(".", "_").replace("/", "_").replace(":", "_")
        
        filename = f"{safe_target}_{timestamp}_recon_results.json"
        filepath = os.path.join(results_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Saved results to {filepath}")
            
            # Update state with results file
            self.state["results_file"] = filepath
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
    
    def set_target(self, target: str, target_type: Optional[str] = None, scope: str = "standard") -> None:
        """
        Set the reconnaissance target
        
        Args:
            target: Target to reconnoiter (domain, IP, etc.)
            target_type: Type of target (domain, ip, etc.) or None to auto-detect
            scope: Scope of reconnaissance (passive, standard, aggressive)
        """
        import re
        
        # Auto-detect target type if not specified
        if target_type is None:
            # Check if target is an IP address
            if re.match(r'^(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?$', target):
                target_type = "ip"
            # Check if target is a domain
            elif re.match(r'^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z]{2,})+$', target):
                target_type = "domain"
            # Default to unknown
            else:
                target_type = "unknown"
        
        # Update state
        self.state["target"] = target
        self.state["target_type"] = target_type
        self.state["scope"] = scope
        
        logger.info(f"Set target to {target} (type: {target_type}, scope: {scope})")
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive report based on the reconnaissance results
        
        Returns:
            Report dictionary
        """
        target = self.state.get("target", "unknown")
        results = self.state.get("results", {})
        
        if not results:
            logger.warning("No results available for report generation")
            return {
                "error": "No reconnaissance results available",
                "target": target
            }
        
        try:
            report = self.analysis_skills.generate_security_report(target, results)
            logger.info(f"Generated security report for {target}")
            return report
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {
                "error": str(e),
                "target": target
            }