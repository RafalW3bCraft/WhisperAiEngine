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

# Run the installation script (requires root privileges for system dependencies)
sudo ./install.sh
```

This script will:
- Check system requirements (OS, Python version, disk space, memory)
- Install system dependencies (Python, PostgreSQL, build tools, networking tools)
- Set up PostgreSQL database with user, password, and database creation
- Install Python dependencies in development mode
- Initialize the database schema
- Optionally configure local AI capabilities
- Finalize installation and optionally create a system-wide command

### Manual Installation

If you prefer manual setup, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/g3r4ki.git
   cd g3r4ki
   ```

2. Install system dependencies (on Debian/Ubuntu/Kali):
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-pip python3-venv python3-dev postgresql postgresql-contrib libpq-dev build-essential git curl wget net-tools nmap netcat-openbsd
   ```

3. Install Python dependencies:
   ```bash
   python3 -m pip install --upgrade pip
   python3 -m pip install -e .
   ```

4. Set up PostgreSQL database:
   ```bash
   sudo systemctl start postgresql
   sudo -u postgres psql -c "CREATE USER g3r4ki WITH PASSWORD 'your_password';"
   sudo -u postgres psql -c "CREATE DATABASE g3r4ki_db OWNER g3r4ki;"
   ```

5. Create a `.env` file with database connection info and optional API keys:
   ```bash
   cat > .env << EOL
   DATABASE_URL=postgresql://g3r4ki:your_password@localhost/g3r4ki_db
   # OPENAI_API_KEY=your_openai_key
   # ANTHROPIC_API_KEY=your_anthropic_key
   # DEEPSEEK_API_KEY=your_deepseek_key
   EOL
   ```

6. Initialize the database schema:
   ```bash
   python3 -m src.database.init_db
   ```

### Additional Setup

- To install system dependencies separately, you can run:
  ```bash
  sudo scripts/install_deps.sh
  ```

- To set up local AI models (llama.cpp, vLLM, GPT4All):
  ```bash
  make setup-llms
  ```

- To set up voice components (Whisper and Piper):
  ```bash
  make setup-voice
  ```

### Optional

- During installation, you may be prompted to create a system-wide command:
  ```bash
  sudo ln -sf $(pwd)/g3r4ki.py /usr/local/bin/g3r4ki
  ```
  This allows running `g3r4ki` from anywhere.

## Getting Started

### Launch G3r4ki

```bash
# Start the interactive shell
python3 g3r4ki.py interactive

# Or start with debugging enabled
python3 g3r4ki.py --debug interactive

# Launch the web interface
python3 g3r4ki.py web
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

## Configuration

### AI Providers

Set up API keys for cloud AI providers by creating a `.env` file:

```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DEEPSEEK_API_KEY=your_deepseek_key
```

### Local AI Models

Configure local AI models for offline operation:

```bash
python3 g3r4ki.py setup local-ai
```

### Database Configuration

Edit database settings in `.env`:

```
DATABASE_URL=postgresql://username:password@hostname/dbname
```

## Troubleshooting

### Common Issues

- Ensure PostgreSQL service is running:
  ```bash
  sudo systemctl status postgresql
  ```

- Verify database connection:
  ```bash
  python3 -c "from src.database import check_connection; check_connection()"
  ```

- Check AI provider connectivity:
  ```bash
  python3 -m src.ai.proxy --test-providers
  ```

- Reinstall G3r4ki if needed:
  ```bash
  python3 g3r4ki.py setup uninstall
  sudo ./install.sh
  ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

© 2024 RafalW3bCraft

## Disclaimer

G3r4ki is designed for educational purposes and authorized security testing only. Users are responsible for complying with all applicable laws and regulations when using this software. The developers assume no liability for misuse or damage caused by this software.
