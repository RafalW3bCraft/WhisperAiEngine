"""
G3r4ki Security Persona Generator

This module provides functionality for generating realistic security personas for
incident response simulations and training exercises.
"""

import json
import random
import logging
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

# List of available persona types
PERSONA_TYPES = [
    'security_analyst',
    'incident_responder',
    'threat_hunter',
    'soc_manager',
    'forensic_analyst',
    'penetration_tester',
    'security_engineer',
    'compliance_officer',
    'red_team_operator',
    'blue_team_defender',
    'security_consultant',
    'malware_analyst',
    'security_architect',
    'ciso',
    'devsecops_engineer'
]

# Experience levels
EXPERIENCE_LEVELS = [
    'novice',
    'junior',
    'intermediate',
    'senior',
    'expert'
]

class SecurityPersonaGenerator:
    """
    Security Persona Generator
    
    This class generates realistic security personas for incident response
    simulations and training exercises.
    """
    
    def __init__(self, ai_proxy):
        """
        Initialize the security persona generator
        
        Args:
            ai_proxy: AI proxy for generating persona details
        """
        self.ai_proxy = ai_proxy
        
    def get_available_persona_types(self) -> List[str]:
        """
        Get a list of available persona types
        
        Returns:
            List of persona type names
        """
        return PERSONA_TYPES
    
    def generate_persona(self, persona_type: str, experience_level: str = 'intermediate') -> Dict[str, Any]:
        """
        Generate a security persona
        
        Args:
            persona_type: Type of security persona
            experience_level: Experience level
            
        Returns:
            Generated persona data
            
        Raises:
            ValueError: If persona type or experience level is invalid
        """
        logger.info(f"Generating {experience_level} {persona_type} persona")
        
        # Validate persona type
        if persona_type not in PERSONA_TYPES:
            raise ValueError(f"Unknown persona type: {persona_type}. Available types: {', '.join(PERSONA_TYPES)}")
        
        # Validate experience level
        if experience_level not in EXPERIENCE_LEVELS:
            raise ValueError(f"Unknown experience level: {experience_level}. Available levels: {', '.join(EXPERIENCE_LEVELS)}")
        
        # Map experience level to years of experience range
        experience_years_map = {
            'novice': (0, 1),
            'junior': (1, 3),
            'intermediate': (3, 7),
            'senior': (7, 12),
            'expert': (12, 25)
        }
        years_min, years_max = experience_years_map[experience_level]
        years_experience = random.randint(years_min, years_max)
        
        # Define core skills based on persona type
        core_skills = {
            'security_analyst': ['SIEM tools', 'Log analysis', 'Security monitoring', 'Threat detection', 'Vulnerability assessment'],
            'incident_responder': ['Incident handling', 'Digital forensics', 'Malware analysis', 'Evidence collection', 'Containment strategies'],
            'threat_hunter': ['Threat intelligence', 'IOC identification', 'Behavioral analysis', 'Advanced persistent threat detection', 'MITRE ATT&CK framework'],
            'soc_manager': ['Team leadership', 'Security operations', 'Risk management', 'Incident coordination', 'Security metrics'],
            'forensic_analyst': ['Digital forensics', 'Chain of custody', 'Disk imaging', 'Memory analysis', 'Evidence handling'],
            'penetration_tester': ['Vulnerability scanning', 'Exploitation techniques', 'Social engineering', 'Web application testing', 'Network penetration'],
            'security_engineer': ['Security architecture', 'Network security', 'Systems hardening', 'Security tools development', 'Security automation'],
            'compliance_officer': ['Regulatory frameworks', 'Compliance auditing', 'Risk assessment', 'Documentation', 'Policy development'],
            'red_team_operator': ['Advanced exploitation', 'Covert operations', 'Custom tool development', 'Evasion techniques', 'Post-exploitation'],
            'blue_team_defender': ['Defense tactics', 'Security monitoring', 'Incident response', 'Security hardening', 'Detection engineering'],
            'security_consultant': ['Security assessments', 'Client communication', 'Recommendation development', 'Industry best practices', 'Risk analysis'],
            'malware_analyst': ['Reverse engineering', 'Malware behavior analysis', 'Sandbox testing', 'IOC development', 'Malware classification'],
            'security_architect': ['Security frameworks', 'Architecture design', 'Defense-in-depth', 'Zero trust models', 'Security standards'],
            'ciso': ['Strategic planning', 'Security program management', 'Executive communication', 'Budget management', 'Risk governance'],
            'devsecops_engineer': ['CI/CD security', 'Secure coding', 'Container security', 'Security automation', 'Pipeline integration']
        }
        
        # Generate the persona using AI
        system_prompt = f"""
        You are a cybersecurity persona generator for security training simulations.
        Create a realistic {experience_level} level {persona_type.replace('_', ' ')} character.
        
        The character should have {years_experience} years of experience in security.
        
        Core skills for this role include: {', '.join(core_skills.get(persona_type, ['Security skills']))}.
        
        Generate a realistic security professional with:
        1. A name (first and last)
        2. Detailed background (education, previous roles, career path)
        3. Technical skills appropriate for their role and experience level
        4. Certifications they might have
        5. Areas of specialty within their field
        
        Format the response as a valid JSON object with the following structure:
        {{
            "name": "Full Name",
            "role": "Security Role Title",
            "experience_level": "{experience_level}",
            "years_experience": {years_experience},
            "background": "Detailed professional background and history",
            "education": "Academic background",
            "skills": ["Skill 1", "Skill 2", "Skill 3", ...],
            "certifications": ["Cert 1", "Cert 2", ...],
            "specialties": ["Specialty 1", "Specialty 2", ...]
        }}
        
        Make the persona realistic but fictional. Don't use real people's names.
        """
        
        user_prompt = f"Generate a realistic {experience_level} {persona_type.replace('_', ' ')} persona for security training."
        
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
                            temperature=0.7
                        )
                        response = result.get('response', '')
                        break
                    except Exception as e:
                        logger.warning(f"Failed to query {provider_id}: {e}")
                        continue
            
            if not response:
                # Fallback to a basic generated persona
                return self._generate_basic_persona(persona_type, experience_level, years_experience)
            
            # Extract JSON from response
            try:
                persona_data = json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON from text response
                json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
                if json_match:
                    try:
                        persona_data = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        # One more attempt with stripped lines
                        try:
                            cleaned_json = '\n'.join(line.strip() for line in json_match.group(1).split('\n'))
                            persona_data = json.loads(cleaned_json)
                        except json.JSONDecodeError:
                            # Fallback to basic persona
                            return self._generate_basic_persona(persona_type, experience_level, years_experience)
                else:
                    # Look for just the JSON object
                    json_match = re.search(r'({[\s\S]*?})', response)
                    if json_match:
                        try:
                            persona_data = json.loads(json_match.group(1))
                        except json.JSONDecodeError:
                            # Fallback to basic persona
                            return self._generate_basic_persona(persona_type, experience_level, years_experience)
                    else:
                        # Fallback to basic persona
                        return self._generate_basic_persona(persona_type, experience_level, years_experience)
            
            # Ensure required fields are present
            if not isinstance(persona_data, dict):
                return self._generate_basic_persona(persona_type, experience_level, years_experience)
                
            # Add metadata
            persona_data['persona_type'] = persona_type
            persona_data['experience_level'] = experience_level
            persona_data['years_experience'] = years_experience
            persona_data['generated_at'] = datetime.now().isoformat()
            
            # Ensure name is present
            if 'name' not in persona_data or not persona_data['name']:
                persona_data['name'] = self._generate_random_name()
                
            # Ensure role is present
            if 'role' not in persona_data or not persona_data['role']:
                persona_data['role'] = persona_type.replace('_', ' ').title()
                
            # Ensure skills are present
            if 'skills' not in persona_data or not persona_data['skills']:
                persona_data['skills'] = core_skills.get(persona_type, ['Security skills'])
            
            return persona_data
            
        except Exception as e:
            logger.error(f"Failed to generate persona: {e}")
            return self._generate_basic_persona(persona_type, experience_level, years_experience)
    
    def _generate_basic_persona(self, persona_type: str, experience_level: str, years_experience: int) -> Dict[str, Any]:
        """
        Generate a basic persona when AI generation fails
        
        Args:
            persona_type: Type of security persona
            experience_level: Experience level
            years_experience: Years of experience
            
        Returns:
            Basic generated persona data
        """
        # Define core skills based on persona type
        core_skills = {
            'security_analyst': ['SIEM tools', 'Log analysis', 'Security monitoring', 'Threat detection', 'Vulnerability assessment'],
            'incident_responder': ['Incident handling', 'Digital forensics', 'Malware analysis', 'Evidence collection', 'Containment strategies'],
            'threat_hunter': ['Threat intelligence', 'IOC identification', 'Behavioral analysis', 'Advanced persistent threat detection', 'MITRE ATT&CK framework'],
            'soc_manager': ['Team leadership', 'Security operations', 'Risk management', 'Incident coordination', 'Security metrics'],
            'forensic_analyst': ['Digital forensics', 'Chain of custody', 'Disk imaging', 'Memory analysis', 'Evidence handling'],
            'penetration_tester': ['Vulnerability scanning', 'Exploitation techniques', 'Social engineering', 'Web application testing', 'Network penetration'],
            'security_engineer': ['Security architecture', 'Network security', 'Systems hardening', 'Security tools development', 'Security automation'],
            'compliance_officer': ['Regulatory frameworks', 'Compliance auditing', 'Risk assessment', 'Documentation', 'Policy development'],
            'red_team_operator': ['Advanced exploitation', 'Covert operations', 'Custom tool development', 'Evasion techniques', 'Post-exploitation'],
            'blue_team_defender': ['Defense tactics', 'Security monitoring', 'Incident response', 'Security hardening', 'Detection engineering'],
            'security_consultant': ['Security assessments', 'Client communication', 'Recommendation development', 'Industry best practices', 'Risk analysis'],
            'malware_analyst': ['Reverse engineering', 'Malware behavior analysis', 'Sandbox testing', 'IOC development', 'Malware classification'],
            'security_architect': ['Security frameworks', 'Architecture design', 'Defense-in-depth', 'Zero trust models', 'Security standards'],
            'ciso': ['Strategic planning', 'Security program management', 'Executive communication', 'Budget management', 'Risk governance'],
            'devsecops_engineer': ['CI/CD security', 'Secure coding', 'Container security', 'Security automation', 'Pipeline integration']
        }
        
        # Define certifications based on persona type and experience
        cert_maps = {
            'novice': ['Security+', 'Network+'],
            'junior': ['Security+', 'SSCP', 'CEH'],
            'intermediate': ['CISSP', 'CEH', 'CCSP', 'CISM'],
            'senior': ['CISSP', 'OSCP', 'CISM', 'CRISC'],
            'expert': ['CISSP', 'OSCP', 'CISM', 'CGRC', 'OSWE']
        }
        
        # Generate random name
        name = self._generate_random_name()
        
        # Create a basic persona
        return {
            'name': name,
            'role': persona_type.replace('_', ' ').title(),
            'persona_type': persona_type,
            'experience_level': experience_level,
            'years_experience': years_experience,
            'background': f"Professional with {years_experience} years of cybersecurity experience focused on {persona_type.replace('_', ' ')} responsibilities.",
            'education': "Bachelor's degree in Computer Science or related field",
            'skills': core_skills.get(persona_type, ['Security skills']),
            'certifications': random.sample(cert_maps.get(experience_level, ['Security+']), min(3, len(cert_maps.get(experience_level, ['Security+'])))),
            'specialties': [f"{persona_type.replace('_', ' ')} specialization"],
            'generated_at': datetime.now().isoformat()
        }
    
    def _generate_random_name(self) -> str:
        """
        Generate a random name
        
        Returns:
            Random name
        """
        first_names = [
            "Alex", "Jordan", "Morgan", "Taylor", "Casey", "Jamie", "Riley", "Avery",
            "Quinn", "Blake", "Reese", "Harper", "Emerson", "Hayden", "Cameron", "Rowan",
            "Dakota", "Skyler", "Elliot", "Parker", "Sawyer", "Kennedy", "Brynn", "Aspen",
            "Michael", "Sarah", "David", "Emily", "James", "Jennifer", "Robert", "Jessica",
            "William", "Ashley", "John", "Amanda", "Christopher", "Stephanie", "Daniel", "Rebecca",
            "Matthew", "Laura", "Andrew", "Melissa", "Joseph", "Danielle", "Ryan", "Elizabeth"
        ]
        
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
            "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
            "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
            "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
            "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell"
        ]
        
        return f"{random.choice(first_names)} {random.choice(last_names)}"