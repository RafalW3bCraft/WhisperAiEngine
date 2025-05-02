#!/usr/bin/env python3
# G3r4ki - AI-powered Linux system for cybersecurity operations
# Main entry point

import os
import sys
import json
import argparse
import logging
import traceback
from typing import Dict, Any, Optional

# Ensure we're in the project directory
project_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_dir)

from src.cli import G3r4kiCLI
from src.config import setup_config, load_config
from src.system import check_system_requirements
from src.web import run_web_server
from src.exploitation.exploitation_command import handle_exploitation_command
from src.incident_response import (
    IncidentResponseSimulator,
    simulate_incident,
    INCIDENT_TYPES,
    PERSONA_TYPES,
    EXPERIENCE_LEVELS
)
from src.offensive.module_loader import ModuleLoader
# Import installation functions directly into this scope
install_g3r4ki = None
uninstall_g3r4ki = None
update_g3r4ki = None
is_g3r4ki_installed = None

# Try to import from the installer module
try:
    from src.system.installer import (
        install_g3r4ki, 
        uninstall_g3r4ki, 
        update_g3r4ki, 
        is_g3r4ki_installed
    )
except ImportError:
    print("Warning: Installation system not available")

def handle_offensive_module_command(args):
    """
    Handle offensive module commands.
    
    Args:
        args: Command line arguments
    """
    import json
    import os
    
    # Create module loader
    module_loader = ModuleLoader()
    
    # Handle list modules command
    if args.offensive_command == "list":
        # List all available modules
        available_modules = module_loader.get_available_modules()
        
        if not available_modules:
            print("\nNo offensive modules found in the system.")
            print("You may need to install additional offensive modules.")
            return
            
        print("\nG3r4ki Offensive Framework - Available Modules")
        print("=" * 60)
        print(f"Total modules: {len(available_modules)}")
        
        # Group modules by category
        categories = {}
        for module_id, metadata in available_modules.items():
            category = module_id.split('.')[0]
            if category not in categories:
                categories[category] = []
            categories[category].append((module_id, metadata))
            
        # Print modules by category
        for category, modules in categories.items():
            print(f"\n{category.title()}:")
            print("-" * len(category.title()))
            for module_id, metadata in modules:
                print(f"- {module_id}: {metadata.name} (v{metadata.version})")
                print(f"  {metadata.description}")
                print(f"  Platforms: {', '.join(metadata.platforms)}")
                print(f"  Stealth: {metadata.stealth_level}/10, Effectiveness: {metadata.effectiveness}/10")
                
        return
        
    # Handle module info command
    elif args.offensive_command == "info":
        if not hasattr(args, 'module_id') or not args.module_id:
            print("Error: No module ID specified.")
            print("Usage: offensive info <module_id>")
            return
            
        try:
            # Check if module exists
            available_modules = module_loader.get_available_modules()
            if args.module_id not in available_modules:
                print(f"Error: Module '{args.module_id}' not found.")
                return
                
            # Get module metadata
            metadata = available_modules[args.module_id]
            
            print(f"\nModule: {metadata.name} (ID: {metadata.id})")
            print("=" * 60)
            print(f"Version: {metadata.version}")
            print(f"Author: {metadata.author}")
            print(f"Description: {metadata.description}")
            print(f"\nTags: {', '.join(metadata.tags)}")
            print(f"Platforms: {', '.join(metadata.platforms)}")
            print(f"Supported mission types: {', '.join(metadata.supported_mission_types)}")
            print("\nMetrics:")
            print(f"- Stealth Level: {metadata.stealth_level}/10")
            print(f"- Effectiveness: {metadata.effectiveness}/10")
            print(f"- Complexity: {metadata.complexity}/10")
            print("\nResource Requirements:")
            for resource, value in metadata.min_resources.items():
                print(f"- {resource}: {value}")
                
            if metadata.dependencies:
                print("\nDependencies:")
                for dep in metadata.dependencies:
                    print(f"- {dep}")
        except Exception as e:
            print(f"Error reading module info: {e}")
            
        return
        
    # Handle run module command
    elif args.offensive_command == "run":
        if not hasattr(args, 'module_id') or not args.module_id:
            print("Error: No module ID specified.")
            print("Usage: offensive run <module_id> [--option value] [...]")
            return
            
        try:
            # Load module
            print(f"Loading module: {args.module_id}")
            module = module_loader.load_module(args.module_id)
            
            # Prepare options
            options = {}
            
            # Add standard options
            if hasattr(args, 'host') and args.host:
                options['host'] = args.host
            if hasattr(args, 'port') and args.port:
                options['port'] = args.port
            if hasattr(args, 'target') and args.target:
                options['target'] = args.target
            if hasattr(args, 'platform') and args.platform:
                options['platform'] = args.platform
            if hasattr(args, 'output') and args.output:
                options['output'] = args.output
                
            # Add module-specific options
            if hasattr(args, 'options') and args.options:
                for opt in args.options:
                    if '=' in opt:
                        key, value = opt.split('=', 1)
                        options[key] = value
                
            # Create execution context
            context = {
                'target': args.target if hasattr(args, 'target') and args.target else 'localhost',
                'options': options
            }
            
            # Execute module
            print(f"Executing module with options: {options}")
            results = module.execute(context)
            
            # Print results
            print("\nExecution Results:")
            print("-" * 20)
            print(f"Status: {results.get('status', 'unknown')}")
            print(f"Message: {results.get('message', 'No message')}")
            
            # Handle specific module types
            if 'shells' in results:
                print("\nGenerated shells:")
                for shell_type, shell in results['shells'].items():
                    print(f"\n--- {shell_type} ---")
                    # Show a preview of the shell (first 200 chars)
                    preview = shell[:200] + "..." if len(shell) > 200 else shell
                    print(preview)
                    
                # Save shells to files if output directory specified
                if 'output' in options:
                    output_dir = options['output']
                    os.makedirs(output_dir, exist_ok=True)
                    
                    for shell_type, shell in results['shells'].items():
                        # Determine file extension
                        if shell_type in ['bash', 'sh']:
                            ext = '.sh'
                        elif shell_type in ['python', 'python3']:
                            ext = '.py'
                        elif shell_type in ['powershell', 'pwsh']:
                            ext = '.ps1'
                        elif shell_type == 'php':
                            ext = '.php'
                        elif shell_type == 'perl':
                            ext = '.pl'
                        elif shell_type == 'ruby':
                            ext = '.rb'
                        elif shell_type == 'java':
                            ext = '.java'
                        elif shell_type == 'jsp':
                            ext = '.jsp'
                        elif shell_type == 'aspx':
                            ext = '.aspx'
                        elif shell_type == 'golang':
                            ext = '.go'
                        elif shell_type == 'nodejs':
                            ext = '.js'
                        else:
                            ext = '.txt'
                            
                        # Save to file
                        filename = f"{shell_type}_shell{ext}"
                        output_path = os.path.join(output_dir, filename)
                        
                        with open(output_path, 'w') as f:
                            f.write(shell)
                            
                        print(f"Saved {shell_type} shell to {output_path}")
            
            # Save results to file if requested
            if hasattr(args, 'save_results') and args.save_results:
                try:
                    with open(args.save_results, 'w') as f:
                        json.dump(results, f, indent=2)
                    print(f"\nResults saved to: {args.save_results}")
                except Exception as e:
                    print(f"Error saving results: {e}")
                
        except Exception as e:
            print(f"Error executing module: {e}")
            
        return
        
    # Handle mission command
    elif args.offensive_command == "mission":
        if not hasattr(args, 'mission_type') or not args.mission_type:
            # Show available mission types
            print("\nG3r4ki Offensive Framework - Available Mission Types")
            print("=" * 60)
            # Import MISSION_PROFILES directly
            from src.offensive import MISSION_PROFILES
            for mission_type, profile in MISSION_PROFILES.items():
                print(f"\n{mission_type.upper()}:")
                print(f"  {profile['description']}")
                print("\nPriority modules:")
                for module in profile['priority_modules']:
                    print(f"- {module}")
                print("\nAvoided modules:")
                for module in profile['avoid_modules']:
                    print(f"- {module}")
            return
            
        try:
            # Create mission chain
            mission_type = args.mission_type
            target_platform = args.platform if hasattr(args, 'platform') and args.platform else 'linux'
            
            # Default resources
            available_resources = {
                'cpu': 2,
                'memory': 512,
                'disk': 1024
            }
            
            print(f"\nCreating module chain for {mission_type} mission on {target_platform} platform")
            
            # Create module chain
            module_chain = module_loader.create_chain(mission_type, target_platform, available_resources)
            
            print(f"\nGenerated module chain ({len(module_chain)} modules):")
            for i, module_id in enumerate(module_chain):
                if module_id in module_loader.available_modules:
                    metadata = module_loader.available_modules[module_id]
                    print(f"{i+1}. {module_id}: {metadata.name}")
                    print(f"   Stealth: {metadata.stealth_level}/10, Effectiveness: {metadata.effectiveness}/10")
                else:
                    print(f"{i+1}. {module_id} (Not available)")
                    
            # Execute the chain if requested
            if hasattr(args, 'execute') and args.execute:
                if not module_chain:
                    print("\nNo modules in chain to execute.")
                    return
                    
                print("\nExecuting module chain...")
                
                # Create context for execution
                options = {}
                
                # Add standard options
                if hasattr(args, 'host') and args.host:
                    options['host'] = args.host
                if hasattr(args, 'port') and args.port:
                    options['port'] = args.port
                if hasattr(args, 'target') and args.target:
                    options['target'] = args.target
                
                target = args.target if hasattr(args, 'target') and args.target else 'localhost'
                
                # Execute chain
                results = module_loader.execute_module_chain(module_chain, target, options)
                
                print("\nExecution results:")
                for module_id, result in results.items():
                    if isinstance(result, dict) and 'status' in result:
                        print(f"- {module_id}: {result['status']} - {result.get('message', '')}")
                    else:
                        print(f"- {module_id}: {result}")
                        
                # Save results to file if requested
                if hasattr(args, 'save_results') and args.save_results:
                    try:
                        with open(args.save_results, 'w') as f:
                            json.dump(results, f, indent=2)
                        print(f"\nResults saved to: {args.save_results}")
                    except Exception as e:
                        print(f"Error saving results: {e}")
                
        except Exception as e:
            print(f"Error executing mission: {e}")
            
        return
    
    # Handle unknown command
    else:
        print(f"Unknown offensive command: {args.offensive_command}")
        print("Available commands: list, info, run, mission")
        return

