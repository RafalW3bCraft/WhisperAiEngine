// G3r4ki Dashboard JavaScript

// Initialize Socket.IO connection
const socket = io();

// Store results data
let scanResults = {};
let reconResults = {};
let vulnResults = {};

// DOM Elements
const scanResultsSummary = document.getElementById('scanResultsSummary');
const scanResultsList = document.getElementById('scanResultsList');
const reconResultsSummary = document.getElementById('reconResultsSummary');
const reconResultsList = document.getElementById('reconResultsList');
const vulnResultsSummary = document.getElementById('vulnResultsSummary');
const vulnResultsList = document.getElementById('vulnResultsList');
const networkOverview = document.getElementById('networkOverview');

// Action buttons
const scanAction = document.getElementById('scanAction');
const reconAction = document.getElementById('reconAction');
const vulnAction = document.getElementById('vulnAction');
const submitTarget = document.getElementById('submitTarget');
const targetInput = document.getElementById('targetInput');

// Modal
const targetModal = new bootstrap.Modal(document.getElementById('targetModal'));

// Current action type
let currentAction = null;

// Initialize network overview visualization
let networkSimulation = null;
let networkSvg = null;

// Initialize dashboard
function initDashboard() {
    // Setup event listeners
    setupEventListeners();
    
    // Initialize network overview
    initNetworkOverview();
    
    // Load initial data
    loadInitialData();
}

// Set up UI event listeners
function setupEventListeners() {
    // Action button click handlers
    scanAction.addEventListener('click', () => {
        currentAction = 'scan';
        document.getElementById('targetModalLabel').textContent = 'Enter Target for Network Scan';
        targetModal.show();
    });
    
    reconAction.addEventListener('click', () => {
        currentAction = 'recon';
        document.getElementById('targetModalLabel').textContent = 'Enter Target for Reconnaissance';
        targetModal.show();
    });
    
    vulnAction.addEventListener('click', () => {
        currentAction = 'vuln';
        document.getElementById('targetModalLabel').textContent = 'Enter Target for Vulnerability Scan';
        targetModal.show();
    });
    
    // Submit target
    submitTarget.addEventListener('click', () => {
        const target = targetInput.value.trim();
        if (target) {
            submitScanRequest(currentAction, target);
            targetModal.hide();
            targetInput.value = '';
        }
    });
    
    // Socket.IO event listeners
    socket.on('connect', () => {
        console.log('Connected to server');
    });
    
    socket.on('scan_update', (data) => {
        console.log('Scan update received:', data);
        loadScanResults();
    });
    
    socket.on('recon_update', (data) => {
        console.log('Recon update received:', data);
        loadReconResults();
    });
    
    socket.on('vuln_update', (data) => {
        console.log('Vulnerability scan update received:', data);
        loadVulnResults();
    });
}

// Initialize network overview visualization
function initNetworkOverview() {
    // Create SVG element
    networkSvg = d3.select('#networkOverview')
        .append('svg')
        .attr('width', '100%')
        .attr('height', '100%');
    
    // Create force simulation
    networkSimulation = d3.forceSimulation()
        .force('link', d3.forceLink().id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(
            networkOverview.clientWidth / 2, 
            networkOverview.clientHeight / 2
        ));
}

// Load initial data from server
function loadInitialData() {
    loadScanResults();
    loadReconResults();
    loadVulnResults();
}

// Load scan results
function loadScanResults() {
    fetch('/api/scans')
        .then(response => response.json())
        .then(data => {
            scanResults = data;
            updateScanResultsUI();
        })
        .catch(error => {
            console.error('Error loading scan results:', error);
        });
}

// Load reconnaissance results
function loadReconResults() {
    fetch('/api/recon')
        .then(response => response.json())
        .then(data => {
            reconResults = data;
            updateReconResultsUI();
        })
        .catch(error => {
            console.error('Error loading recon results:', error);
        });
}

// Load vulnerability scan results
function loadVulnResults() {
    fetch('/api/vuln')
        .then(response => response.json())
        .then(data => {
            vulnResults = data;
            updateVulnResultsUI();
        })
        .catch(error => {
            console.error('Error loading vulnerability scan results:', error);
        });
}

