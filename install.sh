#!/bin/bash

# G3r4ki Installation Script
# This script installs the G3r4ki cybersecurity operations system
# and sets up all required dependencies.

set -e

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logo
display_logo() {
  echo -e "${BLUE}"
  echo "  __ _____  _ _   _    _ "
  echo " / _|__ / || | | | | _(_)"
  echo "| |_ |_ \| || |_| |/ / |"
  echo "|  _|__) |__   _|   <| |"
  echo "|_| |___/   |_| |_|\_\_|"
  echo -e "${NC}"
  echo "AI-powered cybersecurity operations"
  echo "Installation Script"
  echo "----------------------------------------"
}

# Check if running as root or with sudo
check_privileges() {
  if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Warning: Some installation steps require root privileges.${NC}"
    echo "Running without sudo. You may be prompted for your password later."
    SUDO="sudo"
  else
    SUDO=""
  fi
}

# Check system requirements
check_system() {
  echo -e "\n${BLUE}Checking system requirements...${NC}"
  
  # Check OS
  if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "Operating System: $PRETTY_NAME"
    
    # Check if running on Debian, Ubuntu, or Kali
    if [[ "$ID" != "debian" && "$ID" != "ubuntu" && "$ID" != "kali" ]]; then
      echo -e "${YELLOW}Warning: G3r4ki is designed for Debian-based systems (Debian, Ubuntu, Kali).${NC}"
      echo "Installation may not work correctly on $PRETTY_NAME."
      
      read -p "Continue anyway? (y/n) " -n 1 -r
      echo
      if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation aborted."
        exit 1
      fi
    fi
  else
    echo -e "${YELLOW}Warning: Could not determine OS type.${NC}"
  fi
  
  # Check Python version
  if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "Python version: $PYTHON_VERSION"
    
    # Convert version string to integers for comparison
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]); then
      echo -e "${YELLOW}Warning: G3r4ki requires Python 3.10 or newer.${NC}"
      echo "You have Python $PYTHON_VERSION."
      
      read -p "Continue anyway? (y/n) " -n 1 -r
      echo
      if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation aborted."
        exit 1
      fi
    fi
  else
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    echo "Please install Python 3.10 or newer before continuing."
    exit 1
  fi
  
  # Check disk space
  FREE_SPACE=$(df -h . | awk 'NR==2 {print $4}')
  echo "Free disk space: $FREE_SPACE"
  
  # Check memory
  if command -v free &>/dev/null; then
    TOTAL_MEM=$(free -h | awk '/^Mem:/ {print $2}')
    echo "Total memory: $TOTAL_MEM"
  fi
  
  echo -e "${GREEN}System check completed.${NC}"
}

# Install system dependencies
install_system_dependencies() {
  echo -e "\n${BLUE}Installing system dependencies...${NC}"
  
  PACKAGES=(
    "python3-pip"
    "python3-venv"
    "python3-dev"
    "postgresql"
    "postgresql-contrib"
    "libpq-dev"
    "build-essential"
    "git"
    "curl"
    "wget"
    "net-tools"
    "nmap"
    "netcat-openbsd"
  )
  
  # Update package lists
  echo "Updating package lists..."
  $SUDO apt-get update -qq
  
  # Install packages
  echo "Installing required packages..."
  $SUDO apt-get install -y "${PACKAGES[@]}"
  
  echo -e "${GREEN}System dependencies installed.${NC}"
}

