// G3r4ki Network Map JavaScript

// Initialize Socket.IO connection
const socket = io();

// Store results data
let scanResults = {};
let reconResults = {};
let vulnResults = {};
let currentMapData = null;

// DOM Elements
const mapTypeSelect = document.getElementById('mapTypeSelect');
const targetSelect = document.getElementById('targetSelect');
const updateMapBtn = document.getElementById('updateMapBtn');
const liveUpdateCheck = document.getElementById('liveUpdateCheck');
const networkMap = document.getElementById('networkMap');
const nodeDetailsModal = new bootstrap.Modal(document.getElementById('nodeDetailsModal'));
const nodeDetailsTitle = document.getElementById('nodeDetailsTitle');
const nodeDetailsContent = document.getElementById('nodeDetailsContent');

// D3.js visualization elements
let svg = null;
let simulation = null;
let tooltip = null;

// Initialize network map
function initNetworkMap() {
    // Setup event listeners
    setupEventListeners();
    
    // Create D3.js visualization
    createVisualization();
    
    // Load initial data
    loadInitialData();
}

// Set up event listeners
function setupEventListeners() {
    // Map type select change
    mapTypeSelect.addEventListener('change', () => {
        loadTargetsForMapType(mapTypeSelect.value);
    });
    
    // Update map button
    updateMapBtn.addEventListener('click', updateMap);
    
    // Socket.IO event listeners
    socket.on('connect', () => {
        console.log('Connected to server');
    });
    
    socket.on('scan_update', (data) => {
        console.log('Scan update received:', data);
        if (liveUpdateCheck.checked && mapTypeSelect.value === 'scan') {
            loadScanResults().then(() => {
                if (targetSelect.value === data.target) {
                    updateMap();
                }
            });
        }
    });
    
    socket.on('recon_update', (data) => {
        console.log('Recon update received:', data);
        if (liveUpdateCheck.checked && mapTypeSelect.value === 'recon') {
            loadReconResults().then(() => {
                if (targetSelect.value === data.target) {
                    updateMap();
                }
            });
        }
    });
    
    socket.on('vuln_update', (data) => {
        console.log('Vulnerability scan update received:', data);
        if (liveUpdateCheck.checked && mapTypeSelect.value === 'vuln') {
            loadVulnResults().then(() => {
                if (targetSelect.value === data.target) {
                    updateMap();
                }
            });
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', () => {
        if (simulation) {
            simulation
                .force('center', d3.forceCenter(
                    networkMap.clientWidth / 2, 
                    networkMap.clientHeight / 2
                ));
            simulation.alpha(0.3).restart();
        }
    });
}

// Create D3.js visualization
function createVisualization() {
    // Create SVG element
    svg = d3.select('#networkMap')
        .append('svg')
        .attr('width', '100%')
        .attr('height', '100%');
    
    // Create tooltip
    tooltip = d3.select('body')
        .append('div')
        .attr('class', 'tooltip')
        .style('opacity', 0);
    
    // Create force simulation
    simulation = d3.forceSimulation()
        .force('link', d3.forceLink().id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-500))
        .force('center', d3.forceCenter(
            networkMap.clientWidth / 2, 
            networkMap.clientHeight / 2
        ));
}

// Load initial data
function loadInitialData() {
    // Load all results
    Promise.all([
        loadScanResults(),
        loadReconResults(),
        loadVulnResults()
    ]).then(() => {
        // Check for URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const mapType = urlParams.get('type');
        const target = urlParams.get('target');
        
        if (mapType) {
            mapTypeSelect.value = mapType;
        }
        
        // Load targets for selected map type
        loadTargetsForMapType(mapTypeSelect.value).then(() => {
            if (target && targetSelect.querySelector(`option[value="${target}"]`)) {
                targetSelect.value = target;
                updateMap();
            }
        });
    });
}

// Load scan results
function loadScanResults() {
    return fetch('/api/scans')
        .then(response => response.json())
        .then(data => {
            scanResults = data;
            return data;
        })
        .catch(error => {
            console.error('Error loading scan results:', error);
            return {};
        });
}

