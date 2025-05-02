# G3r4ki - AI-Powered Cybersecurity Operations System

G3r4ki is an advanced AI-powered Linux cybersecurity platform that autonomously manages security operations through intelligent, multi-provider AI integration.

```
  __ _____  _ _   _    _ 
 / _|__ / || | | | | _(_)
| |_ |_ \| || |_| |/ / |
|  _|__) |__   _|   <| |
|_| |___/   |_| |_|\_\_|
```

## Key Features

- **Multi-AI Provider Integration**: OpenAI, Anthropic, and DeepSeek support with seamless failover
- **Offline Capability**: Functions with or without internet connectivity using local AI models
- **Advanced CLI**: Natural language processing for intuitive command execution
- **Comprehensive Security Framework**: Offensive and defensive capabilities with no restrictions
- **Autonomous Agents**: Self-improving security automation for continuous enhancement
- **Elite Offensive Modules**: RAT deployment, keylogging, credential harvesting, and C2 integration
- **PostgreSQL Database**: Track operations, agents, and results with a robust data store
- **Auto-Wake System**: Automatic initialization of AI components on launch

## System Requirements

- **OS**: Kali Linux (recommended), Ubuntu, or Debian-based distributions
- **Python**: 3.10+ with pip installed
- **Database**: PostgreSQL (automatically configured on setup)
- **Storage**: At least 2GB free space for core components (more for local AI models)
- **RAM**: Minimum 4GB (8GB+ recommended for local AI)
- **API Keys**: (Optional) OpenAI, Anthropic, and/or DeepSeek for cloud AI capabilities

## Installation

### Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/g3r4ki.git
cd g3r4ki

# Run the installation script
./install.sh
```

### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/g3r4ki.git
   cd g3r4ki
   ```

2. Install Python dependencies:
   ```bash
   pip install -e .
   ```

3. Set up the database:
   ```bash
   # Install PostgreSQL if not already installed
   sudo apt update
   sudo apt install -y postgresql postgresql-contrib

   # Create a PostgreSQL user and database
   sudo -u postgres createuser --interactive --pwprompt g3r4ki
   sudo -u postgres createdb --owner=g3r4ki g3r4ki_db
   ```

4. Configure environment variables:
   ```bash
   # Create a .env file
   cat > .env << EOL
   DATABASE_URL=postgresql://g3r4ki:your_password@localhost/g3r4ki_db
   # Optional: Add API keys for cloud providers
   # OPENAI_API_KEY=your_openai_key
   # ANTHROPIC_API_KEY=your_anthropic_key
   # DEEPSEEK_API_KEY=your_deepseek_key
   EOL
   ```

5. Initialize the database:
   ```bash
   python -m src.database.init_db
   ```

## Getting Started

### Launch G3r4ki

```bash
# Start the interactive shell
python g3r4ki.py interactive

# Or start with debugging enabled
python g3r4ki.py --debug interactive

# Launch the web interface
python g3r4ki.py web
```

### Basic Commands

```
g3r4ki> help                  # Show all available commands
g3r4ki> status                # Display system status
g3r4ki> setup ai              # Configure AI providers
g3r4ki> offensive list        # List offensive modules
g3r4ki> llm providers         # List LLM providers
```

### Using Natural Language Commands

G3r4ki supports natural language commands in the interactive shell:

```
g3r4ki> scan the local network for vulnerabilities
g3r4ki> generate a reverse shell for Windows systems
g3r4ki> create a keylogger for macOS
g3r4ki> show me all active operations
```

## Module Overview

### Offensive Modules

- **RAT Deployment Toolkit**: Deploy polymorphic, cross-platform Remote Access Trojans
- **Keylogging & Screen Capture**: Advanced stealth monitoring tools
- **Command & Control Integration**: Connect to external C2 infrastructure
- **Credential Harvester**: Extract and store credentials from various sources
- **Shell Generator**: Create customized reverse and bind shells for multiple platforms

### Defensive Modules

- **Incident Response Simulator**: Test IR capabilities with realistic scenarios
- **Threat Intelligence**: Aggregate and analyze threat data
- **Penetration Testing**: Automated and guided penetration testing capabilities
- **Vulnerability Scanner**: Identify and assess security weaknesses

### AI Components

- **AI Proxy System**: Unified interface to all AI providers
- **Local AI Manager**: Configure and use local language models
- **Natural Language Processor**: Command understanding and intent extraction
- **Self-Improvement System**: Learn from usage patterns to enhance capabilities

## Configuration

### AI Providers

Set up API keys for cloud AI providers by creating a `.env` file:

```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DEEPSEEK_API_KEY=your_deepseek_key
```

### Local AI Models

Configure local AI models in the configuration:

```bash
python g3r4ki.py setup local-ai
```

### Database Configuration

Edit database settings in `.env`:

```
DATABASE_URL=postgresql://username:password@hostname/dbname
```

## Advanced Usage

### Running in Headless Mode

```bash
python g3r4ki.py --headless offensive run --mission recon --target 192.168.1.0/24
```

### Creating Custom Modules

Create a new module in `src/offensive/modules/my_module/__init__.py` and implement the required interfaces.

### Automating with Agents

Configure autonomous agent behavior:

```bash
python g3r4ki.py agent create --name defender --mission "monitor and respond to threats"
```

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

```bash
# Check database status
sudo systemctl status postgresql

# Verify connection details
python -c "from src.database import check_connection; check_connection()"
```

### AI Provider Connectivity

Test AI provider connectivity:

```bash
python -m src.ai.proxy --test-providers
```

### Reinstalling G3r4ki

To reinstall or reset G3r4ki:

```bash
# Uninstall
python g3r4ki.py setup uninstall

# Reinstall
./install.sh
```

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.

## Disclaimer

G3r4ki is designed for educational purposes and authorized security testing only. Users are responsible for complying with all applicable laws and regulations when using this software. The developers assume no liability for misuse or damage caused by this software.