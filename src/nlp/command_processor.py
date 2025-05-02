"""
Command Processor for G3r4ki's natural language processing.

This module provides the main interface for processing natural language
commands and converting them to executable G3r4ki commands.
"""

import logging
import re
import os
import json
from typing import Dict, Any, List, Tuple, Optional, Union, Callable

from src.config import load_config
from src.nlp.nlp_utils import parse_command, determine_intent, extract_entities
from src.nlp.reasoning_engine import ReasoningEngine

logger = logging.getLogger(__name__)

class CommandProcessor:
    """
    Natural language command processor for G3r4ki.
    
    This class handles the processing of natural language commands,
    converting them to executable G3r4ki commands using NLP techniques
    and AI-based reasoning.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the command processor.
        
        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or load_config()
        self.reasoning_engine = ReasoningEngine(config=self.config)
        
        # Command execution functions
        self.command_handlers = {}
        self.intent_handlers = {}
        
        # Command history
        self.command_history = []
        self.max_history = self.config.get('nlp', {}).get('max_history', 100)
        
        # Load command history if available
        self._load_history()
    
    def _load_history(self):
        """Load command history from file."""
        history_file = os.path.expanduser("~/.g3r4ki/command_history.json")
        try:
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    try:
                        self.command_history = json.load(f)
                        # Trim to max history size
                        if len(self.command_history) > self.max_history:
                            self.command_history = self.command_history[-self.max_history:]
                    except json.JSONDecodeError as e:
                        logger.error(f"Corrupted command history: {e}")
                        # Backup the corrupted file
                        backup_file = f"{history_file}.backup"
                        try:
                            import shutil
                            shutil.copy2(history_file, backup_file)
                            logger.info(f"Backed up corrupted history to {backup_file}")
                        except Exception as be:
                            logger.error(f"Failed to backup corrupted history: {be}")
                        # Initialize with empty history
                        self.command_history = []
        except Exception as e:
            logger.error(f"Error loading command history: {e}")
            self.command_history = []
    
    def _save_history(self):
        """Save command history to file."""
        history_file = os.path.expanduser("~/.g3r4ki/command_history.json")
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(history_file), exist_ok=True)
            
            # Safety check - if history is too large, truncate it
            if len(self.command_history) > self.max_history * 2:
                logger.warning(f"Command history too large ({len(self.command_history)} items), truncating")
                self.command_history = self.command_history[-self.max_history:]
            
            # Validate each history item to prevent corruption
            validated_history = []
            for item in self.command_history:
                if not isinstance(item, dict):
                    logger.warning(f"Invalid history item (not a dict): {item}")
                    continue
                    
                # Make sure the item has required fields
                if 'input' not in item:
                    logger.warning(f"Invalid history item (missing input): {item}")
                    continue
                    
                # Make sure the result field is valid
                if 'result' not in item:
                    item['result'] = {'success': False, 'message': 'No result data'}
                    
                validated_history.append(item)
                
            # Use a temporary file first to prevent corruption
            temp_file = f"{history_file}.temp"
            with open(temp_file, 'w') as f:
                json.dump(validated_history, f)
                
            # Rename temp file to actual file
            # os is already imported at the top of the file
            os.replace(temp_file, history_file)
            
            # Update the history with validated items
            self.command_history = validated_history
        except Exception as e:
            logger.error(f"Error saving command history: {e}")
    
    def register_command_handler(self, command: str, handler: Callable):
        """
        Register a handler function for a specific command.
        
        Args:
            command: The command string
            handler: The handler function that executes the command
        """
        self.command_handlers[command] = handler
    
    def register_intent_handler(self, intent: str, handler: Callable):
        """
        Register a handler function for a specific intent.
        
        Args:
            intent: The intent string
            handler: The handler function that processes the intent
        """
        self.intent_handlers[intent] = handler
    
    def process(self, command_text: str, use_ai: bool = True) -> Dict[str, Any]:
        """
        Process a natural language command.
        
        Args:
            command_text: The natural language command text
            use_ai: Whether to use AI for command understanding
            
        Returns:
            Dictionary with processing results
        """
        # Check if it's a direct command first
        direct_command = self._check_direct_command(command_text)
        if direct_command:
            result = {
                'type': 'direct',
                'command': direct_command,
                'success': True,
                'message': f"Executing command: {direct_command}"
            }
            
            # Add to history
            self.command_history.append({
                'input': command_text,
                'result': result
            })
            self._save_history()
            
            return result
        
        # Process as natural language
        parsed = parse_command(command_text)
        
        # Determine intent using rule-based approach
        rule_intent = determine_intent(command_text, parsed)
        
        # If intent is unknown or AI is requested, use AI reasoning
        final_intent = rule_intent
        entities = {}
        reasoning = ""
        
        if rule_intent == 'unknown' or use_ai:
            try:
                # Use AI reasoning to understand the command
                understanding = self.reasoning_engine.understand_command(command_text, parsed)
                
                # Extract results
                ai_intent = understanding.get('intent', 'unknown')
                confidence = understanding.get('confidence', 0.0)
                ai_entities = understanding.get('entities', {})
                reasoning = understanding.get('reasoning', "")
                
                # Use AI results if confidence is high enough or rule-based intent is unknown
                if rule_intent == 'unknown' or confidence >= 0.7:
                    final_intent = ai_intent
                    entities = ai_entities
                else:
                    # Extract entities using rule-based approach
                    entities = extract_entities(command_text, rule_intent, parsed)
            except Exception as e:
                logger.error(f"Error using AI reasoning: {e}")
                # Fall back to rule-based approach
                final_intent = rule_intent
                entities = extract_entities(command_text, rule_intent, parsed)
        else:
            # Extract entities using rule-based approach
            entities = extract_entities(command_text, rule_intent, parsed)
        
        # Check if we have missing required entities
        missing_entities = self._check_missing_entities(final_intent, entities)
        
        if missing_entities:
            try:
                # Try to resolve missing entities using AI
                resolved = self.reasoning_engine.resolve_entities(
                    command_text, final_intent, entities, missing_entities
                )
                
                resolved_entities = resolved.get('resolved_entities', {})
                confidence = resolved.get('confidence', 0.0)
                
                # Only use resolved entities if confidence is high enough
                if confidence >= 0.6:
                    for key, value in resolved_entities.items():
                        if key in missing_entities:
                            entities[key] = value
            except Exception as e:
                logger.error(f"Error resolving entities: {e}")
        
        # Translate to executable command
        g3r4ki_command = self.reasoning_engine.translate_to_command(final_intent, entities)
        
        # Create result
        result = {
            'type': 'nlp',
            'input': command_text,
            'parsed': parsed,
            'intent': final_intent,
            'entities': entities,
            'command': g3r4ki_command,
            'reasoning': reasoning,
            'success': bool(g3r4ki_command),
            'message': f"Translated to: {g3r4ki_command}" if g3r4ki_command else "Could not understand command"
        }
        
        # Add to history
        self.command_history.append({
            'input': command_text,
            'result': result
        })
        self._save_history()
        
        return result
    
    def _check_direct_command(self, command_text: str) -> str:
        """
        Check if the text is a direct G3r4ki command or a simple natural language variant.
        
        Args:
            command_text: The command text
            
        Returns:
            The direct command if it matches, empty string otherwise
        """
        # Handle edge cases with malformed input
        if not command_text or not isinstance(command_text, str):
            logger.warning(f"Invalid input to _check_direct_command: {command_text}")
            return ""
            
        # Sanitize input - remove quotes and excess whitespace that might cause issues
        if isinstance(command_text, str):
            command_text = command_text.strip().strip('"\'').strip()
            
        # Check for JSON format errors that might be leaking through
        if isinstance(command_text, str) and ('"intent"' in command_text or (command_text.startswith('{') and command_text.endswith('}'))):
            logger.warning(f"Detected potential AI response format in command text: {command_text[:30]}...")
            return ""
            
        # Strip whitespace and lower case
        command = command_text.strip().lower()
        
        # Special handling for specific natural language commands to avoid AI parsing
        # This gives us a fallback mechanism when the reasoning engine fails
        nl_command_mappings = {
            "scan example.com": "scan example.com",
            "scan example": "scan example.com",
            "run a scan on example.com": "scan example.com",
            "scan the website example.com": "scan example.com",
            "check example.com for vulnerabilities": "vuln example.com",
            "search for vulnerabilities on example.com": "vuln example.com",
            "help me": "help",
            "show help": "help",
            "show commands": "help",
            "what commands are available": "help",
            "exit program": "exit",
            "quit the program": "exit",
            "recon example.com": "recon example.com",
            "reconnaissance on example.com": "recon example.com",
            "gather information about example.com": "recon example.com",
        }
        
        # Check for direct natural language matches first
        if command in nl_command_mappings:
            return nl_command_mappings[command]
            
        # Check for partial natural language matches (case insensitive)
        for nl_cmd, direct_cmd in nl_command_mappings.items():
            # Use fuzzy matching for common command variations
            if (nl_cmd in command) or (command in nl_cmd):
                # Only return if it's a close match (to avoid false positives)
                similarity = len(set(command.split()) & set(nl_cmd.split())) / max(len(command.split()), len(nl_cmd.split()))
                if similarity > 0.6:  # Threshold for similarity
                    return direct_cmd
        
        # Check if it's a simple command (e.g., help, exit, scan)
        simple_commands = [
            'help', 'exit', 'quit', 'config', 'system', 'scan',
            'recon', 'vuln', 'tools', 'llm list', 'llm engines'
        ]
        for simple_cmd in simple_commands:
            if command == simple_cmd.lower():
                return simple_cmd
        
        # Check for command patterns with arguments
        cmd_patterns = [
            (r'^scan\s+([^\s]+)(\s+.*)?$', lambda m: f"scan {m.group(1)}{m.group(2) or ''}"),
            (r'^recon\s+([^\s]+)(\s+.*)?$', lambda m: f"recon {m.group(1)}{m.group(2) or ''}"),
            (r'^vuln\s+([^\s]+)(\s+.*)?$', lambda m: f"vuln {m.group(1)}{m.group(2) or ''}"),
            (r'^tools\s+(list|install|scan|info)(\s+.*)?$', lambda m: f"tools {m.group(1)}{m.group(2) or ''}"),
            (r'^llm\s+(list|engines|query)(\s+.*)?$', lambda m: f"llm {m.group(1)}{m.group(2) or ''}"),
            (r'^exploit\s+webshell\s+(list|generate)(\s+.*)?$', lambda m: f"exploit webshell {m.group(1)}{m.group(2) or ''}"),
            (r'^exploit\s+privesc\s+(scan|exploit)(\s+.*)?$', lambda m: f"exploit privesc {m.group(1)}{m.group(2) or ''}"),
        ]
        
        for pattern, formatter in cmd_patterns:
            match = re.match(pattern, command, re.IGNORECASE)
            if match:
                return formatter(match)
        
        return ""
    
    def _check_missing_entities(self, intent: str, entities: Dict[str, Any]) -> List[str]:
        """
        Check if required entities are missing for a given intent.
        
        Args:
            intent: The command intent
            entities: The extracted entities
            
        Returns:
            List of missing required entity names
        """
        missing = []
        
        # Required entities for each intent
        required_entities = {
            'scan': ['target'],
            'recon': ['target'],
            'vuln_scan': ['target'],
            'llm': ['query'],
            'webshell': ['shell_type'],
            'tools': ['subcommand']
        }
        
        # Check if all required entities are present
        if intent in required_entities:
            for entity in required_entities[intent]:
                if entity not in entities:
                    missing.append(entity)
        
        return missing
    
    def execute(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a processed command.
        
        Args:
            result: The processing result from process()
            
        Returns:
            Dictionary with execution results
        """
        command = result.get('command', '')
        if not command:
            return {
                'success': False,
                'message': "No executable command found"
            }
        
        # Check if we have a direct handler for this command
        for cmd_prefix, handler in self.command_handlers.items():
            if command.startswith(cmd_prefix):
                try:
                    handler_result = handler(command)
                    return {
                        'success': True,
                        'result': handler_result,
                        'message': f"Executed: {command}"
                    }
                except Exception as e:
                    logger.error(f"Error executing command handler: {e}")
                    return {
                        'success': False,
                        'error': str(e),
                        'message': f"Error executing: {command}"
                    }
        
        # Check if we have a handler for the intent
        intent = result.get('intent', 'unknown')
        if intent in self.intent_handlers:
            try:
                entities = result.get('entities', {})
                handler_result = self.intent_handlers[intent](entities)
                return {
                    'success': True,
                    'result': handler_result,
                    'message': f"Executed intent: {intent}"
                }
            except Exception as e:
                logger.error(f"Error executing intent handler: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'message': f"Error executing intent: {intent}"
                }
        
        # No handler found
        return {
            'success': False,
            'message': f"No handler found for: {command}"
        }
    
    def get_suggestions(self, input_text: str, max_suggestions: int = 5) -> List[str]:
        """
        Get command suggestions based on input text.
        
        Args:
            input_text: The partial input text
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of command suggestions
        """
        suggestions = []
        
        # Check recent history for similar commands
        for history_item in reversed(self.command_history):
            if len(suggestions) >= max_suggestions:
                break
                
            hist_input = history_item.get('input', '')
            if hist_input.lower().startswith(input_text.lower()) and hist_input not in suggestions:
                suggestions.append(hist_input)
        
        # Add common command templates
        templates = [
            "scan [target]",
            "recon [target]",
            "vuln [target]",
            "llm query [question]",
            "tools list",
            "exploit webshell generate [type]"
        ]
        
        for template in templates:
            if len(suggestions) >= max_suggestions:
                break
                
            if template.lower().startswith(input_text.lower()) and template not in suggestions:
                suggestions.append(template)
        
        return suggestions
    
    def process_and_execute(self, command_text: str, use_ai: bool = True) -> Dict[str, Any]:
        """
        Process and execute a natural language command.
        
        Args:
            command_text: The natural language command text
            use_ai: Whether to use AI for command understanding
            
        Returns:
            Dictionary with execution results
        """
        process_result = self.process(command_text, use_ai)
        if process_result.get('success', False):
            execution_result = self.execute(process_result)
            
            # Combine results
            return {
                **process_result,
                'execution': execution_result
            }
        else:
            return {
                **process_result,
                'execution': {
                    'success': False,
                    'message': "Processing failed, command not executed"
                }
            }
    
    def get_history(self, max_items: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get command history.
        
        Args:
            max_items: Maximum number of history items to return
            
        Returns:
            List of history items
        """
        if max_items is None:
            return self.command_history
        else:
            return self.command_history[-max_items:]
    
    def clear_history(self) -> bool:
        """
        Clear command history.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.command_history = []
            self._save_history()
            return True
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return False