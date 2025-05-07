#!/bin/bash
# G3r4ki - Setup LLM components (llama.cpp, vLLM, GPT4All)

set -e

echo "G3r4ki - Setting up LLM components"
echo "================================="
echo

# Set TMPDIR to a directory with sufficient space for pip build temp files
TMPDIR="$HOME/tmp"
mkdir -p "$TMPDIR"
export TMPDIR

# Check available space on TMPDIR
REQUIRED_SPACE_MB=1024  # 1GB minimum
AVAILABLE_SPACE_MB=$(df "$TMPDIR" | tail -1 | awk '{print $4}')
AVAILABLE_SPACE_MB=$((AVAILABLE_SPACE_MB / 1024))

if [ "$AVAILABLE_SPACE_MB" -lt "$REQUIRED_SPACE_MB" ]; then
    echo "ERROR: Not enough disk space in TMPDIR ($TMPDIR) to proceed with installation."
    echo "Available space: ${AVAILABLE_SPACE_MB}MB, required: ${REQUIRED_SPACE_MB}MB."
    echo "Please free up space or set TMPDIR to a directory with more space."
    exit 1
fi

echo "Using TMPDIR=$TMPDIR with available space ${AVAILABLE_SPACE_MB}MB for pip build temp files."
# Check if running on Replit
REPLIT_ENV=0
if [ -n "$REPL_ID" ]; then
  echo "Running in Replit environment."
  REPLIT_ENV=1
fi

# Configuration
if [ "$REPLIT_ENV" -eq 1 ]; then
  # Replit paths
  LLAMA_CPP_DIR=$PWD/vendor/llama.cpp
  VLLM_DIR=$PWD/vendor/vllm
  GPT4ALL_DIR=$PWD/vendor/gpt4all
  MODELS_DIR=~/.local/share/g3r4ki/models
  PYTHON_VENV_BASE=$PWD
else
    # Always use Linux environment paths
    LLAMA_CPP_DIR=$PWD/vendor/llama.cpp
    VLLM_DIR=$PWD/vendor/vllm
    GPT4ALL_DIR=$PWD/vendor/gpt4all
    MODELS_DIR=~/.local/share/g3r4ki/models
    PYTHON_VENV_BASE=~/.g3r4ki_venvs
fi

mkdir -p "$PYTHON_VENV_BASE"

# Function to check for required tools
check_requirements() {
    echo "Checking requirements..."
    
    # Skip requirement checks for Replit environment
    if [ "$REPLIT_ENV" -eq 1 ]; then
        echo "Running in Replit environment - skipping system requirement checks."
        
        # Create vendor directory for repositories
        mkdir -p $PWD/vendor
        
        return 0
    fi
    
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
    
    # Check for Python3
    if ! command -v python3 &> /dev/null; then
        echo "Error: python3 is not installed. Please install it first."
        exit 1
    fi

    # Check for bc
    if ! command -v bc &> /dev/null; then
        echo "Error: bc is not installed. Please install it first (e.g., sudo apt install bc)."
        exit 1
    fi
    
    # Check for pyenv
    if ! command -v pyenv &> /dev/null; then
        echo "Error: pyenv is not installed. Please install pyenv to manage Python versions."
        exit 1
    fi
    
    echo "All requirements met."
}

# Function to find python3.12 executable path
find_python312() {
    # Try pyenv to find python3.12 path first
    if command -v pyenv &> /dev/null; then
        local pyenv_prefix
        pyenv_prefix=$(pyenv prefix 3.12.0 2>/dev/null || true)
        if [ -n "$pyenv_prefix" ]; then
            echo "$pyenv_prefix/bin/python"
            return
        fi
    fi

    # Then try system python3.12
    if command -v python3.12 &> /dev/null && [ -x "$(command -v python3.12)" ]; then
        echo "python3.12"
        return
    fi

    echo ""
}

# Function to setup python virtual environment for a component
setup_python_venv() {
    local venv_path=$1
    local python_version=$2

    if [ -d "$venv_path" ]; then
        echo "Python virtual environment already exists at $venv_path, reusing it."
    else
        echo "Creating Python virtual environment at $venv_path with Python $python_version..."
        echo "Running command: $python_version -m venv \"$venv_path\""
        $python_version -m venv "$venv_path"
    fi
}

# Function to activate python virtual environment
activate_python_venv() {
    local venv_path=$1
    # shellcheck disable=SC1090
    source "$venv_path/bin/activate"
    echo "Activated Python virtual environment at $venv_path"
}

# Function to deactivate python virtual environment
deactivate_python_venv() {
    deactivate
    echo "Deactivated Python virtual environment"
}