// Update scan results UI
function updateScanResultsUI() {
    const targets = Object.keys(scanResults);
    
    if (targets.length === 0) {
        scanResultsSummary.textContent = 'No scan results available';
        scanResultsList.innerHTML = '';
        return;
    }
    
    // Update summary
    scanResultsSummary.textContent = `${targets.length} scan results available`;
    
    // Update list
    scanResultsList.innerHTML = '';
    targets.forEach(target => {
        const result = scanResults[target];
        const timestamp = new Date(result.timestamp * 1000).toLocaleString();
        
        // Count hosts and open ports
        const hostCount = result.data && result.data.hosts ? result.data.hosts.length : 0;
        let openPortCount = 0;
        
        if (result.data && result.data.hosts) {
            result.data.hosts.forEach(host => {
                host.ports.forEach(port => {
                    if (port.state === 'open') {
                        openPortCount++;
                    }
                });
            });
        }
        
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        listItem.innerHTML = `
            <div><strong>${target}</strong></div>
            <div class="small">Scanned: ${timestamp}</div>
            <div>${hostCount} hosts, ${openPortCount} open ports</div>
            <button class="btn btn-sm btn-outline-primary mt-2 view-scan-btn" data-target="${target}">
                View Details
            </button>
        `;
        
        // Add click event for the button
        listItem.querySelector('.view-scan-btn').addEventListener('click', () => {
            window.location.href = `/network-map?type=scan&target=${encodeURIComponent(target)}`;
        });
        
        scanResultsList.appendChild(listItem);
    });
    
    // Update network overview
    updateNetworkOverview();
}

// Update reconnaissance results UI
function updateReconResultsUI() {
    const targets = Object.keys(reconResults);
    
    if (targets.length === 0) {
        reconResultsSummary.textContent = 'No reconnaissance results available';
        reconResultsList.innerHTML = '';
        return;
    }
    
    // Update summary
    reconResultsSummary.textContent = `${targets.length} recon results available`;
    
    // Update list
    reconResultsList.innerHTML = '';
    targets.forEach(target => {
        const result = reconResults[target];
        const timestamp = new Date(result.timestamp * 1000).toLocaleString();
        
        // Count relevant information
        let domainInfo = '';
        let recordCount = 0;
        let techCount = 0;
        
        if (result.data) {
            if (result.data.domain) {
                domainInfo = `Domain: ${result.data.domain}`;
            }
            
            if (result.data.records) {
                recordCount = result.data.records.length;
            }
            
            if (result.data.targets) {
                techCount = result.data.targets.reduce((count, target) => {
                    return count + (target.technologies ? target.technologies.length : 0);
                }, 0);
            }
        }
        
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        listItem.innerHTML = `
            <div><strong>${target}</strong></div>
            <div class="small">Scanned: ${timestamp}</div>
            <div>${domainInfo}</div>
            <div>${recordCount} DNS records, ${techCount} technologies</div>
            <button class="btn btn-sm btn-outline-primary mt-2 view-recon-btn" data-target="${target}">
                View Details
            </button>
        `;
        
        // Add click event for the button
        listItem.querySelector('.view-recon-btn').addEventListener('click', () => {
            window.location.href = `/network-map?type=recon&target=${encodeURIComponent(target)}`;
        });
        
        reconResultsList.appendChild(listItem);
    });
}

// Update vulnerability scan results UI
function updateVulnResultsUI() {
    const targets = Object.keys(vulnResults);
    
    if (targets.length === 0) {
        vulnResultsSummary.textContent = 'No vulnerability scan results available';
        vulnResultsList.innerHTML = '';
        return;
    }
    
    // Update summary
    vulnResultsSummary.textContent = `${targets.length} vulnerability scan results available`;
    
    // Update list
    vulnResultsList.innerHTML = '';
    targets.forEach(target => {
        const result = vulnResults[target];
        const timestamp = new Date(result.timestamp * 1000).toLocaleString();
        
        // Count vulnerabilities
        let findingsCount = 0;
        let vulnCount = 0;
        
        if (result.data) {
            if (result.data.findings) {
                findingsCount = result.data.findings.length;
            }
            
            if (result.data.vulnerabilities) {
                vulnCount = result.data.vulnerabilities.filter(v => v.vulnerable).length;
            }
        }
        
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        listItem.innerHTML = `
            <div><strong>${target}</strong></div>
            <div class="small">Scanned: ${timestamp}</div>
            <div>${findingsCount} findings, ${vulnCount} vulnerabilities</div>
            <button class="btn btn-sm btn-outline-primary mt-2 view-vuln-btn" data-target="${target}">
                View Details
            </button>
        `;
        
        // Add click event for the button
        listItem.querySelector('.view-vuln-btn').addEventListener('click', () => {
            window.location.href = `/network-map?type=vuln&target=${encodeURIComponent(target)}`;
        });
        
        vulnResultsList.appendChild(listItem);
    });
}

