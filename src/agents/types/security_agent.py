"""
G3r4ki Security Agent

This module provides a specialized agent for security assessment and vulnerability scanning.
The SecurityAgent focuses on identifying vulnerabilities and security issues in targets.
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
logger = logging.getLogger('g3r4ki.agents.security')

class SecurityAgent(Agent):
    """
    Security assessment agent for vulnerability scanning and analysis
    
    This agent specializes in security assessment operations, including:
    - Vulnerability scanning
    - Security configuration analysis
    - Exploit detection
    - Risk assessment
    - Remediation guidance
    """
    
    def __init__(self, 
                 name: str, 
                 description: str,
                 config: Dict[str, Any],
                 parent: Optional[Agent] = None):
        """
        Initialize security agent
        
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
        
        # Try to import advanced vulnerability scanning module if available
        try:
            from src.security.vuln_scan import VulnerabilityScanner
            self.vuln_scanner = VulnerabilityScanner(config)
            self._has_vuln_scanner = True
        except ImportError:
            self.vuln_scanner = None
            self._has_vuln_scanner = False
        
        # Register all skills
        self._register_all_skills()
        
        # Initialize planner
        self.planner = AgentPlanner(config)
        
        logger.info(f"SecurityAgent '{name}' initialized")
    
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
        
        # Register vulnerability scanning skills if available
        if self._has_vuln_scanner:
            for name, method in vars(self.vuln_scanner.__class__).items():
                if callable(method) and not name.startswith('_'):
                    self.register_skill(f"vuln.{name}", getattr(self.vuln_scanner, name))
    
    def plan(self) -> Dict[str, Any]:
        """
        Generate a security assessment plan based on current state and objectives
        
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
        
        # Get scan type from state
        scan_type = self.state.get("scan_type", "basic")
        
        # Create context for planning
        context = {
            "target": target,
            "target_type": self.state.get("target_type", "unknown"),
            "scan_type": scan_type,
            "previous_results": self.state.get("results", {}),
            "has_vuln_scanner": self._has_vuln_scanner
        }
        
        # List of skills available to the agent
        available_skills = list(self.skills.keys())
        
        # Generate constraints based on scan type
        constraints = [
            "The plan must prioritize non-intrusive scans before intrusive ones",
            "All scans must be properly targeted to avoid unintended impact"
        ]
        
        if scan_type == "passive":
            constraints.append("Only passive scanning techniques are allowed")
        elif scan_type == "safe":
            constraints.append("No potentially disruptive techniques are allowed")
        
        # Generate objective based on target type and scan type
        if context["target_type"] == "domain":
            objective = f"Perform {scan_type} security assessment on the domain {target}"
        elif context["target_type"] == "ip":
            objective = f"Perform {scan_type} security assessment on the IP address {target}"
        else:
            objective = f"Perform {scan_type} security assessment on {target}"
        
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
        Execute a security assessment plan
        
        Args:
            plan: Plan dictionary to execute
            
        Returns:
            Tuple of (success, results)
        """
        results = {
            "plan_id": plan.get("plan_id", "unknown"),
            "target": self.state.get("target", "unknown"),
            "scan_type": self.state.get("scan_type", "basic"),
            "steps_completed": 0,
            "steps_failed": 0,
            "steps_results": {},
            "combined_results": {},
            "vulnerabilities": []
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
                self._update_combined_results(results, step_result)
                
                # Update agent state with latest results
                self.state["results"] = results["combined_results"]
                self.state["vulnerabilities"] = results["vulnerabilities"]
                
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
                        self._update_combined_results(results, fallback_result)
                        
                    except Exception as fallback_error:
                        logger.error(f"Fallback for step {step_id} also failed: {str(fallback_error)}")
        
        # Save final results to file
        self._save_results(results)
        
        # Determine overall success
        success = results["steps_completed"] > 0 and results["steps_failed"] < len(steps) / 2
        
        logger.info(f"Plan execution completed: {results['steps_completed']} steps succeeded, {results['steps_failed']} steps failed")
        
        return success, results
    
    def _update_combined_results(self, results: Dict[str, Any], step_result: Any) -> None:
        """
        Update combined results with step result
        
        Args:
            results: Results dictionary to update
            step_result: Result from a step execution
        """
        combined_results = results["combined_results"]
        
        # Handle different types of results based on content
        if isinstance(step_result, dict):
            # Extract key information based on content
            
            # Handle vulnerabilities
            if "vulnerabilities" in step_result:
                for vuln in step_result["vulnerabilities"]:
                    if vuln not in results["vulnerabilities"]:
                        results["vulnerabilities"].append(vuln)
            
            # Handle security issues
            if "security_issues" in step_result:
                if "security_issues" not in combined_results:
                    combined_results["security_issues"] = []
                
                for issue in step_result["security_issues"]:
                    if issue not in combined_results["security_issues"]:
                        combined_results["security_issues"].append(issue)
                        
                        # Convert security issues to vulnerabilities if not already tracked
                        vuln = {
                            "title": issue.get("type", "Security Issue"),
                            "severity": issue.get("risk", "medium"),
                            "description": issue.get("description", ""),
                            "impact": "May increase security risk",
                            "remediation": "Address the security issue"
                        }
                        
                        if vuln not in results["vulnerabilities"]:
                            results["vulnerabilities"].append(vuln)
            
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
            
            # Handle risk factors and exposure level
            if "risk_factors" in step_result:
                if "risk_factors" not in combined_results:
                    combined_results["risk_factors"] = []
                
                for factor in step_result["risk_factors"]:
                    if factor not in combined_results["risk_factors"]:
                        combined_results["risk_factors"].append(factor)
            
            if "exposure_level" in step_result:
                combined_results["exposure_level"] = step_result["exposure_level"]
            
            if "risk_score" in step_result:
                combined_results["risk_score"] = step_result["risk_score"]
            
            # Handle mitigations
            if "mitigations" in step_result:
                if "mitigations" not in combined_results:
                    combined_results["mitigations"] = []
                
                for mitigation in step_result["mitigations"]:
                    if mitigation not in combined_results["mitigations"]:
                        combined_results["mitigations"].append(mitigation)
    
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
        vuln_dir = os.path.join(results_dir, 'vuln')
        os.makedirs(vuln_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = self.state.get("target", "unknown")
        scan_type = self.state.get("scan_type", "basic")
        safe_target = target.replace(".", "_").replace("/", "_").replace(":", "_")
        
        filename = f"{safe_target}_{scan_type}_{timestamp}_security_results.json"
        filepath = os.path.join(vuln_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Saved results to {filepath}")
            
            # Update state with results file
            self.state["results_file"] = filepath
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
    
    def set_target(self, 
                   target: str, 
                   target_type: Optional[str] = None, 
                   scan_type: str = "basic") -> None:
        """
        Set the security assessment target
        
        Args:
            target: Target to assess (domain, IP, etc.)
            target_type: Type of target (domain, ip, etc.) or None to auto-detect
            scan_type: Type of scan (passive, safe, basic, comprehensive)
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
        
        # Validate scan type
        valid_scan_types = ["passive", "safe", "basic", "comprehensive"]
        if scan_type not in valid_scan_types:
            logger.warning(f"Invalid scan type: {scan_type}, defaulting to 'basic'")
            scan_type = "basic"
        
        # Update state
        self.state["target"] = target
        self.state["target_type"] = target_type
        self.state["scan_type"] = scan_type
        
        logger.info(f"Set target to {target} (type: {target_type}, scan_type: {scan_type})")
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive security report based on the assessment results
        
        Returns:
            Report dictionary
        """
        target = self.state.get("target", "unknown")
        scan_type = self.state.get("scan_type", "basic")
        
        # Combine results and vulnerabilities
        report_data = {
            **self.state.get("results", {}),
            "vulnerabilities": self.state.get("vulnerabilities", [])
        }
        
        if not report_data or (not report_data.get("vulnerabilities") and not report_data.get("security_issues")):
            logger.warning("No security findings available for report generation")
            return {
                "error": "No security findings available",
                "target": target,
                "scan_type": scan_type
            }
        
        try:
            report = self.analysis_skills.generate_security_report(target, report_data)
            logger.info(f"Generated security report for {target}")
            return report
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {
                "error": str(e),
                "target": target,
                "scan_type": scan_type
            }