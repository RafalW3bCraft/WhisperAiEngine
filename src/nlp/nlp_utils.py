"""
Utility functions for G3r4ki's natural language processing.

This module provides helper functions for parsing and analyzing
natural language commands.
"""

import re
import string
import logging
from typing import Dict, Any, List, Tuple, Optional, Set, Union

logger = logging.getLogger(__name__)

# Intent patterns
INTENT_PATTERNS = {
    'scan': [
        r'scan\s+([^\s]+)',
        r'port\s+scan',
        r'check\s+(ports|services)',
        r'nmap',
        r'discover\s+(ports|services)',
        r'find\s+open\s+ports'
    ],
    'recon': [
        r'recon(naissance)?',
        r'gather\s+information',
        r'collect\s+information',
        r'lookup',
        r'whois',
        r'find\s+information',
        r'passive\s+recon'
    ],
    'vuln_scan': [
        r'vuln(erability)?\s+scan',
        r'find\s+vulnerabilities',
        r'check\s+(for\s+)?vulnerabilities',
        r'security\s+scan',
        r'CVE'
    ],
    'llm': [
        r'ask\s+',
        r'question',
        r'query\s+',
        r'what\s+is',
        r'how\s+to',
        r'why\s+',
        r'tell\s+me'
    ],
    'webshell': [
        r'web\s*shell',
        r'generate\s+(a\s+)?(php|jsp|asp|aspx)(\s+shell)?',
        r'create\s+(a\s+)?(php|jsp|asp|aspx)(\s+shell)?',
        r'backdoor'
    ],
    'privesc': [
        r'privil?ege\s+escalation',
        r'privesc',
        r'escalate\s+privileges',
        r'root\s+exploit',
        r'sudo\s+vulnerability',
        r'root\s+check'
    ],
    'tools': [
        r'tools?\s+(list|show|install|update)',
        r'list\s+tools',
        r'available\s+tools',
        r'update\s+tools',
        r'install\s+tools'
    ],
    'help': [
        r'help',
        r'how\s+do\s+I',
        r'how\s+to\s+use',
        r'what\s+is',
        r'show\s+commands',
        r'man',
        r'manual'
    ],
    'exit': [
        r'exit',
        r'quit',
        r'close',
        r'bye',
        r'goodbye'
    ]
}

def parse_command(command: str) -> Dict[str, Any]:
    """
    Parse a natural language command into its components.
    
    Args:
        command: The natural language command
        
    Returns:
        Dictionary with parsed components
    """
    # Basic preprocessing
    command = command.strip()
    
    # Tokenize
    tokens = command.split()
    
    # Extract basic entities
    urls = extract_urls(command)
    ips = extract_ips(command)
    domain_names = extract_domain_names(command)
    ports = extract_ports(command)
    options = extract_options(command)
    key_phrases = extract_key_phrases(command)
    
    # Create parsed result
    parsed = {
        "original": command,
        "tokens": tokens,
        "entities": {
            "urls": urls,
            "ips": ips,
            "domain_names": domain_names,
            "ports": ports,
            "options": options,
            "key_phrases": key_phrases
        }
    }
    
    return parsed

def determine_intent(command: str, parsed: Dict[str, Any]) -> str:
    """
    Determine the intent of a command using pattern matching.
    
    Args:
        command: The natural language command
        parsed: The parsed command information
        
    Returns:
        The intent string
    """
    # Lowercase for matching
    lower_command = command.lower()
    
    # Check each intent pattern
    scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        for pattern in patterns:
            if re.search(pattern, lower_command, re.IGNORECASE):
                score += 1
        
        if score > 0:
            scores[intent] = score
    
    # Return the intent with the highest score, or 'unknown'
    if scores:
        max_intent = max(scores.items(), key=lambda x: x[1])[0]
        return max_intent
    else:
        return 'unknown'

