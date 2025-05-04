# G3r4ki - AI-powered Linux system for cybersecurity operations
# Makefile for installation and management

.PHONY: all install install-deps setup-voice setup-llms clean update help

all: install

help:
	@echo "G3r4ki - AI-powered Linux system for cybersecurity operations"
	@echo ""
	@echo "Available targets:"
	@echo "  install      - Install everything (dependencies, voice processing, LLMs)"
	@echo "  install-deps - Install system dependencies"
	@echo "  setup-voice  - Set up Whisper (STT) and Piper (TTS)"
	@echo "  setup-llms   - Set up llama.cpp, vLLM, and GPT4All"
	@echo "  update       - Update G3r4ki components"
	@echo "  clean        - Clean temporary files"

install-deps:
	@echo "Installing system dependencies..."
	@bash ./scripts/install_deps.sh

setup-voice:
	@echo "Setting up voice components (Whisper and Piper)..."
	@bash ./scripts/setup_voice.sh

setup-llms:
	@echo "Setting up LLM components (llama.cpp, vLLM, GPT4All)..."
	@bash ./scripts/setup_llms.sh

install: install-deps setup-voice setup-llms
	@echo "Using existing Python virtual environment at ~/.g3r4ki_venv"
	@echo "Installing Python dependencies..."
	~/.g3r4ki_venv/bin/pip install -e .
	@echo ""
	@echo "G3r4ki installation complete!"
	@echo "Activate the virtual environment with: source ~/.g3r4ki_venv/bin/activate"
	@echo "Run G3r4ki with: python g3r4ki.py"

update:
	@echo "Updating G3r4ki components..."
	git pull
	.venv/bin/pip install -e .
	@echo "G3r4ki updated!"

clean:
	@echo "Cleaning temporary files..."
	rm -rf __pycache__
	rm -rf src/__pycache__
	find . -name "*.pyc" -delete

# Additional targets for separate environments for vLLM and llama.cpp

setup-vllm-env:
	@echo "Setting up separate Python virtual environment for vLLM with torch 2.7.0..."
	@bash -c "\
		if command -v pyenv &> /dev/null; then \
			pyenv install -s 3.12.0 && \
			pyenv virtualenv 3.12.0 g3r4ki-vllm && \
			pyenv activate g3r4ki-vllm && \
			pip install --upgrade pip && \
			pip install torch==2.7.0 vllm; \
		else \
			echo 'pyenv not found. Please install pyenv to use this target.'; \
			exit 1; \
		fi"

setup-llama-env:
	@echo "Setting up separate Python environment for llama.cpp with torch 2.5.0..."
	@bash -c "\
		python3 -m venv ~/.g3r4ki-llama-venv && \
		source ~/.g3r4ki-llama-venv/bin/activate && \
		pip install --upgrade pip && \
		pip install torch==2.5.0 protobuf==4.25.3; \
		deactivate"