// Update network overview visualization
function updateNetworkOverview() {
    // Get the latest scan result (if any)
    const targets = Object.keys(scanResults);
    if (targets.length === 0) {
        return;
    }
    
    // Find the most recent scan
    let latestTarget = targets[0];
    let latestTimestamp = scanResults[latestTarget].timestamp;
    
    targets.forEach(target => {
        if (scanResults[target].timestamp > latestTimestamp) {
            latestTarget = target;
            latestTimestamp = scanResults[target].timestamp;
        }
    });
    
    const scanData = scanResults[latestTarget].data;
    if (!scanData || !scanData.hosts || scanData.hosts.length === 0) {
        return;
    }
    
    // Prepare data for visualization
    const nodes = [];
    const links = [];
    
    // Add central node for the network
    nodes.push({
        id: 'network',
        label: latestTarget,
        type: 'network'
    });
    
    // Add host nodes and links
    scanData.hosts.forEach((host, index) => {
        const hostId = host.ip || host.hostname || `host_${index}`;
        nodes.push({
            id: hostId,
            label: host.hostname || host.ip || `Host ${index}`,
            type: 'host',
            status: host.status
        });
        
        // Link to network
        links.push({
            source: 'network',
            target: hostId
        });
        
        // Add service nodes for open ports
        host.ports.forEach(port => {
            if (port.state === 'open') {
                const serviceId = `${hostId}_${port.port}_${port.protocol}`;
                nodes.push({
                    id: serviceId,
                    label: `${port.service} (${port.port})`,
                    type: 'service',
                    port: port.port,
                    protocol: port.protocol,
                    version: port.version
                });
                
                // Link to host
                links.push({
                    source: hostId,
                    target: serviceId
                });
            }
        });
    });
    
    // Update visualization
    networkSvg.selectAll('*').remove();
    
    // Create links
    const link = networkSvg.append('g')
        .selectAll('line')
        .data(links)
        .enter().append('line')
        .attr('class', 'link');
    
    // Create nodes
    const node = networkSvg.append('g')
        .selectAll('circle')
        .data(nodes)
        .enter().append('circle')
        .attr('class', 'node')
        .attr('r', d => getNodeRadius(d))
        .attr('fill', d => getNodeColor(d))
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    // Add labels
    const label = networkSvg.append('g')
        .selectAll('text')
        .data(nodes)
        .enter().append('text')
        .text(d => d.label)
        .attr('dx', 12)
        .attr('dy', '.35em');
    
    // Update simulation
    networkSimulation
        .nodes(nodes)
        .on('tick', ticked);
    
    networkSimulation.force('link')
        .links(links);
    
    // Restart simulation
    networkSimulation.alpha(1).restart();
    
    // Tick function for updating positions
    function ticked() {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    }
    
    // Drag functions
    function dragstarted(event, d) {
        if (!event.active) networkSimulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    function dragended(event, d) {
        if (!event.active) networkSimulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

// Get node radius based on type
function getNodeRadius(node) {
    switch (node.type) {
        case 'network':
            return 20;
        case 'host':
            return 15;
        case 'service':
            return 10;
        default:
            return 8;
    }
}

// Get node color based on type
function getNodeColor(node) {
    switch (node.type) {
        case 'network':
            return '#4e79a7';
        case 'host':
            return '#f28e2c';
        case 'service':
            return '#59a14f';
        case 'vulnerability':
            return '#e15759';
        default:
            return '#76b7b2';
    }
}

// Submit scan request
function submitScanRequest(action, target) {
    // In a real implementation, this would send an API request to start a scan
    alert(`${action.toUpperCase()} scan requested for ${target}. This would start a scan in a real implementation.`);
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', initDashboard);