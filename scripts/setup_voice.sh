#!/bin/bash
# G3r4ki - Setup voice components (Whisper and Piper)

set -euo pipefail

echo "G3r4ki - Setting up voice components"
echo "==================================="
echo

# Check if running on Replit
REPLIT_ENV=0
if [[ -n "${REPL_ID:-}" ]]; then
  echo "Detected Replit environment."
  REPLIT_ENV=1
fi

# Configuration
if [[ "$REPLIT_ENV" -eq 1 ]]; then
  WHISPER_DIR="$PWD/vendor/whisper.cpp"
  PIPER_DIR="$PWD/vendor/piper"
else
  WHISPER_DIR="$HOME/whisper.cpp"
  PIPER_DIR="$HOME/piper"
fi

# Function to check for required tools
check_requirements() {
    echo "[+] Checking system requirements..."

    for cmd in git make g++ cmake; do
        if ! command -v "$cmd" &> /dev/null; then
            echo "Error: '$cmd' is not installed. Please install it before proceeding."
            exit 1
        fi
    done

    if ! command -v wget &> /dev/null && ! command -v curl &> /dev/null; then
        echo "Error: Neither wget nor curl found. Please install one of them."
        exit 1
    fi

    echo "[+] All requirements satisfied."
}

# Function to download files with fallback
download() {
    local url="$1"
    local output="$2"
    if command -v wget &> /dev/null; then
        wget -q --show-progress -O "$output" "$url"
    elif command -v curl &> /dev/null; then
        curl -L --progress-bar -o "$output" "$url"
    fi
}

# Setup Whisper
setup_whisper() {
    echo "[+] Setting up Whisper.cpp for STT..."
    if [[ -d "$WHISPER_DIR" ]]; then
        echo "[-] Found existing Whisper directory. Pulling updates..."
        cd "$WHISPER_DIR"
        git pull
    else
        echo "[+] Cloning Whisper.cpp..."
        git clone https://github.com/ggerganov/whisper.cpp.git "$WHISPER_DIR"
        cd "$WHISPER_DIR"
    fi

    echo "[+] Building Whisper.cpp..."
    if make -q clean 2>/dev/null; then
        make clean
    else
        echo "[!] No 'clean' target found in Makefile, skipping 'make clean'."
    fi
    if ! make -j; then
        echo "[!] Parallel build failed. Retrying with single thread..."
        make
    fi

    MODEL_FILE="$WHISPER_DIR/models/ggml-tiny.en.bin"
    if [ -f "$MODEL_FILE" ]; then
        echo "Whisper model already exists at $MODEL_FILE, skipping download."
    else
        echo "[+] Downloading Whisper model (tiny.en)..."
        bash ./models/download-ggml-model.sh tiny.en
    fi
    echo "[✓] Whisper setup complete."
}

# Setup Piper
setup_piper() {
    echo "[+] Setting up Piper for TTS..."
    if [[ -d "$PIPER_DIR" ]]; then
        echo "[-] Found existing Piper directory. Pulling updates..."
        cd "$PIPER_DIR"
        git pull
    else
        echo "[+] Cloning Piper repository..."
        git clone https://github.com/rhasspy/piper.git "$PIPER_DIR"
        cd "$PIPER_DIR"
    fi

    mkdir -p "$PIPER_DIR/voices"

    local ARCH OS PIPER_URL
    ARCH=$(uname -m)
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')

    echo "[+] Detecting platform: $ARCH-$OS"
    if [[ "$ARCH" == "x86_64" && "$OS" == "linux" ]]; then
        PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz"
    elif [[ "$ARCH" == "aarch64" && "$OS" == "linux" ]]; then
        PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz"
    else
        echo "[!] No prebuilt Piper binary for $ARCH-$OS. You must build from source manually."
    fi

    if [[ -n "${PIPER_URL:-}" ]]; then
        cd "$PIPER_DIR"
        echo "[+] Downloading Piper binary..."
        if [ -f "piper" ]; then
            echo "Piper binary already exists, skipping download."
        else
            download "$PIPER_URL" "piper.tar.gz"
            tar -xf piper.tar.gz && rm piper.tar.gz
            chmod +x piper || true
        fi
    fi

    mkdir -p "$PIPER_DIR/voices"

    local VOICE_MODEL="$PIPER_DIR/voices/en_US-amy-low.onnx"
    local VOICE_MODEL_JSON="$PIPER_DIR/voices/en_US-amy-low.onnx.json"

    echo "[+] Downloading voice model (en_US-amy-low)..."
    if [ -f "$VOICE_MODEL" ] && [ -f "$VOICE_MODEL_JSON" ]; then
        echo "Voice model files already exist, skipping download."
    else
        download "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx" \
                 "$VOICE_MODEL"

        download "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx.json" \
                 "$VOICE_MODEL_JSON"
    fi

    echo "[✓] Piper setup complete."
}

# Run everything
check_requirements
setup_whisper
setup_piper

echo
echo "✅ Voice components setup complete!"
echo "• Whisper (STT) installed at: $WHISPER_DIR"
echo "• Piper (TTS) installed at: $PIPER_DIR"