# Setup llama.cpp
setup_llama_cpp() {
    echo
    echo "Setting up llama.cpp..."

    # Clone or update repository
    if [ -d "$LLAMA_CPP_DIR" ]; then
        echo "llama.cpp directory found. Updating..."
        cd "$LLAMA_CPP_DIR"
        git pull
    else
        echo "Cloning llama.cpp repository..."
        git clone https://github.com/ggerganov/llama.cpp.git "$LLAMA_CPP_DIR"
        cd "$LLAMA_CPP_DIR"
    fi

    # Check if requirements directory and original requirements file exist
    if [ ! -d "$LLAMA_CPP_DIR/requirements" ]; then
        echo "Error: requirements directory not found in $LLAMA_CPP_DIR."
        echo "Please ensure the llama.cpp repository is cloned correctly."
        exit 1
    fi

    if [ ! -f "$LLAMA_CPP_DIR/requirements/requirements-convert_legacy_llama.txt" ]; then
        echo "Error: requirements-convert_legacy_llama.txt not found in $LLAMA_CPP_DIR/requirements."
        echo "Please ensure the llama.cpp repository is complete."
        exit 1
    fi

    # Create a patched requirements file with torch version updated
    PATCHED_REQ_FILE="$LLAMA_CPP_DIR/requirements/requirements-convert_legacy_llama_patched.txt"
    sed 's/torch~=2.2.1/torch>=2.5.0/' "$LLAMA_CPP_DIR/requirements/requirements-convert_legacy_llama.txt" > "$PATCHED_REQ_FILE"

    # Build llama.cpp using CMake (updated from deprecated Makefile build)
    echo "Building llama.cpp with CMake..."
    rm -rf build
    mkdir build
    cd build
    cmake ..

    # Check for CUDA
    if command -v nvcc &> /dev/null; then
        echo "CUDA found, building with GPU support..."
        LLAMA_CUBLAS=1 cmake --build . -- -j$(nproc)
    else
        echo "CUDA not found, building CPU-only version..."
        cmake --build . -- -j$(nproc)
    fi

    # Create model directory
    mkdir -p "$MODELS_DIR/llama"

    MODEL_FILE="$MODELS_DIR/llama/tinyllama-1.1b-chat-v1.0.Q4_0.gguf"
    if [ -f "$MODEL_FILE" ]; then
        echo "Test model already exists at $MODEL_FILE, skipping download."
    else
        echo "Do you want to download a small test model for llama.cpp? (y/n)"
        read -r download_model

        if [[ "$download_model" == "y" || "$download_model" == "Y" ]]; then
            echo "Downloading TinyLlama model for testing..."
            cd "$LLAMA_CPP_DIR"
            # Use system python3 for llama.cpp dependencies
            python3 -m pip install torch==2.5.0 protobuf==4.25.3
            grep -vE 'torch|protobuf' "$PATCHED_REQ_FILE" > requirements_no_torch.txt
            python3 -m pip install -r requirements_no_torch.txt
            wget -O "$MODEL_FILE" https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_0.gguf
            echo "Test model downloaded to $MODELS_DIR/llama/"
        else
            echo "Skipping model download. You will need to download models manually."
            echo "Models should be placed in: $MODELS_DIR/llama/"
            echo "You can download models from: https://huggingface.co/TheBloke"
        fi
    fi

    echo "llama.cpp setup complete."
}

