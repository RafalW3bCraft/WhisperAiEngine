/**
 * G3r4ki Web Interface JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize socket.io
    const socket = io();
    
    // Navigation tabs
    initializeTabs();
    
    // AI Assistant functionality
    initializeAiAssistant();
    
    // Reverse Shell Generator
    initializeShellGenerator();
    
    // Pentest tabs
    initializePentestTabs();
    
    // Agent system
    initializeAgentSystem();
    
    // Tool management
    initializeToolSystem();
    
    // Terminal functionality
    initializeTerminal(socket);
    
    // Settings functionality
    initializeSettings();
    
    // Load dashboard data
    loadDashboardData();
});

/**
 * Initialize tab navigation
 */
function initializeTabs() {
    const navLinks = document.querySelectorAll('nav a');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links and content sections
            navLinks.forEach(l => l.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(section => {
                section.classList.remove('active');
            });
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Show corresponding content section
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
}

/**
 * Initialize AI Assistant functionality
 */
function initializeAiAssistant() {
    const chatMessages = document.getElementById('chat-messages');
    const userPromptInput = document.getElementById('user-prompt');
    const sendPromptBtn = document.getElementById('send-prompt');
    
    // Send button click handler
    sendPromptBtn.addEventListener('click', function() {
        sendUserPrompt();
    });
    
    // Enter key handler
    userPromptInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendUserPrompt();
        }
    });
    
    // Function to send user prompt to AI
    function sendUserPrompt() {
        const prompt = userPromptInput.value.trim();
        if (!prompt) return;
        
        // Get selected AI provider
        const providerRadios = document.querySelectorAll('input[name="ai-provider"]');
        let selectedProvider = 'openai'; // Default
        
        providerRadios.forEach(radio => {
            if (radio.checked) {
                selectedProvider = radio.value;
            }
        });
        
        // Get system prompt
        const systemPrompt = document.getElementById('system-prompt').value.trim();
        
        // Add user message to chat
        addMessage('user', prompt);
        
        // Clear input
        userPromptInput.value = '';
        
        // Show loading indicator
        const loadingId = addLoadingMessage();
        
        // Send request to API
        fetch('/api/ai/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: prompt,
                provider: selectedProvider,
                system_prompt: systemPrompt
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading message
            removeMessage(loadingId);
            
            if (data.error) {
                addErrorMessage(data.error);
                return;
            }
            
            if (data.response) {
                // Single provider response
                addMessage('ai', data.response, data.provider);
            } else if (data.responses) {
                // Multiple provider responses
                Object.entries(data.responses).forEach(([provider, response]) => {
                    addMessage('ai', response, provider);
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            removeMessage(loadingId);
            addErrorMessage('Failed to get AI response. Check the console for details.');
        });
    }
    
    // Function to add message to chat
    function addMessage(type, content, provider = null) {
        const messageId = 'msg-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.id = messageId;
        messageDiv.className = `message ${type}-message fade-in`;
        
        let messageContent = '';
        
        if (type === 'ai' && provider) {
            messageContent += `<div class="message-provider">${provider}</div>`;
        }
        
        messageContent += `<div class="message-content">${formatMessage(content)}</div>`;
        messageDiv.innerHTML = messageContent;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageId;
    }
    
    // Function to add loading message
    function addLoadingMessage() {
        const messageId = 'loading-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.id = messageId;
        messageDiv.className = 'message ai-message loading-message fade-in';
        messageDiv.innerHTML = '<div class="loading">Thinking</div>';
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageId;
    }
    
    // Function to add error message
    function addErrorMessage(errorText) {
        const messageId = 'error-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.id = messageId;
        messageDiv.className = 'message error-message fade-in';
        messageDiv.innerHTML = `<div class="message-content">Error: ${errorText}</div>`;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageId;
    }
    
    // Function to remove a message
    function removeMessage(messageId) {
        const message = document.getElementById(messageId);
        if (message) {
            message.remove();
        }
    }
    
    // Function to format message content (convert newlines to <br>)
    function formatMessage(content) {
        return content.replace(/\n/g, '<br>');
    }
}

/**
 * Initialize Reverse Shell Generator
 */
function initializeShellGenerator() {
    const shellTypeSelect = document.getElementById('shell-type');
    const shellVariantSelect = document.getElementById('shell-variant');
    const shellIpInput = document.getElementById('shell-ip');
    const shellPortInput = document.getElementById('shell-port');
    const generateShellBtn = document.getElementById('generate-shell-btn');
    const shellOutput = document.getElementById('shell-output');
    const copyShellBtn = document.getElementById('copy-shell-btn');
    const saveShellBtn = document.getElementById('save-shell-btn');
    
    // Load shell types
    fetch('/api/pentest/shells')
        .then(response => response.json())
        .then(data => {
            shellTypeSelect.innerHTML = '<option value="" disabled selected>Select Shell Type</option>';
            
            data.shell_types.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type;
                shellTypeSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading shell types:', error);
            shellOutput.textContent = 'Failed to load shell types. Check console for details.';
        });
    
    // Shell type change handler
    shellTypeSelect.addEventListener('change', function() {
        const selectedType = this.value;
        if (!selectedType) return;
        
        // Reset variant select
        shellVariantSelect.innerHTML = '<option value="" disabled selected>Loading variants...</option>';
        shellVariantSelect.disabled = true;
        
        // Fetch variants for selected shell type
        fetch(`/api/pentest/shells/${selectedType}`)
            .then(response => response.json())
            .then(data => {
                shellVariantSelect.innerHTML = '<option value="" disabled selected>Select Variant</option>';
                
                data.variants.forEach(variant => {
                    const option = document.createElement('option');
                    option.value = variant;
                    option.textContent = variant;
                    shellVariantSelect.appendChild(option);
                });
                
                shellVariantSelect.disabled = false;
            })
            .catch(error => {
                console.error('Error loading shell variants:', error);
                shellVariantSelect.innerHTML = '<option value="" disabled selected>Failed to load variants</option>';
            });
    });
    
    // Generate shell button handler
    generateShellBtn.addEventListener('click', function() {
        const shellType = shellTypeSelect.value;
        const variant = shellVariantSelect.value;
        const ip = shellIpInput.value.trim();
        const port = shellPortInput.value;
        
        if (!shellType) {
            alert('Please select a shell type');
            return;
        }
        
        if (!variant) {
            alert('Please select a variant');
            return;
        }
        
        shellOutput.innerHTML = '<code>Generating shell...</code>';
        
        // Request shell generation
        fetch('/api/pentest/shells/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                shell_type: shellType,
                variant: variant,
                ip: ip,
                port: port
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                shellOutput.innerHTML = `<code>Error: ${data.error}</code>`;
                return;
            }
            
            shellOutput.innerHTML = `<code>${escapeHtml(data.shell)}</code>`;
            copyShellBtn.disabled = false;
            saveShellBtn.disabled = false;
        })
        .catch(error => {
            console.error('Error generating shell:', error);
            shellOutput.innerHTML = '<code>Failed to generate shell. Check console for details.</code>';
        });
    });
    
    // Copy to clipboard button handler
    copyShellBtn.addEventListener('click', function() {
        const shellText = shellOutput.textContent.trim();
        navigator.clipboard.writeText(shellText)
            .then(() => {
                const originalText = this.textContent;
                this.textContent = 'Copied!';
                setTimeout(() => {
                    this.textContent = originalText;
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy:', err);
                alert('Failed to copy to clipboard');
            });
    });
    
    // Save to file button handler
    saveShellBtn.addEventListener('click', function() {
        const shellText = shellOutput.textContent.trim();
        const shellType = shellTypeSelect.value;
        const variant = shellVariantSelect.value;
        
        const blob = new Blob([shellText], { type: 'text/plain' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `${shellType}_${variant}_shell.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });
    
    // Utility function to escape HTML
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

/**
 * Initialize Pentest Tabs
 */
function initializePentestTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn[data-pentest-tab]');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-pentest-tab');
            
            // Hide all tabs
            document.querySelectorAll('.pentest-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Remove active class from all buttons
            tabButtons.forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabId).classList.add('active');
            
            // Add active class to clicked button
            this.classList.add('active');
        });
    });
}

/**
 * Initialize Agent System
 */
function initializeAgentSystem() {
    const agentList = document.getElementById('agent-list');
    const refreshAgentsBtn = document.getElementById('refresh-agents-btn');
    const agentTypeSelect = document.getElementById('agent-type');
    const agentNameInput = document.getElementById('agent-name');
    const agentDescriptionInput = document.getElementById('agent-description');
    const agentTargetInput = document.getElementById('agent-target');
    const createAgentBtn = document.getElementById('create-agent-btn');
    
    // Load agent types
    fetch('/api/agents/types')
        .then(response => response.json())
        .then(data => {
            agentTypeSelect.innerHTML = '<option value="" disabled selected>Select Agent Type</option>';
            
            data.agent_types.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type;
                agentTypeSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading agent types:', error);
            agentTypeSelect.innerHTML = '<option value="" disabled selected>Failed to load agent types</option>';
        });
    
    // Load agents
    function loadAgents() {
        agentList.innerHTML = '<div class="loading">Loading agents</div>';
        
        fetch('/api/agents')
            .then(response => response.json())
            .then(data => {
                if (!data.agents || data.agents.length === 0) {
                    agentList.innerHTML = '<div class="no-agents">No agents available</div>';
                    return;
                }
                
                agentList.innerHTML = '';
                
                data.agents.forEach(agent => {
                    const agentCard = document.createElement('div');
                    agentCard.className = 'agent-card';
                    
                    let statusClass = '';
                    switch (agent.status) {
                        case 'RUNNING':
                            statusClass = 'status-running';
                            break;
                        case 'IDLE':
                            statusClass = 'status-idle';
                            break;
                        case 'ERROR':
                            statusClass = 'status-error';
                            break;
                        default:
                            statusClass = 'status-unknown';
                    }
                    
                    agentCard.innerHTML = `
                        <div class="agent-header">
                            <h4>${agent.name}</h4>
                            <span class="agent-type">${agent.type}</span>
                        </div>
                        <div class="agent-status ${statusClass}">${agent.status}</div>
                        <p class="agent-description">${agent.description || 'No description'}</p>
                        <div class="agent-actions">
                            <button class="secondary-btn" data-agent-id="${agent.agent_id}" data-action="run">Run</button>
                            <button class="secondary-btn" data-agent-id="${agent.agent_id}" data-action="stop">Stop</button>
                            <button class="secondary-btn" data-agent-id="${agent.agent_id}" data-action="report">Report</button>
                        </div>
                    `;
                    
                    agentList.appendChild(agentCard);
                });
                
                // Update agent count on dashboard
                document.getElementById('agent-count').textContent = `${data.agents.length} active agent(s)`;
                
                // Add event listeners to agent action buttons
                document.querySelectorAll('.agent-actions button').forEach(button => {
                    button.addEventListener('click', handleAgentAction);
                });
            })
            .catch(error => {
                console.error('Error loading agents:', error);
                agentList.innerHTML = '<div class="error">Failed to load agents. Check console for details.</div>';
            });
    }
    
    // Handle agent action button clicks
    function handleAgentAction(e) {
        const agentId = this.getAttribute('data-agent-id');
        const action = this.getAttribute('data-action');
        
        console.log(`Agent action: ${action} for agent ID: ${agentId}`);
        
        // TODO: Implement agent actions (run, stop, report)
        // For now, just show an alert
        alert(`Action "${action}" for agent ID "${agentId}" is not implemented yet.`);
    }
    
    // Create agent button handler
    createAgentBtn.addEventListener('click', function() {
        const agentType = agentTypeSelect.value;
        const name = agentNameInput.value.trim();
        const description = agentDescriptionInput.value.trim();
        const target = agentTargetInput.value.trim();
        
        if (!agentType) {
            alert('Please select an agent type');
            return;
        }
        
        if (!name) {
            alert('Please enter an agent name');
            return;
        }
        
        // Disable button during creation
        createAgentBtn.disabled = true;
        createAgentBtn.textContent = 'Creating...';
        
        // Create agent request
        fetch('/api/agents/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                agent_type: agentType,
                name: name,
                description: description,
                target: target || undefined
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(`Error creating agent: ${data.error}`);
                return;
            }
            
            // Clear form
            agentTypeSelect.value = '';
            agentNameInput.value = '';
            agentDescriptionInput.value = '';
            agentTargetInput.value = '';
            
            // Reload agent list
            loadAgents();
            
            // Show success message
            alert(`Agent "${name}" created successfully!`);
        })
        .catch(error => {
            console.error('Error creating agent:', error);
            alert('Failed to create agent. Check console for details.');
        })
        .finally(() => {
            // Re-enable button
            createAgentBtn.disabled = false;
            createAgentBtn.textContent = 'Create Agent';
        });
    });
    
    // Refresh agents button handler
    refreshAgentsBtn.addEventListener('click', loadAgents);
    
    // Load agents on initialization
    loadAgents();
    
    // Set up quick action button on dashboard
    document.querySelector('button[data-action="create-agent"]').addEventListener('click', function() {
        // Navigate to Agents tab
        document.querySelector('nav a[data-tab="agents"]').click();
    });
}

/**
 * Initialize Tool System
 */
function initializeToolSystem() {
    const toolList = document.getElementById('tool-list');
    const toolCategories = document.querySelectorAll('.tool-categories li');
    const scanToolsBtn = document.getElementById('scan-tools-btn');
    
    // Tool category click handler
    toolCategories.forEach(category => {
        category.addEventListener('click', function() {
            const categoryName = this.getAttribute('data-category');
            
            // Remove active class from all categories
            toolCategories.forEach(cat => {
                cat.classList.remove('active');
            });
            
            // Add active class to clicked category
            this.classList.add('active');
            
            // Display tools for selected category
            displayToolsForCategory(categoryName);
        });
    });
    
    // Function to display tools for a category
    function displayToolsForCategory(category) {
        toolList.innerHTML = '<div class="loading">Loading tools</div>';
        
        // TODO: Implement actual tool list API
        // For now, just show a placeholder message
        setTimeout(() => {
            toolList.innerHTML = `<div class="under-construction">Tool list for category "${category}" is under development.</div>`;
        }, 1000);
    }
    
    // Scan tools button handler
    scanToolsBtn.addEventListener('click', function() {
        toolList.innerHTML = '<div class="loading">Scanning for installed tools</div>';
        
        // TODO: Implement actual tool scanning API
        // For now, just show a placeholder message
        setTimeout(() => {
            toolList.innerHTML = '<div class="under-construction">Tool scanning feature is under development.</div>';
        }, 2000);
    });
    
    // Display tools for initially selected category
    const initialCategory = document.querySelector('.tool-categories li.active').getAttribute('data-category');
    displayToolsForCategory(initialCategory);
}

/**
 * Initialize Terminal with Socket.IO
 */
function initializeTerminal(socket) {
    const terminal = document.getElementById('terminal');
    const commandInput = document.getElementById('command-input');
    const runCommandBtn = document.getElementById('run-command-btn');
    
    // Run command button handler
    runCommandBtn.addEventListener('click', function() {
        executeCommand();
    });
    
    // Enter key handler
    commandInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            executeCommand();
        }
    });
    
    // Execute command function
    function executeCommand() {
        const command = commandInput.value.trim();
        if (!command) return;
        
        // Clear input
        commandInput.value = '';
        
        // Add command to terminal
        appendToTerminal(`> ${command}`, 'command');
        
        // Send command to server via Socket.IO
        socket.emit('execute_command', { command: command });
    }
    
    // Socket.IO event handlers
    socket.on('command_output', function(data) {
        if (data.error) {
            appendToTerminal(`Error: ${data.error}`, 'error');
        } else if (data.line) {
            appendToTerminal(data.line);
        } else if (data.completed) {
            appendToTerminal(`Command completed with exit code: ${data.exit_code}`, 'info');
        }
    });
    
    // Function to append text to terminal
    function appendToTerminal(text, className = '') {
        const line = document.createElement('div');
        line.className = `terminal-line ${className}`;
        line.textContent = text;
        
        terminal.appendChild(line);
        terminal.scrollTop = terminal.scrollHeight;
    }
}

/**
 * Initialize Settings
 */
function initializeSettings() {
    const themeSelect = document.getElementById('theme-select');
    const enableAnimations = document.getElementById('enable-animations');
    const toggleVisibilityBtns = document.querySelectorAll('.toggle-visibility-btn');
    
    // Theme selection handler
    themeSelect.addEventListener('change', function() {
        const theme = this.value;
        
        // Apply selected theme
        document.body.className = `theme-${theme}`;
        
        // Save preference to localStorage
        localStorage.setItem('g3r4ki-theme', theme);
    });
    
    // Load saved theme preference
    const savedTheme = localStorage.getItem('g3r4ki-theme');
    if (savedTheme) {
        themeSelect.value = savedTheme;
        document.body.className = `theme-${savedTheme}`;
    }
    
    // Animations toggle handler
    enableAnimations.addEventListener('change', function() {
        const enabled = this.checked;
        
        // Apply animations setting
        document.body.classList.toggle('no-animations', !enabled);
        
        // Save preference to localStorage
        localStorage.setItem('g3r4ki-animations', enabled ? 'enabled' : 'disabled');
    });
    
    // Load saved animations preference
    const savedAnimations = localStorage.getItem('g3r4ki-animations');
    if (savedAnimations === 'disabled') {
        enableAnimations.checked = false;
        document.body.classList.add('no-animations');
    }
    
    // Password visibility toggle
    toggleVisibilityBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.previousElementSibling;
            
            if (input.type === 'password') {
                input.type = 'text';
                this.textContent = 'Hide';
            } else {
                input.type = 'password';
                this.textContent = 'Show';
            }
        });
    });
}

/**
 * Load Dashboard Data
 */
function loadDashboardData() {
    // This function would load various data for the dashboard
    // For now, we'll just update the agent count
    fetch('/api/agents')
        .then(response => response.json())
        .then(data => {
            const count = data.agents ? data.agents.length : 0;
            document.getElementById('agent-count').textContent = `${count} active agent(s)`;
        })
        .catch(error => {
            console.error('Error loading agents for dashboard:', error);
            document.getElementById('agent-count').textContent = 'Error loading agent count';
        });
}

/**
 * Set up quick action buttons on dashboard
 */
document.addEventListener('DOMContentLoaded', function() {
    // Generate Shell button
    document.querySelector('button[data-action="generate-shell"]').addEventListener('click', function() {
        // Navigate to Pentest tab
        document.querySelector('nav a[data-tab="pentest"]').click();
    });
    
    // Run Scan button
    document.querySelector('button[data-action="run-scan"]').addEventListener('click', function() {
        // Navigate to Pentest tab, then to Scan sub-tab
        document.querySelector('nav a[data-tab="pentest"]').click();
        document.querySelector('button[data-pentest-tab="scan"]').click();
    });
});