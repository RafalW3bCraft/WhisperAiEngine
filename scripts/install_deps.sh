#!/bin/bash
# G3r4ki - Install system dependencies

set -e

# Check if running as root, if not re-run with sudo
if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root. Re-running with sudo..."
  exec sudo bash "$0" "$@"
fi

echo "G3r4ki - Installing system dependencies"
echo "======================================"
echo


# Check if running on Replit
if [ -n "$REPL_ID" ]; then
  echo "Running in Replit environment. Using packager tool instead of apt."
  # Skip the root check and system installation in Replit
else
  # Check if running as root
  if [ "$(id -u)" -eq 0 ]; then
    echo "This script is running as root. Continuing installation."
  else
    echo "This script requires root privileges to install packages."
    echo "Please run with: sudo $0"
    exit 1
  fi
fi

# Check if running on Replit
if [ -n "$REPL_ID" ]; then
    # Replit environment setup
    echo "Setting up for Replit environment..."
    
    # Install Python dependencies using packager
    echo "Installing Python dependencies..."
    pip install pyyaml requests numpy huggingface_hub python-dateutil
    
    # Create directories for models and cache
    echo "Creating data directories..."
    mkdir -p ~/.local/share/g3r4ki/models/llama
    mkdir -p ~/.local/share/g3r4ki/models/vllm
    mkdir -p ~/.local/share/g3r4ki/models/gpt4all
    mkdir -p ~/.cache/g3r4ki
    
else:
    # Linux environment setup (non-Replit)
    # Detect OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_NAME=$NAME
        OS_ID=$ID
    else
        echo "Cannot detect operating system."
        exit 1
    fi

    # Inform user
    echo "Detected OS: $OS_NAME"
    echo

    # Update package lists
    echo "Updating package lists..."
    apt update

    # Install essential tools
    echo "Installing essential tools..."
    apt install -y build-essential cmake libssl-dev libcurl4-openssl-dev python3-venv ccache git

    # Install Python and dependencies
    echo "Installing Python and dependencies..."
    apt install -y python3-dev python3-pip python3-venv

    # Install Kali tools if on Kali
    if [[ "$OS_ID" == "kali" ]]; then
        echo "Installing Kali cybersecurity tools..."
        apt install -y kali-tools-information-gathering kali-tools-vulnerability
    else
        # Install basic security tools on non-Kali systems
        echo "Installing basic security tools..."
        apt install -y nmap whois dnsutils nikto sslscan
    fi

    # Install additional tools needed by G3r4ki
    echo "Installing additional tools..."
    apt install -y curl wget tar unzip jq alsa-utils sox

    # Check for NVIDIA GPU
    if command -v nvidia-smi &> /dev/null; then
        echo "NVIDIA GPU detected, installing NVIDIA tools..."
        apt install -y nvidia-cuda-toolkit

        # Check if CUDA is available
        if command -v nvcc &> /dev/null; then
            echo "CUDA toolkit installed successfully."
            nvcc --version
        else
            echo "Warning: CUDA toolkit installation may have failed."
            echo "You may need to install it manually for GPU acceleration."
        fi
    else
        echo "No NVIDIA GPU detected, skipping CUDA installation."
    fi

    # Create Python virtual environment
    echo "Setting up Python virtual environment..."
    VENV_PATH="$HOME/.g3r4ki_venvs/main"
    if [ -d "$VENV_PATH" ]; then
        echo "Python virtual environment $VENV_PATH already exists, skipping creation."
    else
        python3 -m venv "$VENV_PATH"
    fi

    # Install Python dependencies inside the virtual environment
    echo "Installing Python dependencies inside the virtual environment..."
    source "$VENV_PATH/bin/activate"
    pip install --upgrade pip
    deactivate

    # Add aliases to bashrc if they don't exist
    if ! grep -q "alias g3r4ki=" ~/.bashrc; then
        echo "" >> ~/.bashrc
        echo "# G3r4ki aliases" >> ~/.bashrc
    fi
fi

echo
echo "System dependencies installation complete!"
echo
echo "Next steps:"
echo "1. Run: source ~/.bashrc"
echo "2. Setup voice components: make setup-voice"
echo "3. Setup LLM components: make setup-llms"
echo
