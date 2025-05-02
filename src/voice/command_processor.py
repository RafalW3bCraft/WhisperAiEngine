#!/usr/bin/env python3
# G3r4ki Voice Command Processor

import os
import re
import logging
import time
import json
import threading
import queue
from pathlib import Path
from datetime import datetime
import shlex

from src.voice.whisper_stt import WhisperSTT
from src.voice.piper_tts import PiperTTS

logger = logging.getLogger('g3r4ki.voice.command')

class VoiceCommandProcessor:
    """Process voice commands into G3r4ki actions"""
    
    def __init__(self, config, cli_interface=None):
        """
        Initialize voice command processor
        
        Args:
            config: G3r4ki configuration
            cli_interface: Reference to CLI interface for executing commands
        """
        self.config = config
        self.cli_interface = cli_interface
        self.whisper = WhisperSTT(config)
        self.piper = PiperTTS(config)
        
        # Command patterns for recognition
        self.command_patterns = [
            # System commands
            (r'(show|display|view|get).*config(uration)?', 'config show'),
            (r'edit.*config(uration)?', 'config edit'),
            (r'reload.*config(uration)?', 'config reload'),
            (r'save.*config(uration)?', 'config save'),
            (r'(show|display|view|get).*system.*(info|information|details)', 'system info'),
            (r'check.*system.*requirements', 'system check'),
            (r'exit|quit|goodbye|bye', 'exit'),
            
            # Security commands
            (r'scan.*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[-a-zA-Z0-9.]+\.[a-zA-Z]{2,})', self._extract_scan_target),
            (r'recon.*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[-a-zA-Z0-9.]+\.[a-zA-Z]{2,})', self._extract_recon_target),
            (r'(vuln|vulnerability).*scan.*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[-a-zA-Z0-9.]+\.[a-zA-Z]{2,})', self._extract_vuln_target),
            
            # LLM commands
            (r'list.*(llm|language).*(models|engines)', 'llm list'),
            (r'(show|display|view|get).*(llm|language).*(models|engines)', 'llm list'),
            (r'(show|display|view|get).*(available)?.*(llm|language).*(engines)', 'llm engines'),
            (r'(ask|query|prompt).*(llm|language|model).*', self._extract_llm_query),
            
            # General help
            (r'help|assist|guide', 'help'),
            (r'help.*(with)?.*(command|function).*', self._extract_help_topic)
        ]
        
        # Command processing queue and thread
        self.command_queue = queue.Queue()
        self.processing_thread = None
        self.running = False
    
    def is_available(self):
        """Check if voice command processing is available"""
        # We need both speech-to-text and text-to-speech for voice commands
        return self.whisper.is_available() and self.piper.is_available()
    
    def start(self):
        """Start voice command processing in background thread"""
        if self.processing_thread is not None and self.processing_thread.is_alive():
            logger.warning("Voice command processor already running")
            return False
        
        # Check if required components are available
        if not self.is_available():
            logger.error("Voice command processing not available - missing components")
            return False
        
        self.running = True
        self.processing_thread = threading.Thread(target=self._command_loop, daemon=True)
        self.processing_thread.start()
        
        logger.info("Voice command processor started")
        return True
    
    def stop(self):
        """Stop voice command processing"""
        if self.processing_thread is None or not self.processing_thread.is_alive():
            logger.warning("Voice command processor not running")
            return
        
        self.running = False
        self.processing_thread.join(timeout=2.0)
        logger.info("Voice command processor stopped")
    
    def process_audio_file(self, audio_file):
        """
        Process voice command from audio file
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Tuple of (command, response, success)
        """
        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return None, "Audio file not found", False
        
        # Transcribe audio file to text
        text = self.whisper.transcribe(audio_file)
        if not text or text.startswith("Error:"):
            logger.error(f"Failed to transcribe audio: {text}")
            return None, f"Failed to transcribe audio: {text}", False
        
        # Process the text command
        return self.process_text_command(text)
    
    def process_mic_input(self, duration=5):
        """
        Record from microphone and process voice command
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Tuple of (command, response, success)
        """
        # Record from microphone
        text = self.whisper.transcribe_microphone(duration)
        if not text or text.startswith("Error:"):
            logger.error(f"Failed to transcribe audio: {text}")
            return None, f"Failed to transcribe audio: {text}", False
        
        # Process the text command
        return self.process_text_command(text)
    
    def process_text_command(self, text):
        """
        Process text command and execute corresponding G3r4ki actions
        
        Args:
            text: Command text
            
        Returns:
            Tuple of (command, response, success)
        """
        logger.info(f"Processing command: '{text}'")
        
        # Match command against patterns
        cli_command = self._match_command_pattern(text)
        if not cli_command:
            logger.warning(f"Unable to match command: '{text}'")
            return text, "Sorry, I didn't understand that command.", False
        
        # Execute command if CLI interface is available
        if self.cli_interface is not None:
            logger.info(f"Executing CLI command: '{cli_command}'")
            response = self._execute_cli_command(cli_command)
            return text, response, True
        else:
            logger.warning("CLI interface not available for executing command")
            return text, "Voice command processor is not connected to the CLI interface.", False
    
    def speak_response(self, response, block=True):
        """
        Speak the response using text-to-speech
        
        Args:
            response: Response text to speak
            block: Whether to block until speech is complete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.piper.is_available():
            logger.error("Text-to-speech not available")
            return False
        
        # Truncate long responses
        if len(response) > 1000:
            response = response[:1000] + "... Response truncated for speech."
        
        try:
            if block:
                return self.piper.speak(response)
            else:
                threading.Thread(target=self.piper.speak, args=(response,), daemon=True).start()
                return True
        except Exception as e:
            logger.error(f"Failed to speak response: {e}")
            return False
    
    def queue_voice_command(self, command_type, command_data=None):
        """
        Queue a voice command for processing
        
        Args:
            command_type: Type of command ('file', 'mic', 'text')
            command_data: Command data (file path or text)
            
        Returns:
            True if command was queued, False otherwise
        """
        if not self.running:
            logger.warning("Voice command processor not running")
            return False
        
        self.command_queue.put((command_type, command_data))
        return True
    
    def _command_loop(self):
        """Background thread for processing voice commands"""
        logger.info("Voice command loop started")
        
        while self.running:
            try:
                # Check if there are any commands in the queue (non-blocking)
                try:
                    command_type, command_data = self.command_queue.get(block=True, timeout=0.5)
                except queue.Empty:
                    continue
                
                # Process command based on type
                if command_type == 'file' and command_data:
                    _, response, _ = self.process_audio_file(command_data)
                    self.speak_response(response, block=False)
                
                elif command_type == 'mic':
                    _, response, _ = self.process_mic_input(duration=5 if not command_data else command_data)
                    self.speak_response(response, block=False)
                
                elif command_type == 'text' and command_data:
                    _, response, _ = self.process_text_command(command_data)
                    self.speak_response(response, block=False)
                
                else:
                    logger.warning(f"Unknown command type: {command_type}")
                
                # Mark task as done
                self.command_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in voice command loop: {e}")
                time.sleep(1)  # Avoid tight loops on errors
        
        logger.info("Voice command loop ended")
    
    def _match_command_pattern(self, text):
        """
        Match text against command patterns
        
        Args:
            text: Text to match
            
        Returns:
            CLI command string or None if no match
        """
        text = text.lower().strip()
        
        # Try to match each pattern
        for pattern, command in self.command_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # If command is a function, call it with the match object
                if callable(command):
                    return command(match, text)
                else:
                    return command
        
        # No match found
        return None
    
    def _execute_cli_command(self, command):
        """
        Execute command on CLI interface
        
        Args:
            command: CLI command string
            
        Returns:
            Command output
        """
        if not self.cli_interface:
            return "CLI interface not available"
        
        # Split the command into method name and arguments
        parts = shlex.split(command)
        method_name = f"do_{parts[0]}"
        args = ' '.join(parts[1:]) if len(parts) > 1 else ""
        
        # Check if the method exists
        if not hasattr(self.cli_interface, method_name):
            return f"Unknown command: {parts[0]}"
        
        # Redirect stdout to capture output
        import io
        import sys
        original_stdout = sys.stdout
        captured_output = io.StringIO()
        
        try:
            sys.stdout = captured_output
            
            # Execute the command
            method = getattr(self.cli_interface, method_name)
            method(args)
            
            # Get the captured output
            output = captured_output.getvalue()
            return output if output else "Command executed successfully"
            
        except Exception as e:
            return f"Error executing command: {str(e)}"
            
        finally:
            sys.stdout = original_stdout
    
    # Command extraction functions
    def _extract_scan_target(self, match, text):
        """Extract scan target from command text"""
        # Find IP address or domain in the text
        ip_regex = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        domain_regex = r'[-a-zA-Z0-9.]+\.[a-zA-Z]{2,}'
        
        ip_match = re.search(ip_regex, text)
        domain_match = re.search(domain_regex, text)
        
        if ip_match:
            return f"scan {ip_match.group(0)}"
        elif domain_match:
            return f"scan {domain_match.group(0)}"
        else:
            return "scan"
    
    def _extract_recon_target(self, match, text):
        """Extract reconnaissance target from command text"""
        ip_regex = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        domain_regex = r'[-a-zA-Z0-9.]+\.[a-zA-Z]{2,}'
        
        ip_match = re.search(ip_regex, text)
        domain_match = re.search(domain_regex, text)
        
        if domain_match:
            return f"recon {domain_match.group(0)}"
        elif ip_match:
            return f"recon {ip_match.group(0)}"
        else:
            return "recon"
    
    def _extract_vuln_target(self, match, text):
        """Extract vulnerability scan target from command text"""
        ip_regex = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        domain_regex = r'[-a-zA-Z0-9.]+\.[a-zA-Z]{2,}'
        
        ip_match = re.search(ip_regex, text)
        domain_match = re.search(domain_regex, text)
        
        if domain_match:
            return f"vuln {domain_match.group(0)}"
        elif ip_match:
            return f"vuln {ip_match.group(0)}"
        else:
            return "vuln"
    
    def _extract_llm_query(self, match, text):
        """Extract LLM query from command text"""
        # Try to find the query part after keywords like ask, query, prompt
        query_patterns = [
            r'(ask|query|prompt).*(llm|language|model)[^\w]+(.*)',
            r'(ask|query|prompt)[^\w]+(.*)',
        ]
        
        for pattern in query_patterns:
            query_match = re.search(pattern, text, re.IGNORECASE)
            if query_match and len(query_match.groups()) >= 1:
                # Get the last group which should contain the query
                query = query_match.group(len(query_match.groups()))
                if query and len(query) > 2:
                    return f"llm query {query}"
        
        # Fallback: use everything after "llm" as the query
        if "llm" in text:
            query = text.split("llm", 1)[1].strip()
            if query:
                return f"llm query {query}"
        
        return "llm query"
    
    def _extract_help_topic(self, match, text):
        """Extract help topic from command text"""
        topics = ["config", "system", "scan", "recon", "vuln", "llm", "voice"]
        
        for topic in topics:
            if topic in text:
                return f"help {topic}"
        
        return "help"