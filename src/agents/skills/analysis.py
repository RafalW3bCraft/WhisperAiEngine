"""
G3r4ki Analysis Skills

This module provides analysis-related skills for agents, focusing on security data
analysis, vulnerability assessment, and reporting capabilities.
"""

import re
import os
import json
import logging
import subprocess
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from src.agents.skills.base import Skill, skill

# Setup logging
logger = logging.getLogger('g3r4ki.agents.skills.analysis')

class AnalysisSkills(Skill):
    """
    Analysis-related skills for agents
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize analysis skills
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        
        # Create results directories if they don't exist
        self.results_dir = os.path.join(os.getcwd(), 'results')
        self.recon_dir = os.path.join(self.results_dir, 'recon')
        self.scans_dir = os.path.join(self.results_dir, 'scans')
        self.vuln_dir = os.path.join(self.results_dir, 'vuln')
        
        os.makedirs(self.recon_dir, exist_ok=True)
        os.makedirs(self.scans_dir, exist_ok=True)
        os.makedirs(self.vuln_dir, exist_ok=True)
    
    @skill(category="analysis")
    def analyze_port_scan(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze port scan results to identify security implications
        
        Args:
            scan_results: Port scan results dictionary
            
        Returns:
            Analysis results with security implications
        """
        analysis = {
            "high_risk_ports": [],
            "medium_risk_ports": [],
            "low_risk_ports": [],
            "security_implications": [],
            "recommendations": []
        }
        
        # High-risk ports and their implications
        high_risk_ports = {
            21: "FTP - May allow anonymous access or be vulnerable to brute force",
            22: "SSH - Could be vulnerable to brute force if not properly configured",
            23: "Telnet - Transmits data in cleartext and should be disabled",
            25: "SMTP - Could be vulnerable to spam relaying if misconfigured",
            445: "SMB - Could be vulnerable to various exploits (e.g., EternalBlue)",
            1433: "MSSQL - Database server that could be vulnerable if exposed",
            1521: "Oracle DB - Database server that could be vulnerable if exposed",
            3306: "MySQL - Database server that could be vulnerable if exposed",
            3389: "RDP - Remote access that could be vulnerable to brute force",
            5432: "PostgreSQL - Database server that could be vulnerable if exposed",
            5900: "VNC - Could be vulnerable to brute force and sniffing"
        }
        
        # Medium-risk ports
        medium_risk_ports = {
            53: "DNS - Could be vulnerable to cache poisoning or amplification attacks",
            80: "HTTP - Web server that could host vulnerable web applications",
            443: "HTTPS - Web server that could host vulnerable web applications",
            8080: "HTTP Alternate - Often used for web proxies or administration",
            8443: "HTTPS Alternate - Often used for web administration"
        }
        
        # Process each host in scan results
        for host in scan_results.get("hosts", []):
            host_ip = host.get("ip", "unknown")
            
            for port_info in host.get("ports", []):
                port = port_info.get("port")
                state = port_info.get("state")
                service = port_info.get("service", "")
                
                if state != "open":
                    continue
                
                port_risk = {
                    "ip": host_ip,
                    "port": port,
                    "service": service
                }
                
                # Categorize by risk level
                if port in high_risk_ports:
                    port_risk["implication"] = high_risk_ports[port]
                    analysis["high_risk_ports"].append(port_risk)
                    
                    # Add specific recommendations
                    if port == 21:  # FTP
                        analysis["recommendations"].append(f"Disable anonymous FTP access on {host_ip}")
                    elif port == 23:  # Telnet
                        analysis["recommendations"].append(f"Replace Telnet with SSH on {host_ip}")
                    elif port == 3389:  # RDP
                        analysis["recommendations"].append(f"Restrict RDP access with firewall rules on {host_ip}")
                
                elif port in medium_risk_ports:
                    port_risk["implication"] = medium_risk_ports[port]
                    analysis["medium_risk_ports"].append(port_risk)
                    
                    # Add web server recommendations
                    if port in [80, 443, 8080, 8443]:
                        analysis["recommendations"].append(f"Ensure web server on {host_ip}:{port} is patched and properly configured")
                
                else:
                    analysis["low_risk_ports"].append(port_risk)
        
        # General security implications
        if analysis["high_risk_ports"]:
            analysis["security_implications"].append(
                f"Found {len(analysis['high_risk_ports'])} high-risk ports that could potentially be exploited"
            )
            
            analysis["recommendations"].append("Implement a strict firewall policy to limit access to sensitive services")
            analysis["recommendations"].append("Ensure all services are running the latest security patches")
        
        if analysis["medium_risk_ports"]:
            analysis["security_implications"].append(
                f"Found {len(analysis['medium_risk_ports'])} medium-risk ports that should be reviewed"
            )
        
        # Save analysis to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_name = scan_results.get("hosts", [{}])[0].get("host", "unknown")
        safe_target_name = re.sub(r'[^a-zA-Z0-9_-]', '_', target_name)
        
        filename = f"{safe_target_name}_{timestamp}_port_analysis.json"
        filepath = os.path.join(self.scans_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(analysis, f, indent=2)
            analysis["saved_to"] = filepath
        except Exception as e:
            logger.error(f"Error saving analysis: {str(e)}")
        
        return analysis
    
    @skill(category="analysis")
    def analyze_recon_data(self, recon_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze reconnaissance data to identify security insights
        
        Args:
            recon_results: Comprehensive recon results
            
        Returns:
            Analysis with security insights
        """
        analysis = {
            "target": recon_results.get("target", "unknown"),
            "attack_surface": {
                "domains": [],
                "web_servers": [],
                "technologies": [],
                "exposed_services": []
            },
            "security_insights": [],
            "recommendations": []
        }
        
        # Analyze domains and subdomains
        main_domain = recon_results.get("target")
        subdomains = recon_results.get("subdomains", [])
        
        if main_domain:
            analysis["attack_surface"]["domains"].append({
                "domain": main_domain,
                "type": "main"
            })
        
        for subdomain in subdomains:
            analysis["attack_surface"]["domains"].append({
                "domain": subdomain,
                "type": "subdomain"
            })
        
        # Analyze web technologies
        tech_count = {}
        for tech in recon_results.get("web_technologies", []):
            tech_name = tech.get("name", "unknown")
            if tech_name in tech_count:
                tech_count[tech_name] += 1
            else:
                tech_count[tech_name] = 1
                analysis["attack_surface"]["technologies"].append(tech)
        
        # Analyze ports and services
        for port in recon_results.get("open_ports", []):
            service = {
                "port": port.get("port"),
                "protocol": port.get("protocol", "tcp"),
                "service": port.get("service", "unknown")
            }
            analysis["attack_surface"]["exposed_services"].append(service)
        
        # Generate security insights
        if len(subdomains) > 10:
            analysis["security_insights"].append(
                f"Large subdomain footprint ({len(subdomains)} subdomains) increases attack surface"
            )
            analysis["recommendations"].append(
                "Review subdomain inventory and decommission unused subdomains"
            )
        
        # Check for web servers
        web_server_ports = [80, 443, 8080, 8443]
        web_servers = []
        
        for service in analysis["attack_surface"]["exposed_services"]:
            if service["port"] in web_server_ports or "http" in service["service"].lower():
                web_servers.append(service)
                
        if web_servers:
            analysis["attack_surface"]["web_servers"] = web_servers
            analysis["security_insights"].append(
                f"Found {len(web_servers)} web servers that could host vulnerable applications"
            )
            analysis["recommendations"].append(
                "Perform web application security scanning on all web servers"
            )
            analysis["recommendations"].append(
                "Implement a Web Application Firewall (WAF) for critical web applications"
            )
        
        # Technology-specific insights
        tech_insights = {
            "WordPress": "WordPress installations should be kept updated to prevent exploitation of known vulnerabilities",
            "PHP": "PHP applications should be regularly audited for security issues",
            "IIS": "IIS servers should have security hardening applied",
            "Apache": "Apache servers should be configured with security best practices",
            "Nginx": "Nginx servers should be hardened according to security guidelines",
            "jQuery": "Outdated jQuery versions may contain security vulnerabilities",
            "Bootstrap": "Ensure front-end frameworks are updated to prevent XSS vulnerabilities"
        }
        
        for tech in analysis["attack_surface"]["technologies"]:
            tech_name = tech.get("name", "")
            for key, insight in tech_insights.items():
                if key.lower() in tech_name.lower():
                    analysis["security_insights"].append(insight)
                    break
        
        # Save analysis to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_name = recon_results.get("target", "unknown")
        safe_target_name = re.sub(r'[^a-zA-Z0-9_-]', '_', target_name)
        
        filename = f"{safe_target_name}_{timestamp}_recon_analysis.json"
        filepath = os.path.join(self.recon_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(analysis, f, indent=2)
            analysis["saved_to"] = filepath
        except Exception as e:
            logger.error(f"Error saving analysis: {str(e)}")
        
        return analysis
    
    @skill(category="analysis")
    def analyze_network_exposure(self, target: str, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze network exposure and security posture based on scan data
        
        Args:
            target: Target IP or domain
            scan_data: Combined scan data about the target
            
        Returns:
            Network exposure analysis with risk assessment
        """
        analysis = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "exposure_level": "low",  # Default to low
            "risk_factors": [],
            "mitigations": [],
            "exposure_details": {}
        }
        
        # Risk scoring system
        risk_score = 0
        
        # Check open ports
        open_ports = scan_data.get("open_ports", [])
        analysis["exposure_details"]["open_ports"] = len(open_ports)
        
        if len(open_ports) > 10:
            risk_score += 3
            analysis["risk_factors"].append("High number of open ports increases attack surface")
            analysis["mitigations"].append("Close unnecessary ports and implement network segmentation")
        elif len(open_ports) > 5:
            risk_score += 2
            analysis["risk_factors"].append("Moderate number of open ports")
            analysis["mitigations"].append("Review necessary services and close unneeded ports")
        elif len(open_ports) > 0:
            risk_score += 1
        
        # Check for high-risk services
        high_risk_services = ["ftp", "telnet", "rdp", "smb", "rsh", "rlogin"]
        exposed_high_risk = []
        
        for port in open_ports:
            service = port.get("service", "").lower()
            for hrs in high_risk_services:
                if hrs in service:
                    exposed_high_risk.append(f"{service} on port {port.get('port')}")
                    risk_score += 2
        
        if exposed_high_risk:
            analysis["exposure_details"]["high_risk_services"] = exposed_high_risk
            analysis["risk_factors"].append(f"Exposed high-risk services: {', '.join(exposed_high_risk)}")
            analysis["mitigations"].append("Replace or secure high-risk services with modern alternatives")
        
        # Check for web servers
        web_servers = []
        for port in open_ports:
            if port.get("port") in [80, 443, 8080, 8443] or "http" in port.get("service", "").lower():
                web_servers.append(f"{port.get('service')} on port {port.get('port')}")
                risk_score += 1
        
        if web_servers:
            analysis["exposure_details"]["web_servers"] = web_servers
            analysis["risk_factors"].append(f"Web servers could expose vulnerable applications")
            analysis["mitigations"].append("Ensure web servers are properly hardened and regularly scanned")
        
        # Check for database servers
        db_servers = []
        for port in open_ports:
            service = port.get("service", "").lower()
            if any(db in service for db in ["mysql", "mssql", "postgres", "oracle", "mongodb", "redis"]):
                db_servers.append(f"{service} on port {port.get('port')}")
                risk_score += 2
        
        if db_servers:
            analysis["exposure_details"]["database_servers"] = db_servers
            analysis["risk_factors"].append(f"Directly exposed database servers: {', '.join(db_servers)}")
            analysis["mitigations"].append("Place database servers behind application tier and restrict access")
        
        # Set exposure level based on risk score
        if risk_score >= 8:
            analysis["exposure_level"] = "critical"
        elif risk_score >= 5:
            analysis["exposure_level"] = "high"
        elif risk_score >= 3:
            analysis["exposure_level"] = "medium"
        else:
            analysis["exposure_level"] = "low"
        
        analysis["risk_score"] = risk_score
        
        # Add standard mitigations
        if risk_score > 0:
            analysis["mitigations"].append("Implement strict firewall rules to limit access to necessary services")
            analysis["mitigations"].append("Regularly patch all exposed services")
            analysis["mitigations"].append("Monitor for suspicious access patterns")
        
        # Save analysis to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_target_name = re.sub(r'[^a-zA-Z0-9_-]', '_', target)
        
        filename = f"{safe_target_name}_{timestamp}_exposure_analysis.json"
        filepath = os.path.join(self.scans_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(analysis, f, indent=2)
            analysis["saved_to"] = filepath
        except Exception as e:
            logger.error(f"Error saving analysis: {str(e)}")
        
        return analysis
    
    @skill(category="analysis")
    def generate_security_report(self, target: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive security report based on collected data
        
        Args:
            target: Target name
            data: Combined security data
            
        Returns:
            Security report with findings and recommendations
        """
        report = {
            "title": f"Security Assessment Report: {target}",
            "target": target,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "executive_summary": {
                "critical_findings": 0,
                "high_findings": 0,
                "medium_findings": 0,
                "low_findings": 0,
                "summary": ""
            },
            "findings": [],
            "attack_vectors": [],
            "recommendations": [],
            "methodology": [
                "Network Reconnaissance",
                "Port Scanning",
                "Service Enumeration",
                "Vulnerability Analysis"
            ]
        }
        
        # Process findings
        if "vulnerabilities" in data:
            for vuln in data.get("vulnerabilities", []):
                severity = vuln.get("severity", "medium").lower()
                
                finding = {
                    "title": vuln.get("title", "Unnamed Vulnerability"),
                    "severity": severity,
                    "description": vuln.get("description", ""),
                    "impact": vuln.get("impact", ""),
                    "remediation": vuln.get("remediation", "")
                }
                
                report["findings"].append(finding)
                
                # Update counts
                if severity == "critical":
                    report["executive_summary"]["critical_findings"] += 1
                elif severity == "high":
                    report["executive_summary"]["high_findings"] += 1
                elif severity == "medium":
                    report["executive_summary"]["medium_findings"] += 1
                elif severity == "low":
                    report["executive_summary"]["low_findings"] += 1
                
                # Add recommendation
                if "remediation" in vuln and vuln["remediation"] not in report["recommendations"]:
                    report["recommendations"].append(vuln["remediation"])
        
        # Add risk factors as findings if no vulnerabilities provided
        if "risk_factors" in data and not report["findings"]:
            for i, factor in enumerate(data.get("risk_factors", [])):
                finding = {
                    "title": f"Risk Factor {i+1}",
                    "severity": "medium",
                    "description": factor,
                    "impact": "May increase attack surface or risk of compromise",
                    "remediation": ""
                }
                
                # Try to find matching mitigation
                if "mitigations" in data and i < len(data["mitigations"]):
                    finding["remediation"] = data["mitigations"][i]
                
                report["findings"].append(finding)
                report["executive_summary"]["medium_findings"] += 1
        
        # Add network exposure details
        if "exposure_level" in data:
            report["attack_vectors"].append({
                "name": "Network Exposure",
                "risk_level": data.get("exposure_level", "low"),
                "description": f"The target has a {data.get('exposure_level', 'low')} level of network exposure.",
                "details": data.get("exposure_details", {})
            })
        
        # Add exposed services as attack vectors
        if "open_ports" in data:
            services = {}
            for port in data.get("open_ports", []):
                service = port.get("service", "unknown")
                port_num = port.get("port", 0)
                
                if service not in services:
                    services[service] = []
                
                services[service].append(port_num)
            
            for service, ports in services.items():
                # Determine risk level based on service
                risk_level = "low"
                if service.lower() in ["ftp", "telnet", "rdp", "smb"]:
                    risk_level = "high"
                elif service.lower() in ["http", "https", "ssh"]:
                    risk_level = "medium"
                
                report["attack_vectors"].append({
                    "name": f"Exposed {service}",
                    "risk_level": risk_level,
                    "description": f"The service {service} is exposed on ports {', '.join(map(str, ports))}.",
                    "details": {
                        "ports": ports,
                        "service": service
                    }
                })
        
        # Compile recommendations if not already present
        if not report["recommendations"] and "mitigations" in data:
            report["recommendations"].extend(data.get("mitigations", []))
        
        # Add standard recommendations if we don't have enough
        if len(report["recommendations"]) < 3:
            standard_recs = [
                "Implement a defense-in-depth security strategy",
                "Regularly update and patch all systems and applications",
                "Enable logging and monitoring for all critical systems",
                "Implement strong access controls and authentication mechanisms",
                "Conduct regular security assessments and penetration tests"
            ]
            
            for rec in standard_recs:
                if rec not in report["recommendations"]:
                    report["recommendations"].append(rec)
        
        # Generate executive summary
        total_findings = (
            report["executive_summary"]["critical_findings"] +
            report["executive_summary"]["high_findings"] +
            report["executive_summary"]["medium_findings"] +
            report["executive_summary"]["low_findings"]
        )
        
        if report["executive_summary"]["critical_findings"] > 0:
            risk_assessment = "critical"
        elif report["executive_summary"]["high_findings"] > 0:
            risk_assessment = "high"
        elif report["executive_summary"]["medium_findings"] > 0:
            risk_assessment = "medium"
        else:
            risk_assessment = "low"
        
        report["executive_summary"]["summary"] = (
            f"This security assessment identified {total_findings} findings "
            f"({report['executive_summary']['critical_findings']} critical, "
            f"{report['executive_summary']['high_findings']} high, "
            f"{report['executive_summary']['medium_findings']} medium, "
            f"{report['executive_summary']['low_findings']} low). "
            f"The overall security risk is assessed as {risk_assessment}."
        )
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_target_name = re.sub(r'[^a-zA-Z0-9_-]', '_', target)
        
        filename = f"{safe_target_name}_{timestamp}_security_report.json"
        filepath = os.path.join(self.results_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            report["saved_to"] = filepath
        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")
        
        return report
    
    @skill(category="analysis")
    def analyze_web_content(self, url: str, content: str) -> Dict[str, Any]:
        """
        Analyze web content for sensitive information or security issues
        
        Args:
            url: URL of the web content
            content: HTML or text content
            
        Returns:
            Analysis of the web content
        """
        analysis = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "content_length": len(content),
            "sensitive_info_found": False,
            "findings": [],
            "technologies": []
        }
        
        # Look for sensitive information
        patterns = {
            "API Key": r'(api[_-]?key|apikey)["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\'"]',
            "AWS Key": r'(AKIA[0-9A-Z]{16})',
            "Password": r'(password|passwd|pwd)["\']?\s*[:=]\s*["\']([^"\']{8,})["\'"]',
            "Private Key": r'-----BEGIN [A-Z]+ PRIVATE KEY-----',
            "Internal IP": r'(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[0-1]))\d{1,3}\.\d{1,3}',
            "Email Address": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "Access Token": r'(access_token|access[_-]?token)["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\'"]',
            "Secret": r'(secret|app_secret|client_secret)["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{10,})["\'"]',
            "Social Security Number": r'\b\d{3}[-]?\d{2}[-]?\d{4}\b'
        }
        
        for name, pattern in patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                analysis["sensitive_info_found"] = True
                # Don't include the actual sensitive info in the report
                analysis["findings"].append({
                    "type": name,
                    "count": len(matches),
                    "risk": "high" if name in ["API Key", "AWS Key", "Private Key", "Password", "Secret"] else "medium"
                })
        
        # Look for common technologies
        tech_patterns = {
            "jQuery": r'jquery[.-](\d+\.?\d+\.?\d*\.?\d*)',
            "React": r'react[.-](\d+\.?\d+\.?\d*\.?\d*)',
            "Angular": r'angular[.-](\d+\.?\d+\.?\d*\.?\d*)',
            "Bootstrap": r'bootstrap[.-](\d+\.?\d+\.?\d*\.?\d*)',
            "WordPress": r'wp-content|wordpress',
            "PHP": r'php',
            "ASP.NET": r'asp.net|__viewstate',
            "Google Analytics": r'ua-\d{6,}-\d+|ga\([\'"]create[\'"]'
        }
        
        for name, pattern in tech_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                # Try to extract version if possible
                version_match = re.search(pattern, content, re.IGNORECASE)
                version = None
                
                if version_match and len(version_match.groups()) > 0:
                    version = version_match.group(1)
                
                analysis["technologies"].append({
                    "name": name,
                    "version": version
                })
        
        # Look for potential security issues
        security_issues = []
        
        # Check for directory listing
        if "Index of /" in content and "<title>Index of" in content:
            security_issues.append({
                "type": "Directory Listing",
                "risk": "medium",
                "description": "Directory listing is enabled, which can reveal sensitive files and information"
            })
        
        # Check for exposed error messages
        error_patterns = [
            r'sql syntax|mysql error|sql error|oracle error',
            r'exception (?:in|at) (?:/[^ ]+)?|stack trace:|uncaught exception',
            r'<b>warning</b>: [a-z_]+\(\) [^<]+ in <b>',
            r'errors? in your sql syntax',
            r'<h1>Server Error|<h1>Application Error'
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                security_issues.append({
                    "type": "Exposed Error Messages",
                    "risk": "medium",
                    "description": "Detailed error messages can reveal sensitive implementation details"
                })
                break
        
        # Check for HTML comments with potentially sensitive info
        comments = re.findall(r'<!--(.+?)-->', content, re.DOTALL)
        for comment in comments:
            if any(word in comment.lower() for word in ['todo', 'fixme', 'hack', 'workaround', 'password', 'key', 'secret', 'bug']):
                security_issues.append({
                    "type": "Sensitive Comments",
                    "risk": "low",
                    "description": "HTML comments may contain sensitive information or hints about implementation"
                })
                break
        
        analysis["security_issues"] = security_issues
        
        # Save analysis to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        parsed_url = urlparse(url)
        safe_url = re.sub(r'[^a-zA-Z0-9_-]', '_', parsed_url.netloc)
        
        filename = f"{safe_url}_{timestamp}_web_analysis.json"
        filepath = os.path.join(self.recon_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(analysis, f, indent=2)
            analysis["saved_to"] = filepath
        except Exception as e:
            logger.error(f"Error saving analysis: {str(e)}")
        
        return analysis