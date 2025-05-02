"""
G3r4ki Visualization Data Processor

This module processes outputs from security tools into visualization-friendly formats.
"""

import re
import json
import logging
import xml.etree.ElementTree as ET
from collections import defaultdict

# Setup logging
logger = logging.getLogger('g3r4ki.visualization.data_processor')

class DataProcessor:
    """
    Process security tool outputs into visualization-friendly formats
    """
    
    def __init__(self):
        """Initialize data processor"""
        pass
    
    def process(self, data, data_type):
        """
        Process data based on type
        
        Args:
            data: Raw data to process
            data_type: Type of data (nmap, whois, etc.)
            
        Returns:
            Processed data in visualization-friendly format
        """
        if data_type == 'nmap':
            return self.parse_nmap(data)
        elif data_type == 'nmap_xml':
            return self.parse_nmap_xml(data)
        elif data_type == 'whois':
            return self.parse_whois(data)
        elif data_type == 'dig':
            return self.parse_dig(data)
        elif data_type == 'whatweb':
            return self.parse_whatweb(data)
        elif data_type == 'nikto':
            return self.parse_nikto(data)
        elif data_type == 'sslscan':
            return self.parse_sslscan(data)
        else:
            logger.warning(f"Unknown data type: {data_type}")
            return {'raw': data}
    
    def parse_nmap(self, data):
        """
        Parse nmap text output
        
        Args:
            data: Nmap output
            
        Returns:
            Structured data for visualization
        """
        result = {
            'hosts': []
        }
        
        current_host = None
        
        for line in data.splitlines():
            # Skip empty lines
            if not line.strip():
                continue
            
            # Check if it's a new host
            if line.startswith('Nmap scan report for'):
                if current_host:
                    result['hosts'].append(current_host)
                
                # Extract hostname/IP
                host_info = line.replace('Nmap scan report for ', '').strip()
                ip = None
                hostname = None
                
                # Handle format "hostname (ip)"
                ip_match = re.search(r'\((.*?)\)', host_info)
                if ip_match:
                    ip = ip_match.group(1)
                    hostname = host_info.split(' ')[0]
                else:
                    # Check if it's an IP address
                    if re.match(r'^\d+\.\d+\.\d+\.\d+$', host_info):
                        ip = host_info
                    else:
                        hostname = host_info
                
                current_host = {
                    'ip': ip,
                    'hostname': hostname,
                    'status': 'unknown',
                    'os': None,
                    'ports': []
                }
            
            # Check if it's host status
            elif current_host and 'Host is ' in line:
                status_match = re.search(r'Host is (\w+)', line)
                if status_match:
                    current_host['status'] = status_match.group(1)
            
            # Check if it's OS detection
            elif current_host and 'OS details:' in line:
                os_match = re.search(r'OS details: (.*?)$', line)
                if os_match:
                    current_host['os'] = os_match.group(1)
            
            # Check if it's port information
            elif current_host and re.match(r'^\d+/\w+', line):
                parts = line.split()
                if len(parts) >= 3:
                    port_proto = parts[0].split('/')
                    port = int(port_proto[0])
                    protocol = port_proto[1]
                    state = parts[1]
                    service = parts[2]
                    
                    # Extract version if available
                    version = ' '.join(parts[3:]) if len(parts) > 3 else None
                    
                    current_host['ports'].append({
                        'port': port,
                        'protocol': protocol,
                        'state': state,
                        'service': service,
                        'version': version
                    })
        
        # Add the last host if not added yet
        if current_host:
            result['hosts'].append(current_host)
        
        return result
    
    def parse_nmap_xml(self, data):
        """
        Parse nmap XML output
        
        Args:
            data: Nmap XML output
            
        Returns:
            Structured data for visualization
        """
        result = {
            'hosts': []
        }
        
        try:
            # Parse XML
            root = ET.fromstring(data)
            
            # Process each host
            for host in root.findall('.//host'):
                host_data = {
                    'ip': None,
                    'hostname': None,
                    'status': None,
                    'os': None,
                    'ports': []
                }
                
                # Get status
                status = host.find('./status')
                if status is not None:
                    host_data['status'] = status.get('state')
                
                # Get IP address
                addr = host.find('./address[@addrtype="ipv4"]')
                if addr is not None:
                    host_data['ip'] = addr.get('addr')
                
                # Get hostname
                hostname = host.find('./hostnames/hostname')
                if hostname is not None:
                    host_data['hostname'] = hostname.get('name')
                
                # Get OS
                os_match = host.find('./os/osmatch')
                if os_match is not None:
                    host_data['os'] = os_match.get('name')
                
                # Get ports
                for port in host.findall('./ports/port'):
                    port_data = {
                        'port': int(port.get('portid')),
                        'protocol': port.get('protocol'),
                        'state': None,
                        'service': None,
                        'version': None
                    }
                    
                    # Get state
                    state = port.find('./state')
                    if state is not None:
                        port_data['state'] = state.get('state')
                    
                    # Get service
                    service = port.find('./service')
                    if service is not None:
                        port_data['service'] = service.get('name')
                        
                        # Get version
                        version_parts = []
                        if service.get('product'):
                            version_parts.append(service.get('product'))
                        if service.get('version'):
                            version_parts.append(service.get('version'))
                        if service.get('extrainfo'):
                            version_parts.append(service.get('extrainfo'))
                        
                        if version_parts:
                            port_data['version'] = ' '.join(version_parts)
                    
                    host_data['ports'].append(port_data)
                
                result['hosts'].append(host_data)
            
        except Exception as e:
            logger.error(f"Error parsing Nmap XML: {e}")
            result['error'] = str(e)
        
        return result
    
    def parse_whois(self, data):
        """
        Parse whois output
        
        Args:
            data: Whois output
            
        Returns:
            Structured data for visualization
        """
        result = {
            'registrar': None,
            'creation_date': None,
            'updated_date': None,
            'expiration_date': None,
            'name_servers': [],
            'contacts': {
                'registrant': {},
                'admin': {},
                'tech': {}
            },
            'raw': data
        }
        
        lines = data.splitlines()
        current_section = None
        
        for line in lines:
            if not line.strip() or ':' not in line:
                continue
            
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            
            if not value:
                continue
            
            if key == 'registrar':
                result['registrar'] = value
            elif key == 'created date' or key == 'creation date':
                result['creation_date'] = value
            elif key == 'updated date' or key == 'last update':
                result['updated_date'] = value
            elif key == 'expiration date' or key == 'registry expiry date':
                result['expiration_date'] = value
            elif key == 'name server' and value not in result['name_servers']:
                result['name_servers'].append(value)
            elif key == 'registrant organization':
                result['contacts']['registrant']['organization'] = value
            elif key == 'registrant name':
                result['contacts']['registrant']['name'] = value
            elif key == 'registrant email':
                result['contacts']['registrant']['email'] = value
            elif key == 'admin organization':
                result['contacts']['admin']['organization'] = value
            elif key == 'admin name':
                result['contacts']['admin']['name'] = value
            elif key == 'admin email':
                result['contacts']['admin']['email'] = value
            elif key == 'tech organization':
                result['contacts']['tech']['organization'] = value
            elif key == 'tech name':
                result['contacts']['tech']['name'] = value
            elif key == 'tech email':
                result['contacts']['tech']['email'] = value
        
        return result
    
    def parse_dig(self, data):
        """
        Parse dig output
        
        Args:
            data: Dig output
            
        Returns:
            Structured data for visualization
        """
        result = {
            'query': None,
            'records': []
        }
        
        answer_section = False
        for line in data.splitlines():
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith(';'):
                if 'ANSWER SECTION' in line:
                    answer_section = True
                continue
            
            if answer_section:
                parts = line.split()
                if len(parts) >= 5:
                    record = {
                        'name': parts[0],
                        'ttl': parts[1],
                        'class': parts[2],
                        'type': parts[3],
                        'data': ' '.join(parts[4:])
                    }
                    result['records'].append(record)
        
        return result
    
    def parse_whatweb(self, data):
        """
        Parse whatweb output
        
        Args:
            data: WhatWeb output
            
        Returns:
            Structured data for visualization
        """
        result = {
            'targets': []
        }
        
        for line in data.splitlines():
            if not line.strip():
                continue
            
            # Split URL from findings
            parts = line.split(' ', 1)
            if len(parts) < 2:
                continue
            
            url = parts[0]
            findings = parts[1]
            
            # Parse out technologies
            techs = []
            for tech in re.findall(r'\[(.*?)\]', findings):
                name_ver = tech.split(',', 1)
                tech_info = {
                    'name': name_ver[0].strip()
                }
                
                if len(name_ver) > 1:
                    tech_info['details'] = name_ver[1].strip()
                
                techs.append(tech_info)
            
            result['targets'].append({
                'url': url,
                'technologies': techs
            })
        
        return result
    
    def parse_nikto(self, data):
        """
        Parse nikto output
        
        Args:
            data: Nikto output
            
        Returns:
            Structured data for visualization
        """
        result = {
            'target': None,
            'findings': []
        }
        
        for line in data.splitlines():
            line = line.strip()
            
            if not line:
                continue
            
            # Check for target line
            if line.startswith('- Target:'):
                result['target'] = line.replace('- Target:', '').strip()
            
            # Check for finding lines
            elif re.match(r'^\+ ', line):
                # Extract potential vuln ID
                vuln_id_match = re.search(r'OSVDB-(\d+)', line)
                vuln_id = None
                if vuln_id_match:
                    vuln_id = 'OSVDB-' + vuln_id_match.group(1)
                
                # Extract description
                description = line.replace('+ ', '').strip()
                if vuln_id:
                    description = re.sub(r'OSVDB-\d+: ', '', description)
                
                result['findings'].append({
                    'vuln_id': vuln_id,
                    'description': description
                })
        
        return result
    
    def parse_sslscan(self, data):
        """
        Parse sslscan output
        
        Args:
            data: SSLScan output
            
        Returns:
            Structured data for visualization
        """
        result = {
            'target': None,
            'certificates': [],
            'protocols': [],
            'ciphers': [],
            'vulnerabilities': []
        }
        
        current_section = None
        
        for line in data.splitlines():
            line = line.strip()
            
            if not line:
                continue
            
            # Check for target line
            if 'Testing SSL server' in line:
                target_match = re.search(r'Testing SSL server (.*?) on port (\d+)', line)
                if target_match:
                    result['target'] = {
                        'hostname': target_match.group(1),
                        'port': int(target_match.group(2))
                    }
            
            # Check for section headers
            elif 'SSL/TLS Protocols' in line:
                current_section = 'protocols'
            elif 'SSL Certificate' in line:
                current_section = 'certificate'
            elif 'Cipher Suites' in line:
                current_section = 'ciphers'
            
            # Process protocols
            elif current_section == 'protocols' and any(x in line for x in ['enabled', 'disabled']):
                protocol = line.split()[0]
                status = 'enabled' if 'enabled' in line else 'disabled'
                result['protocols'].append({
                    'name': protocol,
                    'status': status
                })
            
            # Process certificate details
            elif current_section == 'certificate':
                if 'Subject:' in line:
                    result['certificates'].append({
                        'subject': line.replace('Subject:', '').strip()
                    })
                elif 'Issuer:' in line and result['certificates']:
                    result['certificates'][-1]['issuer'] = line.replace('Issuer:', '').strip()
                elif 'Signature Algorithm:' in line and result['certificates']:
                    result['certificates'][-1]['signature_algorithm'] = line.replace('Signature Algorithm:', '').strip()
                elif 'Not valid before:' in line and result['certificates']:
                    result['certificates'][-1]['not_before'] = line.replace('Not valid before:', '').strip()
                elif 'Not valid after:' in line and result['certificates']:
                    result['certificates'][-1]['not_after'] = line.replace('Not valid after:', '').strip()
            
            # Process vulnerabilities
            if 'Heartbleed' in line:
                result['vulnerabilities'].append({
                    'name': 'Heartbleed',
                    'vulnerable': 'vulnerable' in line.lower(),
                    'description': 'OpenSSL TLS/DTLS heartbeat information disclosure'
                })
            elif 'POODLE' in line:
                result['vulnerabilities'].append({
                    'name': 'POODLE',
                    'vulnerable': 'vulnerable' in line.lower(),
                    'description': 'SSL 3.0 CBC cipher suites information disclosure'
                })
            elif 'LOGJAM' in line:
                result['vulnerabilities'].append({
                    'name': 'LOGJAM',
                    'vulnerable': 'vulnerable' in line.lower(),
                    'description': 'TLS DHE export-grade cipher suites downgrade'
                })
            elif 'FREAK' in line:
                result['vulnerabilities'].append({
                    'name': 'FREAK',
                    'vulnerable': 'vulnerable' in line.lower(),
                    'description': 'SSL/TLS EXPORT cipher suites downgrade'
                })
            elif 'BEAST' in line:
                result['vulnerabilities'].append({
                    'name': 'BEAST',
                    'vulnerable': 'vulnerable' in line.lower(),
                    'description': 'TLS 1.0 CBC vulnerability allowing chosen-plaintext attacks'
                })
            elif 'SWEET32' in line:
                result['vulnerabilities'].append({
                    'name': 'SWEET32',
                    'vulnerable': 'vulnerable' in line.lower(),
                    'description': 'Birthday attacks against 64-bit block ciphers (3DES, Blowfish)'
                })
        
        return result