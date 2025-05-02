#!/usr/bin/env python3
# G3r4ki Reconnaissance tools

import os
import subprocess
import logging
import tempfile
import re
import time
import json
from pathlib import Path
from datetime import datetime
from src.security.nmap_tools import NmapScanner

logger = logging.getLogger('g3r4ki.security.recon')

class ReconScanner:
    """Reconnaissance scanner integrating multiple tools"""
    
    def __init__(self, config):
        self.config = config
        self.max_depth = config['security'].get('max_recon_depth', 2)
        self.nmap = NmapScanner(config)
    
    def is_domain(self, target):
        """Check if target is a domain name"""
        domain_regex = r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$"
        return re.match(domain_regex, target) is not None and "." in target
    
    def is_ip(self, target):
        """Check if target is an IP address"""
        ip_regex = r"^(\d{1,3}\.){3}\d{1,3}(/\d{1,2})?$"
        return re.match(ip_regex, target) is not None
        
    def is_available(self):
        """Check if reconnaissance tools are available"""
        # Check for minimum required tools
        has_whois = os.system("which whois > /dev/null") == 0
        has_dig = os.system("which dig > /dev/null") == 0
        
        # Check if nmap scanner is available (essential)
        has_nmap = self.nmap.is_available()
        
        # Optional tools
        has_amass = os.system("which amass > /dev/null") == 0
        has_subfinder = os.system("which subfinder > /dev/null") == 0
        has_whatweb = os.system("which whatweb > /dev/null") == 0
        
        # Log availability
        logger.info(f"Recon tools availability: whois={has_whois}, dig={has_dig}, nmap={has_nmap}")
        logger.info(f"Optional tools: amass={has_amass}, subfinder={has_subfinder}, whatweb={has_whatweb}")
        
        # At minimum, we need WHOIS, dig, and Nmap for basic recon
        return has_whois and has_dig and has_nmap
    
    def scan(self, target):
        """
        Perform reconnaissance on target
        
        Args:
            target: Target for reconnaissance (domain or IP)
            
        Returns:
            Reconnaissance results as string
        """
        results = []
        
        # Add header with timestamp
        results.append(f"Reconnaissance Report for {target}")
        results.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        results.append("=" * 60)
        results.append("")
        
        # Choose scan type based on target
        if self.is_domain(target):
            results.append(self._domain_recon(target))
        elif self.is_ip(target):
            results.append(self._ip_recon(target))
        else:
            results.append(f"Error: Invalid target: {target}")
        
        return "\n".join(results)
    
    def _domain_recon(self, domain):
        """Perform domain reconnaissance"""
        results = []
        
        results.append("## Domain Reconnaissance")
        results.append("")
        
        # Whois lookup
        results.append("### WHOIS Information")
        whois_info = self._run_whois(domain)
        results.append(whois_info)
        results.append("")
        
        # DNS enumeration
        results.append("### DNS Records")
        dns_info = self._run_dns_enumeration(domain)
        results.append(dns_info)
        results.append("")
        
        # Subdomain enumeration if tools available
        if os.system("which amass > /dev/null") == 0 or os.system("which subfinder > /dev/null") == 0:
            results.append("### Subdomain Enumeration")
            subdomain_info = self._run_subdomain_enumeration(domain)
            results.append(subdomain_info)
            results.append("")
        
        # Web technologies scan if available
        if os.system("which whatweb > /dev/null") == 0:
            results.append("### Web Technologies")
            tech_info = self._run_whatweb(domain)
            results.append(tech_info)
            results.append("")
        
        # Basic Nmap scan
        results.append("### Network Scan")
        scan_info = self.nmap.scan(domain, "-sS -sV -p80,443,8080,8443")
        results.append(scan_info)
        
        return "\n".join(results)
    
    def _ip_recon(self, ip):
        """Perform IP reconnaissance"""
        results = []
        
        results.append("## IP Reconnaissance")
        results.append("")
        
        # Whois lookup for IP
        results.append("### IP WHOIS Information")
        whois_info = self._run_whois(ip)
        results.append(whois_info)
        results.append("")
        
        # Reverse DNS lookup
        results.append("### Reverse DNS")
        reverse_dns = self._run_reverse_dns(ip)
        results.append(reverse_dns)
        results.append("")
        
        # Full port scan
        results.append("### Network Scan")
        scan_info = self.nmap.scan(ip)
        results.append(scan_info)
        
        return "\n".join(results)
    
    def _run_whois(self, target):
        """Run whois lookup"""
        if os.system("which whois > /dev/null") != 0:
            return "Error: whois command not found. Install with: sudo apt install whois"
        
        try:
            result = subprocess.run(
                ["whois", target],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Extract important parts from whois output
            important_fields = [
                "Domain Name", "Registrar", "Registrant", "Admin", "Tech",
                "Name Server", "Updated Date", "Creation Date", "Expiration Date",
                "Status", "DNSSEC", "Organization", "Address", "City", "State", "Country"
            ]
            
            filtered_output = []
            for line in result.stdout.split('\n'):
                for field in important_fields:
                    if field.lower() in line.lower() and ":" in line:
                        filtered_output.append(line.strip())
            
            if filtered_output:
                return "\n".join(filtered_output)
            else:
                # If no important fields found, return full output (truncated)
                return result.stdout[:2000] + ("..." if len(result.stdout) > 2000 else "")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Whois lookup failed: {e}")
            return f"Error running whois: {e.stderr}"
    
    def _run_dns_enumeration(self, domain):
        """Run DNS enumeration"""
        if os.system("which dig > /dev/null") != 0:
            return "Error: dig command not found. Install with: sudo apt install dnsutils"
        
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME"]
        results = []
        
        for record_type in record_types:
            try:
                result = subprocess.run(
                    ["dig", "+short", domain, record_type],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if result.stdout.strip():
                    results.append(f"{record_type} Records:")
                    for line in result.stdout.strip().split('\n'):
                        results.append(f"  {line}")
                    results.append("")
                
            except subprocess.CalledProcessError as e:
                logger.error(f"DNS enumeration failed for {record_type}: {e}")
        
        if not results:
            return "No DNS records found"
        
        return "\n".join(results)
    
    def _run_reverse_dns(self, ip):
        """Run reverse DNS lookup"""
        if os.system("which dig > /dev/null") != 0:
            return "Error: dig command not found. Install with: sudo apt install dnsutils"
        
        try:
            result = subprocess.run(
                ["dig", "+short", "-x", ip],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.stdout.strip():
                return result.stdout.strip()
            else:
                return "No reverse DNS records found"
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Reverse DNS lookup failed: {e}")
            return f"Error running reverse DNS lookup: {e.stderr}"
    
    def _run_subdomain_enumeration(self, domain):
        """Run subdomain enumeration using available tools"""
        results = []
        subdomains = set()
        
        # Try amass if available (best option)
        if os.system("which amass > /dev/null") == 0:
            try:
                logger.info(f"Running amass subdomain enumeration for {domain}")
                result = subprocess.run(
                    ["amass", "enum", "-passive", "-d", domain],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=300  # Limit to 5 minutes
                )
                
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        subdomains.add(line.strip())
                
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                logger.error(f"Amass enumeration failed or timed out: {e}")
                results.append("Amass enumeration failed or timed out.")
        
        # Try subfinder if available
        if os.system("which subfinder > /dev/null") == 0:
            try:
                logger.info(f"Running subfinder enumeration for {domain}")
                result = subprocess.run(
                    ["subfinder", "-d", domain, "-silent"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=300  # Limit to 5 minutes
                )
                
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        subdomains.add(line.strip())
                
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                logger.error(f"Subfinder enumeration failed or timed out: {e}")
                results.append("Subfinder enumeration failed or timed out.")
        
        # Format results
        if subdomains:
            results.append(f"Found {len(subdomains)} subdomains:")
            for subdomain in sorted(subdomains):
                results.append(f"  {subdomain}")
        else:
            results.append("No subdomains found")
        
        return "\n".join(results)
    
    def _run_whatweb(self, domain):
        """Run WhatWeb to identify web technologies"""
        try:
            result = subprocess.run(
                ["whatweb", "-a", "3", domain],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            return result.stdout.strip()
            
        except subprocess.CalledProcessError as e:
            logger.error(f"WhatWeb scan failed: {e}")
            return f"Error running WhatWeb: {e.stderr}"
