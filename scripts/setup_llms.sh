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
  PYTHON_VENV_BASE=$PWD
else
  # Regular paths
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

# Function to check and install python version using pyenv
check_and_install_python_version() {
    local required_version=$1
    echo "Checking Python version $required_version with pyenv..."

    if ! pyenv versions --bare | grep -q "^${required_version}$"; then
        echo "Python $required_version is not installed. Installing..."
        pyenv install "$required_version"
    else
        echo "Python $required_version is already installed."
    fi
}

# Function to setup python virtual environment for a component
setup_python_venv() {
    local venv_path=$1
    local python_version=$2

    if [ -d "$venv_path" ]; then
        echo "Python virtual environment already exists at $venv_path, reusing it."
    else
        echo "Creating Python virtual environment at $venv_path with Python $python_version..."
        pyenv shell "$python_version"
        pyenv which python
        pyenv exec python -m venv "$venv_path"
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

    local required_python_version="3.12.0"
    local venv_path="$PYTHON_VENV_BASE/vllm"

    check_and_install_python_version "$required_python_version"
    setup_python_venv "$venv_path" "$required_python_version"
    activate_python_venv "$venv_path"

    echo "Python version in virtual environment: $(python --version)"

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
    pip install --upgrade pip

    # Install vLLM
    echo "Installing vLLM..."
    pip install -e .

    # Create model directory
    mkdir -p "$MODELS_DIR/vllm"

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

# Setup GPT4All
setup_gpt4all() {
    echo
    echo "Setting up GPT4All..."

    local required_python_version="3.10.0"
    local venv_path="$PYTHON_VENV_BASE/gpt4all"

    check_and_install_python_version "$required_python_version"
    setup_python_venv "$venv_path" "$required_python_version"
    activate_python_venv "$venv_path"

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

    deactivate_python_venv

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
