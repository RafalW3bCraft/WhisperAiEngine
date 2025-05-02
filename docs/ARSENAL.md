# G3r4ki Cyber Arsenal

This document outlines the complete toolkit available in the G3r4ki Cyber LLM War Machine. Each category serves a specific purpose in cybersecurity operations, reconnaissance, and analysis.

## 🧠 Inference Core (Offline AI)
| Tools | Purpose |
|-------|---------|
| llama.cpp | Efficient C++ implementation for running LLM models with low resources |
| vLLM | High-throughput and memory-efficient inference engine |
| GPT4All | Local running chatbot and assistant with no internet required |

**Purpose**: Run powerful AI models locally for recon automation, scripting, vulnerability triage, and other analysis tasks without cloud dependencies.

## 🎙️ Voice Command Center
| Tools | Purpose |
|-------|---------|
| Whisper.cpp | Offline speech recognition |
| Piper TTS | Offline text-to-speech synthesis |

**Purpose**: Enable voice input and output for hands-free control of the Cyber LLM via natural language commands.

## 🕵️ Recon/Enumeration
| Tools | Purpose |
|-------|---------|
| nmap | Network discovery and security auditing |
| amass | In-depth attack surface mapping and asset discovery |
| subfinder | Subdomain discovery tool |
| whatweb | Next generation web scanner |
| ffuf | Fast web fuzzer |
| masscan | Mass IP port scanner |
| dnsrecon | DNS enumeration script |
| aquatone | Visual inspection of websites across large amounts of hosts |

**Purpose**: Comprehensive reconnaissance, network scanning, domain discovery, web fuzzing, and live asset detection.

## 🔗 Remote Access / Exploitation
| Tools | Purpose |
|-------|---------|
| Paramiko | Python SSH implementation |
| OpenSSH | Secure remote login and file transfer |

**Purpose**: Secure control over remote targets/servers for attack or infrastructure management.

## 📊 Interface (Single Control Panel)
| Tools | Purpose |
|-------|---------|
| Flask | Lightweight web server framework |
| D3.js | JavaScript library for data visualization |
| Socket.io | Real-time bidirectional event-based communication |

**Purpose**: Web interface for real-time visualization and interactive control panel.

## 🛡️ Defense Modules
| Tools | Purpose |
|-------|---------|
| UFW | Uncomplicated Firewall for network protection |
| Suricata | Network threat detection engine |
| Fail2Ban | Intrusion prevention software |
| Incident Response Simulator | Comprehensive training for security incidents |

**Purpose**: Local firewall protection, intrusion detection, automatic IP banning, and incident response training.

### Incident Response Simulator
| Component | Capabilities |
|-----------|--------------|
| Scenario Generator | AI-powered creation of realistic incident scenarios |
| Security Persona Generator | Creation of personalized security personas with varying skill levels |
| Simulation Engine | Step-by-step incident response process with real-time evaluation |
| Report Generator | Comprehensive incident response report generation |

## 🏗️ Automation / Scripting Core
| Tools | Purpose |
|-------|---------|
| Makefile | Build automation tool |
| CMake | Cross-platform build system |
| Ansible | IT automation platform |

**Purpose**: Automate builds, deployments, and mass exploitation setups.

## 💣 Offensive Framework
| Tools | Purpose |
|-------|---------|
| Metasploit | Penetration testing framework |
| Sliver | Adversary emulation framework |
| G3r4ki Pentest Modules | Integrated penetration testing capabilities |

**Purpose**: Post-exploitation, RAT deployment, and Red Team operations.

### G3r4ki Pentest Modules
| Module | Capabilities |
|--------|--------------|
| Shells Library | Extensive collection of reverse shells for different languages |
| Enumeration | Automated system enumeration and vulnerability detection |
| Privilege Escalation | Comprehensive collection of privilege escalation techniques |

## 📈 Data Handling & Analysis
| Tools | Purpose |
|-------|---------|
| Pandas | Data analysis and manipulation library |
| Polars | Fast DataFrame library |

**Purpose**: Process scan outputs, handle large reconnaissance datasets, and automate target sorting.

## 🛠️ Linux Admin & Scheduling
| Tools | Purpose |
|-------|---------|
| systemd timers | System and service manager for Linux |
| cron | Time-based job scheduler |

**Purpose**: Task automation, scheduled attacks, and recurring jobs.

## 🌐 Threat Intel
| Tools | Purpose |
|-------|---------|
| MISP | Open source threat intelligence platform |
| ThreatFox | Platform for sharing IOCs |

**Purpose**: Pull fresh IOCs, CVEs, and vulnerabilities for automated scanning and targeting.

## 🏰 Advanced Red Team Modules
| Tools | Purpose |
|-------|---------|
| impacket | Collection of Python classes for network protocols |
| bloodhound-python | Python based ingestor for BloodHound |
| kerbrute | Tool to perform Kerberos pre-auth bruteforcing |

**Purpose**: Active Directory exploitation, credential gathering, and privilege escalation.

---

## Integration Status

| Category | Integration Status | Notes |
|----------|-------------------|-------|
| Inference Core | ✅ | Integrated with llama.cpp, vLLM, and GPT4All |
| Voice Command Center | ✅ | Implemented with Whisper.cpp and Piper TTS |
| Recon/Enumeration | ✅ | Basic integration with nmap |
| Interface | ✅ | Real-time visualization dashboard implemented |
| Data Handling | 🟨 | Partial implementation |
| Penetration Testing | ✅ | Integrated shell library, enumeration, and privilege escalation techniques |
| Agent System | ✅ | Autonomous agent framework with planning capabilities |
| Incident Response | ✅ | One-Click Incident Response Simulator with comprehensive training capabilities |
| Advanced Red Team | 🟨 | Partial implementation (needs integration with external tools) |

## Planned Enhancements

- Complete integration of all enumeration tools
- Add full Metasploit/Sliver framework integration
- Implement threat intelligence feeds
- Enhance the incident response simulator with more interactive features
- Integrate threat intelligence with incident response training
- Add AI-driven attack path analysis
- Implement scenario-based security training with gamification elements
- Create collaborative incident response simulation for team training