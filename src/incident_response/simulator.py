"""
G3r4ki Incident Response Simulator.

This module provides a comprehensive incident response simulation environment
for cybersecurity training and education.
"""

import os
import json
import re
import random
import logging
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

from src.ai.ai_proxy import AIProxy
from src.config import load_config
from src.incident_response.personas import SecurityPersonaGenerator, PERSONA_TYPES, EXPERIENCE_LEVELS
from src.incident_response.reporting import IncidentReport

logger = logging.getLogger(__name__)

# List of available incident types
INCIDENT_TYPES = [
    'malware_infection', 
    'ransomware_attack', 
    'data_breach', 
    'ddos_attack',
    'phishing_attack', 
    'insider_threat', 
    'unauthorized_access', 
    'privilege_escalation',
    'zero_day_exploit', 
    'social_engineering', 
    'supply_chain_attack', 
    'credential_compromise',
    'web_application_attack', 
    'iot_device_compromise', 
    'cloud_security_breach', 
    'network_intrusion'
]

# Map difficulty levels to guidance parameters
DIFFICULTY_SETTINGS = {
    'easy': {
        'guidance_level': 'detailed',
        'step_count': 6,
        'error_forgiveness': 0.8,
        'evaluation_strictness': 0.3
    },
    'medium': {
        'guidance_level': 'moderate',
        'step_count': 8,
        'error_forgiveness': 0.5,
        'evaluation_strictness': 0.6
    },
    'hard': {
        'guidance_level': 'minimal',
        'step_count': 10,
        'error_forgiveness': 0.3,
        'evaluation_strictness': 0.8
    },
    'expert': {
        'guidance_level': 'none',
        'step_count': 12,
        'error_forgiveness': 0.1,
        'evaluation_strictness': 0.95
    }
}

def simulate_incident(incident_type: str, difficulty: str = 'medium') -> Dict[str, Any]:
    """
    Quick utility function to simulate an incident without creating a full simulator.
    
    Args:
        incident_type: Type of incident to simulate
        difficulty: Difficulty level (easy, medium, hard, expert)
        
    Returns:
        Simulation results
    """
    simulator = IncidentResponseSimulator()
    simulation = simulator.start_simulation(incident_type=incident_type, difficulty=difficulty)
    
    print(f"\nSimulating {incident_type.replace('_', ' ').title()} incident...")
    print(f"Difficulty: {difficulty.title()}")
    print(f"Organization: {simulation.get('organization', {}).get('name', 'Unknown Organization')}")
    print(f"Simulation ID: {simulation.get('simulation_id', 'Unknown')}")
    
    return simulation