def extract_entities(command: str, intent: str, parsed: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract entities based on the determined intent.
    
    Args:
        command: The natural language command
        intent: The command intent
        parsed: The parsed command information
        
    Returns:
        Dictionary with extracted entities
    """
    entities = {}
    
    if intent == 'scan':
        # Extract target, ports
        targets = parsed["entities"]["ips"] + parsed["entities"]["domain_names"] + parsed["entities"]["urls"]
        if targets:
            entities["target"] = targets[0]
        
        if parsed["entities"]["ports"]:
            entities["ports"] = parsed["entities"]["ports"]
    
    elif intent == 'recon':
        # Extract target
        targets = parsed["entities"]["domain_names"] + parsed["entities"]["urls"] + parsed["entities"]["ips"]
        if targets:
            entities["target"] = targets[0]
    
    elif intent == 'vuln_scan':
        # Extract target
        targets = parsed["entities"]["ips"] + parsed["entities"]["domain_names"] + parsed["entities"]["urls"]
        if targets:
            entities["target"] = targets[0]
    
    elif intent == 'llm':
        # Extract query
        # Remove intent-related prefixes to get the actual query
        query_prefixes = [
            "ask", "question", "query", "what is", "how to", "why", "tell me"
        ]
        query = command
        for prefix in query_prefixes:
            if command.lower().startswith(prefix):
                query = command[len(prefix):].strip()
                break
        
        entities["query"] = query
        
        # Check for specific providers or models
        providers = ["openai", "anthropic", "deepseek", "ollama", "gpt", "claude"]
        for provider in providers:
            if provider in command.lower():
                entities["provider"] = provider
                break
    
    elif intent == 'webshell':
        # Extract shell_type, variant, password
        shell_types = ["php", "jsp", "asp", "aspx", "perl", "python", "ruby", "bash"]
        for shell_type in shell_types:
            if shell_type in command.lower():
                entities["shell_type"] = shell_type
                break
        
        if "shell_type" not in entities:
            entities["shell_type"] = "php"  # Default
        
        variants = ["basic", "mini", "obfuscated", "eval", "uploader"]
        for variant in variants:
            if variant in command.lower():
                entities["variant"] = variant
                break
        
        password_match = re.search(r'password[:\s]+([^\s,]+)', command, re.IGNORECASE)
        if password_match:
            entities["password"] = password_match.group(1)
        
        output_match = re.search(r'(save|output|to)[:\s]+([^\s,]+)', command, re.IGNORECASE)
        if output_match:
            entities["output"] = output_match.group(2)
    
    elif intent == 'privesc':
        # Generally no entities needed for privesc
        pass
    
    elif intent == 'tools':
        # Extract subcommand
        for subcmd in ["list", "install", "update", "show", "info"]:
            if subcmd in command.lower():
                entities["subcommand"] = subcmd
                break
        
        if "subcommand" not in entities:
            entities["subcommand"] = "list"  # Default
        
        # Extract tool name if installing
        if entities["subcommand"] == "install":
            tool_match = re.search(r'install[:\s]+([^\s,]+)', command, re.IGNORECASE)
            if tool_match:
                entities["tool_name"] = tool_match.group(1)
    
    elif intent == 'help':
        # Extract topic
        help_prefixes = ["help", "how do i", "how to use", "what is", "show commands", "man", "manual"]
        topic = command
        for prefix in help_prefixes:
            if command.lower().startswith(prefix):
                topic = command[len(prefix):].strip()
                break
        
        if topic and topic != command:
            entities["topic"] = topic
    
    return entities

def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    return re.findall(url_pattern, text)

def extract_ips(text: str) -> List[str]:
    """Extract IP addresses from text."""
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    candidates = re.findall(ip_pattern, text)
    
    # Validate IPs (simple validation)
    valid_ips = []
    for ip in candidates:
        octets = ip.split('.')
        if all(0 <= int(octet) <= 255 for octet in octets):
            valid_ips.append(ip)
    
    return valid_ips

def extract_domain_names(text: str) -> List[str]:
    """Extract domain names from text."""
    # This is a simplified pattern, not covering all TLDs
    domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
    domains = re.findall(domain_pattern, text)
    
    # Filter out some common words that might match but aren't domains
    common_words = ["e.g", "i.e", "etc.", "vs.", "ex.", "fig."]
    return [d for d in domains if d not in common_words]

def extract_ports(text: str) -> List[int]:
    """Extract port numbers from text."""
    # Look for explicit port references
    port_patterns = [
        r'port\s+(\d+)',
        r'ports?\s+(\d+(?:[-,]\d+)*)',
        r':(\d+)'  # For URL-style port specifications
    ]
    
    ports = []
    for pattern in port_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Handle port ranges and lists
            if '-' in match:
                start, end = map(int, match.split('-'))
                ports.extend(range(start, end + 1))
            elif ',' in match:
                ports.extend(map(int, match.split(',')))
            else:
                try:
                    ports.append(int(match))
                except ValueError:
                    pass
    
    # Filter to valid port range and remove duplicates
    return sorted(list(set(p for p in ports if 1 <= p <= 65535)))

def extract_options(text: str) -> Dict[str, str]:
    """Extract command-line style options from text."""
    # Look for --option or -o style options
    option_pattern = r'-{1,2}([a-zA-Z][a-zA-Z0-9_-]*)(?:[=\s]+([^\s,]+))?'
    matches = re.findall(option_pattern, text)
    
    options = {}
    for option, value in matches:
        options[option] = value if value else True
    
    return options

def extract_key_phrases(text: str) -> List[str]:
    """Extract key phrases that might indicate specific operations."""
    phrases = [
        "port scan", "vulnerability scan", "reconnaissance", "privilege escalation",
        "reverse shell", "bind shell", "web shell", "penetration test",
        "password cracking", "dictionary attack", "brute force", "fuzzing",
        "information gathering", "exploit", "payload", "metasploit"
    ]
    
    found_phrases = []
    for phrase in phrases:
        if phrase in text.lower():
            found_phrases.append(phrase)
    
    return found_phrases