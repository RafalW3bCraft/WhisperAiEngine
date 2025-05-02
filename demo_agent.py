#!/usr/bin/env python3
"""
Demo script to show the G3r4ki agent system in action
"""

import os
import sys
import json
import time
from datetime import datetime

# Add the current directory to the path so G3r4ki modules can be imported
sys.path.insert(0, os.getcwd())

from src.config import load_config
from src.agents.core import AgentManager
from src.agents.types.recon_agent import ReconAgent
from src.agents.types.security_agent import SecurityAgent

def main():
    """Run the agent system demo"""
    print("\n===== G3r4ki Agent System Demo =====\n")
    
    # Load configuration
    config = load_config()
    
    # Initialize agent manager
    agent_manager = AgentManager(config)
    
    # Register agent types
    agent_manager.register_agent_type("recon", ReconAgent)
    agent_manager.register_agent_type("security", SecurityAgent)
    
    print("Agent system initialized")
    
    # Show agent status
    print("\n--- Agent Status ---")
    agent_count = len(agent_manager.list_agents())
    print(f"Active Agents: {agent_count}")
    print(f"Agent Types: recon, security")
    
    # Create a new agent
    target = "example.com"
    agent_name = f"demo-recon-{int(time.time())}"
    print(f"\n--- Creating Agent ---")
    print(f"Creating recon agent '{agent_name}' targeting {target}...")
    
    agent = agent_manager.create_agent(
        agent_type="recon",
        name=agent_name,
        description=f"Demo reconnaissance agent for target {target}"
    )
    
    if agent:
        # Configure the agent
        agent.set_target(target)
        print(f"Agent created with ID: {agent.agent_id}")
        
        # List the agents
        print("\n--- Listing Agents ---")
        agents = agent_manager.list_agents()
        for agent_info in agents:
            print(f"ID: {agent_info['id']}")
            print(f"Name: {agent_info['name']}")
            print(f"Status: {agent_info['status']}")
            print(f"Created: {agent_info['created_at']}")
            print()
        
        # Generate the plan
        print(f"\n--- Agent Planning ---")
        print("Generating reconnaissance plan...")
        plan = agent.plan()
        
        if "steps" in plan and plan["steps"]:
            print(f"Plan generated with {len(plan['steps'])} steps:")
            for step in plan["steps"]:
                print(f"  Step {step.get('id')}: {step.get('name')} - using {step.get('skill')}")
        else:
            print("No steps in the plan or error occurred.")
        
        # Run the agent
        print("\n--- Running Agent ---")
        print(f"Would normally execute the agent with: agent_manager.run_agent('{agent.agent_id}')")
        print("(Not running automatically to prevent actual scanning)")
        
        # Generate a report
        print("\n--- Generating Report ---")
        print("Would normally generate a report with: agent.generate_report()")
        print("(Not generating automatically since scan wasn't performed)")
        
        # Results would be in the 'results/' directory
        print("\nResults would be stored in the following directories:")
        print("- results/recon/ - Reconnaissance results")
        print("- results/scans/ - Port scan results")
        print("- results/vuln/ - Vulnerability scan results")
    
    print("\n===== Demo Complete =====\n")
    
if __name__ == "__main__":
    main()