# Set up PostgreSQL database
setup_database() {
  echo -e "\n${BLUE}Setting up PostgreSQL database...${NC}"
  
  # Check if PostgreSQL is running
  if ! $SUDO systemctl is-active --quiet postgresql; then
    echo "Starting PostgreSQL service..."
    $SUDO systemctl start postgresql
  fi
  
  # Create database user and database
  echo "Creating database user and database..."
  
  DB_USER="g3r4ki"
  DB_NAME="g3r4ki_db"
  
  # Generate a random password
  DB_PASSWORD=$(openssl rand -base64 12)
  
  # Check if user already exists
  if ! $SUDO -i -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
    echo "Creating PostgreSQL user '$DB_USER'..."
    $SUDO -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
  else
    echo "PostgreSQL user '$DB_USER' already exists."
    # Update password for existing user
    $SUDO -u postgres psql -c "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
  fi

  # Reload PostgreSQL to apply changes
  echo "Reloading PostgreSQL service to apply user password changes..."
  $SUDO systemctl reload postgresql
  
  # Check if database already exists
  if ! $SUDO -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1; then
    echo "Creating PostgreSQL database '$DB_NAME'..."
    $SUDO -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
  else
    echo "PostgreSQL database '$DB_NAME' already exists."
  fi
  
  # Create .env file with database connection info
  echo "Creating .env file with database connection information..."
  cat > .env << EOL
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME
# OPENAI_API_KEY=
# DEEPSEEK_API_KEY=
# ANTHROPIC_API_KEY=
EOL

  # Load environment variables from .env file
  export $(grep -v '^#' .env | xargs)
  
  echo -e "${GREEN}Database setup completed.${NC}"
  echo -e "Database credentials stored in ${YELLOW}.env${NC} file."
}

# Install Python dependencies
install_python_dependencies() {
  echo -e "\n${BLUE}Installing Python dependencies...${NC}"
  
  # Install or upgrade pip
  python3 -m pip install --upgrade pip
  
  # Install the package in development mode
  python3 -m pip install -e .
  
  echo -e "${GREEN}Python dependencies installed.${NC}"
}

# Initialize database schema
initialize_database() {
  echo -e "\n${BLUE}Initializing database schema...${NC}"
  
  # Create database tables
  python3 -m src.database.init_db
  
  echo -e "${GREEN}Database schema initialized.${NC}"
}

# Configure local AI (optional)
configure_local_ai() {
  echo -e "\n${BLUE}Configuring local AI capabilities...${NC}"
  
  read -p "Do you want to set up local AI capabilities? (requires additional disk space) (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    mkdir -p ~/.g3r4ki/models
    
    # Create local AI config
    cat > ~/.g3r4ki/local_ai_config.yaml << EOL
providers:
  llama.cpp:
    enabled: true
    models: []
    model_path: ~/.g3r4ki/models
  gpt4all:
    enabled: true
    models: []
    model_path: ~/.g3r4ki/models
  vllm:
    enabled: false
    models: []
    model_path: ~/.g3r4ki/models
settings:
  download_models: true
  use_local_first: false
  fallback_to_cloud: true
EOL
    
    echo -e "${GREEN}Local AI configuration created.${NC}"
    echo "You can download models by running: python g3r4ki.py setup local-ai --download-model"
  else
    echo "Skipping local AI setup."
  fi
}

# Finalize installation
finalize_installation() {
  echo -e "\n${BLUE}Finalizing installation...${NC}"
  
  # Make g3r4ki.py executable
  chmod +x g3r4ki.py
  
  # Create directory for logs and data
  mkdir -p ~/.g3r4ki/logs
  mkdir -p ~/.g3r4ki/data
  
  # Create symlink in /usr/local/bin if user wants
  read -p "Would you like to create a system-wide command for G3r4ki? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    $SUDO ln -sf "$(pwd)/g3r4ki.py" /usr/local/bin/g3r4ki
    echo -e "${GREEN}System-wide command created. You can now run 'g3r4ki' from anywhere.${NC}"
  fi
  
  echo -e "${GREEN}Installation completed successfully!${NC}"
}

# Display completion message
display_completion() {
  echo -e "\n${GREEN}=======================================${NC}"
  echo -e "${GREEN} G3r4ki installation completed!${NC}"
  echo -e "${GREEN}=======================================${NC}"
  echo
  echo -e "To start G3r4ki, run:"
  echo -e "${YELLOW}y${NC}"
  echo
  echo -e "Documentation is available at:"
  echo -e "${YELLOW}./docs/README.md${NC}"
  echo
  echo -e "For cloud AI capabilities, edit the ${YELLOW}.env${NC} file and add your API keys."
  echo
  echo -e "Thanks for installing G3r4ki!"
  echo -e "${BLUE}Happy hacking!${NC}"
  echo
}

# Main installation process
main() {
  display_logo
  check_privileges
  check_system
  install_system_dependencies
  setup_database
  install_python_dependencies
  initialize_database
  configure_local_ai
  finalize_installation
  display_completion
}

# Run the main installation process
main