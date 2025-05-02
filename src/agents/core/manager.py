"""
G3r4ki Agent Manager

This module provides the Agent Manager, which handles the lifecycle of multiple agents,
including creation, tracking, and coordination between agents.
"""

import os
import json
import logging
import threading
from typing import Dict, List, Any, Optional, Union, Type

from src.agents.core.base import Agent, AgentStatus

# Setup logging
logger = logging.getLogger('g3r4ki.agents.manager')

class AgentManager:
    """
    Manages multiple agents, their lifecycle, and coordination
    
    Attributes:
        agents: Dictionary of active agents
        config: Configuration dictionary
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize agent manager
        
        Args:
            config: Configuration dictionary
        """
        self.agents = {}  # agent_id -> agent instance
        self.config = config
        
        # Agent registry of available agent types
        self.agent_registry = {}  # agent_type -> agent_class
        
        # State directory for persistence
        self.state_dir = os.path.expanduser(
            config.get('agents', {}).get('state_dir', '~/.local/share/g3r4ki/agents')
        )
        os.makedirs(self.state_dir, exist_ok=True)
        
        # Locks for thread safety
        self._agents_lock = threading.RLock()
        
        logger.info("Agent manager initialized")
    
    def register_agent_type(self, agent_type: str, agent_class: Type[Agent]) -> bool:
        """
        Register an agent type with its implementing class
        
        Args:
            agent_type: Type identifier for the agent
            agent_class: Class implementing the agent
            
        Returns:
            True if successful, False otherwise
        """
        if agent_type in self.agent_registry:
            logger.warning(f"Agent type '{agent_type}' already registered, overwriting")
        
        self.agent_registry[agent_type] = agent_class
        logger.debug(f"Registered agent type '{agent_type}'")
        return True
    
    def create_agent(self, 
                     agent_type: str, 
                     name: str, 
                     description: str, 
                     agent_config: Optional[Dict[str, Any]] = None) -> Optional[Agent]:
        """
        Create a new agent of the specified type
        
        Args:
            agent_type: Type of agent to create
            name: Name for the agent
            description: Description of the agent
            agent_config: Agent-specific configuration
            
        Returns:
            Created agent instance or None if creation failed
        """
        if agent_type not in self.agent_registry:
            logger.error(f"Unknown agent type: {agent_type}")
            return None
        
        try:
            # Merge agent-specific config with global config
            merged_config = dict(self.config)
            if agent_config:
                merged_config.update(agent_config)
            
            # Create agent instance
            agent = self.agent_registry[agent_type](
                name=name,
                description=description,
                config=merged_config
            )
            
            # Register the agent
            with self._agents_lock:
                self.agents[agent.agent_id] = agent
            
            logger.info(f"Created agent '{name}' of type '{agent_type}' with ID {agent.agent_id}")
            return agent
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            return None
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID
        
        Args:
            agent_id: ID of the agent to retrieve
            
        Returns:
            Agent instance or None if not found
        """
        with self._agents_lock:
            return self.agents.get(agent_id)
    
    def get_agents_by_name(self, name: str) -> List[Agent]:
        """
        Get agents by name
        
        Args:
            name: Name to search for
            
        Returns:
            List of matching agents
        """
        with self._agents_lock:
            return [agent for agent in self.agents.values() if agent.name == name]
    
    def get_agents_by_status(self, status: AgentStatus) -> List[Agent]:
        """
        Get agents by status
        
        Args:
            status: Status to filter by
            
        Returns:
            List of matching agents
        """
        with self._agents_lock:
            return [agent for agent in self.agents.values() if agent.status == status]
    
    def run_agent(self, agent_id: str, async_run: bool = False) -> Union[bool, threading.Thread]:
        """
        Run an agent by ID
        
        Args:
            agent_id: ID of the agent to run
            async_run: Whether to run asynchronously
            
        Returns:
            If async_run is False, returns success status
            If async_run is True, returns Thread object
        """
        agent = self.get_agent(agent_id)
        if not agent:
            logger.error(f"Agent not found: {agent_id}")
            return False
        
        if async_run:
            thread = threading.Thread(target=agent.run)
            thread.daemon = True
            thread.start()
            logger.info(f"Started agent '{agent.name}' ({agent_id}) asynchronously")
            return thread
        else:
            success, _ = agent.run()
            return success
    
    def stop_agent(self, agent_id: str) -> bool:
        """
        Stop an agent by ID
        
        Args:
            agent_id: ID of the agent to stop
            
        Returns:
            True if successful, False otherwise
        """
        agent = self.get_agent(agent_id)
        if not agent:
            logger.error(f"Agent not found: {agent_id}")
            return False
        
        # Set status to paused
        agent.status = AgentStatus.PAUSED
        agent.save_state()
        
        # Note: This doesn't actually stop execution if the agent is running
        # in a separate thread. The agent code needs to check its status
        # periodically and terminate execution if status is PAUSED.
        
        logger.info(f"Stopped agent '{agent.name}' ({agent_id})")
        return True
    
    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove an agent by ID
        
        Args:
            agent_id: ID of the agent to remove
            
        Returns:
            True if successful, False otherwise
        """
        with self._agents_lock:
            if agent_id not in self.agents:
                logger.error(f"Agent not found: {agent_id}")
                return False
            
            agent = self.agents[agent_id]
            del self.agents[agent_id]
            
            logger.info(f"Removed agent '{agent.name}' ({agent_id})")
            return True
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all active agents
        
        Returns:
            List of agent information dictionaries
        """
        with self._agents_lock:
            return [
                {
                    "id": agent.agent_id,
                    "name": agent.name,
                    "description": agent.description,
                    "status": agent.status.value,
                    "created_at": agent.created_at.isoformat(),
                    "last_action_time": agent.last_action_time.isoformat()
                }
                for agent in self.agents.values()
            ]
    
    def save_all_agents(self) -> bool:
        """
        Save state of all agents
        
        Returns:
            True if all agents were saved successfully, False otherwise
        """
        success = True
        with self._agents_lock:
            for agent in self.agents.values():
                if not agent.save_state():
                    success = False
        
        return success
    
    def load_agent(self, agent_id: str, agent_type: str) -> Optional[Agent]:
        """
        Load an agent from disk
        
        Args:
            agent_id: ID of the agent to load
            agent_type: Type of the agent to load
            
        Returns:
            Loaded agent or None if not found
        """
        if agent_type not in self.agent_registry:
            logger.error(f"Unknown agent type: {agent_type}")
            return None
        
        agent_class = self.agent_registry[agent_type]
        agent = agent_class.load_state(agent_id, self.config)
        
        if agent:
            with self._agents_lock:
                self.agents[agent.agent_id] = agent
            
            logger.info(f"Loaded agent '{agent.name}' ({agent_id})")
        
        return agent
    
    def load_all_agents(self) -> int:
        """
        Load all agent states from disk
        
        Returns:
            Number of agents loaded successfully
        """
        if not os.path.exists(self.state_dir):
            logger.warning(f"Agent state directory does not exist: {self.state_dir}")
            return 0
        
        count = 0
        for filename in os.listdir(self.state_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.state_dir, filename), 'r') as f:
                        state_data = json.load(f)
                    
                    agent_id = state_data.get('agent_id')
                    if not agent_id:
                        continue
                    
                    # We need to know the agent type, which is not stored in the state file
                    # In a real implementation, we would need to store this information
                    # For now, we'll skip loading agents from disk
                    
                    # The following is commented out because we don't have agent type info
                    # agent = self.load_agent(agent_id, agent_type)
                    # if agent:
                    #     count += 1
                    
                except Exception as e:
                    logger.error(f"Error loading agent state from {filename}: {str(e)}")
        
        return count