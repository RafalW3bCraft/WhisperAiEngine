"""
G3r4ki Network Skills

This module provides network-related skills for agents, such as scanning,
port enumeration, service detection, and DNS resolution.
"""

import socket
import logging
import subprocess
from typing import Dict, List, Any, Optional, Union

from src.agents.skills.base import Skill, skill
from src.security.nmap_tools import NmapScanner

# Setup logging
logger = logging.getLogger('g3r4ki.agents.skills.network')

class NetworkSkills(Skill):
    """
    Network-related skills for agents
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize network skills
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.nmap = NmapScanner(config)
    
    @skill(category="network")
    def port_scan(self, 
                  target: str, 
                  ports: Optional[str] = None, 
                  scan_type: str = "basic") -> Dict[str, Any]:
        """
        Perform a port scan on a target
        
        Args:
            target: Target IP or hostname
            ports: Ports to scan (e.g., '22,80,443' or '1-1000')
            scan_type: Type of scan (basic, quick, or full)
            
        Returns:
            Scan results
        """
        scan_type_map = {
            "basic": "",
            "quick": "-F",  # Fast scan
            "full": "-sV"   # Service detection
        }
        
        options = scan_type_map.get(scan_type, "")
        if ports:
            options += f" -p {ports}"
        
        # Perform scan
        results = self.nmap.raw_scan(target, options)
        
        # Parse and return results
        return self._parse_nmap_results(results)
    
    @skill(category="network")
    def dns_lookup(self, hostname: str) -> Dict[str, Any]:
        """
        Perform DNS lookup on a hostname
        
        Args:
            hostname: Hostname to resolve
            
        Returns:
            Resolved IP and additional information
        """
        try:
            ip_address = socket.gethostbyname(hostname)
            
            # Get additional information using host command
            try:
                process = subprocess.run(
                    ["host", hostname],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                host_output = process.stdout
            except:
                host_output = ""
            
            return {
                "hostname": hostname,
                "ip_address": ip_address,
                "additional_info": host_output.strip(),
                "success": True
            }
        except socket.gaierror as e:
            logger.error(f"DNS lookup error for {hostname}: {str(e)}")
            return {
                "hostname": hostname,
                "error": str(e),
                "success": False
            }
    
    @skill(category="network")
    def check_port(self, host: str, port: int, timeout: float = 2.0) -> Dict[str, Any]:
        """
        Check if a specific port is open on a host
        
        Args:
            host: Target hostname or IP
            port: Port number to check
            timeout: Connection timeout in seconds
            
        Returns:
            Port status information
        """
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # Try to connect
            result = sock.connect_ex((host, port))
            
            # Process result
            is_open = (result == 0)
            
            # Try to get service banner if port is open
            banner = ""
            if is_open:
                try:
                    sock.send(b"\\r\\n\\r\\n")
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                except:
                    pass
            
            sock.close()
            
            return {
                "host": host,
                "port": port,
                "is_open": is_open,
                "banner": banner,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error checking port {port} on {host}: {str(e)}")
            return {
                "host": host,
                "port": port,
                "is_open": False,
                "error": str(e),
                "success": False
            }
    
    @skill(category="network")
    def trace_route(self, target: str, max_hops: int = 30) -> Dict[str, Any]:
        """
        Perform traceroute to a target
        
        Args:
            target: Target hostname or IP
            max_hops: Maximum number of hops
            
        Returns:
            Traceroute results
        """
        try:
            # Use traceroute command
            process = subprocess.run(
                ["traceroute", "-m", str(max_hops), target],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = process.stdout
            
            # Parse traceroute output
            lines = output.strip().split("\\n")
            hops = []
            
            for line in lines[1:]:  # Skip the header line
                parts = line.split()
                if len(parts) >= 3:
                    hop_num = parts[0]
                    
                    # Handle timeout cases
                    if parts[1] == "*" and parts[2] == "*":
                        hops.append({
                            "hop": hop_num,
                            "host": "*",
                            "ip": "*",
                            "time_ms": 0
                        })
                    else:
                        # Extract hostname/IP and timing
                        hop_data = {
                            "hop": hop_num,
                            "host": parts[1],
                            "time_ms": 0
                        }
                        
                        # Check if the hop has hostname and IP
                        if "(" in parts[1] and ")" in parts[1]:
                            host_ip = parts[1].split("(")[1].split(")")[0]
                            hostname = parts[1].split("(")[0]
                            hop_data["host"] = hostname
                            hop_data["ip"] = host_ip
                        else:
                            hop_data["ip"] = parts[1]
                        
                        # Extract timing if available
                        for part in parts:
                            if "ms" in part:
                                try:
                                    hop_data["time_ms"] = float(part.replace("ms", ""))
                                    break
                                except:
                                    pass
                        
                        hops.append(hop_data)
            
            return {
                "target": target,
                "hops": hops,
                "raw_output": output,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error running traceroute to {target}: {str(e)}")
            return {
                "target": target,
                "error": str(e),
                "success": False
            }
    
    def _parse_nmap_results(self, nmap_output: str) -> Dict[str, Any]:
        """
        Parse nmap output into a structured format
        
        Args:
            nmap_output: Raw nmap output
            
        Returns:
            Parsed results
        """
        # This is a simplified parser - in a real implementation, you'd want
        # to use a proper nmap parsing library or the XML output
        
        lines = nmap_output.split("\\n")
        results = {"hosts": []}
        current_host = None
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check for scan report (new host)
            if "Nmap scan report for" in line:
                if current_host:
                    results["hosts"].append(current_host)
                
                # Extract hostname/IP
                host_data = line.split("Nmap scan report for ")[1]
                current_host = {
                    "host": host_data,
                    "ip": "",
                    "ports": []
                }
                
                # Extract IP if hostname is given
                if "(" in host_data and ")" in host_data:
                    hostname = host_data.split("(")[0].strip()
                    ip = host_data.split("(")[1].split(")")[0]
                    current_host["host"] = hostname
                    current_host["ip"] = ip
                else:
                    current_host["ip"] = host_data
            
            # Check for port information
            elif current_host and "/tcp" in line or "/udp" in line:
                parts = line.split()
                if len(parts) >= 2:
                    port_data = parts[0].split("/")
                    service = " ".join(parts[2:]) if len(parts) > 2 else ""
                    
                    port_info = {
                        "port": int(port_data[0]),
                        "protocol": port_data[1],
                        "state": parts[1],
                        "service": service
                    }
                    
                    current_host["ports"].append(port_info)
        
        # Add the last host
        if current_host:
            results["hosts"].append(current_host)
        
        return results