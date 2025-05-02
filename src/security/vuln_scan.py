#!/usr/bin/env python3
# G3r4ki Vulnerability Scanner

import os
import subprocess
import logging
import tempfile
import re
import time
import json
from pathlib import Path
from datetime import datetime

logger = logging.getLogger('g3r4ki.security.vuln')

class VulnerabilityScanner:
    """Vulnerability scanner integrating multiple tools"""
    
    def __init__(self, config):
        self.config = config
        self.timeout = config['security'].get('vuln_scan_timeout', 300)
    
    def is_domain_or_ip(self, target):
        """Check if target is a domain name or IP address"""
        domain_regex = r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$"
        ip_regex = r"^(\d{1,3}\.){3}\d{1,3}(/\d{1,2})?$"
        return re.match(domain_regex, target) is not None or re.match(ip_regex, target) is not None
        
    def is_available(self):
        """Check if vulnerability scanning tools are available"""
        # Check for minimum required tools - at least nmap is essential
        has_nmap = os.system("which nmap > /dev/null") == 0
        
        # Optional tools
        has_nikto = os.system("which nikto > /dev/null") == 0
        has_sslscan = os.system("which sslscan > /dev/null") == 0
        
        # Log availability
        logger.info(f"Vulnerability scanning tools availability: nmap={has_nmap}, nikto={has_nikto}, sslscan={has_sslscan}")
        
        # We need at least Nmap for vulnerability scanning
        return has_nmap
    
    def scan(self, target):
        """
        Perform vulnerability scan on target
        
        Args:
            target: Target for vulnerability scan (domain or IP)
            
        Returns:
            Vulnerability scan results as string
        """
        results = []
        
        # Add header with timestamp
        results.append(f"Vulnerability Scan Report for {target}")
        results.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        results.append("=" * 60)
        results.append("")
        
        # Validate target
        if not self.is_domain_or_ip(target):
            return f"Error: Invalid target: {target}"
        
        # Run Nikto scan if available
        results.append("## Web Vulnerability Scan (Nikto)")
        nikto_results = self._run_nikto(target)
        results.append(nikto_results)
        results.append("")
        
        # Run SSLScan if available
        results.append("## SSL/TLS Security Scan")
        ssl_results = self._run_sslscan(target)
        results.append(ssl_results)
        results.append("")
        
        # Run basic nmap scripts
        results.append("## Network Vulnerability Scan")
        nmap_results = self._run_nmap_vuln(target)
        results.append(nmap_results)
        
        return "\n".join(results)
    
    def _run_nikto(self, target):
        """Run Nikto web vulnerability scanner"""
        if os.system("which nikto > /dev/null") != 0:
            return "Nikto not found. Install with: sudo apt install nikto"
        
        try:
            logger.info(f"Running Nikto scan on {target}")
            
            # First check if http or https
            http_url = f"http://{target}"
            https_url = f"https://{target}"
            
            # Try HTTPS first
            url = https_url
            
            result = subprocess.run(
                ["nikto", "-h", url, "-maxtime", str(self.timeout)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.timeout + 30  # Add a little buffer
            )
            
            return self._format_nikto_output(result.stdout)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Nikto scan failed: {e}")
            return f"Error running Nikto: {e.stderr}"
        except subprocess.TimeoutExpired:
            logger.warning(f"Nikto scan timed out after {self.timeout} seconds")
            return f"Nikto scan timed out after {self.timeout} seconds"
    
    def _format_nikto_output(self, output):
        """Format Nikto output to be more readable"""
        # Remove ANSI color codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        output = ansi_escape.sub('', output)
        
        # Split by lines
        lines = output.strip().split('\n')
        
        # Filter out less important lines
        filtered_lines = []
        for line in lines:
            # Skip scan info lines unless they contain timing data
            if "- Nikto" in line and "scan report" in line and "seconds" not in line:
                continue
            
            # Keep vulnerability findings and important info
            filtered_lines.append(line)
        
        return "\n".join(filtered_lines)
    
    def _run_sslscan(self, target):
        """Run SSLScan to check SSL/TLS configuration"""
        if os.system("which sslscan > /dev/null") != 0:
            return "SSLScan not found. Install with: sudo apt install sslscan"
        
        try:
            logger.info(f"Running SSLScan on {target}")
            
            result = subprocess.run(
                ["sslscan", "--no-colour", target],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=120  # 2 minute timeout for SSL scan
            )
            
            # Format output to extract important info
            formatted_output = self._format_sslscan_output(result.stdout)
            
            return formatted_output
            
        except subprocess.CalledProcessError as e:
            logger.error(f"SSLScan failed: {e}")
            if "Could not open a connection" in e.stderr:
                return "No SSL/TLS service detected on the target"
            return f"Error running SSLScan: {e.stderr}"
        except subprocess.TimeoutExpired:
            logger.warning("SSLScan timed out")
            return "SSLScan timed out after 120 seconds"
    
    def _format_sslscan_output(self, output):
        """Format SSLScan output to highlight important findings"""
        lines = output.strip().split('\n')
        
        # Sections to extract
        sections = {
            "ssl_protocols": [],
            "weak_ciphers": [],
            "certificate_info": [],
            "vulnerabilities": []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
                
            # Protocol versions
            if "Protocols" in line or "SSLv" in line or "TLSv" in line:
                current_section = "ssl_protocols"
                sections[current_section].append(line)
            
            # Weak ciphers
            elif "Ciphers" in line or "Preferred " in line or "Accepted " in line:
                if "WEAK" in line or "weak" in line:
                    current_section = "weak_ciphers"
                    sections[current_section].append(line)
            
            # Certificate info
            elif "Certificate" in line or "Subject:" in line or "Issuer:" in line or "Altnames:" in line:
                current_section = "certificate_info"
                sections[current_section].append(line)
            
            # Known vulnerabilities
            elif "Heartbleed" in line or "ROBOT" in line or "BREACH" in line or "POODLE" in line or "FREAK" in line or "DROWN" in line or "LogJam" in line:
                current_section = "vulnerabilities"
                sections[current_section].append(line)
            
            # Continue adding to current section
            elif current_section:
                sections[current_section].append(line)
        
        # Build formatted output
        result = []
        
        if sections["vulnerabilities"]:
            result.append("### SSL/TLS Vulnerabilities")
            result.extend(sections["vulnerabilities"])
            result.append("")
        
        if sections["ssl_protocols"]:
            result.append("### Supported Protocols")
            result.extend(sections["ssl_protocols"])
            result.append("")
        
        if sections["weak_ciphers"]:
            result.append("### Weak Cipher Suites")
            result.extend(sections["weak_ciphers"])
            result.append("")
        
        if sections["certificate_info"]:
            result.append("### Certificate Information")
            result.extend(sections["certificate_info"])
            result.append("")
        
        if not result:
            return "No SSL/TLS issues found or no SSL/TLS service detected"
        
        return "\n".join(result)
    
    def _run_nmap_vuln(self, target):
        """Run Nmap with vulnerability scripts"""
        if os.system("which nmap > /dev/null") != 0:
            return "Nmap not found. Install with: sudo apt install nmap"
        
        try:
            logger.info(f"Running Nmap vulnerability scan on {target}")
            
            result = subprocess.run(
                [
                    "nmap", "-sV", "--script", "vuln", 
                    "--script-timeout", "60",
                    "-p", "21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5900,8080",
                    target
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.timeout
            )
            
            # Filter output to only include findings
            return self._format_nmap_vuln_output(result.stdout)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Nmap vulnerability scan failed: {e}")
            return f"Error running Nmap vulnerability scan: {e.stderr}"
        except subprocess.TimeoutExpired:
            logger.warning(f"Nmap vulnerability scan timed out after {self.timeout} seconds")
            return f"Nmap vulnerability scan timed out after {self.timeout} seconds"
    
    def _format_nmap_vuln_output(self, output):
        """Format Nmap vulnerability scan output"""
        lines = output.strip().split('\n')
        
        result = []
        capture = False
        vulnerable_ports = []
        
        for line in lines:
            # Capture port information
            if re.match(r"^\d+/\w+\s+open", line):
                capture = True
                result.append(line)
                port_num = line.split('/')[0]
                vulnerable_ports.append(port_num)
            # Capture vulnerability information
            elif capture and "|" in line and "_" in line:
                result.append(line)
            # Capture vulnerability details
            elif capture and line.startswith("|") and "VULNERABLE" in line:
                result.append(line)
        
        if not result:
            return "No vulnerabilities found"
        
        header = f"Found potential vulnerabilities on ports: {', '.join(vulnerable_ports)}\n"
        return header + "\n".join(result)
