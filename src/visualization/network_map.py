"""
G3r4ki Network Map Visualization

This module provides network mapping functionality for G3r4ki.
"""

import os
import json
import logging
import networkx as nx

# Setup logging
logger = logging.getLogger('g3r4ki.visualization.network_map')

class NetworkMap:
    """
    Network map visualization for G3r4ki
    
    Creates graph representations of network scans and security data for
    visualization in the web interface.
    """
    
    def __init__(self):
        """Initialize network map"""
        pass
    
    def create_map_from_nmap(self, nmap_data):
        """
        Create a network map from Nmap scan data
        
        Args:
            nmap_data: Processed Nmap data
            
        Returns:
            Network graph data for visualization
        """
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add network node
        G.add_node("network", label="Network", type="network")
        
        # Process each host
        if 'hosts' in nmap_data:
            for host_idx, host in enumerate(nmap_data['hosts']):
                # Create host ID
                host_id = host.get('ip') or host.get('hostname') or f"host_{host_idx}"
                
                # Add host node
                G.add_node(
                    host_id,
                    label=host.get('hostname') or host.get('ip') or f"Host {host_idx}",
                    type="host",
                    status=host.get('status'),
                    ip=host.get('ip'),
                    hostname=host.get('hostname'),
                    os=host.get('os')
                )
                
                # Link host to network
                G.add_edge("network", host_id)
                
                # Process each port/service
                if 'ports' in host:
                    for port_idx, port in enumerate(host['ports']):
                        if port['state'] == 'open':
                            # Create service ID
                            service_id = f"{host_id}_port_{port['port']}_{port['protocol']}"
                            
                            # Add service node
                            G.add_node(
                                service_id,
                                label=f"{port['service']} ({port['port']})",
                                type="service",
                                port=port['port'],
                                protocol=port['protocol'],
                                service=port['service'],
                                version=port.get('version')
                            )
                            
                            # Link service to host
                            G.add_edge(host_id, service_id)
        
        # Convert to visualization format
        return self._graph_to_vis_format(G)
    
    def create_map_from_recon(self, recon_data, domain=None):
        """
        Create a network map from reconnaissance data
        
        Args:
            recon_data: Processed reconnaissance data
            domain: Optional domain name
            
        Returns:
            Network graph data for visualization
        """
        # Create a directed graph
        G = nx.DiGraph()
        
        # Determine domain
        if not domain and 'domain' in recon_data:
            domain = recon_data['domain']
        
        # Add domain node if available
        if domain:
            G.add_node(domain, label=domain, type="domain")
            main_node = domain
        else:
            G.add_node("target", label="Target", type="target")
            main_node = "target"
        
        # Process DNS records
        if 'records' in recon_data:
            for record_idx, record in enumerate(recon_data['records']):
                record_id = f"record_{record_idx}"
                record_label = f"{record['type']}: {record['data']}"
                
                G.add_node(
                    record_id,
                    label=record_label,
                    type="record",
                    record_type=record['type'],
                    record_data=record['data']
                )
                
                G.add_edge(main_node, record_id)
        
        # Process technologies
        if 'targets' in recon_data:
            for target_idx, target in enumerate(recon_data['targets']):
                if 'url' in target:
                    url_id = f"url_{target_idx}"
                    
                    G.add_node(
                        url_id,
                        label=target['url'],
                        type="url",
                        url=target['url']
                    )
                    
                    G.add_edge(main_node, url_id)
                    
                    # Process technologies
                    if 'technologies' in target:
                        for tech_idx, tech in enumerate(target['technologies']):
                            tech_id = f"tech_{target_idx}_{tech_idx}"
                            
                            G.add_node(
                                tech_id,
                                label=tech['name'],
                                type="technology",
                                name=tech['name'],
                                details=tech.get('details')
                            )
                            
                            G.add_edge(url_id, tech_id)
        
        # Convert to visualization format
        return self._graph_to_vis_format(G)
    
    def create_map_from_vuln(self, vuln_data, target=None):
        """
        Create a network map from vulnerability scan data
        
        Args:
            vuln_data: Processed vulnerability scan data
            target: Optional target host/domain
            
        Returns:
            Network graph data for visualization
        """
        # Create a directed graph
        G = nx.DiGraph()
        
        # Determine target
        if not target and 'target' in vuln_data:
            if isinstance(vuln_data['target'], dict):
                target = vuln_data['target'].get('hostname') or vuln_data['target'].get('ip')
            else:
                target = vuln_data['target']
        
        # Add target node
        if target:
            G.add_node(target, label=target, type="target")
            main_node = target
        else:
            G.add_node("target", label="Target", type="target")
            main_node = "target"
        
        # Process findings
        if 'findings' in vuln_data:
            for finding_idx, finding in enumerate(vuln_data['findings']):
                finding_id = f"finding_{finding_idx}"
                
                G.add_node(
                    finding_id,
                    label=finding.get('vuln_id') or f"Finding {finding_idx+1}",
                    type="finding",
                    vuln_id=finding.get('vuln_id'),
                    description=finding.get('description')
                )
                
                G.add_edge(main_node, finding_id)
        
        # Process vulnerabilities
        if 'vulnerabilities' in vuln_data:
            for vuln_idx, vuln in enumerate(vuln_data['vulnerabilities']):
                if vuln.get('vulnerable', False):
                    vuln_id = f"vuln_{vuln_idx}"
                    
                    G.add_node(
                        vuln_id,
                        label=vuln['name'],
                        type="vulnerability",
                        name=vuln['name'],
                        description=vuln.get('description')
                    )
                    
                    G.add_edge(main_node, vuln_id)
        
        # Convert to visualization format
        return self._graph_to_vis_format(G)
    
    def _graph_to_vis_format(self, G):
        """
        Convert NetworkX graph to visualization format
        
        Args:
            G: NetworkX graph
            
        Returns:
            Dictionary with nodes and links for visualization
        """
        nodes = []
        links = []
        
        # Convert nodes
        for node_id in G.nodes():
            node_data = G.nodes[node_id]
            node = {
                'id': node_id,
                'label': node_data.get('label', node_id),
                'type': node_data.get('type', 'unknown')
            }
            
            # Add other attributes
            for key, value in node_data.items():
                if key not in ['id', 'label', 'type']:
                    node[key] = value
            
            nodes.append(node)
        
        # Convert edges
        for edge in G.edges():
            links.append({
                'source': edge[0],
                'target': edge[1]
            })
        
        return {
            'nodes': nodes,
            'links': links
        }
    
    def save_map_to_file(self, map_data, filename):
        """
        Save network map to a file
        
        Args:
            map_data: Network map data
            filename: Output filename
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(filename, 'w') as f:
                json.dump(map_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving network map: {e}")
            return False
    
    def load_map_from_file(self, filename):
        """
        Load network map from a file
        
        Args:
            filename: Input filename
            
        Returns:
            Network map data or None if error
        """
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading network map: {e}")
            return None