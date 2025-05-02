# G3r4ki - AI-Powered Cybersecurity Platform

G3r4ki is an advanced AI-powered Linux cybersecurity platform that autonomously manages security operations through intelligent, multi-provider AI integration. The platform provides comprehensive offensive and defensive capabilities for security professionals.

## Core Features

### Multi-AI Provider Integration
- **Cloud AI Providers**: OpenAI, Anthropic, DeepSeek
- **Local AI Models**: Llama.cpp, vLLM, GPT4All
- **Auto-wake Feature**: AI automatically initializes on launch
- **Fallback Capability**: Switches between online and offline modes seamlessly

### Advanced Command Interface
- **Natural Language Processing**: Control the system using natural language
- **Voice Interface**: Voice command capabilities
- **Interactive Shell**: Command-line interface with AI assistance
- **Web Interface**: Browser-based control panel

### G3r4ki Offensive Framework
- **RAT Deployment Toolkit**: Cross-platform remote access capabilities
- **Advanced Keylogging**: Cross-platform keyboard and screen monitoring
- **Command-and-Control**: Built-in C2 server and external integrations
- **Credential Harvesting**: Extract credentials from various sources
- **Data Exfiltration**: Multi-channel data extraction capabilities
- **Evasion Techniques**: Anti-detection and defense circumvention
- **Reverse Shell Generator**: Multi-platform shell creation
- **Post-Exploitation Tools**: Maintain access and gather information

### Defensive Capabilities
- **Incident Response Simulator**: 16 different incident types for training
- **Threat Intelligence**: Integrate with various threat feeds
- **Vulnerability Assessment**: Identify and analyze security weaknesses
- **Security Monitoring**: Track and alert on suspicious activities

### Database Integration
- **Operation Tracking**: Monitor all offensive and defensive operations
- **Agent Management**: Track deployed agents and their status
- **Evidence Collection**: Store and organize collected data
- **Activity Logging**: Comprehensive activity history

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/user/g3r4ki.git
cd g3r4ki

# Install dependencies
pip install -r requirements.txt

# Run setup
python g3r4ki.py setup
```

### Configuration

1. Set up API keys for cloud AI providers (optional but recommended):
   - Create a `.env` file in the root directory
   - Add your API keys:
     ```
     OPENAI_API_KEY=your-openai-api-key
     ANTHROPIC_API_KEY=your-anthropic-api-key
     DEEPSEEK_API_KEY=your-deepseek-api-key
     ```

2. Configure local AI models for offline operation (optional):
   ```bash
   python g3r4ki.py llm download --model llama2-7b --provider llama.cpp
   ```

3. Initialize the database:
   ```bash
   python src/database/init_db.py
   ```

### Basic Usage

```bash
# Start interactive shell
python g3r4ki.py interactive

# Start web interface
python g3r4ki.py web

# Use voice interface
python g3r4ki.py voice --listen

# Run offensive module
python g3r4ki.py offensive rat --generate windows --c2 example.com --port 8443

# Run incident simulator
python g3r4ki.py incident --type ransomware
```

## Documentation

- [AI Usage Guide](AI_USAGE.md) - Detailed guide for using AI capabilities
- [Offensive Modules](OFFENSIVE_MODULES.md) - Documentation for the offensive framework
- [Incident Response](INCIDENT_RESPONSE.md) - Guide to incident response capabilities
- [API Reference](API_REFERENCE.md) - Reference for programmatic integration

## Architecture

G3r4ki is built with a modular architecture that separates concerns into distinct components:

- **System Core**: Foundation components, dependency management, auto-wake system
- **AI Layer**: Unified AI proxy, multi-provider support, online/offline capabilities
- **Database Layer**: PostgreSQL integration, ORM models, activity tracking
- **Web Interface**: Flask-based web interface with SocketIO for real-time communication
- **CLI Layer**: Command-line interface with natural language processing
- **Offensive Framework**: Modular offensive security tools
- **Defensive Framework**: Incident response and security monitoring tools

## Development

The project uses a standard Python package structure with the following key directories:

- **src/**: Source code for the application
  - **ai/**: AI integration modules
  - **cli/**: Command-line interface
  - **database/**: Database models and operations
  - **llm/**: Language model interfaces
  - **offensive/**: Offensive security modules
  - **security/**: Core security functionality
  - **system/**: System integration and management
  - **web/**: Web interface components

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is intended for authorized security testing purposes only. Use responsibly and ethically.

## Acknowledgements

Special thanks to the open-source security tools community and AI research organizations that make this project possible.