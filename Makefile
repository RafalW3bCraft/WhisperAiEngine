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
	@echo "Creating Python virtual environment..."
	python3 -m venv .venv
	@echo "Installing Python dependencies..."
	.venv/bin/pip install -e .
	@echo ""
	@echo "G3r4ki installation complete!"
	@echo "Activate the virtual environment with: source .venv/bin/activate"
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
