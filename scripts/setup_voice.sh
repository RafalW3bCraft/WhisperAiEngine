#!/bin/bash
# G3r4ki - Setup voice components (Whisper and Piper)

set -e

echo "G3r4ki - Setting up voice components"
echo "==================================="
echo

# Check if running on Replit
REPLIT_ENV=0
if [ -n "$REPL_ID" ]; then
  echo "Running in Replit environment."
  REPLIT_ENV=1
fi

# Configuration
if [ "$REPLIT_ENV" -eq 1 ]; then
  # Replit paths
  WHISPER_DIR=$PWD/vendor/whisper.cpp
  PIPER_DIR=$PWD/vendor/piper
else
  # Regular paths
  WHISPER_DIR=~/whisper.cpp
  PIPER_DIR=~/piper
fi

# Function to check for required tools
check_requirements() {
    echo "Checking requirements..."
    
    # Check for Git
    if ! command -v git &> /dev/null; then
        echo "Error: git is not installed. Please install it first."
        exit 1
    fi
    
    # Check for build tools
    if ! command -v make &> /dev/null || ! command -v g++ &> /dev/null; then
        echo "Error: Build tools not found. Please install build-essential first."
        exit 1
    fi
    
    # Check for CMake
    if ! command -v cmake &> /dev/null; then
        echo "Error: cmake is not installed. Please install it first."
        exit 1
    fi
    
    echo "All requirements met."
}

# Function to setup Whisper for STT
setup_whisper() {
    echo
    echo "Setting up Whisper.cpp for speech-to-text..."
    
    # Clone or update repository
    if [ -d "$WHISPER_DIR" ]; then
        echo "Whisper directory found. Updating..."
        cd "$WHISPER_DIR"
        git pull
    else
        echo "Cloning Whisper.cpp repository..."
        git clone https://github.com/ggerganov/whisper.cpp.git "$WHISPER_DIR"
        cd "$WHISPER_DIR"
    fi
    
    # Build Whisper
    echo "Building Whisper.cpp..."
    make clean
    make -j
    
    # Download a model
    echo "Downloading Whisper model (tiny.en)..."
    bash ./models/download-ggml-model.sh tiny.en
    
    echo "Whisper.cpp setup complete."
}

# Function to setup Piper for TTS
setup_piper() {
    echo
    echo "Setting up Piper for text-to-speech..."
    
    # Clone or update repository
    if [ -d "$PIPER_DIR" ]; then
        echo "Piper directory found. Updating..."
        cd "$PIPER_DIR"
        git pull
    else
        echo "Cloning Piper repository..."
        git clone https://github.com/rhasspy/piper.git "$PIPER_DIR"
        cd "$PIPER_DIR"
    fi
    
    # Create voices directory if it doesn't exist
    mkdir -p "$PIPER_DIR/voices"
    
    # Download prebuilt binary if available
    echo "Downloading Piper binary..."
    
    # Determine architecture
    ARCH=$(uname -m)
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    
    # Download URL based on architecture
    PIPER_URL=""
    if [ "$ARCH" = "x86_64" ] && [ "$OS" = "linux" ]; then
        PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz"
    elif [ "$ARCH" = "aarch64" ] && [ "$OS" = "linux" ]; then
        PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz"
    else
        echo "Warning: No prebuilt Piper binary for $ARCH-$OS. You may need to build from source."
        # We'll continue anyway to download voice models
    fi
    
    if [ -n "$PIPER_URL" ]; then
        cd "$PIPER_DIR"
        wget -O piper.tar.gz "$PIPER_URL"
        tar -xf piper.tar.gz
        rm piper.tar.gz
        chmod +x piper
    fi
    
    # Download a voice model
    echo "Downloading Piper voice model (en_US-amy-low)..."
    wget -O "$PIPER_DIR/voices/en_US-amy-low.onnx" https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx
    wget -O "$PIPER_DIR/voices/en_US-amy-low.onnx.json" https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx.json
    
    echo "Piper setup complete."
}

# Main script
check_requirements
setup_whisper
setup_piper

echo
echo "Voice components setup complete!"
echo "You can now use Whisper for STT and Piper for TTS."
echo
