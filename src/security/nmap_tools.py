#!/usr/bin/env python3
# G3r4ki Nmap integration

import os
import subprocess
import logging
import tempfile
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

logger = logging.getLogger('g3r4ki.security.nmap')

class NmapScanner:
    """Interface for Nmap network scanner"""
    
    def __init__(self, config):
        self.config = config
        self.nmap_args = config['security'].get('nmap_args', '-sS -sV -p-')
    
    def is_available(self):
        """Check if Nmap is available"""
        return os.system("which nmap > /dev/null") == 0
    
    def validate_target(self, target):
        """
        Validate target is a proper IP address, hostname, or CIDR range
        
        Args:
            target: Target string to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Simple IP address regex (not perfect but good enough for basic validation)
        ip_regex = r"^(\d{1,3}\.){3}\d{1,3}(/\d{1,2})?$"
        
        # Hostname regex (simplified)
        hostname_regex = r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$"
        
        if re.match(ip_regex, target) or re.match(hostname_regex, target):
            return True
        
        logger.warning(f"Invalid target: {target}")
        return False
    
    def scan(self, target, options=None):
        """
        Perform Nmap scan on target
        
        Args:
            target: Target to scan (IP, hostname, or CIDR range)
            options: Additional Nmap options
            
        Returns:
            Scan results as string
        """
        if not self.is_available():
            logger.error("Nmap is not installed. Install with: sudo apt install nmap")
            return "Error: Nmap is not installed. Install with: sudo apt install nmap"
        
        if not self.validate_target(target):
            return f"Error: Invalid target: {target}"
        
        # Create temp file for XML output
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
            xml_output = tmp.name
        
        try:
            # Build Nmap command
            cmd = ["nmap"]
            
            # Add arguments from config
            if self.nmap_args:
                cmd.extend(self.nmap_args.split())
            
            # Add additional options if provided
            if options:
                cmd.extend(options.split())
            
            # Add XML output
            cmd.extend(["-oX", xml_output])
            
            # Add target
            cmd.append(target)
            
            logger.info(f"Running Nmap scan: {' '.join(cmd)}")
            start_time = time.time()
            
            # Run Nmap
            process = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            scan_time = time.time() - start_time
            
            # Parse XML output
            results = self._parse_xml_output(xml_output)
            
            # Add scan information
            scan_info = f"Nmap scan of {target} completed in {scan_time:.2f} seconds\n"
            scan_info += f"Command: {' '.join(cmd)}\n\n"
            
            return scan_info + results
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Nmap scan failed: {e}")
            logger.error(f"STDERR: {e.stderr}")
            return f"Error: Nmap scan failed: {e.stderr}"
        finally:
            # Clean up temp file
            if os.path.exists(xml_output):
                os.unlink(xml_output)
    
    def _parse_xml_output(self, xml_file):
        """
        Parse Nmap XML output into readable text
        
        Args:
            xml_file: Path to Nmap XML output file
            
        Returns:
            Formatted scan results
        """
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            output = []
            
            # Process each host
            for host in root.findall('host'):
                # Get address
                address = host.find('address').get('addr')
                output.append(f"Host: {address}")
                
                # Get hostname if available
                hostnames = host.find('hostnames')
                if hostnames is not None:
                    for hostname in hostnames.findall('hostname'):
                        output.append(f"Hostname: {hostname.get('name')}")
                
                # Process ports
                ports = host.find('ports')
                if ports is not None:
                    output.append("\nOpen Ports:")
                    
                    for port in ports.findall('port'):
                        port_id = port.get('portid')
                        protocol = port.get('protocol')
                        
                        # Get service info
                        service_info = ""
                        service = port.find('service')
                        if service is not None:
                            service_name = service.get('name', '')
                            service_product = service.get('product', '')
                            service_version = service.get('version', '')
                            
                            service_info = service_name
                            if service_product:
                                service_info += f" ({service_product}"
                                if service_version:
                                    service_info += f" {service_version}"
                                service_info += ")"
                        
                        # Get state info
                        state = port.find('state')
                        if state is not None and state.get('state') == 'open':
                            output.append(f"  {port_id}/{protocol}: {service_info}")
                
                output.append("") # Add blank line between hosts
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Error parsing Nmap XML output: {e}")
            return f"Error parsing Nmap output: {e}"