// Load reconnaissance results
function loadReconResults() {
    return fetch('/api/recon')
        .then(response => response.json())
        .then(data => {
            reconResults = data;
            return data;
        })
        .catch(error => {
            console.error('Error loading recon results:', error);
            return {};
        });
}

// Load vulnerability scan results
function loadVulnResults() {
    return fetch('/api/vuln')
        .then(response => response.json())
        .then(data => {
            vulnResults = data;
            return data;
        })
        .catch(error => {
            console.error('Error loading vulnerability scan results:', error);
            return {};
        });
}

// Load targets for selected map type
function loadTargetsForMapType(mapType) {
    // Clear current options
    targetSelect.innerHTML = '<option value="">Select a target</option>';
    
    // Get targets based on map type
    let targets = [];
    
    switch (mapType) {
        case 'scan':
            targets = Object.keys(scanResults);
            break;
        case 'recon':
            targets = Object.keys(reconResults);
            break;
        case 'vuln':
            targets = Object.keys(vulnResults);
            break;
    }
    
    // Add options for each target
    targets.forEach(target => {
        const option = document.createElement('option');
        option.value = target;
        option.textContent = target;
        targetSelect.appendChild(option);
    });
    
    // Return a promise that resolves when the DOM is updated
    return new Promise(resolve => {
        setTimeout(resolve, 0);
    });
}

// Update the network map
function updateMap() {
    const mapType = mapTypeSelect.value;
    const target = targetSelect.value;
    
    if (!target) {
        return;
    }
    
    // Get map data based on type and target
    let mapData = null;
    
    switch (mapType) {
        case 'scan':
            if (scanResults[target] && scanResults[target].data) {
                // For simplicity, use a predefined network graph structure
                // In a real implementation, this would call the API to get the graph data
                mapData = createNetworkMapFromScan(scanResults[target].data);
            }
            break;
        case 'recon':
            if (reconResults[target] && reconResults[target].data) {
                mapData = createNetworkMapFromRecon(reconResults[target].data);
            }
            break;
        case 'vuln':
            if (vulnResults[target] && vulnResults[target].data) {
                mapData = createNetworkMapFromVuln(vulnResults[target].data);
            }
            break;
    }
    
    if (mapData) {
        currentMapData = mapData;
        renderNetworkMap(mapData);
    }
}

// Create network map from scan data
function createNetworkMapFromScan(scanData) {
    // This is a simplified implementation for demonstration
    // In a real implementation, this would call the API to get the proper graph data
    
    const nodes = [];
    const links = [];
    
    // Add central node for the network
    nodes.push({
        id: 'network',
        label: 'Network',
        type: 'network'
    });
    
    // Add host nodes and links
    if (scanData.hosts) {
        scanData.hosts.forEach((host, index) => {
            const hostId = host.ip || host.hostname || `host_${index}`;
            nodes.push({
                id: hostId,
                label: host.hostname || host.ip || `Host ${index}`,
                type: 'host',
                status: host.status,
                os: host.os,
                data: host
            });
            
            // Link to network
            links.push({
                source: 'network',
                target: hostId
            });
            
            // Add service nodes for open ports
            if (host.ports) {
                host.ports.forEach(port => {
                    if (port.state === 'open') {
                        const serviceId = `${hostId}_${port.port}_${port.protocol}`;
                        nodes.push({
                            id: serviceId,
                            label: `${port.service} (${port.port})`,
                            type: 'service',
                            port: port.port,
                            protocol: port.protocol,
                            version: port.version,
                            data: port
                        });
                        
                        // Link to host
                        links.push({
                            source: hostId,
                            target: serviceId
                        });
                    }
                });
            }
        });
    }
    
    return { nodes, links };
}

