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
setup_vllm() {
    echo
    echo "Setting up vLLM..."
    
    # Determine python executable for virtual environment
    if command -v python3.11 &> /dev/null; then
        PYTHON_EXEC=python3.11
    elif command -v python3 &> /dev/null; then
        PYTHON_EXEC=python3
    else
        echo "Error: No suitable Python interpreter found (python3.11 or python3)."
        exit 1
    fi
    
    # Check if virtual environment exists, create if not
    if [ ! -d "$PYTHON_VENV" ]; then
        echo "Creating Python virtual environment with $PYTHON_EXEC..."
        $PYTHON_EXEC -m venv "$PYTHON_VENV"
    fi
    
    # Activate virtual environment
    source "$PYTHON_VENV/bin/activate"
    
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
    
    # Create model directory
    mkdir -p "$MODELS_DIR/vllm"
    
    # Install vLLM
    echo "Installing vLLM..."
    
    # Check if CUDA is available
    if command -v nvcc &> /dev/null; then
        echo "CUDA found, installing vLLM with GPU support..."
        pip install -e .
    else
        echo "CUDA not found, installing CPU-only version..."
        pip install -e ".[cpu]"
    fi
    
    # Deactivate virtual environment
    deactivate
    
    echo "vLLM setup complete."
    echo "Note: vLLM can use HuggingFace models directly without downloading them."
    echo "You can also download models to: $MODELS_DIR/vllm/"
}

# Function to setup GPT4All
setup_gpt4all() {
    echo
    echo "Setting up GPT4All..."
    
    # Create directories
    mkdir -p "$GPT4ALL_DIR"
    mkdir -p "$MODELS_DIR/gpt4all"
    
    # Check operating system and architecture
    OS=$(uname -s)
    ARCH=$(uname -m)
    
    if [ "$OS" = "Linux" ]; then
        if [ "$ARCH" = "x86_64" ]; then
            echo "Downloading GPT4All for Linux x86_64..."
            wget -O /tmp/gpt4all.deb https://gpt4all.io/installers/gpt4all_2.5.3_linux_x64.deb
            
            # Extract files without installing
            echo "Extracting GPT4All CLI..."
            dpkg-deb -x /tmp/gpt4all.deb /tmp/gpt4all-extract
            cp /tmp/gpt4all-extract/usr/bin/gpt4all-cli "$GPT4ALL_DIR/"
            rm -rf /tmp/gpt4all-extract
            rm /tmp/gpt4all.deb
            
            chmod +x "$GPT4ALL_DIR/gpt4all-cli"
        else
            echo "Warning: Pre-built GPT4All binary not available for $ARCH."
            echo "You may need to build from source or use a different LLM backend."
        fi
    else
        echo "Warning: Pre-built GPT4All binary not available for $OS."
        echo "You may need to build from source or use a different LLM backend."
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

