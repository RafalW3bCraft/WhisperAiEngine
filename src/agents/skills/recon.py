"""
G3r4ki Reconnaissance Skills

This module provides reconnaissance-related skills for agents, such as domain
enumeration, subdomain discovery, and OSINT collection.
"""

import re
import json
import logging
import subprocess
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urlparse

from src.agents.skills.base import Skill, skill
from src.security.recon import ReconScanner

# Setup logging
logger = logging.getLogger('g3r4ki.agents.skills.recon')

class ReconSkills(Skill):
    """
    Reconnaissance-related skills for agents
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize recon skills
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.recon = ReconScanner(config)
        
        # Try to import advanced recon module if available
        try:
            from src.security.advanced_recon import AdvancedRecon
            self.advanced_recon = AdvancedRecon(config)
            self._has_advanced_recon = self.advanced_recon.is_available()
        except ImportError:
            self.advanced_recon = None
            self._has_advanced_recon = False
    
    @skill(category="recon")
    def subdomain_enumeration(self, domain: str) -> Dict[str, Any]:
        """
        Enumerate subdomains for a domain
        
        Args:
            domain: Target domain
            
        Returns:
            Discovered subdomains
        """
        if self._has_advanced_recon:
            # Use advanced recon if available
            subfinder_results = self.advanced_recon.run_subfinder(domain)
            subdomains = subfinder_results.get("subdomains", [])
            
            if not subdomains and hasattr(self.advanced_recon, "run_amass"):
                # Try amass if subfinder found nothing
                amass_results = self.advanced_recon.run_amass(domain, timeout=300)
                subdomains = amass_results.get("subdomains", [])
        else:
            # Fallback to simple DNS lookups for common subdomains
            subdomains = self._basic_subdomain_enum(domain)
        
        return {
            "domain": domain,
            "subdomains": subdomains,
            "count": len(subdomains),
            "success": True
        }
    
    @skill(category="recon")
    def domain_whois(self, domain: str) -> Dict[str, Any]:
        """
        Get WHOIS information for a domain
        
        Args:
            domain: Target domain
            
        Returns:
            WHOIS information
        """
        try:
            # Use whois command
            process = subprocess.run(
                ["whois", domain],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = process.stdout
            
            # Try to extract key information
            registrar = self._extract_whois_field(output, ["Registrar:", "Registrar"])
            created_date = self._extract_whois_field(output, [
                "Creation Date:", "Created:", "Registry Creation Date:", 
                "Domain Registration Date:"
            ])
            expiry_date = self._extract_whois_field(output, [
                "Registry Expiry Date:", "Expiration Date:", "Expiry Date:", 
                "Domain Expiration Date:"
            ])
            updated_date = self._extract_whois_field(output, [
                "Updated Date:", "Last Updated On:", "Last Modified:"
            ])
            
            nameservers = []
            ns_pattern = re.compile(r"Name Server:\s*(.+?)$", re.MULTILINE | re.IGNORECASE)
            for match in ns_pattern.finditer(output):
                nameservers.append(match.group(1).strip())
            
            return {
                "domain": domain,
                "registrar": registrar,
                "created_date": created_date,
                "expiry_date": expiry_date,
                "updated_date": updated_date,
                "nameservers": nameservers,
                "raw_data": output,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error getting WHOIS for {domain}: {str(e)}")
            return {
                "domain": domain,
                "error": str(e),
                "success": False
            }
    
    @skill(category="recon")
    def web_technologies(self, url: str) -> Dict[str, Any]:
        """
        Identify technologies used by a website
        
        Args:
            url: Target URL
            
        Returns:
            Detected technologies
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        if self._has_advanced_recon and hasattr(self.advanced_recon, "run_whatweb"):
            # Use WhatWeb if available
            results = self.advanced_recon.run_whatweb(url)
            
            if "error" in results:
                return {
                    "url": url,
                    "error": results["error"],
                    "success": False
                }
            
            technologies = []
            for target in results.get("targets", []):
                for tech in target.get("technologies", []):
                    tech_info = {
                        "name": tech.get("name", "")
                    }
                    if "version" in tech:
                        tech_info["version"] = tech["version"]
                    technologies.append(tech_info)
            
            return {
                "url": url,
                "domain": domain,
                "technologies": technologies,
                "success": True
            }
        else:
            # Fallback to basic HTTP headers check
            return self._basic_tech_detection(url)
    
    @skill(category="recon")
    def content_discovery(self, url: str, wordlist_type: str = "common") -> Dict[str, Any]:
        """
        Discover content (directories, files) on a website
        
        Args:
            url: Target URL
            wordlist_type: Type of wordlist to use (common, medium, large)
            
        Returns:
            Discovered content
        """
        if self._has_advanced_recon and hasattr(self.advanced_recon, "run_ffuf"):
            # Map wordlist type to path
            wordlist_map = {
                "common": "/usr/share/wordlists/dirb/common.txt",
                "medium": "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
                "large": "/usr/share/wordlists/dirbuster/directory-list-2.3-big.txt"
            }
            
            wordlist = wordlist_map.get(wordlist_type, None)
            
            # Add FUZZ keyword if not present
            if "FUZZ" not in url:
                if url.endswith("/"):
                    url = url + "FUZZ"
                else:
                    url = url + "/FUZZ"
            
            # Run ffuf
            results = self.advanced_recon.run_ffuf(url, wordlist)
            
            if "error" in results:
                return {
                    "url": url,
                    "error": results["error"],
                    "success": False
                }
            
            # Process results
            findings = []
            for item in results.get("findings", []):
                if item.get("status", 0) < 400:  # Only include non-error responses
                    findings.append({
                        "url": item.get("url", ""),
                        "status": item.get("status", 0),
                        "size": item.get("length", 0)
                    })
            
            return {
                "url": url,
                "findings": findings,
                "count": len(findings),
                "success": True
            }
        else:
            # Simple fallback
            return {
                "url": url,
                "error": "Content discovery requires advanced recon tools",
                "success": False
            }
    
    @skill(category="recon")
    def comprehensive_recon(self, target: str) -> Dict[str, Any]:
        """
        Perform comprehensive reconnaissance on a target
        
        Args:
            target: Target domain or IP
            
        Returns:
            Comprehensive reconnaissance results
        """
        results = {
            "target": target,
            "domain_info": {},
            "subdomains": [],
            "ip_addresses": [],
            "web_technologies": [],
            "open_ports": [],
            "success": True
        }
        
        # Determine if target is a domain or IP
        is_ip = re.match(r'^(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?$', target)
        
        if not is_ip:
            # Domain-specific reconnaissance
            try:
                # Get domain WHOIS
                whois_info = self.domain_whois(target)
                results["domain_info"] = whois_info
                
                # Enumerate subdomains
                subdomain_info = self.subdomain_enumeration(target)
                results["subdomains"] = subdomain_info.get("subdomains", [])
                
                # Form URL if necessary
                url = f"http://{target}" if not target.startswith(("http://", "https://")) else target
                
                # Identify web technologies
                tech_info = self.web_technologies(url)
                results["web_technologies"] = tech_info.get("technologies", [])
                
            except Exception as e:
                logger.error(f"Error in comprehensive recon for {target}: {str(e)}")
                results["errors"] = [str(e)]
                results["success"] = False
        
        # For both domains and IPs
        try:
            from src.agents.skills.network import NetworkSkills
            network_skills = NetworkSkills(self.config)
            
            # Perform port scan
            scan_results = network_skills.port_scan(target, scan_type="quick")
            
            for host in scan_results.get("hosts", []):
                for port in host.get("ports", []):
                    if port["state"] == "open":
                        results["open_ports"].append({
                            "port": port["port"],
                            "protocol": port["protocol"],
                            "service": port["service"]
                        })
            
            # Add IP addresses
            if is_ip:
                results["ip_addresses"].append(target)
            else:
                for subdomain in results["subdomains"]:
                    try:
                        ip = network_skills.dns_lookup(subdomain).get("ip_address")
                        if ip and ip not in results["ip_addresses"]:
                            results["ip_addresses"].append(ip)
                    except:
                        pass
        
        except Exception as e:
            logger.error(f"Error in port scanning for {target}: {str(e)}")
            if "errors" not in results:
                results["errors"] = []
            results["errors"].append(str(e))
        
        return results
    
    def _basic_subdomain_enum(self, domain: str) -> List[str]:
        """
        Basic subdomain enumeration using DNS lookups
        
        Args:
            domain: Target domain
            
        Returns:
            List of discovered subdomains
        """
        # Common subdomains to check
        common_subdomains = [
            "www", "mail", "remote", "blog", "webmail", "server", "ns1", "ns2",
            "smtp", "secure", "vpn", "m", "shop", "ftp", "mail2", "test",
            "portal", "dns", "admin", "host", "api", "dev", "web", "support"
        ]
        
        discovered = []
        
        for sub in common_subdomains:
            subdomain = f"{sub}.{domain}"
            try:
                # Try to resolve subdomain
                from src.agents.skills.network import NetworkSkills
                network_skills = NetworkSkills(self.config)
                result = network_skills.dns_lookup(subdomain)
                
                if result.get("success", False):
                    discovered.append(subdomain)
            except:
                pass
        
        return discovered
    
    def _extract_whois_field(self, whois_data: str, field_names: List[str]) -> str:
        """
        Extract a field from WHOIS data
        
        Args:
            whois_data: Raw WHOIS data
            field_names: Possible field names to look for
            
        Returns:
            Extracted field value or empty string
        """
        for field in field_names:
            pattern = re.compile(f"{field}\\s*(.+?)$", re.MULTILINE | re.IGNORECASE)
            match = pattern.search(whois_data)
            if match:
                return match.group(1).strip()
        return ""
    
    def _basic_tech_detection(self, url: str) -> Dict[str, Any]:
        """
        Basic technology detection using HTTP headers
        
        Args:
            url: Target URL
            
        Returns:
            Detected technologies
        """
        import requests
        
        try:
            # Get HTTP headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            
            technologies = []
            
            # Check server header
            server = response.headers.get("Server", "")
            if server:
                technologies.append({"name": f"Server: {server}"})
            
            # Check for common technologies
            if "X-Powered-By" in response.headers:
                technologies.append({"name": f"X-Powered-By: {response.headers['X-Powered-By']}"})
            
            if "Set-Cookie" in response.headers:
                cookies = response.headers["Set-Cookie"]
                if "PHPSESSID" in cookies:
                    technologies.append({"name": "PHP"})
                if "JSESSIONID" in cookies:
                    technologies.append({"name": "Java"})
                if "ASP.NET_SessionId" in cookies:
                    technologies.append({"name": "ASP.NET"})
            
            # Check for common JS frameworks in HTML
            html = response.text.lower()
            if "jquery" in html:
                technologies.append({"name": "jQuery"})
            if "bootstrap" in html:
                technologies.append({"name": "Bootstrap"})
            if "react" in html and "reactdom" in html:
                technologies.append({"name": "React"})
            if "angular" in html:
                technologies.append({"name": "Angular"})
            if "vue" in html:
                technologies.append({"name": "Vue.js"})
            
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            return {
                "url": url,
                "domain": domain,
                "technologies": technologies,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error in basic tech detection for {url}: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "success": False
            }