// Create network map from reconnaissance data
function createNetworkMapFromRecon(reconData) {
    const nodes = [];
    const links = [];
    
    // Add domain node
    if (reconData.domain) {
        nodes.push({
            id: reconData.domain,
            label: reconData.domain,
            type: 'domain',
            data: reconData
        });
        
        // Add DNS records
        if (reconData.records) {
            reconData.records.forEach((record, index) => {
                const recordId = `record_${index}`;
                nodes.push({
                    id: recordId,
                    label: `${record.type}: ${record.data}`,
                    type: 'record',
                    recordType: record.type,
                    data: record
                });
                
                // Link to domain
                links.push({
                    source: reconData.domain,
                    target: recordId
                });
            });
        }
    }
    
    // Add technology nodes
    if (reconData.targets) {
        reconData.targets.forEach((target, targetIndex) => {
            if (target.url) {
                const urlId = `url_${targetIndex}`;
                nodes.push({
                    id: urlId,
                    label: target.url,
                    type: 'url',
                    data: target
                });
                
                // Link to domain if possible
                if (reconData.domain && target.url.includes(reconData.domain)) {
                    links.push({
                        source: reconData.domain,
                        target: urlId
                    });
                }
                
                // Add technology nodes
                if (target.technologies) {
                    target.technologies.forEach((tech, techIndex) => {
                        const techId = `tech_${targetIndex}_${techIndex}`;
                        nodes.push({
                            id: techId,
                            label: tech.name,
                            type: 'technology',
                            data: tech
                        });
                        
                        // Link to URL
                        links.push({
                            source: urlId,
                            target: techId
                        });
                    });
                }
            }
        });
    }
    
    return { nodes, links };
}

// Create network map from vulnerability scan data
function createNetworkMapFromVuln(vulnData) {
    const nodes = [];
    const links = [];
    
    // Add target node
    const targetId = 'target';
    let targetLabel = 'Target';
    
    if (vulnData.target) {
        if (typeof vulnData.target === 'object') {
            targetLabel = vulnData.target.hostname || vulnData.target.ip || 'Target';
        } else {
            targetLabel = vulnData.target;
        }
    }
    
    nodes.push({
        id: targetId,
        label: targetLabel,
        type: 'host',
        data: vulnData.target
    });
    
    // Add findings
    if (vulnData.findings) {
        vulnData.findings.forEach((finding, index) => {
            const findingId = `finding_${index}`;
            nodes.push({
                id: findingId,
                label: finding.vuln_id || `Finding ${index + 1}`,
                type: 'finding',
                data: finding
            });
            
            // Link to target
            links.push({
                source: targetId,
                target: findingId
            });
        });
    }
    
    // Add vulnerabilities
    if (vulnData.vulnerabilities) {
        vulnData.vulnerabilities.forEach((vuln, index) => {
            if (vuln.vulnerable) {
                const vulnId = `vuln_${index}`;
                nodes.push({
                    id: vulnId,
                    label: vuln.name,
                    type: 'vulnerability',
                    data: vuln
                });
                
                // Link to target
                links.push({
                    source: targetId,
                    target: vulnId
                });
            }
        });
    }
    
    // Add certificates
    if (vulnData.certificates) {
        vulnData.certificates.forEach((cert, index) => {
            const certId = `cert_${index}`;
            nodes.push({
                id: certId,
                label: `Certificate`,
                type: 'certificate',
                data: cert
            });
            
            // Link to target
            links.push({
                source: targetId,
                target: certId
            });
        });
    }
    
    return { nodes, links };
}

