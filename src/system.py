#!/usr/bin/env python3
# G3r4ki system utilities and requirements checking

import os
import sys
import platform
import subprocess
import shutil
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('g3r4ki.system')

def check_command(command):
    """Check if a command is available"""
    return shutil.which(command) is not None

def run_command(command, shell=False):
    """Run a command and return its output"""
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=True, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            result = subprocess.run(command.split(), check=True, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {command}")
        logger.error(f"Error: {e.stderr.decode('utf-8')}")
        return None

def check_gpu():
    """Check for NVIDIA GPU and CUDA availability"""
    has_gpu = False
    cuda_version = None
    
    # Check for nvidia-smi
    if check_command("nvidia-smi"):
        try:
            # Run nvidia-smi to get GPU info
            gpu_info = run_command("nvidia-smi --query-gpu=name,driver_version --format=csv,noheader")
            if gpu_info:
                has_gpu = True
                logger.info(f"NVIDIA GPU detected: {gpu_info}")
                
                # Check CUDA version
                nvcc_check = run_command("nvcc --version")
                if nvcc_check:
                    for line in nvcc_check.split('\n'):
                        if "release" in line.lower():
                            cuda_version = line.split("release")[1].strip().split(",")[0]
                            logger.info(f"CUDA version: {cuda_version}")
        except Exception as e:
            logger.warning(f"Error checking GPU: {e}")
    
    return has_gpu, cuda_version

def check_system_requirements():
    """Check if the system meets requirements for G3r4ki"""
    logger.info("Checking system requirements...")
    
    # OS check
    os_name = platform.system()
    if os_name != "Linux":
        logger.warning(f"Unsupported OS: {os_name}. G3r4ki is designed for Linux.")
    
    distro = platform.freedesktop_os_release()["NAME"] if hasattr(platform, "freedesktop_os_release") else "Unknown"
    logger.info(f"OS: {distro}")
    
    # Check Python version
    python_version = platform.python_version()
    logger.info(f"Python version: {python_version}")
    if int(python_version.split('.')[0]) < 3 or (int(python_version.split('.')[0]) == 3 and int(python_version.split('.')[1]) < 8):
        logger.warning("Python 3.8+ is recommended")
    
    # Check essential commands
    essential_commands = [
        "git", "cmake", "make", "gcc", "g++", "python3", 
        "pip", "wget", "curl", "tar", "unzip"
    ]
    
    missing_commands = []
    for cmd in essential_commands:
        if not check_command(cmd):
            missing_commands.append(cmd)
    
    if missing_commands:
        logger.warning(f"Missing essential commands: {', '.join(missing_commands)}")
        logger.warning("Install missing packages with: sudo apt install build-essential cmake python3-pip curl wget git")
    else:
        logger.info("All essential commands are available")
    
    # Check for security tools
    security_tools = ["nmap", "amass", "gobuster", "nikto", "sqlmap", "ffuf"]
    
    available_tools = []
    missing_tools = []
    
    for tool in security_tools:
        if check_command(tool):
            available_tools.append(tool)
        else:
            missing_tools.append(tool)
    
    if available_tools:
        logger.info(f"Available security tools: {', '.join(available_tools)}")
    
    if missing_tools:
        logger.warning(f"Missing security tools: {', '.join(missing_tools)}")
        if distro.lower() in ["kali", "kali linux", "kali gnu/linux"]:
            logger.info("On Kali Linux, install missing tools with: sudo apt install kali-tools-information-gathering kali-tools-vulnerability")
        else:
            logger.info("Install missing tools from package manager or consider using Kali Linux")
    
    # Check GPU availability
    has_gpu, cuda_version = check_gpu()
    
    if has_gpu:
        logger.info("NVIDIA GPU is available")
        if cuda_version:
            logger.info(f"CUDA version: {cuda_version}")
        else:
            logger.warning("CUDA not detected or version could not be determined")
    else:
        logger.warning("NVIDIA GPU not detected. Performance will be limited for LLM operations.")
    
    # Check memory
    try:
        mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
        mem_gib = mem_bytes/(1024.**3)
        logger.info(f"System memory: {mem_gib:.1f} GiB")
        
        if mem_gib < 8:
            logger.warning("Less than 8 GiB RAM detected. This may be insufficient for running larger models.")
        elif mem_gib < 16:
            logger.info("8-16 GiB RAM detected. Sufficient for smaller models only.")
        else:
            logger.info("16+ GiB RAM detected. Sufficient for most operations.")
    except:
        logger.warning("Could not determine system memory")
    
    # Check disk space
    try:
        disk = os.statvfs(os.path.expanduser("~"))
        free_space_bytes = disk.f_bavail * disk.f_frsize
        free_space_gib = free_space_bytes / (1024**3)
        
        logger.info(f"Free disk space: {free_space_gib:.1f} GiB")
        
        if free_space_gib < 10:
            logger.warning("Less than 10 GiB free space detected. This may be insufficient for LLM models.")
        elif free_space_gib < 20:
            logger.info("10-20 GiB free space detected. Sufficient for smaller models only.")
        else:
            logger.info("20+ GiB free space detected. Sufficient for most operations.")
    except:
        logger.warning("Could not determine free disk space")
    
    return True

def setup_environment():
    """Setup the G3r4ki environment"""
    from src.config import CONFIG_DIR, MODELS_DIR, TEMP_DIR, setup_config
    
    # Create necessary directories
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Ensure configuration exists
    config = setup_config()
    
    return config

def get_hardware_info():
    """Get system hardware information"""
    hw_info = {
        "cpu": {
            "cores": os.cpu_count(),
            "model": "Unknown"
        },
        "memory": {
            "total_gb": 0
        },
        "gpu": {
            "available": False,
            "model": "None",
            "cuda_version": None
        }
    }
    
    # Get CPU info
    try:
        if os.path.exists('/proc/cpuinfo'):
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('model name'):
                        hw_info["cpu"]["model"] = line.split(':')[1].strip()
                        break
    except:
        pass
    
    # Get memory info
    try:
        mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
        hw_info["memory"]["total_gb"] = round(mem_bytes/(1024.**3), 1)
    except:
        pass
    
    # Get GPU info
    has_gpu, cuda_version = check_gpu()
    hw_info["gpu"]["available"] = has_gpu
    hw_info["gpu"]["cuda_version"] = cuda_version
    
    if has_gpu:
        try:
            gpu_info = run_command("nvidia-smi --query-gpu=name --format=csv,noheader")
            if gpu_info:
                hw_info["gpu"]["model"] = gpu_info
        except:
            pass
    
    return hw_info
