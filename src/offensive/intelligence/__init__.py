"""
G3r4ki Offensive Framework - Threat Intelligence Module

This module provides threat intelligence capabilities for G3r4ki offensive operations,
integrating with MISP, ThreatFox, OpenCTI, and other threat intel platforms to
provide real-time intelligence for offensive operations.

No capability limitations or restrictions are enforced.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Union

# Configure logging
logger = logging.getLogger("g3r4ki.offensive.intelligence")

class ThreatIntelligenceManager:
    """Manage threat intelligence for G3r4ki offensive operations."""
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """
        Initialize the threat intelligence manager.
        
        Args:
            options: Module configuration options
        """
        self.options = options or {}
        self.output_dir = self.options.get("output_dir", "results/intelligence")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # API keys - should be obtained via external configuration/vault
        self.api_keys = {
            "misp": self.options.get("misp_api_key", os.environ.get("MISP_API_KEY", "")),
            "threatfox": self.options.get("threatfox_api_key", os.environ.get("THREATFOX_API_KEY", "")),
            "opencti": self.options.get("opencti_api_key", os.environ.get("OPENCTI_API_KEY", "")),
            "virustotal": self.options.get("virustotal_api_key", os.environ.get("VIRUSTOTAL_API_KEY", "")),
            "abuseipdb": self.options.get("abuseipdb_api_key", os.environ.get("ABUSEIPDB_API_KEY", "")),
            "shodan": self.options.get("shodan_api_key", os.environ.get("SHODAN_API_KEY", "")),
            "greynoise": self.options.get("greynoise_api_key", os.environ.get("GREYNOISE_API_KEY", "")),
            "alienvault": self.options.get("alienvault_api_key", os.environ.get("ALIENVAULT_API_KEY", "")),
            "censys": self.options.get("censys_api_key", os.environ.get("CENSYS_API_KEY", "")),
            "vulners": self.options.get("vulners_api_key", os.environ.get("VULNERS_API_KEY", ""))
        }
        
        # API endpoints
        self.api_endpoints = {
            "misp": self.options.get("misp_url", "https://misp.example.com"),
            "threatfox": "https://threatfox-api.abuse.ch/api/v1/",
            "opencti": self.options.get("opencti_url", "https://opencti.example.com"),
            "virustotal": "https://www.virustotal.com/api/v3/",
            "abuseipdb": "https://api.abuseipdb.com/api/v2/",
            "shodan": "https://api.shodan.io/",
            "greynoise": "https://api.greynoise.io/v3/",
            "alienvault": "https://otx.alienvault.com/api/v1/",
            "censys": "https://search.censys.io/api/v2/",
            "vulners": "https://vulners.com/api/v3/"
        }
    
    def query_misp(self, query_type: str, query_value: str) -> Dict[str, Any]:
        """
        Query MISP for threat intelligence.
        
        Args:
            query_type: Type of query (attribute, event, tag, etc.)
            query_value: Value to query for
            
        Returns:
            Dictionary with query results
        """
        if not self.api_keys["misp"]:
            return {"success": False, "error": "MISP API key not configured"}
        
        try:
            endpoint = f"{self.api_endpoints['misp']}/attributes/restSearch"
            headers = {
                "Authorization": self.api_keys["misp"],
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            if query_type == "attribute":
                data = {
                    "returnFormat": "json",
                    "value": query_value
                }
            elif query_type == "event":
                data = {
                    "returnFormat": "json",
                    "eventid": query_value
                }
            elif query_type == "tag":
                data = {
                    "returnFormat": "json",
                    "tags": query_value
                }
            else:
                return {"success": False, "error": f"Unsupported query type: {query_type}"}
            
            response = requests.post(endpoint, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                
                # Save result to file
                output_file = os.path.join(self.output_dir, f"misp_{query_type}_{query_value.replace(':', '_').replace('/', '_')}.json")
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)
                
                return {
                    "success": True,
                    "results": result,
                    "count": len(result.get("response", {}).get("Attribute", [])),
                    "output_file": output_file
                }
            else:
                return {
                    "success": False,
                    "error": f"MISP query failed with status code {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            logger.error(f"MISP query error: {e}")
            return {"success": False, "error": str(e)}
    
    def query_threatfox(self, query_type: str, query_value: str) -> Dict[str, Any]:
        """
        Query ThreatFox for threat intelligence.
        
        Args:
            query_type: Type of query (ioc, malware, tag, etc.)
            query_value: Value to query for
            
        Returns:
            Dictionary with query results
        """
        if not self.api_keys["threatfox"]:
            return {"success": False, "error": "ThreatFox API key not configured"}
        
        try:
            endpoint = self.api_endpoints["threatfox"]
            headers = {
                "API-KEY": self.api_keys["threatfox"],
                "Content-Type": "application/json"
            }
            
            if query_type == "ioc":
                data = {
                    "query": "search_ioc",
                    "search_term": query_value
                }
            elif query_type == "malware":
                data = {
                    "query": "malware",
                    "malware": query_value
                }
            elif query_type == "tag":
                data = {
                    "query": "tag",
                    "tag": query_value
                }
            else:
                return {"success": False, "error": f"Unsupported query type: {query_type}"}
            
            response = requests.post(endpoint, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                
                # Save result to file
                output_file = os.path.join(self.output_dir, f"threatfox_{query_type}_{query_value.replace(':', '_').replace('/', '_')}.json")
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)
                
                return {
                    "success": True,
                    "results": result,
                    "count": len(result.get("data", [])),
                    "output_file": output_file
                }
            else:
                return {
                    "success": False,
                    "error": f"ThreatFox query failed with status code {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            logger.error(f"ThreatFox query error: {e}")
            return {"success": False, "error": str(e)}
    
    def query_virustotal(self, query_type: str, query_value: str) -> Dict[str, Any]:
        """
        Query VirusTotal for threat intelligence.
        
        Args:
            query_type: Type of query (ip, domain, file, url)
            query_value: Value to query for
            
        Returns:
            Dictionary with query results
        """
        if not self.api_keys["virustotal"]:
            return {"success": False, "error": "VirusTotal API key not configured"}
        
        try:
            headers = {
                "x-apikey": self.api_keys["virustotal"],
                "Content-Type": "application/json"
            }
            
            if query_type == "ip":
                endpoint = f"{self.api_endpoints['virustotal']}ip_addresses/{query_value}"
            elif query_type == "domain":
                endpoint = f"{self.api_endpoints['virustotal']}domains/{query_value}"
            elif query_type == "file":
                # For file hashes (MD5, SHA-1, SHA-256)
                endpoint = f"{self.api_endpoints['virustotal']}files/{query_value}"
            elif query_type == "url":
                # URL needs to be encoded
                import urllib.parse
                encoded_url = urllib.parse.quote_plus(query_value)
                endpoint = f"{self.api_endpoints['virustotal']}urls/{encoded_url}"
            else:
                return {"success": False, "error": f"Unsupported query type: {query_type}"}
            
            response = requests.get(endpoint, headers=headers)
            if response.status_code == 200:
                result = response.json()
                
                # Save result to file
                output_file = os.path.join(self.output_dir, f"virustotal_{query_type}_{query_value.replace(':', '_').replace('/', '_')}.json")
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)
                
                return {
                    "success": True,
                    "results": result,
                    "output_file": output_file
                }
            else:
                return {
                    "success": False,
                    "error": f"VirusTotal query failed with status code {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            logger.error(f"VirusTotal query error: {e}")
            return {"success": False, "error": str(e)}
    
    def query_shodan(self, query_type: str, query_value: str) -> Dict[str, Any]:
        """
        Query Shodan for threat intelligence.
        
        Args:
            query_type: Type of query (ip, search, ports, etc.)
            query_value: Value to query for
            
        Returns:
            Dictionary with query results
        """
        if not self.api_keys["shodan"]:
            return {"success": False, "error": "Shodan API key not configured"}
        
        try:
            if query_type == "ip":
                endpoint = f"{self.api_endpoints['shodan']}shodan/host/{query_value}?key={self.api_keys['shodan']}"
            elif query_type == "search":
                import urllib.parse
                encoded_query = urllib.parse.quote_plus(query_value)
                endpoint = f"{self.api_endpoints['shodan']}shodan/host/search?key={self.api_keys['shodan']}&query={encoded_query}"
            elif query_type == "ports":
                endpoint = f"{self.api_endpoints['shodan']}shodan/ports/{query_value}?key={self.api_keys['shodan']}"
            else:
                return {"success": False, "error": f"Unsupported query type: {query_type}"}
            
            response = requests.get(endpoint)
            if response.status_code == 200:
                result = response.json()
                
                # Save result to file
                output_file = os.path.join(self.output_dir, f"shodan_{query_type}_{query_value.replace(':', '_').replace('/', '_')}.json")
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)
                
                return {
                    "success": True,
                    "results": result,
                    "output_file": output_file
                }
            else:
                return {
                    "success": False,
                    "error": f"Shodan query failed with status code {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            logger.error(f"Shodan query error: {e}")
            return {"success": False, "error": str(e)}
    
    def query_greynoise(self, query_type: str, query_value: str) -> Dict[str, Any]:
        """
        Query GreyNoise for threat intelligence.
        
        Args:
            query_type: Type of query (ip, quick, gnql, etc.)
            query_value: Value to query for
            
        Returns:
            Dictionary with query results
        """
        if not self.api_keys["greynoise"]:
            return {"success": False, "error": "GreyNoise API key not configured"}
        
        try:
            headers = {
                "key": self.api_keys["greynoise"],
                "Content-Type": "application/json"
            }
            
            if query_type == "ip":
                endpoint = f"{self.api_endpoints['greynoise']}community/{query_value}"
            elif query_type == "quick":
                endpoint = f"{self.api_endpoints['greynoise']}community/quick/{query_value}"
            elif query_type == "gnql":
                import urllib.parse
                encoded_query = urllib.parse.quote_plus(query_value)
                endpoint = f"{self.api_endpoints['greynoise']}community/query?query={encoded_query}"
            else:
                return {"success": False, "error": f"Unsupported query type: {query_type}"}
            
            response = requests.get(endpoint, headers=headers)
            if response.status_code == 200:
                result = response.json()
                
                # Save result to file
                output_file = os.path.join(self.output_dir, f"greynoise_{query_type}_{query_value.replace(':', '_').replace('/', '_')}.json")
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)
                
                return {
                    "success": True,
                    "results": result,
                    "output_file": output_file
                }
            else:
                return {
                    "success": False,
                    "error": f"GreyNoise query failed with status code {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            logger.error(f"GreyNoise query error: {e}")
            return {"success": False, "error": str(e)}
    
    def query_abuseipdb(self, ip: str, days: int = 30) -> Dict[str, Any]:
        """
        Query AbuseIPDB for IP reputation.
        
        Args:
            ip: IP address to check
            days: Number of days to check (1-365)
            
        Returns:
            Dictionary with query results
        """
        if not self.api_keys["abuseipdb"]:
            return {"success": False, "error": "AbuseIPDB API key not configured"}
        
        try:
            endpoint = f"{self.api_endpoints['abuseipdb']}check"
            headers = {
                "Key": self.api_keys["abuseipdb"],
                "Accept": "application/json"
            }
            params = {
                "ipAddress": ip,
                "maxAgeInDays": days,
                "verbose": True
            }
            
            response = requests.get(endpoint, headers=headers, params=params)
            if response.status_code == 200:
                result = response.json()
                
                # Save result to file
                output_file = os.path.join(self.output_dir, f"abuseipdb_{ip.replace('.', '_')}.json")
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)
                
                return {
                    "success": True,
                    "results": result,
                    "output_file": output_file
                }
            else:
                return {
                    "success": False,
                    "error": f"AbuseIPDB query failed with status code {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            logger.error(f"AbuseIPDB query error: {e}")
            return {"success": False, "error": str(e)}
    
    def query_alienvault(self, query_type: str, query_value: str) -> Dict[str, Any]:
        """
        Query AlienVault OTX for threat intelligence.
        
        Args:
            query_type: Type of query (ip, domain, file, url)
            query_value: Value to query for
            
        Returns:
            Dictionary with query results
        """
        if not self.api_keys["alienvault"]:
            return {"success": False, "error": "AlienVault API key not configured"}
        
        try:
            headers = {
                "X-OTX-API-KEY": self.api_keys["alienvault"],
                "Content-Type": "application/json"
            }
            
            if query_type == "ip":
                endpoint = f"{self.api_endpoints['alienvault']}indicators/IPv4/{query_value}/general"
            elif query_type == "domain":
                endpoint = f"{self.api_endpoints['alienvault']}indicators/domain/{query_value}/general"
            elif query_type == "file":
                # For file hashes (MD5, SHA-1, SHA-256)
                endpoint = f"{self.api_endpoints['alienvault']}indicators/file/{query_value}/general"
            elif query_type == "url":
                import urllib.parse
                encoded_url = urllib.parse.quote_plus(query_value)
                endpoint = f"{self.api_endpoints['alienvault']}indicators/url/{encoded_url}/general"
            else:
                return {"success": False, "error": f"Unsupported query type: {query_type}"}
            
            response = requests.get(endpoint, headers=headers)
            if response.status_code == 200:
                result = response.json()
                
                # Save result to file
                output_file = os.path.join(self.output_dir, f"alienvault_{query_type}_{query_value.replace(':', '_').replace('/', '_')}.json")
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)
                
                return {
                    "success": True,
                    "results": result,
                    "output_file": output_file
                }
            else:
                return {
                    "success": False,
                    "error": f"AlienVault query failed with status code {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            logger.error(f"AlienVault query error: {e}")
            return {"success": False, "error": str(e)}
    
    def query_vulners(self, query_type: str, query_value: str) -> Dict[str, Any]:
        """
        Query Vulners for vulnerability intelligence.
        
        Args:
            query_type: Type of query (cve, software, text)
            query_value: Value to query for
            
        Returns:
            Dictionary with query results
        """
        if not self.api_keys["vulners"]:
            return {"success": False, "error": "Vulners API key not configured"}
        
        try:
            endpoint = f"{self.api_endpoints['vulners']}search/id"
            headers = {
                "Content-Type": "application/json"
            }
            
            if query_type == "cve":
                data = {
                    "id": query_value,
                    "apiKey": self.api_keys["vulners"]
                }
            elif query_type == "software":
                data = {
                    "software": query_value,
                    "type": "software",
                    "apiKey": self.api_keys["vulners"]
                }
                endpoint = f"{self.api_endpoints['vulners']}burp/software"
            elif query_type == "text":
                data = {
                    "query": query_value,
                    "apiKey": self.api_keys["vulners"]
                }
                endpoint = f"{self.api_endpoints['vulners']}search/audit"
            else:
                return {"success": False, "error": f"Unsupported query type: {query_type}"}
            
            response = requests.post(endpoint, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                
                # Save result to file
                output_file = os.path.join(self.output_dir, f"vulners_{query_type}_{query_value.replace(':', '_').replace('/', '_')}.json")
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)
                
                return {
                    "success": True,
                    "results": result,
                    "output_file": output_file
                }
            else:
                return {
                    "success": False,
                    "error": f"Vulners query failed with status code {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            logger.error(f"Vulners query error: {e}")
            return {"success": False, "error": str(e)}
    
    def build_target_profile(self, target: str) -> Dict[str, Any]:
        """
        Build a comprehensive target profile using multiple threat intelligence sources.
        
        Args:
            target: Target to profile (IP, domain, or hostname)
            
        Returns:
            Dictionary with target profile
        """
        results = {
            "target": target,
            "profile_data": {},
            "success": True
        }
        
        # Determine target type
        import ipaddress
        import re
        
        try:
            ipaddress.ip_address(target)
            target_type = "ip"
        except ValueError:
            if re.match(r'^[a-zA-Z0-9][-a-zA-Z0-9]+\.[a-zA-Z0-9][-a-zA-Z0-9]+', target):
                target_type = "domain"
            else:
                target_type = "hostname"
        
        # Collect intelligence based on target type
        if target_type == "ip":
            # Query various sources for IP intelligence
            results["profile_data"]["shodan"] = self.query_shodan("ip", target).get("results", {})
            results["profile_data"]["abuseipdb"] = self.query_abuseipdb(target).get("results", {})
            results["profile_data"]["greynoise"] = self.query_greynoise("ip", target).get("results", {})
            results["profile_data"]["alienvault"] = self.query_alienvault("ip", target).get("results", {})
            results["profile_data"]["virustotal"] = self.query_virustotal("ip", target).get("results", {})
        elif target_type == "domain":
            # Query various sources for domain intelligence
            results["profile_data"]["virustotal"] = self.query_virustotal("domain", target).get("results", {})
            results["profile_data"]["alienvault"] = self.query_alienvault("domain", target).get("results", {})
        
        # Save the combined profile
        output_file = os.path.join(self.output_dir, f"target_profile_{target.replace('.', '_')}.json")
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        
        results["output_file"] = output_file
        return results
    
    def check_malware_indicators(self, indicators: List[str]) -> Dict[str, Any]:
        """
        Check a list of indicators against threat intelligence sources.
        
        Args:
            indicators: List of indicators (hashes, IPs, domains, etc.)
            
        Returns:
            Dictionary with check results
        """
        results = {
            "indicators": indicators,
            "check_results": {},
            "success": True
        }
        
        for indicator in indicators:
            # Determine indicator type
            import ipaddress
            import re
            
            indicator_type = None
            try:
                ipaddress.ip_address(indicator)
                indicator_type = "ip"
            except ValueError:
                if re.match(r'^[a-zA-Z0-9][-a-zA-Z0-9]+\.[a-zA-Z0-9][-a-zA-Z0-9]+', indicator):
                    indicator_type = "domain"
                elif re.match(r'^[a-fA-F0-9]{32}$', indicator):
                    indicator_type = "md5"
                elif re.match(r'^[a-fA-F0-9]{40}$', indicator):
                    indicator_type = "sha1"
                elif re.match(r'^[a-fA-F0-9]{64}$', indicator):
                    indicator_type = "sha256"
                else:
                    indicator_type = "unknown"
            
            results["check_results"][indicator] = {
                "type": indicator_type,
                "sources": {}
            }
            
            # Check against appropriate sources based on indicator type
            if indicator_type == "ip":
                results["check_results"][indicator]["sources"]["virustotal"] = self.query_virustotal("ip", indicator).get("results", {})
                results["check_results"][indicator]["sources"]["threatfox"] = self.query_threatfox("ioc", indicator).get("results", {})
            elif indicator_type == "domain":
                results["check_results"][indicator]["sources"]["virustotal"] = self.query_virustotal("domain", indicator).get("results", {})
                results["check_results"][indicator]["sources"]["threatfox"] = self.query_threatfox("ioc", indicator).get("results", {})
            elif indicator_type in ["md5", "sha1", "sha256"]:
                results["check_results"][indicator]["sources"]["virustotal"] = self.query_virustotal("file", indicator).get("results", {})
                results["check_results"][indicator]["sources"]["threatfox"] = self.query_threatfox("ioc", indicator).get("results", {})
        
        # Save the results
        output_file = os.path.join(self.output_dir, f"indicator_check_{len(indicators)}_indicators.json")
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        
        results["output_file"] = output_file
        return results