def handle_incident_response_command(args):
    """
    Handle incident response commands.
    
    Args:
        args: Command line arguments
    """
    # Basic validation to prevent None access
    if not hasattr(args, 'incident_command') or not args.incident_command:
        print("Error: No incident response command specified.")
        print("Available commands: simulate, list, personas, reports")
        return
    
    # Create a simulator instance
    simulator = IncidentResponseSimulator()
    
    # Handle incident list command
    if args.incident_command == "list":
        incident_types = simulator.get_available_incident_types()
        print("\nAvailable Incident Types for Simulation:")
        print("---------------------------------------")
        for incident_type in incident_types:
            print(f"- {incident_type.replace('_', ' ').title()}")
        return
    
    # Handle personas commands
    elif args.incident_command == "personas":
        # Basic validation to prevent None access
        if not hasattr(args, 'persona_command') or not args.persona_command:
            print("Error: No persona command specified.")
            print("Available commands: list, generate")
            return
            
        # Create persona generator
        persona_generator = simulator.persona_generator
        
        # List available persona types
        if args.persona_command == "list":
            persona_types = persona_generator.get_available_persona_types()
            print("\nAvailable Security Persona Types:")
            print("--------------------------------")
            for persona_type in persona_types:
                print(f"- {persona_type.replace('_', ' ').title()}")
        
        # Generate a security persona
        elif args.persona_command == "generate":
            try:
                # Generate persona
                persona = persona_generator.generate_persona(
                    persona_type=args.type,
                    experience_level=args.experience
                )
                
                # Print persona details
                print(f"\nGenerated Security Persona: {persona.get('name', 'Unnamed')}")
                print(f"Role: {persona.get('role', 'Unknown')}")
                print(f"Experience Level: {persona.get('experience_level', 'Unknown')}")
                print(f"Years of Experience: {persona.get('years_experience', 'Unknown')}")
                print(f"\nBackground:")
                print(f"{persona.get('background', 'No background information available.')}")
                
                print(f"\nSkills:")
                for skill in persona.get('skills', []):
                    print(f"- {skill}")
                
                # Save to file if output specified
                if hasattr(args, 'output') and args.output:
                    import json
                    with open(args.output, 'w') as f:
                        json.dump(persona, f, indent=2)
                    print(f"\nPersona saved to: {args.output}")
            except Exception as e:
                print(f"Error generating persona: {e}")
        
        else:
            print(f"Unknown persona command: {args.persona_command}")
        
        return
    
    # Handle simulation command
    elif args.incident_command == "simulate":
        try:
            # Display a welcome banner
            print("\n" + "=" * 80)
            print("G3r4ki ONE-CLICK INCIDENT RESPONSE SIMULATOR".center(80))
            print("=" * 80)
            print("\nInitializing simulation environment...")
            
            # Determine incident type
            incident_type = None
            if hasattr(args, 'type') and args.type:
                incident_type = args.type
                print(f"Selected incident type: {incident_type.replace('_', ' ').title()}")
            else:
                # Let user select an incident type interactively
                incident_types = simulator.get_available_incident_types()
                print("\nAvailable Incident Types:")
                for i, inc_type in enumerate(incident_types, 1):
                    print(f"{i}. {inc_type.replace('_', ' ').title()}")
                
                try:
                    selection = input("\nSelect an incident type (number or name, press Enter for random): ")
                    if selection.strip():
                        if selection.isdigit() and 1 <= int(selection) <= len(incident_types):
                            incident_type = incident_types[int(selection) - 1]
                        else:
                            # Try to match by name
                            selection = selection.lower().replace(' ', '_')
                            if selection in incident_types:
                                incident_type = selection
                            else:
                                # Find closest match
                                matches = [t for t in incident_types if selection in t]
                                if matches:
                                    incident_type = matches[0]
                                    print(f"Using closest match: {incident_type.replace('_', ' ').title()}")
                                
                    if incident_type:
                        print(f"Selected: {incident_type.replace('_', ' ').title()}")
                    else:
                        print("Using a random incident type")
                except KeyboardInterrupt:
                    print("\nSimulation setup cancelled.")
                    return
            
            # Determine difficulty
            difficulty = "medium"
            if hasattr(args, 'difficulty') and args.difficulty:
                difficulty = args.difficulty
            else:
                # Let user select difficulty interactively
                print("\nDifficulty Levels:")
                print("1. Easy - For beginners, with detailed guidance")
                print("2. Medium - Balanced challenge with some hints")
                print("3. Hard - Challenging scenarios, minimal guidance")
                print("4. Expert - Advanced scenarios, realistic complexity")
                
                try:
                    selection = input("\nSelect difficulty level (1-4, press Enter for Medium): ")
                    if selection.strip():
                        if selection == "1" or selection.lower() == "easy":
                            difficulty = "easy"
                        elif selection == "3" or selection.lower() == "hard":
                            difficulty = "hard"
                        elif selection == "4" or selection.lower() == "expert":
                            difficulty = "expert"
                    print(f"Difficulty set to: {difficulty.title()}")
                except KeyboardInterrupt:
                    print("\nSimulation setup cancelled.")
                    return
            
            # Determine persona
            persona_type = None
            if hasattr(args, 'persona') and args.persona:
                persona_type = args.persona
            else:
                # Ask if user wants a specific persona
                try:
                    # Check if we're in a non-interactive environment
                    import sys
                    if not sys.stdin.isatty():
                        use_specific = 'n'  # Default to no in non-interactive mode
                        print("\nNon-interactive mode detected. Using default persona.")
                    else:
                        use_specific = input("\nWould you like to use a specific security persona? (y/n, default: n): ")
                    if use_specific.lower() == 'y':
                        persona_types = simulator.persona_generator.get_available_persona_types()
                        print("\nAvailable Security Personas:")
                        for i, p_type in enumerate(persona_types, 1):
                            print(f"{i}. {p_type.replace('_', ' ').title()}")
                        
                        # Check for non-interactive mode
                        if not sys.stdin.isatty():
                            print("\nNon-interactive mode. Auto-selecting a default persona type.")
                            selection = "1"  # Default to first persona type
                        else:
                            selection = input("\nSelect a persona type (number or name): ")
                        if selection.strip():
                            if selection.isdigit() and 1 <= int(selection) <= len(persona_types):
                                persona_type = persona_types[int(selection) - 1]
                            else:
                                # Try to match by name
                                selection = selection.lower().replace(' ', '_')
                                if selection in persona_types:
                                    persona_type = selection
                                else:
                                    # Find closest match
                                    matches = [t for t in persona_types if selection in t]
                                    if matches:
                                        persona_type = matches[0]
                        
                        if persona_type:
                            print(f"Using persona type: {persona_type.replace('_', ' ').title()}")
                        else:
                            print("Using auto-generated persona matched to scenario")
                    else:
                        print("Using auto-generated persona matched to scenario")
                except KeyboardInterrupt:
                    print("\nSimulation setup cancelled.")
                    return
            
            print("\nPreparing simulation environment...")
            print("Generating realistic scenario...")
            print("Creating security persona profile...")
            
            # Start the simulation
            simulation = simulator.start_simulation(
                incident_type=incident_type,
                difficulty=difficulty,
                persona_type=persona_type
            )
            
            print("\n" + "=" * 80)
            print(f"INCIDENT RESPONSE SIMULATION: {simulation.get('title', 'Untitled Scenario')}".center(80))
            print("=" * 80)
            print(f"Simulation ID: {simulation.get('simulation_id', 'Unknown')}")
            print(f"Organization: {simulation.get('organization', {}).get('name', 'Unknown Organization')}")
            print(f"Industry: {simulation.get('organization', {}).get('industry', 'Unknown')}")
            
            print("\n📋 SECURITY PERSONA:")
            persona = simulation.get('persona', {})
            print(f"Name: {persona.get('name', 'Unknown')}")
            print(f"Role: {persona.get('role', 'Security Analyst')}")
            print(f"Experience: {persona.get('experience_level', 'intermediate').title()}")
            
            print("\n🚨 INITIAL ALERT:")
            print(simulation.get('initial_alert', 'No alert information available.'))
            
            print("\n🔄 Simulation is now running in interactive mode.")
            print("You'll step through the incident response process.")
            print("At each step, you'll receive information and be asked to respond.")
            print("Type 'exit' at any prompt to end the simulation.")
            
            # Interactive simulation loop
            while True:
                # Get next step
                step = simulator.get_next_step()
                
                # Check if simulation is complete
                if step.get('status') == 'complete':
                    print("\n" + "=" * 60)
                    print("SIMULATION COMPLETE")
                    print("=" * 60)
                    print(step.get('message', 'Simulation has ended.'))
                    
                    # Generate report
                    print("\nGenerating incident report...")
                    report_result = simulator.generate_report()
                    print(f"Report generated: {report_result.get('report_file')}")
                    
                    # Show summary
                    print("\nEXECUTIVE SUMMARY:")
                    summary = report_result.get('report_summary', '')
                    if len(summary) > 500:
                        print(summary[:500] + "...\n(Summary truncated, see full report)")
                    else:
                        print(summary)
                    
                    break
                
                # Display step information
                print("\n" + "-" * 60)
                print(f"STEP {step.get('step_number')}/{step.get('total_steps')}: {step.get('action', 'Action')}")
                print("-" * 60)
                print(f"Description: {step.get('description', 'No description available.')}")
                
                if step.get('technical_details'):
                    print("\nTechnical Details:")
                    print(step.get('technical_details'))
                
                if step.get('guidance'):
                    print("\nGuidance:")
                    guidance = step.get('guidance', '')
                    if guidance and len(guidance) > 300:
                        print(guidance[:300] + "...\n(Guidance truncated)")
                    else:
                        print(guidance or "No guidance available.")
                
                # Get user response
                print("\nWhat actions would you take in this situation? (Type your response, or 'exit' to quit)")
                # Check for non-interactive mode
                if not sys.stdin.isatty():
                    user_response = "Following standard incident response procedures for this type of incident."
                    print(f"Auto-response (non-interactive mode): {user_response}")
                else:
                    user_response = input("> ")
                
                # Check for exit
                if user_response.lower() in ['exit', 'quit']:
                    simulator.end_simulation(reason="User ended simulation")
                    print("Simulation ended by user.")
                    break
                
                # Submit user response
                result = simulator.submit_step_response(user_response)
                
                # Display evaluation
                evaluation = result.get('evaluation', {})
                print("\nEVALUATION:")
                print(f"Score: {evaluation.get('score', 0)}/100")
                
                print("\nStrengths:")
                for strength in evaluation.get('strengths', []):
                    print(f"- {strength}")
                
                print("\nAreas for Improvement:")
                for area in evaluation.get('improvement_areas', []):
                    print(f"- {area}")
                
                print("\nRecommendation:")
                print(evaluation.get('recommendation', 'No recommendation available.'))
                
                # Check if simulation is complete
                if result.get('is_complete', False):
                    print("\n" + "=" * 60)
                    print("SIMULATION COMPLETE")
                    print("=" * 60)
                    print("Final Score:", result.get('final_score', {}).get('overall_score', 0))
                    break
                
                # Pause before next step
                # Check for non-interactive mode
                if not sys.stdin.isatty():
                    print("\nAuto-continuing to next step (non-interactive mode)...")
                else:
                    input("\nPress Enter to continue to the next step...")
                
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user.")
            simulator.end_simulation(reason="User interrupted simulation")
        except Exception as e:
            print(f"Error during simulation: {e}")
            import traceback
            traceback.print_exc()
        
        return
    
    # Handle reports commands
    elif args.incident_command == "reports":
        # Basic validation to prevent None access
        if not hasattr(args, 'report_command') or not args.report_command:
            print("Error: No report command specified.")
            print("Available commands: list, view, generate")
            return
            
        # List available reports
        if args.report_command == "list":
            # Get reports from simulator
            reports_dir = simulator.reports_dir
            reports = []
            
            if os.path.exists(reports_dir):
                for filename in os.listdir(reports_dir):
                    if filename.endswith(".json"):
                        report_path = os.path.join(reports_dir, filename)
                        try:
                            with open(report_path, 'r') as f:
                                report_data = json.load(f)
                                reports.append({
                                    'id': report_data.get('report_id', 'Unknown'),
                                    'title': report_data.get('title', 'Untitled Report'),
                                    'date': report_data.get('generated_at', 'Unknown'),
                                    'file': filename
                                })
                        except Exception as e:
                            print(f"Error reading report {filename}: {e}")
            
            # Display reports
            if reports:
                print("\nAvailable Incident Response Reports:")
                print("=" * 80)
                print(f"{'ID':<15} {'Date':<25} {'Title':<40}")
                print("-" * 80)
                for report in reports:
                    print(f"{report['id']:<15} {report['date'][:19]:<25} {report['title'][:40]}")
                print("\nUse 'g3r4ki.py incident reports view <report_id>' to view a specific report")
            else:
                print("\nNo incident response reports found.")
                print("Use 'g3r4ki.py incident simulate' to run a simulation and generate reports.")
            
            return
            
        # View a specific report
        elif args.report_command == "view":
            if not hasattr(args, 'report_id') or not args.report_id:
                print("Error: No report ID specified.")
                print("Usage: g3r4ki.py incident reports view <report_id>")
                return
                
            reports_dir = simulator.reports_dir
            report_found = False
            
            if os.path.exists(reports_dir):
                for filename in os.listdir(reports_dir):
                    if filename.endswith(".json"):
                        report_path = os.path.join(reports_dir, filename)
                        try:
                            with open(report_path, 'r') as f:
                                report_data = json.load(f)
                                if report_data.get('report_id') == args.report_id:
                                    report_found = True
                                    
                                    # Display report in a nice format
                                    print("\n" + "=" * 80)
                                    print(f"INCIDENT RESPONSE REPORT: {report_data.get('title', 'Untitled')}".center(80))
                                    print("=" * 80)
                                    print(f"Report ID: {report_data.get('report_id', 'Unknown')}")
                                    print(f"Generated: {report_data.get('generated_at', 'Unknown')}")
                                    print(f"Incident Type: {report_data.get('incident_type', 'Unknown').replace('_', ' ').title()}")
                                    print(f"Simulation ID: {report_data.get('simulation_id', 'Unknown')}")
                                    
                                    print("\nEXECUTIVE SUMMARY:")
                                    print("-" * 80)
                                    print(report_data.get('executive_summary', 'No summary available.'))
                                    
                                    print("\nINCIDENT DETAILS:")
                                    print("-" * 80)
                                    print(f"Organization: {report_data.get('organization', {}).get('name', 'Unknown')}")
                                    print(f"Industry: {report_data.get('organization', {}).get('industry', 'Unknown')}")
                                    print(f"Incident Date: {report_data.get('incident_date', 'Unknown')}")
                                    print(f"Detection Date: {report_data.get('detection_date', 'Unknown')}")
                                    
                                    print("\nSCOPE OF COMPROMISE:")
                                    print("-" * 80)
                                    print(report_data.get('scope_of_compromise', 'No information available.'))
                                    
                                    print("\nTECHNICAL ANALYSIS:")
                                    print("-" * 80)
                                    print(report_data.get('technical_analysis', 'No technical analysis available.'))
                                    
                                    print("\nIMPACT ASSESSMENT:")
                                    print("-" * 80)
                                    print(report_data.get('impact_assessment', 'No impact assessment available.'))
                                    
                                    print("\nREMEDIATION STEPS:")
                                    print("-" * 80)
                                    for i, step in enumerate(report_data.get('remediation_steps', []), 1):
                                        print(f"{i}. {step}")
                                    
                                    print("\nRECOMMENDATIONS:")
                                    print("-" * 80)
                                    for i, rec in enumerate(report_data.get('recommendations', []), 1):
                                        print(f"{i}. {rec}")
                                    
                                    print("\nPERFORMANCE EVALUATION:")
                                    print("-" * 80)
                                    print(f"Overall Score: {report_data.get('performance', {}).get('overall_score', 0)}/100")
                                    print(f"Response Time: {report_data.get('performance', {}).get('response_time', 'Unknown')}")
                                    
                                    # Strengths and areas for improvement
                                    print("\nStrengths:")
                                    for strength in report_data.get('performance', {}).get('strengths', []):
                                        print(f"- {strength}")
                                    
                                    print("\nAreas for Improvement:")
                                    for area in report_data.get('performance', {}).get('improvement_areas', []):
                                        print(f"- {area}")
                                    
                                    break
                        except Exception as e:
                            print(f"Error reading report {filename}: {e}")
            
            if not report_found:
                print(f"Report with ID '{args.report_id}' not found.")
                print("Use 'g3r4ki.py incident reports list' to see available reports.")
            
            return
            
        # Generate a new report
        elif args.report_command == "generate":
            if not hasattr(args, 'simulation_id') or not args.simulation_id:
                print("Error: No simulation ID specified.")
                print("Usage: g3r4ki.py incident reports generate <simulation_id>")
                return
                
            try:
                # Generate report
                print(f"Generating report for simulation {args.simulation_id}...")
                report_result = simulator.generate_report(args.simulation_id)
                
                print(f"\nReport generated successfully!")
                print(f"Report ID: {report_result.get('report_id', 'Unknown')}")
                print(f"Report File: {report_result.get('report_file', 'Unknown')}")
                
                # Show summary
                print("\nEXECUTIVE SUMMARY:")
                print("-" * 80)
                summary = report_result.get('report_summary', '')
                if len(summary) > 500:
                    print(summary[:500] + "...\n(Summary truncated, see full report)")
                else:
                    print(summary)
                    
                print("\nUse 'g3r4ki.py incident reports view <report_id>' to view the full report.")
                
            except Exception as e:
                print(f"Error generating report: {e}")
                import traceback
                traceback.print_exc()
            
            return
        
        else:
            print(f"Unknown report command: {args.report_command}")
            print("Available commands: list, view, generate")
        
        return
    
    else:
        print(f"Unknown incident response command: {args.incident_command}")
        print("Available commands: simulate, list, personas, reports")