// Render the network map
function renderNetworkMap(data) {
    // Clear existing visualization
    svg.selectAll('*').remove();
    
    // Stop current simulation
    if (simulation) {
        simulation.stop();
    }
    
    // Create the links
    const link = svg.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(data.links)
        .enter().append('line')
        .attr('class', 'link')
        .attr('stroke-width', 1.5);
    
    // Create the nodes
    const node = svg.append('g')
        .attr('class', 'nodes')
        .selectAll('circle')
        .data(data.nodes)
        .enter().append('circle')
        .attr('class', 'node')
        .attr('r', d => getNodeRadius(d))
        .attr('fill', d => getNodeColor(d))
        .on('mouseover', handleNodeMouseOver)
        .on('mouseout', handleNodeMouseOut)
        .on('click', handleNodeClick)
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    // Add text labels
    const text = svg.append('g')
        .attr('class', 'labels')
        .selectAll('text')
        .data(data.nodes)
        .enter().append('text')
        .text(d => d.label)
        .attr('font-size', d => {
            switch (d.type) {
                case 'network':
                case 'domain':
                    return 14;
                default:
                    return 12;
            }
        })
        .attr('dx', d => getNodeRadius(d) + 5)
        .attr('dy', '.35em');
    
    // Update the simulation
    simulation.nodes(data.nodes)
        .on('tick', ticked);
    
    simulation.force('link')
        .links(data.links);
    
    // Restart the simulation
    simulation.alpha(1).restart();
    
    // Define tick function
    function ticked() {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        text
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    }
    
    // Mouse over handler
    function handleNodeMouseOver(event, d) {
        // Show tooltip
        tooltip.transition()
            .duration(200)
            .style('opacity', .9);
        
        tooltip.html(getNodeTooltip(d))
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px');
        
        // Highlight node
        d3.select(this)
            .attr('stroke', '#000')
            .attr('stroke-width', 2);
    }
    
    // Mouse out handler
    function handleNodeMouseOut() {
        // Hide tooltip
        tooltip.transition()
            .duration(500)
            .style('opacity', 0);
        
        // Remove highlight
        d3.select(this)
            .attr('stroke', null)
            .attr('stroke-width', null);
    }
    
    // Click handler
    function handleNodeClick(event, d) {
        // Show node details modal
        showNodeDetails(d);
    }
    
    // Drag functions
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

// Get node radius based on type
function getNodeRadius(node) {
    switch (node.type) {
        case 'network':
        case 'domain':
            return 25;
        case 'host':
            return 20;
        case 'service':
        case 'url':
            return 15;
        case 'vulnerability':
            return 18;
        default:
            return 12;
    }
}

// Get node color based on type
function getNodeColor(node) {
    switch (node.type) {
        case 'network':
        case 'domain':
            return '#4e79a7';
        case 'host':
            return '#f28e2c';
        case 'service':
        case 'url':
            return '#59a14f';
        case 'vulnerability':
            return '#e15759';
        case 'finding':
            return '#d4a6c8';
        case 'certificate':
            return '#bab0ac';
        default:
            return '#76b7b2';
    }
}

// Get tooltip content for node
function getNodeTooltip(node) {
    let content = `<strong>${node.label}</strong><br>Type: ${node.type}`;
    
    switch (node.type) {
        case 'host':
            if (node.os) content += `<br>OS: ${node.os}`;
            if (node.status) content += `<br>Status: ${node.status}`;
            break;
        case 'service':
            content += `<br>Port: ${node.port}/${node.protocol}`;
            if (node.version) content += `<br>Version: ${node.version}`;
            break;
        case 'vulnerability':
            content += `<br>Status: ${node.data && node.data.vulnerable ? 'Vulnerable' : 'Not Vulnerable'}`;
            break;
        case 'record':
            content += `<br>Type: ${node.recordType}`;
            break;
        case 'technology':
            if (node.data && node.data.details) content += `<br>Details: ${node.data.details}`;
            break;
    }
    
    return content;
}

// Show node details in modal
function showNodeDetails(node) {
    // Set modal title
    nodeDetailsTitle.textContent = `${node.label} Details`;
    
    // Build content based on node type
    let content = `<div class="node-detail-item">
        <span class="node-detail-label">Type:</span> ${node.type}
    </div>`;
    
    switch (node.type) {
        case 'host':
            if (node.data) {
                if (node.data.ip) {
                    content += `<div class="node-detail-item">
                        <span class="node-detail-label">IP:</span> ${node.data.ip}
                    </div>`;
                }
                
                if (node.data.hostname) {
                    content += `<div class="node-detail-item">
                        <span class="node-detail-label">Hostname:</span> ${node.data.hostname}
                    </div>`;
                }
                
                if (node.data.status) {
                    content += `<div class="node-detail-item">
                        <span class="node-detail-label">Status:</span> ${node.data.status}
                    </div>`;
                }
                
                if (node.data.os) {
                    content += `<div class="node-detail-item">
                        <span class="node-detail-label">OS:</span> ${node.data.os}
                    </div>`;
                }
                
                if (node.data.ports && node.data.ports.length > 0) {
                    content += `<div class="node-detail-item">
                        <span class="node-detail-label">Open Ports:</span>
                        <table class="table table-sm table-striped mt-2">
                            <thead>
                                <tr>
                                    <th>Port</th>
                                    <th>Protocol</th>
                                    <th>Service</th>
                                    <th>Version</th>
                                </tr>
                            </thead>
                            <tbody>`;
                    
                    node.data.ports.forEach(port => {
                        if (port.state === 'open') {
                            content += `<tr>
                                <td>${port.port}</td>
                                <td>${port.protocol}</td>
                                <td>${port.service}</td>
                                <td>${port.version || '-'}</td>
                            </tr>`;
                        }
                    });
                    
                    content += `</tbody>
                        </table>
                    </div>`;
                }
            }
            break;
            
        case 'service':
            if (node.data) {
                content += `<div class="node-detail-item">
                    <span class="node-detail-label">Port:</span> ${node.data.port}
                </div>
                <div class="node-detail-item">
                    <span class="node-detail-label">Protocol:</span> ${node.data.protocol}
                </div>
                <div class="node-detail-item">
                    <span class="node-detail-label">Service:</span> ${node.data.service}
                </div>`;
                
                if (node.data.version) {
                    content += `<div class="node-detail-item">
                        <span class="node-detail-label">Version:</span> ${node.data.version}
                    </div>`;
                }
            }
            break;
            
        case 'vulnerability':
            if (node.data) {
                content += `<div class="node-detail-item">
                    <span class="node-detail-label">Status:</span> 
                    <span class="${node.data.vulnerable ? 'vuln-high' : ''}">${node.data.vulnerable ? 'Vulnerable' : 'Not Vulnerable'}</span>
                </div>`;
                
                if (node.data.description) {
                    content += `<div class="node-detail-item">
                        <span class="node-detail-label">Description:</span> ${node.data.description}
                    </div>`;
                }
            }
            break;
            
        case 'finding':
            if (node.data) {
                if (node.data.vuln_id) {
                    content += `<div class="node-detail-item">
                        <span class="node-detail-label">Vulnerability ID:</span> ${node.data.vuln_id}
                    </div>`;
                }
                
                if (node.data.description) {
                    content += `<div class="node-detail-item">
                        <span class="node-detail-label">Description:</span> ${node.data.description}
                    </div>`;
                }
            }
            break;
            
        case 'certificate':
            if (node.data) {
                if (node.data.subject) {
                    content += `<div class="node-detail-item">
                        <span class="node-detail-label">Subject:</span> ${node.data.subject}
                    </div>`;
                }
                
                if (node.data.issuer) {
                    content += `<div class="node-detail-item">
                        <span class="node-detail-label">Issuer:</span> ${node.data.issuer}
                    </div>`;
                }
                
                if (node.data.signature_algorithm) {
                    content += `<div class="node-detail-item">
                        <span class="node-detail-label">Algorithm:</span> ${node.data.signature_algorithm}
                    </div>`;
                }
            }
            break;
            
        case 'record':
            if (node.data) {
                content += `<div class="node-detail-item">
                    <span class="node-detail-label">Type:</span> ${node.data.type}
                </div>
                <div class="node-detail-item">
                    <span class="node-detail-label">Data:</span> ${node.data.data}
                </div>`;
                
                if (node.data.ttl) {
                    content += `<div class="node-detail-item">
                        <span class="node-detail-label">TTL:</span> ${node.data.ttl}
                    </div>`;
                }
            }
            break;
            
        case 'technology':
            if (node.data) {
                content += `<div class="node-detail-item">
                    <span class="node-detail-label">Name:</span> ${node.data.name}
                </div>`;
                
                if (node.data.details) {
                    content += `<div class="node-detail-item">
                        <span class="node-detail-label">Details:</span> ${node.data.details}
                    </div>`;
                }
            }
            break;
    }
    
    // Set content and show modal
    nodeDetailsContent.innerHTML = content;
    nodeDetailsModal.show();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initNetworkMap);