"""
G3r4ki Agent Manager

This module provides the agent management system for G3r4ki.
"""

import logging
import importlib
from typing import Dict, List, Optional, Any, Type

from src.agents.core.base import Agent

# Setup logging
logger = logging.getLogger("g3r4ki.agents.manager")

class AgentManager:
    """
    Agent Manager

    This class manages all agent operations including creation, listing, and execution.
    """
    
    def __init__(self):
        """Initialize the agent manager"""
        self.agents = {}  # Maps agent_id to Agent instances
        self.agent_types = {}  # Maps agent_type to Agent class
        
        # Register built-in agent types
        self._register_default_agent_types()
        
        logger.info("Agent manager initialized")
    
    def _register_default_agent_types(self):
        """Register the default agent types"""
        # Register any built-in agent types here
        # For now, just a placeholder for the structure
        try:
            # Try to import and register the PentestAgent if available
            from src.agents.types.pentest_agent import PentestAgent
            self.register_agent_type("pentest", PentestAgent)
            logger.info("Pentest agent registered")
        except ImportError:
            logger.warning("Pentest agent module not found")
    
    def register_agent_type(self, agent_type: str, agent_class: Type[Agent]):
        """
        Register a new agent type
        
        Args:
            agent_type: Type name
            agent_class: Agent class
        """
        self.agent_types[agent_type] = agent_class
        logger.info(f"Registered agent type: {agent_type}")
    
    def create_agent(self, agent_type: str, name: str, description: Optional[str] = None) -> Agent:
        """
        Create a new agent
        
        Args:
            agent_type: Type of agent to create
            name: Name for the agent
            description: Optional description
            
        Returns:
            Created agent instance
            
        Raises:
            ValueError: If agent type is unknown
        """
        if agent_type not in self.agent_types:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = self.agent_types[agent_type]
        agent = agent_class(name, description)
        
        # Store the agent
        self.agents[agent.agent_id] = agent
        
        logger.info(f"Created agent: {name} ({agent.agent_id}) of type {agent_type}")
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all agents
        
        Returns:
            List of agent status dictionaries
        """
        return [agent.get_status() for agent in self.agents.values()]
    
    def get_agent_types(self) -> List[str]:
        """
        Get available agent types
        
        Returns:
            List of agent type names
        """
        return list(self.agent_types.keys())
    
    def run_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Run an agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Results from the agent execution
            
        Raises:
            ValueError: If agent not found
        """
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        
        logger.info(f"Running agent: {agent.name} ({agent_id})")
        return agent.run()
    
    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent
        
        Args:
            agent_id: Agent ID
            
        Returns:
            True if agent was removed, False if not found
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            del self.agents[agent_id]
            logger.info(f"Removed agent: {agent.name} ({agent_id})")
            return True
        
        logger.warning(f"Agent not found for removal: {agent_id}")
        return False