class IncidentResponseSimulator:
    """
    Incident Response Simulator
    
    This class manages incident response simulations, allowing users to practice
    responding to various cybersecurity incidents in a realistic environment.
    """
    
    def __init__(self):
        """Initialize the incident response simulator"""
        # Load configuration
        self.config = load_config()
        
        # Load AI proxy for scenario generation
        self.ai_proxy = AIProxy(self.config)
        
        # Initialize persona generator
        self.persona_generator = SecurityPersonaGenerator(self.ai_proxy)
        
        # Initialize report generator
        self.report_generator = IncidentReport(self.ai_proxy)
        
        # Set up directories
        self.base_dir = os.path.expanduser(self.config.get('incident_response_dir', '~/.g3r4ki/incident_response'))
        self.scenarios_dir = os.path.join(self.base_dir, 'scenarios')
        self.reports_dir = os.path.join(self.base_dir, 'reports')
        
        os.makedirs(self.scenarios_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Current simulation state
        self.current_simulation = None
        self.current_step = 0
        self.total_steps = 0
        self.user_responses = []
        self.step_evaluations = []
        self.simulation_complete = False
    
    def get_available_incident_types(self) -> List[str]:
        """
        Get a list of available incident types.
        
        Returns:
            List of incident type names
        """
        return INCIDENT_TYPES
    
    def generate_scenario(self, incident_type: str, difficulty: str = 'medium', persona_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a new incident response scenario.
        
        Args:
            incident_type: Type of incident
            difficulty: Difficulty level (easy, medium, hard, expert)
            persona_type: Optional type of security persona to use
            
        Returns:
            Generated scenario data
        """
        logger.info(f"Generating {incident_type} scenario with {difficulty} difficulty")
        
        # Validate incident type
        if incident_type not in INCIDENT_TYPES:
            raise ValueError(f"Unknown incident type: {incident_type}. Available types: {', '.join(INCIDENT_TYPES)}")
        
        # Validate difficulty
        if difficulty not in DIFFICULTY_SETTINGS:
            raise ValueError(f"Unknown difficulty: {difficulty}. Available difficulties: {', '.join(DIFFICULTY_SETTINGS.keys())}")
        
        # Generate persona if not specified
        if persona_type and persona_type not in PERSONA_TYPES:
            logger.warning(f"Unknown persona type: {persona_type}. Using auto-generated persona.")
            persona_type = None
        
        # Create persona
        if not persona_type:
            # Select persona type based on incident type
            # For example, ransomware attacks work well with incident responders
            persona_mapping = {
                'ransomware_attack': ['incident_responder', 'malware_analyst', 'forensic_analyst'],
                'data_breach': ['security_analyst', 'incident_responder', 'compliance_officer'],
                'phishing_attack': ['security_analyst', 'threat_hunter', 'red_team_operator'],
                'social_engineering': ['security_consultant', 'red_team_operator', 'security_awareness_trainer'],
                'malware_infection': ['malware_analyst', 'security_analyst', 'forensic_analyst'],
                'privilege_escalation': ['security_engineer', 'soc_manager', 'blue_team_defender'],
                'web_application_attack': ['security_engineer', 'penetration_tester', 'devsecops_engineer']
            }
            
            if incident_type in persona_mapping:
                persona_type = random.choice(persona_mapping[incident_type])
            else:
                persona_type = random.choice(PERSONA_TYPES)
        
        # Select experience level based on difficulty
        experience_mapping = {
            'easy': ['novice', 'junior'],
            'medium': ['junior', 'intermediate'],
            'hard': ['intermediate', 'senior'],
            'expert': ['senior', 'expert']
        }
        experience_level = random.choice(experience_mapping[difficulty])
        
        # Generate persona
        persona = self.persona_generator.generate_persona(
            persona_type=persona_type,
            experience_level=experience_level
        )
        
        # Generate organization details
        organization_types = [
            "Healthcare Provider", "Financial Institution", "Technology Company", 
            "Government Agency", "Educational Institution", "Retail Corporation",
            "Manufacturing Company", "Energy Utility", "Transportation Service",
            "Media Organization", "Legal Firm", "Non-Profit Organization",
            "Insurance Provider", "E-commerce Platform", "Hospitality Service"
        ]
        
        organization_name_prefixes = [
            "Global", "Advanced", "United", "Secure", "Innovative", "National", 
            "Strategic", "Universal", "Dynamic", "Premier", "Elite", "Pacific", 
            "Atlantic", "Metropolitan", "Continental", "Integrated", "Digital", 
            "Precision", "Allied", "Summit", "Horizon", "Sapphire", "Emerald", 
            "Crystal", "Platinum", "Golden", "Silver", "Azure", "Vertex", "Apex"
        ]
        
        organization_name_suffixes = [
            "Systems", "Solutions", "Technologies", "Enterprises", "Industries", 
            "Corporation", "Group", "Partners", "Associates", "Networks", "Services", 
            "Applications", "Platforms", "Dynamics", "Innovations", "Consultants", 
            "International", "Global", "Data", "Security", "Healthcare", "Financial", 
            "Energy", "Communications", "Logistics", "Resources", "Materials", "Institute"
        ]
        
        org_type = random.choice(organization_types)
        org_name = f"{random.choice(organization_name_prefixes)} {random.choice(organization_name_suffixes)}"
        
        # Determine industries based on organization type
        industry_mapping = {
            "Healthcare Provider": "Healthcare",
            "Financial Institution": "Finance",
            "Technology Company": "Technology",
            "Government Agency": "Government",
            "Educational Institution": "Education",
            "Retail Corporation": "Retail",
            "Manufacturing Company": "Manufacturing",
            "Energy Utility": "Energy",
            "Transportation Service": "Transportation",
            "Media Organization": "Media",
            "Legal Firm": "Legal",
            "Non-Profit Organization": "Non-Profit",
            "Insurance Provider": "Insurance",
            "E-commerce Platform": "E-commerce",
            "Hospitality Service": "Hospitality"
        }
        industry = industry_mapping.get(org_type, "Technology")
        
        # Generate organization size
        org_sizes = {
            "small": {
                "employees_range": "50-200",
                "annual_revenue": "$5-20 million",
                "infrastructure": "Small IT team, primarily cloud-based, limited security resources"
            },
            "medium": {
                "employees_range": "201-1000",
                "annual_revenue": "$20-100 million",
                "infrastructure": "Dedicated IT department, hybrid cloud/on-premises, growing security capabilities"
            },
            "large": {
                "employees_range": "1001-10000",
                "annual_revenue": "$100 million - $1 billion",
                "infrastructure": "Robust IT division, complex hybrid environment, established security operation center"
            },
            "enterprise": {
                "employees_range": "10000+",
                "annual_revenue": "$1 billion+",
                "infrastructure": "Global IT infrastructure, distributed data centers, comprehensive security operations"
            }
        }
        org_size = random.choice(list(org_sizes.keys()))
        
        # Create organization object
        organization = {
            "name": org_name,
            "type": org_type,
            "industry": industry,
            "size": org_size,
            "details": org_sizes[org_size]
        }
        
        # Set up difficulty parameters
        difficulty_params = DIFFICULTY_SETTINGS[difficulty]
        
        # Generate simulation ID
        simulation_id = f"SIM-{incident_type[:3].upper()}-{str(uuid.uuid4())[:8]}"
        
        # Now use AI to generate the scenario details
        system_prompt = f"""
        You are an expert incident response scenario creator for cybersecurity training.
        Generate a realistic {incident_type.replace('_', ' ')} incident scenario for a {difficulty} difficulty level training exercise.
        
        The scenario should be for {organization['name']}, a {organization['type']} in the {organization['industry']} industry.
        Organization size: {organization['size']} ({organization['details']['employees_range']} employees, {organization['details']['annual_revenue']} annual revenue).
        Infrastructure: {organization['details']['infrastructure']}
        
        The security persona responding to this incident is:
        Name: {persona['name']}
        Role: {persona['role']}
        Experience: {persona['experience_level']} level ({persona['years_experience']} years experience)
        
        Create a realistic scenario with:
        1. A detailed incident description
        2. Initial alerts or indicators of compromise
        3. Affected systems and potential impact
        4. Technical details appropriate for {difficulty} difficulty
        5. Timeline of events
        
        Format the response as a valid JSON object with the following structure:
        {{
            "title": "Brief incident title",
            "description": "Detailed description of the incident",
            "initial_alert": "The first alert or indicator that was detected",
            "affected_systems": ["List of affected systems"],
            "potential_impact": "Potential business impact of the incident",
            "technical_details": "Technical details about the attack/incident",
            "timeline": [
                {{ "timestamp": "YYYY-MM-DD HH:MM:SS", "event": "Description of what happened" }}
            ],
            "ioc_indicators": ["List of indicators of compromise"],
            "attacker_profile": "Information about the attacker (if known)",
            "recommended_steps": ["List of recommended response steps"]
        }}
        
        Make the scenario challenging but realistic, with appropriate technical details for a {persona['experience_level']} {persona['role']}.
        """
        
        user_prompt = f"Generate a detailed, realistic {incident_type.replace('_', ' ')} incident scenario for cybersecurity training."
        
        try:
            # Query AI with fallback to different providers
            provider_order = ['openai', 'anthropic', 'deepseek']
            response = None
            
            for provider_id in provider_order:
                if self.ai_proxy.is_provider_available(provider_id):
                    try:
                        result = self.ai_proxy.query(
                            provider_id=provider_id,
                            prompt=user_prompt,
                            system_prompt=system_prompt,
                            max_tokens=2048,
                            temperature=0.7
                        )
                        response = result.get('response', '')
                        break
                    except Exception as e:
                        logger.warning(f"Failed to query {provider_id}: {e}")
                        continue
            
            if not response:
                raise ValueError("No AI providers available to generate scenario")
            
            # Extract JSON from response
            scenario_data = None
            
            # Try to parse response as JSON directly
            try:
                scenario_data = json.loads(response)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON from text response
                json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
                if json_match:
                    try:
                        scenario_data = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        # One more attempt with stripped lines
                        try:
                            cleaned_json = '\n'.join(line.strip() for line in json_match.group(1).split('\n'))
                            scenario_data = json.loads(cleaned_json)
                        except json.JSONDecodeError:
                            raise ValueError("Could not extract JSON from response")
                else:
                    # Look for just the JSON object
                    json_match = re.search(r'({[\s\S]*?})', response)
                    if json_match:
                        try:
                            scenario_data = json.loads(json_match.group(1))
                        except json.JSONDecodeError:
                            raise ValueError("Could not extract JSON from response")
                    else:
                        scenario_data = response
            
            # Add metadata
            scenario_data['generated_at'] = datetime.now().isoformat()
            scenario_data['incident_id'] = f"INC-{incident_type[:3].upper()}-{random.randint(10000, 99999)}"
            scenario_data['simulation_id'] = simulation_id
            scenario_data['incident_type'] = incident_type
            scenario_data['difficulty'] = difficulty
            scenario_data['persona'] = persona
            scenario_data['organization'] = organization
            scenario_data['total_steps'] = difficulty_params['step_count']
            
            # Save scenario to file
            scenario_file = os.path.join(
                self.scenarios_dir, 
                f"{incident_type}_{scenario_data['incident_id']}.json"
            )
            with open(scenario_file, 'w') as f:
                json.dump(scenario_data, f, indent=2)
                
            return scenario_data
            
        except Exception as e:
            logger.error(f"Failed to generate scenario: {e}")
            raise ValueError(f"Failed to generate scenario: {e}")
    
    def start_simulation(self, 
                        incident_type: Optional[str] = None,
                        scenario_id: Optional[str] = None,
                        persona_type: Optional[str] = None,
                        difficulty: str = "medium") -> Dict[str, Any]:
        """
        Start a new incident response simulation.
        
        Args:
            incident_type: Type of incident to simulate (if generating new scenario)
            scenario_id: Existing scenario ID to use (instead of generating)
            persona_type: Type of security persona to use
            difficulty: Difficulty level (easy, medium, hard, expert)
            
        Returns:
            Simulation data
        """
        logger.info(f"Starting simulation with difficulty {difficulty}")
        
        if scenario_id:
            # Try to load existing scenario
            scenario_files = [
                os.path.join(self.scenarios_dir, f)
                for f in os.listdir(self.scenarios_dir)
                if f.endswith(".json") and scenario_id in f
            ]
            
            if not scenario_files:
                raise ValueError(f"No scenario found with ID: {scenario_id}")
            
            with open(scenario_files[0], 'r') as f:
                self.current_simulation = json.load(f)
                
        else:
            # Choose random incident type if not specified
            if not incident_type:
                incident_type = random.choice(INCIDENT_TYPES)
            
            # Generate new scenario
            self.current_simulation = self.generate_scenario(
                incident_type=incident_type,
                difficulty=difficulty,
                persona_type=persona_type
            )
        
        # Initialize simulation state
        self.current_step = 0
        self.total_steps = self.current_simulation.get('total_steps', 8)
        self.user_responses = []
        self.step_evaluations = []
        self.simulation_complete = False
        self.current_simulation['steps'] = []
        
        logger.info(f"Simulation started: {self.current_simulation.get('title')}")
        return self.current_simulation
    
    def get_next_step(self) -> Dict[str, Any]:
        """
        Get the next step in the current simulation.
        
        Returns:
            Step data
        """
        if not self.current_simulation:
            raise ValueError("No active simulation")
            
        if self.simulation_complete:
            return {
                'status': 'complete',
                'message': 'Simulation is complete. No more steps available.'
            }
            
        self.current_step += 1
        difficulty = self.current_simulation.get('difficulty', 'medium')
        guidance_level = DIFFICULTY_SETTINGS[difficulty]['guidance_level']
        
        # Define step based on standard incident response framework and progress
        step_templates = [
            # Step 1: Initial Triage
            {
                'step_number': 1,
                'action': 'Initial Triage',
                'description': 'Perform initial triage of the incident to determine its scope and severity.',
                'technical_details': f"You've received an alert about a potential {self.current_simulation.get('incident_type', 'security incident').replace('_', ' ')}. Initial indicators suggest {self.current_simulation.get('initial_alert', 'suspicious activity')}",
                'guidance': {
                    'detailed': 'You should classify the incident, determine its severity and scope. Document all initial findings and establish whether this is a true positive or false positive. Check affected systems and estimate potential impact.',
                    'moderate': 'Classify the incident and determine its severity. Validate whether this is a true security incident and identify affected systems.',
                    'minimal': 'Assess the incident and determine if it requires further investigation.',
                    'none': ''
                }
            },
            # Step 2: Containment
            {
                'step_number': 2,
                'action': 'Containment',
                'description': 'Implement containment measures to prevent the incident from spreading or causing further damage.',
                'technical_details': f"The incident involves {self.current_simulation.get('affected_systems', ['unknown systems'])} with potential impact including {self.current_simulation.get('potential_impact', 'unknown impact')}.",
                'guidance': {
                    'detailed': 'Isolate affected systems from the network. Consider implementing network blocks, disabling compromised accounts, or stopping affected services. Document all containment actions taken and their timestamps.',
                    'moderate': 'Contain the spread of the incident by isolating affected systems and implementing appropriate blocks.',
                    'minimal': 'Apply containment measures to prevent further damage.',
                    'none': ''
                }
            },
            # Step 3: Evidence Collection
            {
                'step_number': 3,
                'action': 'Evidence Collection',
                'description': 'Collect and preserve evidence for analysis and potential legal proceedings.',
                'technical_details': f"You need to gather evidence from affected systems, including {self.current_simulation.get('ioc_indicators', ['logs', 'memory dumps', 'network traffic'])}.",
                'guidance': {
                    'detailed': 'Collect system logs, memory dumps, network traffic captures, and other relevant data. Ensure proper chain of custody and use forensically sound methods. Document all evidence collected with timestamps.',
                    'moderate': 'Gather logs and evidence from affected systems using forensic best practices.',
                    'minimal': 'Collect relevant evidence for further analysis.',
                    'none': ''
                }
            },
            # Step 4: Threat Analysis
            {
                'step_number': 4,
                'action': 'Threat Analysis',
                'description': 'Analyze the threat to determine the attack vector, techniques used, and potential impact.',
                'technical_details': f"Technical analysis shows {self.current_simulation.get('technical_details', 'unknown details')}.",
                'guidance': {
                    'detailed': 'Identify the attack vector and techniques used. Determine the indicators of compromise (IoCs) and the timeline of events. Use threat intelligence to identify known attackers or campaigns.',
                    'moderate': 'Analyze the attack vector, techniques, and timeline to understand how the incident occurred.',
                    'minimal': 'Determine how the attack was conducted and identify all compromised assets.',
                    'none': ''
                }
            },
            # Step 5: Impact Assessment
            {
                'step_number': 5,
                'action': 'Impact Assessment',
                'description': 'Assess the impact of the incident on systems, data, users, and the organization.',
                'technical_details': f"You need to determine the full impact of this {self.current_simulation.get('incident_type', 'incident').replace('_', ' ')} on the organization.",
                'guidance': {
                    'detailed': 'Quantify the impact on systems, data, users, and business processes. Determine if any sensitive data was compromised or stolen. Calculate downtime costs and regulatory implications.',
                    'moderate': 'Assess the operational, financial, and reputational impact of the incident.',
                    'minimal': 'Determine what was affected and the severity of the impact.',
                    'none': ''
                }
            },
            # Step 6: Eradication
            {
                'step_number': 6,
                'action': 'Eradication',
                'description': 'Remove the threat from the environment and eliminate any persistence mechanisms.',
                'technical_details': f"The attacker profile suggests {self.current_simulation.get('attacker_profile', 'unknown attacker')} with potential persistence mechanisms in place.",
                'guidance': {
                    'detailed': 'Remove malware, close vulnerabilities, update software, and eliminate all attacker persistence mechanisms. Verify that all compromised accounts are secured and reset. Scan for any remaining indicators of compromise.',
                    'moderate': 'Remove the threat completely and eliminate any backdoors or persistence mechanisms.',
                    'minimal': 'Clean affected systems and remove any attacker access.',
                    'none': ''
                }
            },
            # Step 7: Recovery
            {
                'step_number': 7,
                'action': 'Recovery',
                'description': 'Restore affected systems to normal operation and verify their security.',
                'technical_details': f"Systems that need recovery include {', '.join(self.current_simulation.get('affected_systems', ['unknown systems']))}.",
                'guidance': {
                    'detailed': 'Restore systems from clean backups, verify data integrity, and implement additional security controls. Test systems before returning them to production. Gradually restore service with continuous monitoring.',
                    'moderate': 'Restore systems to normal operation while ensuring they remain secure.',
                    'minimal': 'Bring systems back online after confirming they are secure.',
                    'none': ''
                }
            },
            # Step 8: Reporting
            {
                'step_number': 8,
                'action': 'Reporting',
                'description': 'Document the incident, response actions, and findings in a comprehensive report.',
                'technical_details': f"You need to create a detailed report about this {self.current_simulation.get('incident_type', 'incident').replace('_', ' ')} incident.",
                'guidance': {
                    'detailed': 'Create detailed technical and executive reports documenting the incident, response actions, timeline, and recommendations. Include all evidence, findings, and lessons learned. Prepare for any necessary regulatory notifications.',
                    'moderate': 'Document the incident, response actions, and findings for stakeholders and regulatory requirements.',
                    'minimal': 'Report on what happened and how it was resolved.',
                    'none': ''
                }
            },
            # Step 9: Notification
            {
                'step_number': 9,
                'action': 'Notification',
                'description': 'Notify relevant stakeholders, including management, affected users, and potentially regulators.',
                'technical_details': f"Based on the incident assessment, you need to determine who needs to be notified about this {self.current_simulation.get('incident_type', 'incident').replace('_', ' ')}.",
                'guidance': {
                    'detailed': 'Identify all stakeholders who need to be notified, including executives, legal, affected users, customers, partners, and regulators. Prepare tailored messages for each audience with appropriate detail level. Follow all regulatory notification requirements and timelines.',
                    'moderate': 'Notify appropriate stakeholders and fulfill any regulatory reporting requirements.',
                    'minimal': 'Inform necessary parties about the incident.',
                    'none': ''
                }
            },
            # Step 10: Post-Incident Review
            {
                'step_number': 10,
                'action': 'Post-Incident Review',
                'description': 'Conduct a post-incident review to identify lessons learned and areas for improvement.',
                'technical_details': f"Review the entire incident response process for this {self.current_simulation.get('incident_type', 'incident').replace('_', ' ')}.",
                'guidance': {
                    'detailed': 'Conduct a thorough review of the incident and response process. Document what went well and what could be improved. Update incident response plans, security controls, and training based on lessons learned. Identify root causes and systemic issues.',
                    'moderate': 'Analyze the response effectiveness and identify areas for improvement.',
                    'minimal': 'Determine lessons learned from the incident.',
                    'none': ''
                }
            },
            # Step 11: Security Enhancement
            {
                'step_number': 11,
                'action': 'Security Enhancement',
                'description': 'Implement security enhancements to prevent similar incidents in the future.',
                'technical_details': f"Based on the incident analysis, you need to recommend security improvements for {self.current_simulation.get('organization', {}).get('name', 'the organization')}.",
                'guidance': {
                    'detailed': 'Implement technical controls, policy changes, and process improvements to address root causes and vulnerabilities. This may include additional monitoring, access controls, network segmentation, training, or other security measures.',
                    'moderate': 'Recommend and implement security improvements to prevent similar incidents.',
                    'minimal': 'Implement preventive measures for the future.',
                    'none': ''
                }
            },
            # Step 12: Long-term Planning
            {
                'step_number': 12,
                'action': 'Long-term Planning',
                'description': 'Develop long-term security strategy and roadmap based on incident insights.',
                'technical_details': f"Create a strategic security roadmap for {self.current_simulation.get('organization', {}).get('name', 'the organization')} following this {self.current_simulation.get('incident_type', 'incident').replace('_', ' ')}.",
                'guidance': {
                    'detailed': 'Develop a comprehensive security strategy addressing gaps revealed by the incident. Create a prioritized roadmap with short and long-term initiatives. Seek executive support and budget for security program enhancement.',
                    'moderate': 'Develop a strategic security plan to address fundamental security gaps.',
                    'minimal': 'Create a long-term security improvement plan.',
                    'none': ''
                }
            }
        ]
        
        # Get steps based on total step count
        max_steps = min(self.total_steps, len(step_templates))
        available_steps = step_templates[:max_steps]
        
        if self.current_step > max_steps:
            self.simulation_complete = True
            return {
                'status': 'complete',
                'message': 'Incident response simulation completed successfully. You have completed all required steps.'
            }
        
        # Get current step from templates
        step_template = available_steps[self.current_step - 1]
        
        # Add guidance based on difficulty level
        step = {
            'step_number': self.current_step,
            'total_steps': max_steps,
            'action': step_template['action'],
            'description': step_template['description'],
            'technical_details': step_template['technical_details'],
            'guidance': step_template['guidance'][guidance_level],
            'status': 'active'
        }
        
        # Save step to simulation
        self.current_simulation.setdefault('steps', []).append(step)
        
        return step
    
    def submit_step_response(self, user_response: str) -> Dict[str, Any]:
        """
        Submit a response to the current step.
        
        Args:
            user_response: User's response to the step
            
        Returns:
            Evaluation results
        """
        if not self.current_simulation:
            raise ValueError("No active simulation")
            
        if self.simulation_complete:
            return {
                'status': 'error',
                'message': 'Simulation is already complete'
            }
            
        if not user_response:
            return {
                'status': 'error',
                'message': 'Empty response not allowed'
            }
        
        # Store user response
        self.user_responses.append(user_response)
        
        # Get current step
        current_steps = self.current_simulation.get('steps', [])
        if not current_steps or len(current_steps) < self.current_step:
            raise ValueError(f"Step {self.current_step} not available")
            
        current_step = current_steps[self.current_step - 1]
        
        # Evaluate response using AI
        system_prompt = f"""
        You are an expert incident response evaluator for cybersecurity training.
        Evaluate the trainee's response to a simulated {self.current_simulation.get('incident_type', 'security incident').replace('_', ' ')}.
        
        SIMULATION DETAILS:
        Title: {self.current_simulation.get('title', 'Untitled Incident')}
        Type: {self.current_simulation.get('incident_type', 'Unknown').replace('_', ' ').title()}
        Organization: {self.current_simulation.get('organization', {}).get('name', 'Unknown Organization')}
        
        CURRENT STEP:
        Step {self.current_step} of {self.total_steps}: {current_step.get('action', 'Action')}
        Description: {current_step.get('description', 'No description')}
        Technical details: {current_step.get('technical_details', 'No technical details')}
        
        TRAINEE PROFILE:
        Name: {self.current_simulation.get('persona', {}).get('name', 'Unnamed')}
        Role: {self.current_simulation.get('persona', {}).get('role', 'Security Analyst')}
        Experience: {self.current_simulation.get('persona', {}).get('experience_level', 'intermediate')}
        
        TRAINEE RESPONSE:
        {user_response}
        
        EVALUATION INSTRUCTIONS:
        1. Assess the completeness and correctness of the response for this specific step
        2. Consider the trainee's experience level when evaluating
        3. Identify key strengths in the response
        4. Identify areas for improvement
        5. Provide a score from 0-100
        6. Give specific, actionable recommendations
        
        Format your response as a valid JSON object with the following structure:
        {{
            "score": 85,
            "strengths": ["Strength 1", "Strength 2"],
            "improvement_areas": ["Area 1", "Area 2"],
            "recommendation": "Specific recommendation for improvement",
            "explanation": "Explanation of score and evaluation"
        }}
        
        Be fair but educational in your assessment, focusing on helping the trainee improve.
        """
        
        user_prompt = f"Evaluate this incident response for step {self.current_step}: {current_step.get('action', 'Action')}"
        
        try:
            # Query AI with fallback to different providers
            provider_order = ['openai', 'anthropic', 'deepseek']
            response = None
            
            for provider_id in provider_order:
                if self.ai_proxy.is_provider_available(provider_id):
                    try:
                        result = self.ai_proxy.query(
                            provider_id=provider_id,
                            prompt=user_prompt,
                            system_prompt=system_prompt,
                            max_tokens=1024,
                            temperature=0.3
                        )
                        response = result.get('response', '')
                        break
                    except Exception as e:
                        logger.warning(f"Failed to query {provider_id}: {e}")
                        continue
            
            if not response:
                # Fallback basic evaluation
                evaluation = {
                    "score": 70,
                    "strengths": ["Provided a response to the incident step"],
                    "improvement_areas": ["Consider providing more detail in future responses"],
                    "recommendation": "Focus on addressing all aspects of the incident step",
                    "explanation": "Basic automated evaluation due to AI provider unavailability"
                }
            else:
                # Extract JSON from response
                try:
                    evaluation = json.loads(response)
                except json.JSONDecodeError:
                    # Try to extract JSON from text response
                    import re
                    json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
                    if json_match:
                        try:
                            evaluation = json.loads(json_match.group(1))
                        except json.JSONDecodeError:
                            # One more attempt with stripped lines
                            try:
                                cleaned_json = '\n'.join(line.strip() for line in json_match.group(1).split('\n'))
                                evaluation = json.loads(cleaned_json)
                            except json.JSONDecodeError:
                                # Fallback evaluation
                                evaluation = {
                                    "score": 75,
                                    "strengths": ["Provided a response to the incident step"],
                                    "improvement_areas": ["Consider providing more detail in future responses"],
                                    "recommendation": "Focus on addressing all aspects of the incident step",
                                    "explanation": "Basic automated evaluation due to parsing error"
                                }
                    else:
                        # Look for just the JSON object
                        json_match = re.search(r'({[\s\S]*?})', response)
                        if json_match:
                            try:
                                evaluation = json.loads(json_match.group(1))
                            except json.JSONDecodeError:
                                # Fallback evaluation
                                evaluation = {
                                    "score": 75,
                                    "strengths": ["Provided a response to the incident step"],
                                    "improvement_areas": ["Consider providing more detail in future responses"],
                                    "recommendation": "Focus on addressing all aspects of the incident step",
                                    "explanation": "Basic automated evaluation due to parsing error"
                                }
                        else:
                            # Fallback evaluation
                            evaluation = {
                                "score": 75,
                                "strengths": ["Provided a response to the incident step"],
                                "improvement_areas": ["Consider providing more detail in future responses"],
                                "recommendation": "Focus on addressing all aspects of the incident step",
                                "explanation": "Basic automated evaluation due to parsing error"
                            }
            
            # Store evaluation
            self.step_evaluations.append(evaluation)
            
            # Update step with user response and evaluation
            current_step['user_response'] = user_response
            current_step['evaluation'] = evaluation
            
            # Check if this was the last step
            is_complete = self.current_step >= self.total_steps
            
            if is_complete:
                self.simulation_complete = True
                
                # Calculate final score
                scores = [e.get('score', 0) for e in self.step_evaluations]
                overall_score = sum(scores) / len(scores) if scores else 0
                
                # Generate aggregated strengths and improvement areas
                all_strengths = []
                all_improvements = []
                
                for eval_data in self.step_evaluations:
                    all_strengths.extend(eval_data.get('strengths', []))
                    all_improvements.extend(eval_data.get('improvement_areas', []))
                
                # Get unique values while preserving order
                seen_strengths = set()
                unique_strengths = [x for x in all_strengths if not (x in seen_strengths or seen_strengths.add(x))]
                
                seen_improvements = set()
                unique_improvements = [x for x in all_improvements if not (x in seen_improvements or seen_improvements.add(x))]
                
                # Limit to top 5
                top_strengths = unique_strengths[:5]
                top_improvements = unique_improvements[:5]
                
                # Create final evaluation
                final_evaluation = {
                    'overall_score': round(overall_score, 1),
                    'total_steps_completed': self.current_step,
                    'strengths': top_strengths,
                    'improvement_areas': top_improvements,
                    'completion_time': str(datetime.now())
                }
                
                # Add to simulation
                self.current_simulation['final_evaluation'] = final_evaluation
                
                # Save completed simulation
                self._save_simulation()
                
                return {
                    'evaluation': evaluation,
                    'is_complete': True,
                    'final_score': final_evaluation
                }
            
            return {
                'evaluation': evaluation,
                'is_complete': False
            }
            
        except Exception as e:
            logger.error(f"Failed to evaluate response: {e}")
            # Provide a basic evaluation as fallback
            basic_evaluation = {
                "score": 70,
                "strengths": ["Provided a response to the incident"],
                "improvement_areas": ["System couldn't fully evaluate your response"],
                "recommendation": "Continue to the next step",
                "explanation": f"Error during evaluation: {str(e)}"
            }
            self.step_evaluations.append(basic_evaluation)
            
            # Update step with user response and basic evaluation
            current_step['user_response'] = user_response
            current_step['evaluation'] = basic_evaluation
            
            return {
                'evaluation': basic_evaluation,
                'is_complete': False,
                'error': str(e)
            }
    
    def _save_simulation(self) -> None:
        """Save the current simulation state to file"""
        if not self.current_simulation:
            return
            
        simulation_id = self.current_simulation.get('simulation_id', f"SIM-{str(uuid.uuid4())[:8]}")
        simulation_file = os.path.join(
            self.scenarios_dir, 
            f"{simulation_id}_simulation.json"
        )
        
        with open(simulation_file, 'w') as f:
            json.dump(self.current_simulation, f, indent=2)
            
        logger.info(f"Simulation saved: {simulation_file}")
    
    def end_simulation(self, reason: str = "User ended simulation") -> None:
        """
        End the current simulation.
        
        Args:
            reason: Reason for ending the simulation
        """
        if not self.current_simulation:
            return
            
        self.current_simulation['end_reason'] = reason
        self.current_simulation['end_time'] = datetime.now().isoformat()
        self.simulation_complete = True
        
        # Save the current state
        self._save_simulation()
        
        logger.info(f"Simulation ended: {reason}")
    
    def generate_report(self, simulation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive incident response report.
        
        Args:
            simulation_id: Optional simulation ID (uses current simulation if None)
            
        Returns:
            Report generation results
        """
        # Use current simulation if no ID provided
        if not simulation_id and self.current_simulation:
            simulation = self.current_simulation
        elif simulation_id:
            # Try to load the specified simulation
            simulation_files = [
                os.path.join(self.scenarios_dir, f)
                for f in os.listdir(self.scenarios_dir)
                if f.endswith(".json") and simulation_id in f
            ]
            
            if not simulation_files:
                raise ValueError(f"No simulation found with ID: {simulation_id}")
            
            with open(simulation_files[0], 'r') as f:
                simulation = json.load(f)
        else:
            raise ValueError("No simulation specified and no active simulation")
            
        # Generate the report using the report generator
        report_data = self.report_generator.generate_report(simulation)
        
        # Save the report to file
        report_file = self.report_generator.save_report(report_data, self.reports_dir)
        
        # Extract ID and summary for return
        report_id = report_data.get('report_id', '')
        executive_summary = report_data.get('executive_summary', '')
        
        logger.info(f"Report generated: {report_file}")
        
        return {
            'report_id': report_id,
            'report_file': report_file,
            'report_summary': executive_summary
        }