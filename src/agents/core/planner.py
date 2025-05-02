"""
G3r4ki Agent Planner

This module provides planning capabilities for agents, allowing them to generate
sequences of actions to achieve goals.
"""

import uuid
import logging
from typing import Dict, List, Any, Optional, Tuple, Union

from src.llm.manager import LLMManager

# Setup logging
logger = logging.getLogger('g3r4ki.agents.planner')

class AgentPlanner:
    """
    Planning system for agents
    
    This class handles planning for agents, leveraging the LLM to generate plans.
    """
    
    def __init__(self, config: Dict[str, Any], llm_manager: Optional[LLMManager] = None):
        """
        Initialize agent planner
        
        Args:
            config: Configuration dictionary
            llm_manager: Optional LLM manager to use (will create one if not provided)
        """
        self.config = config
        self.llm_manager = llm_manager or LLMManager(config)
        
        # Default settings
        self.default_engine = config.get('agents', {}).get('default_engine', 'llama.cpp')
        self.default_model = config.get('agents', {}).get('default_model', None)
        
        logger.info("Agent planner initialized")
    
    def create_plan(self, 
                    objective: str, 
                    context: Dict[str, Any],
                    available_skills: List[str],
                    constraints: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a plan to achieve an objective
        
        Args:
            objective: The goal to achieve
            context: Contextual information for planning
            available_skills: List of skill names the agent can use
            constraints: Optional constraints on the plan
            
        Returns:
            Plan dictionary with steps
        """
        constraints = constraints or []
        
        # Build planning prompt
        prompt = self._build_planning_prompt(
            objective=objective,
            context=context,
            available_skills=available_skills,
            constraints=constraints
        )
        
        # Generate plan using LLM
        try:
            # Use the LLM to generate a plan
            response = self.llm_manager.query(
                prompt, 
                engine=self.default_engine, 
                model=self.default_model
            )
            
            # Parse plan from response
            plan = self._parse_plan_from_response(response)
            
            # Check if plan has steps, if not use fallback planning
            if not plan.get("steps", []):
                logger.warning("LLM-generated plan has no steps, using fallback planning")
                plan = self._generate_fallback_plan(objective, context, available_skills)
            
            logger.info(f"Generated plan with {len(plan.get('steps', []))} steps")
            return plan
        except Exception as e:
            logger.error(f"Error generating plan with LLM: {str(e)}")
            logger.info("Using fallback planning method")
            
            # Use fallback planning method
            plan = self._generate_fallback_plan(objective, context, available_skills)
            logger.info(f"Generated fallback plan with {len(plan.get('steps', []))} steps")
            return plan
    
    def _generate_fallback_plan(self, 
                               objective: str, 
                               context: Dict[str, Any],
                               available_skills: List[str]) -> Dict[str, Any]:
        """
        Generate a fallback plan without using LLM
        
        Args:
            objective: The goal to achieve
            context: Contextual information for planning
            available_skills: List of skill names the agent can use
            
        Returns:
            Plan dictionary with steps
        """
        plan_id = str(uuid.uuid4())
        target = context.get("target", "unknown")
        target_type = context.get("target_type", "unknown")
        
        # Create a basic plan based on target type
        steps = []
        step_id = 1
        
        # Filter skills to those we can use
        network_skills = [s for s in available_skills if s.startswith("network.")]
        recon_skills = [s for s in available_skills if s.startswith("recon.")]
        analysis_skills = [s for s in available_skills if s.startswith("analysis.")]
        
        if target_type == "domain":
            # Sequence for domain targets
            
            # 1. Domain WHOIS lookup
            if "recon.domain_whois" in available_skills:
                steps.append({
                    "id": step_id,
                    "name": "Domain WHOIS Lookup",
                    "description": f"Get WHOIS information for {target}",
                    "skill": "recon.domain_whois",
                    "parameters": {"domain": target},
                    "expected_outcome": "Basic domain registration information",
                    "fallback": None
                })
                step_id += 1
            
            # 2. DNS lookups
            if "network.dns_lookup" in available_skills:
                steps.append({
                    "id": step_id,
                    "name": "DNS Lookup",
                    "description": f"Resolve DNS for {target}",
                    "skill": "network.dns_lookup",
                    "parameters": {"hostname": target},
                    "expected_outcome": "IP address information",
                    "fallback": None
                })
                step_id += 1
            
            # 3. Subdomain enumeration
            if "recon.subdomain_enumeration" in available_skills:
                steps.append({
                    "id": step_id,
                    "name": "Subdomain Enumeration",
                    "description": f"Discover subdomains of {target}",
                    "skill": "recon.subdomain_enumeration",
                    "parameters": {"domain": target},
                    "expected_outcome": "List of subdomains",
                    "fallback": None
                })
                step_id += 1
            
            # 4. Web tech identification
            if "recon.web_technologies" in available_skills:
                steps.append({
                    "id": step_id,
                    "name": "Web Technology Identification",
                    "description": f"Identify technologies used by {target} website",
                    "skill": "recon.web_technologies",
                    "parameters": {"url": f"http://{target}"},
                    "expected_outcome": "List of web technologies",
                    "fallback": None
                })
                step_id += 1
            
        elif target_type == "ip":
            # Sequence for IP address targets
            
            # 1. Port scan
            if "network.port_scan" in available_skills:
                steps.append({
                    "id": step_id,
                    "name": "Basic Port Scan",
                    "description": f"Scan common ports on {target}",
                    "skill": "network.port_scan",
                    "parameters": {"target": target, "scan_type": "basic"},
                    "expected_outcome": "List of open ports and services",
                    "fallback": None
                })
                step_id += 1
            
            # 2. Traceroute
            if "network.trace_route" in available_skills:
                steps.append({
                    "id": step_id,
                    "name": "Traceroute",
                    "description": f"Perform traceroute to {target}",
                    "skill": "network.trace_route",
                    "parameters": {"target": target},
                    "expected_outcome": "Network path information",
                    "fallback": None
                })
                step_id += 1
        
        # For all target types, add analysis steps if applicable
        if steps and analysis_skills:
            # Add port scan analysis if we did a port scan
            if "analysis.analyze_port_scan" in analysis_skills and any("port_scan" in step.get("skill", "") for step in steps):
                steps.append({
                    "id": step_id,
                    "name": "Port Scan Analysis",
                    "description": "Analyze port scan results",
                    "skill": "analysis.analyze_port_scan",
                    "parameters": {"scan_results": {"reference": "port_scan_results"}},
                    "expected_outcome": "Security analysis of open ports",
                    "fallback": None
                })
                step_id += 1
            
            # Add comprehensive analysis
            if "analysis.analyze_recon_data" in analysis_skills:
                steps.append({
                    "id": step_id,
                    "name": "Reconnaissance Analysis",
                    "description": "Analyze all reconnaissance data",
                    "skill": "analysis.analyze_recon_data",
                    "parameters": {"recon_results": {"reference": "combined_results"}},
                    "expected_outcome": "Comprehensive security analysis",
                    "fallback": None
                })
                step_id += 1
            
            # Add network exposure analysis
            if "analysis.analyze_network_exposure" in analysis_skills:
                steps.append({
                    "id": step_id,
                    "name": "Network Exposure Analysis",
                    "description": f"Analyze network exposure for {target}",
                    "skill": "analysis.analyze_network_exposure",
                    "parameters": {"target": target, "scan_data": {"reference": "combined_results"}},
                    "expected_outcome": "Network exposure assessment",
                    "fallback": None
                })
                step_id += 1
            
            # Final comprehensive recon
            if "recon.comprehensive_recon" in recon_skills:
                steps.append({
                    "id": step_id,
                    "name": "Comprehensive Reconnaissance",
                    "description": f"Perform comprehensive reconnaissance on {target}",
                    "skill": "recon.comprehensive_recon",
                    "parameters": {"target": target},
                    "expected_outcome": "Combined reconnaissance results",
                    "fallback": None
                })
                step_id += 1
        
        return {
            "plan_id": plan_id,
            "objective": objective,
            "target": target,
            "steps": steps
        }
    
    def _build_planning_prompt(self, 
                               objective: str, 
                               context: Dict[str, Any],
                               available_skills: List[str],
                               constraints: List[str]) -> str:
        """
        Build a prompt for planning
        
        Args:
            objective: The goal to achieve
            context: Contextual information for planning
            available_skills: List of skill names the agent can use
            constraints: Constraints on the plan
            
        Returns:
            Planning prompt for the LLM
        """
        # Format context as string
        context_str = ""
        for key, value in context.items():
            context_str += f"{key}: {value}\\n"
        
        # Format available skills
        skills_str = ", ".join(available_skills)
        
        # Format constraints
        constraints_str = "\\n".join([f"- {constraint}" for constraint in constraints])
        if not constraints_str:
            constraints_str = "None"
        
        # Build prompt
        prompt = f"""
You are a cybersecurity AI agent tasked with creating a detailed plan to achieve an objective.
Generate a step-by-step plan in JSON format.

# OBJECTIVE
{objective}

# CONTEXT
{context_str}

# AVAILABLE SKILLS
{skills_str}

# CONSTRAINTS
{constraints_str}

# OUTPUT FORMAT
Respond with a valid JSON object containing:
1. "plan_id": A unique identifier for this plan
2. "objective": The objective being addressed
3. "steps": An array of steps, each with:
   - "id": Step number
   - "name": Brief name of the step
   - "description": Detailed description
   - "skill": The skill to use (must be from available skills)
   - "parameters": Object containing parameters for the skill
   - "expected_outcome": What this step should achieve
   - "fallback": What to do if the step fails

RESPOND ONLY WITH THE JSON PLAN. Do not include any other text.
"""
        return prompt
    
    def _parse_plan_from_response(self, response: str) -> Dict[str, Any]:
        """
        Parse a plan from the LLM response
        
        Args:
            response: LLM response text
            
        Returns:
            Parsed plan dictionary
        """
        import json
        import re
        
        try:
            # Handle empty or None responses
            if not response:
                logger.error("Empty response from LLM")
                raise ValueError("Empty response from LLM")
                
            # Clean up the response to extract JSON
            response = response.strip()
            original_response = response  # Save original for debugging
            
            # Try to extract from code blocks first
            json_content = None
            
            # Try JSON code block
            json_block_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
            if json_block_match:
                json_content = json_block_match.group(1).strip()
            
            # Try generic code block if JSON-specific wasn't found
            if not json_content:
                code_block_match = re.search(r'```\s*([\s\S]*?)\s*```', response)
                if code_block_match:
                    json_content = code_block_match.group(1).strip()
            
            # Look for content that resembles JSON (starts with { and ends with })
            if not json_content:
                json_pattern_match = re.search(r'(\{[\s\S]*\})', response)
                if json_pattern_match:
                    json_content = json_pattern_match.group(1).strip()
            
            # Use the extracted JSON content if found, otherwise use the original response
            if json_content:
                response = json_content
            
            # Try to parse as-is first
            try:
                plan = json.loads(response)
            except json.JSONDecodeError as e:
                logger.warning(f"Initial JSON parsing failed: {str(e)}, attempting fixes")
                
                # Attempt common JSON fixes
                fixed_response = response
                
                # Replace single quotes with double quotes
                fixed_response = fixed_response.replace("'", "\"")
                
                # Fix missing quotes around property names
                fixed_response = re.sub(r'(\s*?)(\w+)(\s*?):', r'\1"\2"\3:', fixed_response)
                
                # Clean up trailing commas in arrays and objects
                fixed_response = re.sub(r',\s*}', '}', fixed_response)
                fixed_response = re.sub(r',\s*]', ']', fixed_response)
                
                # Add missing quotes to string values
                # This is more complex and might not catch all cases
                
                try:
                    plan = json.loads(fixed_response)
                    logger.info("Successfully parsed JSON after fixes")
                except json.JSONDecodeError as e2:
                    logger.error(f"JSON parsing failed after fixes: {str(e2)}")
                    logger.debug(f"Original response: {original_response}")
                    logger.debug(f"Fixed response: {fixed_response}")
                    raise
            
            # Validate and fix plan structure
            if not isinstance(plan, dict):
                logger.error("Parsed JSON is not a dictionary")
                plan = {"error": "Invalid plan format - not a dictionary"}
            
            # Add required fields
            if "plan_id" not in plan:
                plan["plan_id"] = str(uuid.uuid4())
                
            if "objective" not in plan and "objective" in self.__dict__:
                plan["objective"] = self.objective
            
            # Handle steps
            if "steps" not in plan:
                plan["steps"] = []
            elif not isinstance(plan["steps"], list):
                logger.warning(f"Steps is not a list, got {type(plan['steps']).__name__}")
                plan["steps"] = []
            
            # Validate and fix individual steps
            valid_steps = []
            for i, step in enumerate(plan["steps"]):
                if not isinstance(step, dict):
                    logger.warning(f"Skipping invalid step at index {i}: not a dictionary")
                    continue
                
                # Fix required fields
                if "id" not in step:
                    step["id"] = i + 1
                
                if "name" not in step:
                    step["name"] = f"Step {step['id']}"
                
                if "skill" not in step:
                    logger.warning(f"Step {i+1} missing required 'skill' field")
                    # Skip steps without skills as they're not executable
                    continue
                
                if "parameters" not in step or not isinstance(step["parameters"], dict):
                    step["parameters"] = {}
                
                if "description" not in step:
                    step["description"] = step["name"]
                
                valid_steps.append(step)
            
            plan["steps"] = valid_steps
            
            logger.info(f"Successfully parsed plan with {len(valid_steps)} valid steps")
            return plan
            
        except Exception as e:
            logger.error(f"Failed to parse plan from LLM response: {str(e)}")
            
            # Create a minimal plan
            return {
                "plan_id": str(uuid.uuid4()),
                "objective": "Unknown (parsing error)",
                "error": f"Failed to parse plan from LLM response: {str(e)}",
                "steps": []
            }
    
    def evaluate_plan(self, plan: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Evaluate a plan for feasibility and completeness
        
        Args:
            plan: Plan to evaluate
            
        Returns:
            Tuple of (is_valid, issues)
        """
        issues = []
        
        # Check basic plan structure
        if "steps" not in plan or not plan["steps"]:
            issues.append("Plan has no steps")
            return False, issues
        
        # Check each step
        for i, step in enumerate(plan["steps"]):
            if "skill" not in step:
                issues.append(f"Step {i+1} is missing a skill")
            
            if "parameters" not in step or not isinstance(step["parameters"], dict):
                issues.append(f"Step {i+1} has invalid parameters")
        
        # Plan is valid if there are no issues
        is_valid = len(issues) == 0
        return is_valid, issues
    
    def refine_plan(self, 
                    plan: Dict[str, Any], 
                    issues: List[str],
                    available_skills: List[str]) -> Dict[str, Any]:
        """
        Refine a plan based on identified issues
        
        Args:
            plan: Original plan
            issues: Issues to address
            available_skills: List of skill names the agent can use
            
        Returns:
            Refined plan
        """
        # Build refining prompt
        import json
        
        plan_json = json.dumps(plan, indent=2)
        issues_str = "\\n".join([f"- {issue}" for issue in issues])
        skills_str = ", ".join(available_skills)
        
        prompt = f"""
You are a cybersecurity AI agent tasked with refining a plan that has some issues.
Fix the plan to address the identified issues while maintaining the original objective.

# ORIGINAL PLAN
```json
{plan_json}
```

# ISSUES TO FIX
{issues_str}

# AVAILABLE SKILLS
{skills_str}

# OUTPUT FORMAT
Respond with a valid JSON object containing the refined plan with the same structure as the original.
RESPOND ONLY WITH THE JSON PLAN. Do not include any other text.
"""
        
        try:
            # Use the LLM to refine the plan
            response = self.llm_manager.query(
                prompt, 
                engine=self.default_engine, 
                model=self.default_model
            )
            
            # Parse refined plan from response
            refined_plan = self._parse_plan_from_response(response)
            
            logger.info(f"Refined plan with {len(refined_plan.get('steps', []))} steps")
            return refined_plan
        except Exception as e:
            logger.error(f"Error refining plan: {str(e)}")
            # Return the original plan if refinement fails
            return plan