def main():
    """Main entry point for G3r4ki"""
    parser = argparse.ArgumentParser(
        description="G3r4ki - AI-powered Linux system for cybersecurity operations"
    )
    
    # Global flags
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--config", type=str, help="Path to custom config file")
    
    # Create subparsers for different command groups
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Setup commands
    setup_parser = subparsers.add_parser("setup", help="Setup and configuration")
    setup_parser.add_argument("--check", action="store_true", help="Check system requirements")
    setup_parser.add_argument("--install-deps", action="store_true", help="Install system dependencies")
    setup_parser.add_argument("--setup-voice", action="store_true", help="Setup voice components")
    setup_parser.add_argument("--setup-llms", action="store_true", help="Setup LLM components")
    setup_parser.add_argument("--install-system", action="store_true", help="Install G3r4ki system-wide")
    setup_parser.add_argument("--uninstall-system", action="store_true", help="Uninstall G3r4ki from system")
    setup_parser.add_argument("--update-system", action="store_true", help="Update system-wide G3r4ki installation")
    setup_parser.add_argument("--keep-config", action="store_true", help="Keep user config during uninstallation")
    
    # LLM commands
    llm_parser = subparsers.add_parser("llm", help="LLM operations")
    llm_parser.add_argument("--list", action="store_true", help="List available LLMs and AI providers")
    llm_parser.add_argument("--query", type=str, help="Query an LLM")
    llm_parser.add_argument("--engine", type=str, help="Specify LLM engine (llama.cpp, vllm, gpt4all)")
    llm_parser.add_argument("--model", type=str, help="Specify model name")
    llm_parser.add_argument("--ai", action="store_true", help="Use the unified AI system")
    llm_parser.add_argument("--provider", type=str, help="Specify AI provider")
    llm_parser.add_argument("--system", type=str, help="System prompt for AI")
    
    # Voice commands
    voice_parser = subparsers.add_parser("voice", help="Voice operations")
    voice_parser.add_argument("--stt", type=str, help="Speech to text from audio file")
    voice_parser.add_argument("--tts", type=str, help="Text to speech")
    voice_parser.add_argument("--output", type=str, help="Output file for TTS")
    voice_parser.add_argument("--command", type=str, help="Process voice command from audio file")
    voice_parser.add_argument("--listen", action="store_true", help="Listen for voice command from microphone")
    voice_parser.add_argument("--duration", type=int, default=5, help="Recording duration in seconds for listen mode")
    voice_parser.add_argument("--speak", action="store_true", help="Speak the response")
    
    # Security commands
    sec_parser = subparsers.add_parser("sec", help="Security operations")
    sec_parser.add_argument("--scan", type=str, help="Scan target (IP/domain)")
    sec_parser.add_argument("--recon", type=str, help="Perform reconnaissance on target")
    sec_parser.add_argument("--vuln", type=str, help="Vulnerability scan on target")
    sec_parser.add_argument("--output", type=str, help="Output file for scan results")
    
    # Tool management group
    sec_tools_group = sec_parser.add_argument_group("Tool Management")
    sec_tools_group.add_argument("--tools-list", action="store_true", help="List available security tools")
    sec_tools_group.add_argument("--tools-scan", action="store_true", help="Scan for installed security tools")
    sec_tools_group.add_argument("--tools-info", type=str, help="Get information about a specific tool")
    sec_tools_group.add_argument("--tools-install", type=str, help="Install a tool or category")
    sec_tools_group.add_argument("--tools-categories", action="store_true", help="List available tool categories")
    sec_tools_group.add_argument("--force", action="store_true", help="Force reinstallation when installing tools")
    
    # Interactive mode
    subparsers.add_parser("interactive", help="Start interactive shell")
    
    # Web interface
    web_parser = subparsers.add_parser("web", help="Start web interface")
    web_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    web_parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    web_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    # Offensive Framework commands
    offensive_parser = subparsers.add_parser("offensive", help="G3r4ki Offensive Framework Elite Module operations")
    offensive_subparsers = offensive_parser.add_subparsers(dest="offensive_command", help="Offensive framework command")
    
    # Offensive modules list command
    offensive_list_parser = offensive_subparsers.add_parser("list", help="List available offensive modules")
    
    # Offensive module info command
    offensive_info_parser = offensive_subparsers.add_parser("info", help="Show module information")
    offensive_info_parser.add_argument("module_id", type=str, help="Module ID to show info for")
    
    # Offensive module run command
    offensive_run_parser = offensive_subparsers.add_parser("run", help="Run an offensive module")
    offensive_run_parser.add_argument("module_id", type=str, help="Module ID to run")
    offensive_run_parser.add_argument("--host", type=str, help="Target host or listener address")
    offensive_run_parser.add_argument("--port", type=int, help="Target port or listener port")
    offensive_run_parser.add_argument("--target", type=str, help="Target specification")
    offensive_run_parser.add_argument("--platform", type=str, choices=["linux", "windows", "macos"], help="Target platform")
    offensive_run_parser.add_argument("--output", type=str, help="Output directory for generated files")
    offensive_run_parser.add_argument("--save-results", type=str, help="Save results to JSON file")
    offensive_run_parser.add_argument("--options", type=str, nargs="+", help="Module-specific options (key=value)")
    
    # Offensive mission command
    offensive_mission_parser = offensive_subparsers.add_parser("mission", help="Create and run mission-based module chains")
    offensive_mission_parser.add_argument("--mission-type", type=str, choices=["stealth", "loud", "persistence", "data_extraction"], help="Mission type")
    offensive_mission_parser.add_argument("--target", type=str, help="Target specification")
    offensive_mission_parser.add_argument("--platform", type=str, choices=["linux", "windows", "macos"], help="Target platform")
    offensive_mission_parser.add_argument("--host", type=str, help="Listener host address")
    offensive_mission_parser.add_argument("--port", type=int, help="Listener port")
    offensive_mission_parser.add_argument("--execute", action="store_true", help="Execute the generated module chain")
    offensive_mission_parser.add_argument("--save-results", type=str, help="Save results to JSON file")
    
    # Incident Response commands
    ir_parser = subparsers.add_parser("incident", help="Incident response operations")
    ir_subparsers = ir_parser.add_subparsers(dest="incident_command", help="Incident response command")
    
    # Simulate incident command
    simulate_parser = ir_subparsers.add_parser("simulate", help="Start incident response simulation")
    simulate_parser.add_argument("--type", type=str, help="Type of incident to simulate")
    simulate_parser.add_argument("--difficulty", type=str, default="medium", 
                              choices=["easy", "medium", "hard", "expert"],
                              help="Difficulty level of simulation")
    simulate_parser.add_argument("--persona", type=str, help="Type of security persona to use")
    
    # List incident types command
    ir_list_parser = ir_subparsers.add_parser("list", help="List available incident types")
    
    # Personas commands
    personas_parser = ir_subparsers.add_parser("personas", help="Security persona management")
    personas_subparsers = personas_parser.add_subparsers(dest="persona_command", help="Persona command")
    
    personas_list_parser = personas_subparsers.add_parser("list", help="List available security persona types")
    
    personas_generate_parser = personas_subparsers.add_parser("generate", help="Generate security persona")
    personas_generate_parser.add_argument("type", help="Type of security persona to generate")
    personas_generate_parser.add_argument("--experience", type=str, default="intermediate",
                                      choices=["novice", "junior", "intermediate", "senior", "expert"],
                                      help="Experience level of persona")
    personas_generate_parser.add_argument("--output", type=str, help="Output file for generated persona")
    
    # Reports command
    reports_parser = ir_subparsers.add_parser("reports", help="Incident report management")
    reports_subparsers = reports_parser.add_subparsers(dest="report_command", help="Report command")
    
    reports_list_parser = reports_subparsers.add_parser("list", help="List available incident reports")
    
    reports_view_parser = reports_subparsers.add_parser("view", help="View specific incident report")
    reports_view_parser.add_argument("id", help="ID of the incident report to view")
    
    reports_generate_parser = reports_subparsers.add_parser("generate", help="Generate report for simulation")
    reports_generate_parser.add_argument("simulation_id", help="ID of the simulation to generate report for")
    reports_generate_parser.add_argument("--output", type=str, help="Output file for report")
    
    # Exploitation commands
    exploit_parser = subparsers.add_parser("exploit", help="Exploitation operations")
    exploit_subparsers = exploit_parser.add_subparsers(dest="exploit_command", help="Exploitation command")
    
    # Network scanning command
    scan_parser = exploit_subparsers.add_parser("scan", help="Scan a target")
    scan_parser.add_argument("target", help="Target to scan (IP, hostname, or CIDR)")
    scan_parser.add_argument("--type", default="default", help="Scan type")
    scan_parser.add_argument("--ports", help="Ports to scan (e.g., '22,80,443' or '1-1000')")
    scan_parser.add_argument("--output", help="Output file for scan results")
    
    # FTP scanning command
    ftp_parser = exploit_subparsers.add_parser("ftp", help="FTP scanning operations")
    ftp_subparsers = ftp_parser.add_subparsers(dest="ftp_command", help="FTP command")
    
    ftp_check_parser = ftp_subparsers.add_parser("check", help="Check FTP service")
    ftp_check_parser.add_argument("target", help="Target to check")
    ftp_check_parser.add_argument("--port", type=int, default=21, help="FTP port")
    
    ftp_anon_parser = ftp_subparsers.add_parser("anon", help="Try anonymous FTP login")
    ftp_anon_parser.add_argument("target", help="Target to check")
    ftp_anon_parser.add_argument("--port", type=int, default=21, help="FTP port")
    
    ftp_get_parser = ftp_subparsers.add_parser("get", help="Download file from FTP server")
    ftp_get_parser.add_argument("target", help="Target server")
    ftp_get_parser.add_argument("remote_path", help="Remote file path")
    ftp_get_parser.add_argument("local_path", help="Local destination path")
    ftp_get_parser.add_argument("--port", type=int, default=21, help="FTP port")
    ftp_get_parser.add_argument("--username", default="anonymous", help="FTP username")
    ftp_get_parser.add_argument("--password", default="anonymous@example.com", help="FTP password")
    
    # SMB scanning command
    smb_parser = exploit_subparsers.add_parser("smb", help="SMB scanning operations")
    smb_subparsers = smb_parser.add_subparsers(dest="smb_command", help="SMB command")
    
    smb_check_parser = smb_subparsers.add_parser("check", help="Check SMB service")
    smb_check_parser.add_argument("target", help="Target to check")
    
    smb_enum_parser = smb_subparsers.add_parser("enum", help="Enumerate SMB shares")
    smb_enum_parser.add_argument("target", help="Target to check")
    smb_enum_parser.add_argument("--username", default="", help="SMB username")
    smb_enum_parser.add_argument("--password", default="", help="SMB password")
    
    smb_list_parser = smb_subparsers.add_parser("list", help="List SMB share contents")
    smb_list_parser.add_argument("target", help="Target server")
    smb_list_parser.add_argument("share", help="Share name")
    smb_list_parser.add_argument("--path", default="", help="Directory path within share")
    smb_list_parser.add_argument("--username", default="", help="SMB username")
    smb_list_parser.add_argument("--password", default="", help="SMB password")
    
    # Webshell generation command
    webshell_parser = exploit_subparsers.add_parser("webshell", help="Generate webshells")
    webshell_subparsers = webshell_parser.add_subparsers(dest="webshell_command", help="Webshell command")
    
    webshell_list_parser = webshell_subparsers.add_parser("list", help="List available webshells")
    
    webshell_generate_parser = webshell_subparsers.add_parser("generate", help="Generate webshell")
    webshell_generate_parser.add_argument("type", help="Webshell type (php, asp, aspx, jsp, python)")
    webshell_generate_parser.add_argument("--variant", default="basic", help="Webshell variant")
    webshell_generate_parser.add_argument("--password", help="Password protection")
    webshell_generate_parser.add_argument("--output", help="Output file")
    
    # Privilege escalation command
    privesc_parser = exploit_subparsers.add_parser("privesc", help="Privilege escalation operations")
    privesc_subparsers = privesc_parser.add_subparsers(dest="privesc_command", help="Privilege escalation command")
    
    privesc_scan_parser = privesc_subparsers.add_parser("scan", help="Scan for privilege escalation vectors")
    privesc_scan_parser.add_argument("--output", help="Output file")
    
    privesc_exploit_parser = privesc_subparsers.add_parser("exploit", help="Exploit a privilege escalation vector")
    privesc_exploit_parser.add_argument("--suid", help="SUID binary to exploit")
    
    args = parser.parse_args()
    
    # Initialize configuration
    if args.config:
        config = load_config(args.config)
    else:
        config = setup_config()
    
    # Initialize debug mode
    if args.debug:
        config['debug'] = True
    
    # Check if no command was provided, default to interactive
    if not args.command:
        args.command = "interactive"
    
    # Handle setup commands
    if args.command == "setup":
        if args.check:
            check_system_requirements()
        elif args.install_deps:
            os.system("bash ./scripts/install_deps.sh")
        elif args.setup_voice:
            os.system("bash ./scripts/setup_voice.sh")
        elif args.setup_llms:
            os.system("bash ./scripts/setup_llms.sh")
        elif args.install_system:
            # Install G3r4ki system-wide
            print("Installing G3r4ki system-wide...")
            if install_g3r4ki is not None:
                if install_g3r4ki():
                    print("G3r4ki has been successfully installed system-wide.")
                    print("You can now run 'g3r4ki' from any directory.")
                else:
                    print("Failed to install G3r4ki system-wide.")
                    print("Make sure you have root privileges (try with sudo).")
            else:
                print("Error: Installation system not available.")
                print("Make sure the system module is properly installed.")
        elif args.uninstall_system:
            # Uninstall G3r4ki from system
            print("Uninstalling G3r4ki from system...")
            if uninstall_g3r4ki is not None:
                if uninstall_g3r4ki(keep_user_config=args.keep_config):
                    print("G3r4ki has been successfully uninstalled.")
                    if args.keep_config:
                        print("User configuration files have been preserved.")
                    else:
                        print("All configuration files have been removed.")
                else:
                    print("Failed to uninstall G3r4ki.")
                    print("Make sure you have root privileges (try with sudo).")
            else:
                print("Error: Installation system not available.")
                print("Make sure the system module is properly installed.")
        elif args.update_system:
            # Update G3r4ki installation
            print("Updating G3r4ki installation...")
            if update_g3r4ki is not None:
                if update_g3r4ki():
                    print("G3r4ki has been successfully updated.")
                else:
                    print("Failed to update G3r4ki.")
                    print("Make sure you have root privileges (try with sudo).")
            else:
                print("Error: Installation system not available.")
                print("Make sure the system module is properly installed.")
        else:
            print("Available setup options:")
            print("  --check              : Check system requirements")
            print("  --install-deps       : Install system dependencies")
            print("  --setup-voice        : Setup voice components")
            print("  --setup-llms         : Setup LLM components")
            print("  --install-system     : Install G3r4ki system-wide")
            print("  --uninstall-system   : Uninstall G3r4ki from system")
            print("  --update-system      : Update system-wide G3r4ki installation")
            print("  --keep-config        : Keep user config during uninstallation")
        return
    
    # Initialize CLI and start the appropriate mode
    cli = G3r4kiCLI(config)
    
    if args.command == "interactive":
        cli.start_interactive_mode()
    elif args.command == "llm":
        cli.handle_llm_command(args)
    elif args.command == "voice":
        cli.handle_voice_command(args)
    elif args.command == "sec":
        cli.handle_security_command(args)
    elif args.command == "web":
        print(f"Starting G3r4ki web interface at http://{args.host}:{args.port}")
        run_web_server(host=args.host, port=args.port, debug=args.debug)
    elif args.command == "incident":
        handle_incident_response_command(args)
    elif args.command == "exploit":
        handle_exploitation_command(args)
    elif args.command == "offensive":
        handle_offensive_module_command(args)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting G3r4ki...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        if os.environ.get("G3R4KI_DEBUG", "0") == "1":
            import traceback
            traceback.print_exc()
        sys.exit(1)
