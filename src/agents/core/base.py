"""
G3r4ki Agent Base Module

This module provides the base Agent class and related functionality.
"""

import uuid
import time
import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Union, TypeVar, Generic, Type

# Setup logging
logger = logging.getLogger("g3r4ki.agents.core")

class AgentStatus(Enum):
    """Agent status enum"""
    INITIALIZING = "INITIALIZING"
    IDLE = "IDLE"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"

class Agent:
    """
    Base Agent class for G3r4ki
    
    This provides common functionality for all agent types.
    """
    
    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize a new agent
        
        Args:
            name: Name of the agent
            description: Optional description
        """
        self.agent_id = str(uuid.uuid4())
        self.name = name
        self.description = description or f"G3r4ki Agent: {name}"
        self.status = AgentStatus.INITIALIZING
        self.created_at = time.time()
        self.last_active = time.time()
        self.target = None
        self.results = {}
        
        logger.info(f"Agent created: {self.name} ({self.agent_id})")
        self.status = AgentStatus.IDLE
    
    def set_target(self, target: str) -> None:
        """
        Set the target for this agent
        
        Args:
            target: Target to operate on (IP, domain, etc.)
        """
        self.target = target
        logger.info(f"Agent {self.name} target set to: {target}")
    
    def run(self) -> Dict[str, Any]:
        """
        Run the agent
        
        This method should be overridden by subclasses.
        
        Returns:
            Dictionary containing the results
        """
        self.status = AgentStatus.EXECUTING
        self.last_active = time.time()
        
        try:
            logger.info(f"Running agent: {self.name}")
            # Implement in subclasses
            pass
        except Exception as e:
            logger.error(f"Error running agent {self.name}: {str(e)}")
            self.status = AgentStatus.ERROR
            self.results = {"error": str(e)}
        
        self.status = AgentStatus.COMPLETED
        return self.results
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent
        
        Returns:
            Dictionary with status information
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "description": self.description,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "target": self.target
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a report of the agent's activities and findings
        
        Returns:
            Dictionary with report data
        """
        # Basic report, should be extended by subclasses
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "description": self.description,
            "target": self.target,
            "created_at": self.created_at,
            "last_active": self.last_active,
            "results": self.results
        }