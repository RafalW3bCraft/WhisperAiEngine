#!/bin/bash
# G3r4ki - Setup LLM components (llama.cpp, vLLM, GPT4All)

set -e

echo "G3r4ki - Setting up LLM components"
echo "================================="
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
  LLAMA_CPP_DIR=$PWD/vendor/llama.cpp
  VLLM_DIR=$PWD/vendor/vllm
  GPT4ALL_DIR=$PWD/vendor/gpt4all
  MODELS_DIR=~/.local/share/g3r4ki/models
  PYTHON_VENV=$PWD
else
  # Regular paths
  LLAMA_CPP_DIR=$PWD/vendor/llama.cpp
  VLLM_DIR=$PWD/vendor/vllm
  GPT4ALL_DIR=$PWD/vendor/gpt4all
  MODELS_DIR=~/.local/share/g3r4ki/models
  PYTHON_VENV=~/.g3r4ki_venv
fi

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
    
    # Check for Python
    if ! command -v python3 &> /dev/null; then
        echo "Error: python3 is not installed. Please install it first."
        exit 1
    fi

    # Check for bc
    if ! command -v bc &> /dev/null; then
        echo "Error: bc is not installed. Please install it first (e.g., sudo apt install bc)."
        exit 1
    fi
    
    echo "All requirements met."
}

# Function to setup llama.cpp
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
    
    echo "Do you want to download a small test model for llama.cpp? (y/n)"
    read -r download_model
    
    if [[ "$download_model" == "y" || "$download_model" == "Y" ]]; then
        echo "Downloading TinyLlama model for testing..."
        cd "$LLAMA_CPP_DIR"
        # Install compatible torch and protobuf versions first
        python3 -m pip install torch==2.5.0 protobuf==4.25.3
        # Then install other requirements excluding torch and protobuf using patched requirements file
        grep -vE 'torch|protobuf' "$PATCHED_REQ_FILE" > requirements_no_torch.txt
        python3 -m pip install -r requirements_no_torch.txt
        python3 scripts/convert.py --outfile "$MODELS_DIR/llama/tinyllama-1.1b-chat-v1.0.Q4_0.gguf" --outtype q4_0 https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_0.gguf
        echo "Test model downloaded to $MODELS_DIR/llama/"
    else
        echo "Skipping model download. You will need to download models manually."
        echo "Models should be placed in: $MODELS_DIR/llama/"
        echo "You can download models from: https://huggingface.co/TheBloke"
    fi
    
    echo "llama.cpp setup complete."
}

# Function to setup vLLM
REQUIRED_PYTHON_VERSION="3.12.0"

check_pyenv_and_python() {
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"

    echo "Checking pyenv and required Python version..."

    if ! command -v pyenv &> /dev/null; then
        echo "⚠️ pyenv is not installed. Please install pyenv to manage Python versions."
        exit 1
    fi

    if ! pyenv versions --bare | grep -q "^$REQUIRED_PYTHON_VERSION$"; then
        echo "⚠️ Python $REQUIRED_PYTHON_VERSION is not installed."
        echo "Installing Python $REQUIRED_PYTHON_VERSION using pyenv..."
        pyenv install $REQUIRED_PYTHON_VERSION
    fi

    # Set python version for current shell session explicitly
    pyenv shell $REQUIRED_PYTHON_VERSION
    echo "Using Python version $(python --version)"
}
setup_python_venv() {
    echo "Setting up Python virtual environment..."

    if [ -d "$PYTHON_VENV" ]; then
        echo "Removing existing virtual environment at $PYTHON_VENV"
        rm -rf "$PYTHON_VENV"
    fi

    PYENV_PYTHON=$(pyenv which python)
    echo "Using pyenv Python at $PYENV_PYTHON to create virtual environment"
    "$PYENV_PYTHON" -m venv "$PYTHON_VENV"

    source "$PYTHON_VENV/bin/activate"
    echo "Python virtual environment activated."
}

deactivate_python_venv() {
    deactivate
    echo "Python virtual environment deactivated."
}

setup_vllm() {
    echo "Setting up vLLM..."

    check_pyenv_and_python
    setup_python_venv

    # Confirm python version in venv
    echo "Python version in virtual environment: $($PYTHON_VENV/bin/python --version)"

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

    # Upgrade pip in the virtual environment
    echo "Upgrading pip in the virtual environment..."
    "$PYTHON_VENV/bin/python" -m pip install --upgrade pip

    # Install vLLM
    echo "Installing vLLM..."
    "$PYTHON_VENV/bin/pip" install -e .

    # Create model directory
    mkdir -p "$MODELS_DIR/vllm"

    # Prompt to download test model
    echo "Do you want to download a small test model for vLLM? (y/n)"
    read -r download_model

    if [[ "$download_model" == "y" || "$download_model" == "Y" ]]; then
        echo "Downloading a small test model for vLLM..."
        wget -O "$MODELS_DIR/vllm/test-model.bin" https://huggingface.co/vllm/test-model/resolve/main/test-model.bin
        echo "Test model downloaded to $MODELS_DIR/vllm/"
    else
        echo "Skipping model download. You will need to download models manually."
        echo "Models should be placed in: $MODELS_DIR/vllm/"
        echo "You can download models from: https://huggingface.co/vllm"
    fi

    deactivate_python_venv

    echo "vLLM setup complete."
}

# Function to setup GPT4All
setup_gpt4all() {
    echo
    echo "Setting up GPT4All..."
    
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
    
    # Prompt to download test model
    echo "Do you want to download a test model for GPT4All? (y/n)"
    read -r download_model
    
    if [[ "$download_model" == "y" || "$download_model" == "Y" ]]; then
        echo "Downloading a small GPT4All model for testing..."
        wget -O "$MODELS_DIR/gpt4all/ggml-gpt4all-j-v1.3-groovy.bin" https://gpt4all.io/models/ggml-gpt4all-j-v1.3-groovy.bin
        echo "Test model downloaded to $MODELS_DIR/gpt4all/"
    else
        echo "Skipping model download. You will need to download models manually."
        echo "Models should be placed in: $MODELS_DIR/gpt4all/"
        echo "You can download models from: https://gpt4all.io/models/models.json"
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