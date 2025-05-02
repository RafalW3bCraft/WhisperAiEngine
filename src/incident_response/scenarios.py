"""
G3r4ki Incident Response Scenarios.

This module provides functionality for managing and loading incident
response scenarios for simulation.
"""

import os
import json
import logging
import glob
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class IncidentScenario:
    """
    Represents an incident response scenario.
    
    This class encapsulates all the data and functionality related
    to a specific incident response scenario.
    """
    
    def __init__(self, scenario_data: Dict[str, Any]):
        """
        Initialize a scenario from data.
        
        Args:
            scenario_data: Dictionary containing scenario data
        """
        self.data = scenario_data
        self.id = scenario_data.get("incident_id", "unknown")
        self.title = scenario_data.get("title", "Unnamed Scenario")
        self.incident_type = scenario_data.get("incident_type", "unknown")
        self.difficulty = scenario_data.get("difficulty", "medium")
        
    def get_step(self, step_number: int) -> Dict[str, Any]:
        """
        Get a specific step from the scenario.
        
        Args:
            step_number: Step number (0-based index)
            
        Returns:
            Step data or empty dict if step doesn't exist
        """
        steps = self.data.get("steps", [])
        if 0 <= step_number < len(steps):
            return steps[step_number]
        return {}
        
    def get_total_steps(self) -> int:
        """
        Get the total number of steps in the scenario.
        
        Returns:
            Number of steps
        """
        return len(self.data.get("steps", []))
        
    def get_indicators(self) -> List[Dict[str, Any]]:
        """
        Get the indicators of compromise for this scenario.
        
        Returns:
            List of IoC dictionaries
        """
        return self.data.get("indicators", [])
        
    def get_questions(self) -> List[Dict[str, Any]]:
        """
        Get the assessment questions for this scenario.
        
        Returns:
            List of question dictionaries
        """
        return self.data.get("questions", [])
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the scenario to a dictionary.
        
        Returns:
            Dictionary representation of the scenario
        """
        return self.data

def load_scenario(scenario_id: str, scenarios_dir: str) -> Optional[Dict[str, Any]]:
    """
    Load a scenario by ID.
    
    Args:
        scenario_id: Scenario ID or filename
        scenarios_dir: Directory containing scenario files
        
    Returns:
        Scenario data or None if not found
    """
    # First, try to load by exact filename
    scenario_path = os.path.join(scenarios_dir, f"{scenario_id}.json")
    
    if not os.path.exists(scenario_path):
        # Try to find by ID in any filename
        pattern = os.path.join(scenarios_dir, f"*_{scenario_id}.json")
        matches = glob.glob(pattern)
        
        if not matches:
            # Try searching in all JSON files for the ID
            all_json = glob.glob(os.path.join(scenarios_dir, "*.json"))
            for json_file in all_json:
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        if data.get("incident_id") == scenario_id:
                            scenario_path = json_file
                            break
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"Error reading scenario file {json_file}: {e}")
                    continue
    
    if os.path.exists(scenario_path):
        try:
            with open(scenario_path, 'r') as f:
                scenario_data = json.load(f)
                return scenario_data
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading scenario {scenario_id}: {e}")
            return None
    
    logger.error(f"Scenario not found: {scenario_id}")
    return None

def get_available_scenarios(scenarios_dir: str) -> List[Dict[str, Any]]:
    """
    Get a list of available scenarios.
    
    Args:
        scenarios_dir: Directory containing scenario files
        
    Returns:
        List of scenario metadata dictionaries
    """
    scenarios = []
    
    # Find all JSON files in the scenarios directory
    json_files = glob.glob(os.path.join(scenarios_dir, "*.json"))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                
                # Extract metadata
                scenarios.append({
                    "id": data.get("incident_id", os.path.basename(json_file)),
                    "title": data.get("title", "Unnamed Scenario"),
                    "incident_type": data.get("incident_type", "unknown"),
                    "difficulty": data.get("difficulty", "medium"),
                    "organization": data.get("organization", {}).get("name", "Unknown Organization"),
                    "file_path": json_file
                })
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading scenario file {json_file}: {e}")
            continue
    
    return scenarios

def filter_scenarios(scenarios: List[Dict[str, Any]], 
                    incident_type: Optional[str] = None,
                    difficulty: Optional[str] = None,
                    keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Filter scenarios by type, difficulty, or keyword.
    
    Args:
        scenarios: List of scenario dictionaries
        incident_type: Incident type to filter by
        difficulty: Difficulty level to filter by
        keyword: Keyword to search in title and organization
        
    Returns:
        Filtered list of scenarios
    """
    filtered = scenarios
    
    if incident_type:
        filtered = [s for s in filtered if s.get("incident_type") == incident_type]
    
    if difficulty:
        filtered = [s for s in filtered if s.get("difficulty") == difficulty]
    
    if keyword:
        keyword = keyword.lower()
        filtered = [s for s in filtered if 
                   keyword in s.get("title", "").lower() or 
                   keyword in s.get("organization", "").lower()]
    
    return filtered