# Setup vLLM
setup_vllm() {
    echo
    echo "Setting up vLLM..."

    # Remember old python
    OLD_PYTHON=$(which python3)

    # Ensure Python 3.12 is installed via pyenv
    if pyenv versions --bare | grep -q "^3.12.0$"; then
        echo "Python 3.12.0 already installed via pyenv, skipping installation."
    else
        echo "Installing Python 3.12.0 via pyenv..."
        pyenv install 3.12.0
    fi

    # Determine python3.12 path
    PYTHON312=$(pyenv prefix 3.12.0)/bin/python3.12
    if [ ! -x "$PYTHON312" ]; then
        echo "Error: python3.12 not found after pyenv install"; exit 1
    fi

    # Create and activate virtual environment
    VENV_PATH="$PYTHON_VENV_BASE/vllm"
    if [ -d "$VENV_PATH" ]; then
        echo "Python virtual environment for vLLM already exists at $VENV_PATH, reusing it."
    else
        echo "Creating venv for vLLM at $VENV_PATH using Python 3.12"
        "$PYTHON312" -m venv "$VENV_PATH"
    fi
    source "$VENV_PATH/bin/activate"
    echo "Activated venv: $(which python) --version"

    # Ensure vendor directory exists
    mkdir -p "$(dirname "$VLLM_DIR")"

    # Clone or update repository
    if [ -d "$VLLM_DIR" ]; then
        echo "vLLM directory found. Updating..."
        cd "$VLLM_DIR"
        git pull
    else
        echo "Cloning vLLM repository..."
        git clone https://github.com/vllm-project/vllm.git "$VLLM_DIR"
        cd "$VLLM_DIR"
    fi

    # Upgrade pip in the virtual environment only if needed
    PIP_VERSION_BEFORE=$(pip --version | awk '{print $2}')
    pip install --upgrade pip
    PIP_VERSION_AFTER=$(pip --version | awk '{print $2}')
    if [ "$PIP_VERSION_BEFORE" = "$PIP_VERSION_AFTER" ]; then
        echo "pip is already up to date."
    else
        echo "pip upgraded from $PIP_VERSION_BEFORE to $PIP_VERSION_AFTER."
    fi

    # Check if vLLM is already installed in editable mode
    if pip show vllm &> /dev/null; then
        echo "vLLM is already installed in the virtual environment, skipping reinstall."
    else
        echo "Installing vLLM..."
        pip install -e .
    fi

    # Create model directory
    mkdir -p "$MODELS_DIR/vllm"

    MODEL_FILE="$MODELS_DIR/vllm/test-model.bin"
    if [ -f "$MODEL_FILE" ]; then
        echo "Test model already exists at $MODEL_FILE, skipping download."
    else
        echo "Do you want to download a small test model for vLLM? (y/n)"
        read -r download_model

        if [[ "$download_model" == "y" || "$download_model" == "Y" ]]; then
            echo "Downloading a small test model for vLLM..."
            wget -O "$MODEL_FILE" https://huggingface.co/Vanessasml/cyber-risk-llama-2-7b
            echo "Test model downloaded to $MODELS_DIR/vllm/"
        else
            echo "Skipping model download. You will need to download models manually."
            echo "Models should be placed in: $MODELS_DIR/vllm/"
            echo "You can download models from: https://huggingface.co/vllm"
        fi
    fi

    echo "vLLM setup complete."

    # Deactivate venv and restore python
    deactivate
    echo "Restored Python to: $OLD_PYTHON --version" && $OLD_PYTHON --version
}

# Setup GPT4All
setup_gpt4all() {
    echo
    echo "Setting up GPT4All..."

    # Use same environment as setup_llama_cpp (system python3)
    # No separate venv or python version management here

    # Create directories
    mkdir -p "$GPT4ALL_DIR"
    mkdir -p "$MODELS_DIR/gpt4all"

    # Clone or update GPT4All repository
    if [ -d "$GPT4ALL_DIR" ]; then
        echo "GPT4All directory found. Updating..."
        cd "$GPT4ALL_DIR"
        git pull
    else
        echo "Cloning GPT4All repository..."
        git clone https://github.com/nomic-ai/gpt4all.git "$GPT4ALL_DIR"
        cd "$GPT4ALL_DIR"
    fi

    # Make sure gpt4all-cli is executable if it exists
    if [ -f "$GPT4ALL_DIR/gpt4all-cli" ]; then
        chmod +x "$GPT4ALL_DIR/gpt4all-cli"
    fi

    MODEL_FILE="$MODELS_DIR/gpt4all/ggml-gpt4all-j-v1.3-groovy.bin"
    if [ -f "$MODEL_FILE" ]; then
        echo "Test model already exists at $MODEL_FILE, skipping download."
    else
        echo "Do you want to download a test model for GPT4All? (y/n)"
        read -r download_model

        if [[ "$download_model" == "y" || "$download_model" == "Y" ]]; then
            echo "Downloading a small GPT4All model for testing..."
            wget -O "$MODEL_FILE" https://huggingface.co/jeiku/Nous-Capybara-3B-V1.9-Q4_K_M-GGUF
            echo "Test model downloaded to $MODELS_DIR/gpt4all/"
        else
            echo "Skipping model download. You will need to download models manually."
            echo "Models should be placed in: $MODELS_DIR/gpt4all/"
            echo "You can download models from: https://gpt4all.io/models/models.json"
        fi
    fi

    echo "GPT4All setup complete."
}

# Main script
check_requirements
setup_llama_cpp
setup_vllm
setup_gpt4all



echo
echo "LLM components setup complete!"
echo "You can now use llama.cpp, vLLM, and GPT4All for local AI operations."
echo
echo "Tips:"
echo "  - You may need to download larger models for production use"
echo "  - Custom models can be placed in: $MODELS_DIR"
echo "  - Use 'g3r4ki llm list' to see available models"
echo "  - Use 'g3r4ki llm query' to interact with models"
echo
