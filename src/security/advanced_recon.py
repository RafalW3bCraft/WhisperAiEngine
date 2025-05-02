"""
G3r4ki Advanced Reconnaissance Module

This module provides advanced reconnaissance capabilities using various tools:
- Amass: Attack surface mapping and asset discovery
- Subfinder: Subdomain discovery tool
- Whatweb: Web technology fingerprinting
- FFuf: Fast web fuzzer for content discovery
- Masscan: Fast IP port scanner
- DNSRecon: DNS enumeration script
- Aquatone: Visual website inspection
"""

import os
import re
import subprocess
import json
import logging
import tempfile
import shutil
from datetime import datetime

# Setup logging
logger = logging.getLogger('g3r4ki.security.advanced_recon')

class AdvancedRecon:
    """
    Advanced reconnaissance capabilities using multiple specialized tools
    """
    
    def __init__(self, config):
        """
        Initialize advanced recon module
        
        Args:
            config: G3r4ki configuration
        """
        self.config = config
        self.results_dir = os.path.expanduser(
            config.get('visualization', {}).get('results_dir', 'results')
        )
        
    def is_available(self):
        """
        Check if any advanced recon tools are available
        
        Returns:
            True if any tools are available, False otherwise
        """
        # Try to use the tool manager first
        try:
            from src.security.tool_manager import ToolManager
            
            tool_manager = ToolManager(self.config)
            tools = ['amass', 'subfinder', 'whatweb', 'ffuf', 'masscan', 'dnsrecon', 'aquatone']
            available = []
            
            for tool in tools:
                if tool_manager.is_tool_installed(tool):
                    available.append(tool)
                    
            if available:
                logger.info(f"Available advanced recon tools: {', '.join(available)}")
                return True
            else:
                logger.warning("No advanced recon tools available")
                logger.info("You can install tools using: g3r4ki tools install recon")
                return False
        except Exception as e:
            logger.error(f"Error using tool manager: {e}")
            # Fall back to basic tool checking
            tools = ['amass', 'subfinder', 'whatweb', 'ffuf', 'masscan', 'dnsrecon', 'aquatone']
            available = []
            
            for tool in tools:
                if self._check_tool(tool):
                    available.append(tool)
                    
            if available:
                logger.info(f"Available advanced recon tools (fallback check): {', '.join(available)}")
                return True
            else:
                logger.warning("No advanced recon tools available")
                return False
    
    def _check_tool(self, tool):
        """
        Check if a specific tool is available
        
        Args:
            tool: Tool name to check
            
        Returns:
            True if available, False otherwise
        """
        try:
            if shutil.which(tool):
                return True
                
            # Special case for Python-based tools like dnsrecon
            if tool == 'dnsrecon' and shutil.which('dnsrecon.py'):
                return True
                
            return False
        except Exception as e:
            logger.error(f"Error checking for {tool}: {e}")
            return False

    def run_amass(self, domain, timeout=600):
        """
        Run Amass for subdomain enumeration
        
        Args:
            domain: Target domain
            timeout: Timeout in seconds
            
        Returns:
            Dictionary with results
        """
        logger.info(f"Running Amass on {domain}")
        
        if not self._check_tool('amass'):
            logger.error("Amass is not available")
            return {"error": "Amass is not installed or not in PATH"}
        
        # Create temp file for output
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        output_file.close()
        
        try:
            cmd = ['amass', 'enum', '-d', domain, '-json', output_file.name, '-timeout', str(timeout)]
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Amass error: {stderr}")
                return {"error": f"Amass error: {stderr}"}
            
            # Process results
            results = {"subdomains": [], "ip_addresses": [], "sources": []}
            
            with open(output_file.name, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if 'name' in data and data['name'] not in results['subdomains']:
                            results['subdomains'].append(data['name'])
                        
                        if 'addresses' in data:
                            for addr in data['addresses']:
                                if 'ip' in addr and addr['ip'] not in results['ip_addresses']:
                                    results['ip_addresses'].append(addr['ip'])
                        
                        if 'source' in data and data['source'] not in results['sources']:
                            results['sources'].append(data['source'])
                    except json.JSONDecodeError:
                        continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error running Amass: {e}")
            return {"error": f"Error running Amass: {str(e)}"}
        finally:
            # Clean up
            try:
                os.unlink(output_file.name)
            except:
                pass
    
    def run_subfinder(self, domain):
        """
        Run Subfinder for subdomain discovery
        
        Args:
            domain: Target domain
            
        Returns:
            Dictionary with results
        """
        logger.info(f"Running Subfinder on {domain}")
        
        if not self._check_tool('subfinder'):
            logger.error("Subfinder is not available")
            return {"error": "Subfinder is not installed or not in PATH"}
        
        try:
            cmd = ['subfinder', '-d', domain, '-silent']
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Subfinder error: {stderr}")
                return {"error": f"Subfinder error: {stderr}"}
            
            # Process results
            subdomains = [line.strip() for line in stdout.splitlines() if line.strip()]
            
            return {"subdomains": subdomains}
            
        except Exception as e:
            logger.error(f"Error running Subfinder: {e}")
            return {"error": f"Error running Subfinder: {str(e)}"}
    
    def run_whatweb(self, target):
        """
        Run WhatWeb for web technology fingerprinting
        
        Args:
            target: Target URL or domain
            
        Returns:
            Dictionary with results
        """
        logger.info(f"Running WhatWeb on {target}")
        
        if not self._check_tool('whatweb'):
            logger.error("WhatWeb is not available")
            return {"error": "WhatWeb is not installed or not in PATH"}
        
        try:
            cmd = ['whatweb', '--quiet', '--log-json=-', target]
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"WhatWeb error: {stderr}")
                return {"error": f"WhatWeb error: {stderr}"}
            
            # Process results
            results = {"targets": []}
            
            try:
                data = json.loads(stdout)
                for entry in data:
                    target_info = {
                        "url": entry.get("target", ""),
                        "ip": entry.get("ip", ""),
                        "technologies": []
                    }
                    
                    for tech, info in entry.get("plugins", {}).items():
                        if tech not in ["Summary", "Title", "IP"]:
                            tech_info = {"name": tech}
                            
                            if isinstance(info, dict) and "version" in info:
                                tech_info["version"] = info["version"][0]
                            
                            target_info["technologies"].append(tech_info)
                    
                    results["targets"].append(target_info)
            except json.JSONDecodeError:
                logger.error("Error parsing WhatWeb JSON output")
                # Fallback to parsing regular output
                results["raw"] = stdout
            
            return results
            
        except Exception as e:
            logger.error(f"Error running WhatWeb: {e}")
            return {"error": f"Error running WhatWeb: {str(e)}"}
    
    def run_ffuf(self, url, wordlist=None):
        """
        Run FFuf for web fuzzing and content discovery
        
        Args:
            url: Target URL with FUZZ keyword
            wordlist: Path to wordlist (default: common.txt)
            
        Returns:
            Dictionary with results
        """
        logger.info(f"Running FFuf on {url}")
        
        if not self._check_tool('ffuf'):
            logger.error("FFuf is not available")
            return {"error": "FFuf is not installed or not in PATH"}
        
        if "FUZZ" not in url:
            url = url.rstrip('/') + "/FUZZ"
            logger.info(f"FUZZ keyword not found in URL, using {url}")
        
        # Default wordlist location for different OSes
        if not wordlist:
            possible_paths = [
                "/usr/share/wordlists/dirb/common.txt",
                "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
                "/usr/share/seclists/Discovery/Web-Content/common.txt"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    wordlist = path
                    break
        
        if not wordlist or not os.path.exists(wordlist):
            logger.error("No valid wordlist found")
            return {"error": "No valid wordlist found. Please specify one with --wordlist."}
        
        try:
            # Create temp file for output
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
            output_file.close()
            
            cmd = [
                'ffuf', 
                '-w', wordlist, 
                '-u', url, 
                '-o', output_file.name,
                '-of', 'json',
                '-s'  # Silent mode
            ]
            
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0 and process.returncode != 1:
                # FFuf may return 1 when it finds results
                logger.error(f"FFuf error: {stderr}")
                return {"error": f"FFuf error: {stderr}"}
            
            # Process results
            results = {"findings": []}
            
            try:
                with open(output_file.name, 'r') as f:
                    data = json.load(f)
                    
                    for result in data.get("results", []):
                        findings = {
                            "url": result.get("url", ""),
                            "status": result.get("status", 0),
                            "length": result.get("length", 0),
                            "words": result.get("words", 0),
                            "lines": result.get("lines", 0)
                        }
                        
                        results["findings"].append(findings)
            except json.JSONDecodeError:
                logger.error("Error parsing FFuf JSON output")
                results["raw"] = stdout
            
            return results
            
        except Exception as e:
            logger.error(f"Error running FFuf: {e}")
            return {"error": f"Error running FFuf: {str(e)}"}
        finally:
            # Clean up
            try:
                os.unlink(output_file.name)
            except:
                pass
    
    def run_masscan(self, target, ports="1-1000"):
        """
        Run Masscan for fast port scanning
        
        Args:
            target: Target IP or CIDR range
            ports: Ports to scan
            
        Returns:
            Dictionary with results
        """
        logger.info(f"Running Masscan on {target}")
        
        if not self._check_tool('masscan'):
            logger.error("Masscan is not available")
            return {"error": "Masscan is not installed or not in PATH"}
        
        try:
            # Create temp file for output
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
            output_file.close()
            
            cmd = [
                'masscan', 
                target, 
                '--ports', ports,
                '-oJ', output_file.name,
                '--rate', '1000'
            ]
            
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Masscan error: {stderr}")
                return {"error": f"Masscan error: {stderr}"}
            
            # Process results
            results = {"hosts": []}
            
            try:
                with open(output_file.name, 'r') as f:
                    data = json.load(f)
                    
                    # Group by IP address
                    hosts = {}
                    
                    for entry in data:
                        if "ip" in entry:
                            ip = entry.get("ip", "")
                            if ip not in hosts:
                                hosts[ip] = {"ip": ip, "ports": []}
                            
                            port_info = {
                                "port": entry.get("port", 0),
                                "protocol": entry.get("proto", ""),
                                "state": "open",
                                "service": "unknown"
                            }
                            
                            hosts[ip]["ports"].append(port_info)
                    
                    results["hosts"] = list(hosts.values())
            except json.JSONDecodeError:
                logger.error("Error parsing Masscan JSON output")
                # Try to parse regular output format
                host_pattern = re.compile(r'Discovered open port (\d+)/(\w+) on (\d+\.\d+\.\d+\.\d+)')
                hosts = {}
                
                for line in stdout.splitlines():
                    match = host_pattern.search(line)
                    if match:
                        port, protocol, ip = match.groups()
                        
                        if ip not in hosts:
                            hosts[ip] = {"ip": ip, "ports": []}
                        
                        port_info = {
                            "port": int(port),
                            "protocol": protocol,
                            "state": "open",
                            "service": "unknown"
                        }
                        
                        hosts[ip]["ports"].append(port_info)
                
                results["hosts"] = list(hosts.values())
            
            return results
            
        except Exception as e:
            logger.error(f"Error running Masscan: {e}")
            return {"error": f"Error running Masscan: {str(e)}"}
        finally:
            # Clean up
            try:
                os.unlink(output_file.name)
            except:
                pass
    
    def run_dnsrecon(self, domain):
        """
        Run DNSRecon for DNS enumeration
        
        Args:
            domain: Target domain
            
        Returns:
            Dictionary with results
        """
        logger.info(f"Running DNSRecon on {domain}")
        
        dnsrecon_cmd = 'dnsrecon'
        if not self._check_tool('dnsrecon') and self._check_tool('dnsrecon.py'):
            dnsrecon_cmd = 'dnsrecon.py'
        elif not self._check_tool('dnsrecon'):
            logger.error("DNSRecon is not available")
            return {"error": "DNSRecon is not installed or not in PATH"}
        
        try:
            # Create temp file for output
            output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
            output_file.close()
            
            cmd = [
                dnsrecon_cmd, 
                '-d', domain,
                '-j', output_file.name
            ]
            
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"DNSRecon error: {stderr}")
                return {"error": f"DNSRecon error: {stderr}"}
            
            # Process results
            results = {"records": []}
            
            try:
                with open(output_file.name, 'r') as f:
                    data = json.load(f)
                    
                    for entry in data:
                        record = {
                            "name": entry.get("name", ""),
                            "type": entry.get("type", ""),
                            "address": entry.get("address", ""),
                            "ttl": entry.get("ttl", 0)
                        }
                        
                        results["records"].append(record)
            except json.JSONDecodeError:
                logger.error("Error parsing DNSRecon JSON output")
                results["raw"] = stdout
            
            return results
            
        except Exception as e:
            logger.error(f"Error running DNSRecon: {e}")
            return {"error": f"Error running DNSRecon: {str(e)}"}
        finally:
            # Clean up
            try:
                os.unlink(output_file.name)
            except:
                pass
    
    def comprehensive_scan(self, target):
        """
        Perform a comprehensive reconnaissance scan on a target
        
        Args:
            target: Target domain or IP
            
        Returns:
            Dictionary with comprehensive results
        """
        logger.info(f"Starting comprehensive reconnaissance on {target}")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "reconnaissance": {}
        }
        
        # Determine if target is a domain or IP
        is_ip = re.match(r'^(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?$', target)
        
        if not is_ip:
            # Domain-specific reconnaissance
            logger.info(f"Target {target} appears to be a domain, running domain-specific tools")
            
            # Check available tools
            available_tools = []
            
            for tool in ['subfinder', 'amass', 'dnsrecon', 'whatweb']:
                if self._check_tool(tool):
                    available_tools.append(tool)
            
            if 'subfinder' in available_tools:
                logger.info("Running Subfinder...")
                results['reconnaissance']['subfinder'] = self.run_subfinder(target)
            
            if 'amass' in available_tools:
                logger.info("Running Amass (limited to 5 minutes)...")
                results['reconnaissance']['amass'] = self.run_amass(target, timeout=300)
            
            if 'dnsrecon' in available_tools:
                logger.info("Running DNSRecon...")
                results['reconnaissance']['dnsrecon'] = self.run_dnsrecon(target)
            
            if 'whatweb' in available_tools:
                logger.info("Running WhatWeb...")
                results['reconnaissance']['whatweb'] = self.run_whatweb(target)
                
                # Extract URLs for content discovery
                target_urls = []
                whatweb_results = results['reconnaissance'].get('whatweb', {})
                for target_info in whatweb_results.get('targets', []):
                    if 'url' in target_info:
                        target_urls.append(target_info['url'])
                
                # Run FFuf on discovered URLs
                if 'ffuf' in available_tools and target_urls:
                    logger.info("Running FFuf content discovery...")
                    results['reconnaissance']['ffuf'] = {}
                    
                    for url in target_urls[:3]:  # Limit to first 3 URLs
                        results['reconnaissance']['ffuf'][url] = self.run_ffuf(url)
        else:
            # IP-specific reconnaissance
            logger.info(f"Target {target} appears to be an IP address, running IP-specific tools")
            
            # Check available tools
            available_tools = []
            
            for tool in ['masscan', 'whatweb']:
                if self._check_tool(tool):
                    available_tools.append(tool)
            
            if 'masscan' in available_tools:
                logger.info("Running Masscan...")
                results['reconnaissance']['masscan'] = self.run_masscan(target)
            
            if 'whatweb' in available_tools:
                logger.info("Running WhatWeb...")
                results['reconnaissance']['whatweb'] = self.run_whatweb(target)
        
        return results
        
    def get_available_tools(self):
        """
        Get list of available tools
        
        Returns:
            Dictionary with tool availability status
        """
        tools = {
            'amass': self._check_tool('amass'),
            'subfinder': self._check_tool('subfinder'),
            'whatweb': self._check_tool('whatweb'),
            'ffuf': self._check_tool('ffuf'),
            'masscan': self._check_tool('masscan'),
            'dnsrecon': self._check_tool('dnsrecon') or self._check_tool('dnsrecon.py'),
            'aquatone': self._check_tool('aquatone')
        }
        
        return tools