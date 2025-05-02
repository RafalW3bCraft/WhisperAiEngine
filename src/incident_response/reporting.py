"""
G3r4ki Incident Response Reporting.

This module provides functionality for generating comprehensive incident
response reports based on simulation data.
"""

import json
import logging
import re
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class IncidentReport:
    """
    Incident Report Generator
    
    This class generates comprehensive incident response reports based on
    simulation data and evaluation results.
    """
    
    def __init__(self, ai_proxy):
        """
        Initialize the incident report generator
        
        Args:
            ai_proxy: AI proxy for generating report content
        """
        self.ai_proxy = ai_proxy
    
    def generate_report(self, simulation_data: Dict[str, Any], simulation_log: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive incident response report
        
        Args:
            simulation_data: Simulation data
            simulation_log: Optional simulation log for detailed reporting
            
        Returns:
            Generated report data
        """
        logger.info(f"Generating report for simulation {simulation_data.get('simulation_id', 'unknown')}")
        
        # Generate report ID
        report_id = f"REP-{simulation_data.get('incident_type', 'INC')[:3].upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Prepare base report data
        report_data = {
            'report_id': report_id,
            'title': f"Incident Response Report: {simulation_data.get('title', 'Untitled Incident')}",
            'generated_at': datetime.now().isoformat(),
            'simulation_id': simulation_data.get('simulation_id', 'Unknown'),
            'incident_id': simulation_data.get('incident_id', 'Unknown'),
            'incident_type': simulation_data.get('incident_type', 'Unknown'),
            'organization': simulation_data.get('organization', {}),
            'incident_date': simulation_data.get('timeline', [{}])[0].get('timestamp', 'Unknown') if simulation_data.get('timeline') else 'Unknown',
            'detection_date': simulation_data.get('timeline', [{}])[1].get('timestamp', 'Unknown') if len(simulation_data.get('timeline', [])) > 1 else 'Unknown',
            'scope_of_compromise': f"Affected systems: {', '.join(simulation_data.get('affected_systems', ['Unknown']))}",
            'technical_analysis': simulation_data.get('technical_details', 'No technical analysis available'),
            'impact_assessment': simulation_data.get('potential_impact', 'No impact assessment available')
        }
        
        # Add performance evaluation if available
        if 'final_evaluation' in simulation_data:
            report_data['performance'] = simulation_data['final_evaluation']
        else:
            # Create basic performance data
            report_data['performance'] = {
                'overall_score': 0,
                'response_time': 'Unknown',
                'strengths': ["No evaluation data available"],
                'improvement_areas': ["No evaluation data available"]
            }
        
        # Generate executive summary using AI
        executive_summary = self._generate_executive_summary(simulation_data)
        report_data['executive_summary'] = executive_summary
        
        # Create remediation steps based on the incident
        remediation_steps = []
        for step in simulation_data.get('recommended_steps', []):
            remediation_steps.append(step)
        
        if not remediation_steps:
            # Add generic steps based on incident type
            incident_type = simulation_data.get('incident_type', 'security_incident')
            if 'malware' in incident_type or 'ransomware' in incident_type:
                remediation_steps = [
                    "Isolate infected systems from the network",
                    "Remove malware using approved security tools",
                    "Restore systems from clean backups",
                    "Patch vulnerabilities that allowed the initial infection",
                    "Implement enhanced endpoint protection"
                ]
            elif 'data_breach' in incident_type:
                remediation_steps = [
                    "Identify and close the access vector used for the breach",
                    "Reset all potentially compromised credentials",
                    "Implement data loss prevention controls",
                    "Enhance monitoring for sensitive data access",
                    "Review and strengthen access control policies"
                ]
            elif 'phishing' in incident_type:
                remediation_steps = [
                    "Reset credentials for affected users",
                    "Block malicious sender domains and URLs",
                    "Scan for any downloaded malware or payloads",
                    "Enhance email security filtering",
                    "Conduct additional security awareness training"
                ]
            else:
                remediation_steps = [
                    "Patch all identified vulnerabilities",
                    "Update security monitoring rules",
                    "Implement additional security controls",
                    "Review and enhance security policies",
                    "Conduct security awareness training"
                ]
        
        report_data['remediation_steps'] = remediation_steps
        
        # Create recommendations based on the incident
        recommendations = []
        for i, step in enumerate(simulation_data.get('steps', [])):
            if 'evaluation' in step and 'recommendation' in step['evaluation']:
                recommendations.append(step['evaluation']['recommendation'])
        
        if not recommendations:
            # Add generic recommendations
            incident_type = simulation_data.get('incident_type', 'security_incident')
            if 'malware' in incident_type or 'ransomware' in incident_type:
                recommendations = [
                    "Implement application whitelisting to prevent unauthorized code execution",
                    "Enhance backup strategy with offline/air-gapped backups",
                    "Implement network segmentation to limit lateral movement",
                    "Deploy advanced endpoint detection and response (EDR) solutions",
                    "Conduct regular vulnerability scanning and patching"
                ]
            elif 'data_breach' in incident_type:
                recommendations = [
                    "Implement data encryption for sensitive information",
                    "Deploy data loss prevention (DLP) technology",
                    "Enhance identity and access management controls",
                    "Conduct regular data security audits",
                    "Implement least privilege access principles"
                ]
            elif 'phishing' in incident_type:
                recommendations = [
                    "Implement DMARC, SPF, and DKIM email authentication",
                    "Deploy advanced email filtering and anti-phishing controls",
                    "Conduct regular phishing simulation exercises",
                    "Implement multi-factor authentication across all systems",
                    "Develop clear procedures for reporting suspicious emails"
                ]
            else:
                recommendations = [
                    "Implement a comprehensive security awareness program",
                    "Enhance security monitoring and threat detection capabilities",
                    "Conduct regular security assessments and penetration testing",
                    "Review and update incident response procedures",
                    "Implement defense-in-depth security architecture"
                ]
        
        report_data['recommendations'] = recommendations
        
        # Include simulation steps if available
        if simulation_data.get('steps'):
            report_data['response_steps'] = []
            for step in simulation_data.get('steps', []):
                step_data = {
                    'step_number': step.get('step_number'),
                    'action': step.get('action'),
                    'description': step.get('description'),
                    'user_response': step.get('user_response', 'No response recorded'),
                    'evaluation': step.get('evaluation', {})
                }
                report_data['response_steps'].append(step_data)
        
        return report_data
    
    def save_report(self, report_data: Dict[str, Any], output_dir: Optional[str] = None) -> str:
        """
        Save a report to file
        
        Args:
            report_data: Report data
            output_dir: Optional output directory
            
        Returns:
            Path to the saved report file
        """
        if not output_dir:
            # Use default directory
            output_dir = os.path.expanduser('~/.g3r4ki/incident_response/reports')
            os.makedirs(output_dir, exist_ok=True)
        
        report_id = report_data.get('report_id', f"REP-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        report_file = os.path.join(output_dir, f"{report_id}_report.json")
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        logger.info(f"Report saved to: {report_file}")
        return report_file
    
    def _generate_executive_summary(self, simulation_data: Dict[str, Any]) -> str:
        """
        Generate an executive summary using AI
        
        Args:
            simulation_data: Simulation data
            
        Returns:
            Executive summary text
        """
        # Try to use AI to generate executive summary
        system_prompt = f"""
        You are an incident response reporting expert. Generate a comprehensive executive summary for the following incident:
        
        Title: {simulation_data.get('title', 'Untitled Incident')}
        Type: {simulation_data.get('incident_type', 'Unknown').replace('_', ' ').title()}
        Organization: {simulation_data.get('organization', {}).get('name', 'Unknown Organization')}
        Industry: {simulation_data.get('organization', {}).get('industry', 'Unknown')}
        
        Description: {simulation_data.get('description', 'No description available')}
        
        Technical Details: {simulation_data.get('technical_details', 'No technical details available')}
        
        Affected Systems: {', '.join(simulation_data.get('affected_systems', ['Unknown']))}
        
        Potential Impact: {simulation_data.get('potential_impact', 'Unknown impact')}
        
        Write a professional, concise executive summary (300-400 words) that explains:
        1. What happened
        2. How it was detected
        3. Impact to the organization
        4. Key actions taken
        5. Current status
        6. Recommendations going forward
        
        Use a formal, professional tone appropriate for executive leadership.
        """
        
        user_prompt = f"Generate an executive summary for a {simulation_data.get('incident_type', 'security incident').replace('_', ' ')} incident report."
        
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
                            temperature=0.5
                        )
                        response = result.get('response', '')
                        break
                    except Exception as e:
                        logger.warning(f"Failed to query {provider_id}: {e}")
                        continue
            
            if not response:
                return self._generate_basic_summary(simulation_data)
                
            return response
                
        except Exception as e:
            logger.error(f"Failed to generate executive summary: {e}")
            return self._generate_basic_summary(simulation_data)
    
    def _generate_basic_summary(self, simulation_data: Dict[str, Any]) -> str:
        """
        Generate a basic executive summary when AI generation fails
        
        Args:
            simulation_data: Simulation data
            
        Returns:
            Basic executive summary text
        """
        incident_type = simulation_data.get('incident_type', 'security incident').replace('_', ' ').title()
        org_name = simulation_data.get('organization', {}).get('name', 'the organization')
        affected_systems = ', '.join(simulation_data.get('affected_systems', ['systems']))
        impact = simulation_data.get('potential_impact', 'potential business disruption')
        
        return f"""
Executive Summary: {incident_type} at {org_name}

This report documents a {incident_type} that was detected at {org_name}. The incident affected {affected_systems} with potential impact including {impact}. The security team responded according to established incident response procedures to contain, eradicate, and recover from the incident.

Initial detection occurred through security monitoring systems, followed by a comprehensive investigation to determine the scope and impact. The incident has been contained and affected systems have been restored to normal operation.

Recommendations include strengthening security controls, enhancing monitoring capabilities, and conducting additional security awareness training to prevent similar incidents in the future.
"""