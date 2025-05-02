#!/usr/bin/env python3
# G3r4ki Self-Improvement Module

import os
import sys
import json
import time
import hashlib
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import subprocess
import shutil

logger = logging.getLogger('g3r4ki.enhancement')

class SelfImprovementManager:
    """
    Self-Improvement Manager
    
    This class provides capabilities for G3r4ki to adapt and improve itself
    based on usage patterns, feedback, and self-analysis.
    
    Features:
    - Command usage tracking and optimization
    - Performance monitoring and enhancement
    - Self-diagnosis and repair
    - Automatic updates for components when online
    - Learning from successful operations
    - Configuration optimization
    """
    
    def __init__(self, config):
        """
        Initialize the self-improvement manager
        
        Args:
            config: G3r4ki configuration
        """
        self.config = config
        
        # Ensure config contains necessary paths
        if 'paths' not in config:
            config['paths'] = {}
        
        # Set data directory using existing paths or create defaults
        if 'data_dir' not in config['paths']:
            # If config doesn't have data_dir, create one
            if 'config_dir' in config['paths']:
                base_dir = os.path.dirname(config['paths']['config_dir'])
                config['paths']['data_dir'] = os.path.join(base_dir, '.local/share/g3r4ki')
            else:
                # Ultimate fallback
                config['paths']['data_dir'] = os.path.expanduser('~/.local/share/g3r4ki')
        
        # Setup directory structure
        self.data_dir = os.path.join(config['paths']['data_dir'], 'enhancement')
        self.usage_data_file = os.path.join(self.data_dir, 'usage_data.json')
        self.performance_file = os.path.join(self.data_dir, 'performance_metrics.json')
        self.learning_file = os.path.join(self.data_dir, 'learned_patterns.json')
        
        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data files if they don't exist
        self._init_data_files()
        
        # Set up improvement schedule
        self.last_improvement_time = self._get_last_improvement_time()
        
        # Performance thresholds for triggering improvements
        self.performance_thresholds = {
            'response_time': 5.0,  # seconds
            'memory_usage': 500,   # MB
            'error_rate': 0.05     # 5% error rate
        }
        
        logger.info("Self-improvement manager initialized")
    
    def _init_data_files(self):
        """Initialize data files if they don't exist"""
        # Usage data
        if not os.path.exists(self.usage_data_file):
            with open(self.usage_data_file, 'w') as f:
                json.dump({
                    'commands': {},
                    'total_sessions': 0,
                    'last_update': time.time()
                }, f)
        
        # Performance metrics
        if not os.path.exists(self.performance_file):
            with open(self.performance_file, 'w') as f:
                json.dump({
                    'response_times': [],
                    'memory_usage': [],
                    'error_rates': [],
                    'last_update': time.time()
                }, f)
        
        # Learning data
        if not os.path.exists(self.learning_file):
            with open(self.learning_file, 'w') as f:
                json.dump({
                    'learned_patterns': {},
                    'successful_workflows': [],
                    'optimized_configs': {},
                    'last_update': time.time()
                }, f)
    
    def _get_last_improvement_time(self) -> float:
        """Get the timestamp of the last self-improvement run"""
        timestamp_file = os.path.join(self.data_dir, 'last_improvement.txt')
        
        if os.path.exists(timestamp_file):
            with open(timestamp_file, 'r') as f:
                try:
                    return float(f.read().strip())
                except:
                    return 0
        
        return 0
    
    def _update_last_improvement_time(self):
        """Update the timestamp of the last self-improvement run"""
        timestamp_file = os.path.join(self.data_dir, 'last_improvement.txt')
        
        with open(timestamp_file, 'w') as f:
            f.write(str(time.time()))
        
        self.last_improvement_time = time.time()
    
    def record_command_usage(self, command: str, success: bool, duration: float):
        """
        Record command usage statistics
        
        Args:
            command: Command executed
            success: Whether the command executed successfully
            duration: Execution duration in seconds
        """
        try:
            with open(self.usage_data_file, 'r') as f:
                usage_data = json.load(f)
            
            if command not in usage_data['commands']:
                usage_data['commands'][command] = {
                    'count': 0,
                    'success_count': 0,
                    'total_duration': 0,
                    'last_used': time.time()
                }
            
            usage_data['commands'][command]['count'] += 1
            if success:
                usage_data['commands'][command]['success_count'] += 1
            usage_data['commands'][command]['total_duration'] += duration
            usage_data['commands'][command]['last_used'] = time.time()
            usage_data['last_update'] = time.time()
            
            with open(self.usage_data_file, 'w') as f:
                json.dump(usage_data, f)
                
        except Exception as e:
            logger.error(f"Error recording command usage: {e}")
    
    def record_performance_metrics(self, response_time: float, memory_usage: float):
        """
        Record system performance metrics
        
        Args:
            response_time: Response time in seconds
            memory_usage: Memory usage in MB
        """
        try:
            with open(self.performance_file, 'r') as f:
                performance_data = json.load(f)
            
            # Add new metrics
            performance_data['response_times'].append({
                'value': response_time,
                'timestamp': time.time()
            })
            
            performance_data['memory_usage'].append({
                'value': memory_usage,
                'timestamp': time.time()
            })
            
            # Limit history to last 1000 entries
            if len(performance_data['response_times']) > 1000:
                performance_data['response_times'] = performance_data['response_times'][-1000:]
            
            if len(performance_data['memory_usage']) > 1000:
                performance_data['memory_usage'] = performance_data['memory_usage'][-1000:]
            
            performance_data['last_update'] = time.time()
            
            with open(self.performance_file, 'w') as f:
                json.dump(performance_data, f)
                
        except Exception as e:
            logger.error(f"Error recording performance metrics: {e}")
    
    def record_error(self, component: str, error_message: str, context: Optional[Dict[str, Any]] = None):
        """
        Record error occurrence for tracking and analysis
        
        Args:
            component: Component where error occurred
            error_message: Error message
            context: Additional context about the error
        """
        try:
            error_file = os.path.join(self.data_dir, 'errors.json')
            
            if os.path.exists(error_file):
                with open(error_file, 'r') as f:
                    error_data = json.load(f)
            else:
                error_data = {
                    'errors': [],
                    'total_count': 0,
                    'last_update': time.time()
                }
            
            # Add new error
            error_data['errors'].append({
                'component': component,
                'message': error_message,
                'context': context or {},
                'timestamp': time.time()
            })
            
            error_data['total_count'] += 1
            error_data['last_update'] = time.time()
            
            # Limit history to last 1000 entries
            if len(error_data['errors']) > 1000:
                error_data['errors'] = error_data['errors'][-1000:]
            
            with open(error_file, 'w') as f:
                json.dump(error_data, f)
                
        except Exception as e:
            logger.error(f"Error recording error data: {e}")
    
    def learn_from_successful_operation(self, operation_type: str, details: Dict[str, Any], outcome: Dict[str, Any]):
        """
        Learn from successful operations to improve future performance
        
        Args:
            operation_type: Type of operation (scan, exploit, etc.)
            details: Operation details
            outcome: Operation outcome
        """
        try:
            with open(self.learning_file, 'r') as f:
                learning_data = json.load(f)
            
            # Add to successful workflows
            learning_data['successful_workflows'].append({
                'type': operation_type,
                'details': details,
                'outcome': outcome,
                'timestamp': time.time()
            })
            
            # Update learned patterns
            if operation_type not in learning_data['learned_patterns']:
                learning_data['learned_patterns'][operation_type] = []
            
            # Extract patterns from operation
            pattern = self._extract_pattern(operation_type, details, outcome)
            if pattern:
                learning_data['learned_patterns'][operation_type].append(pattern)
            
            # Limit history
            if len(learning_data['successful_workflows']) > 500:
                learning_data['successful_workflows'] = learning_data['successful_workflows'][-500:]
            
            learning_data['last_update'] = time.time()
            
            with open(self.learning_file, 'w') as f:
                json.dump(learning_data, f)
                
        except Exception as e:
            logger.error(f"Error learning from operation: {e}")
    
    def _extract_pattern(self, operation_type: str, details: Dict[str, Any], outcome: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract patterns from a successful operation
        
        Args:
            operation_type: Type of operation
            details: Operation details
            outcome: Operation outcome
            
        Returns:
            Extracted pattern or None
        """
        # This would contain more sophisticated pattern extraction in a production system
        if operation_type == 'scan':
            return {
                'target_type': details.get('target_type'),
                'effective_options': details.get('options', {}),
                'discovery_rate': len(outcome.get('findings', [])) / max(1, details.get('duration', 1)),
                'timestamp': time.time()
            }
        elif operation_type == 'exploit':
            return {
                'vulnerability_type': details.get('vulnerability_type'),
                'target_os': details.get('target_os'),
                'success_factors': outcome.get('success_factors', []),
                'timestamp': time.time()
            }
        
        return None
    
    def run_self_improvement(self, force: bool = False) -> Dict[str, Any]:
        """
        Run self-improvement routines
        
        This method analyzes usage patterns, performance metrics,
        and error data to optimize the system.
        
        Args:
            force: Force improvement even if the scheduled time hasn't arrived
            
        Returns:
            Dictionary with improvement results
        """
        # Check if it's time for improvement (every 24 hours by default)
        improvement_interval = self.config.get('enhancement', {}).get('improvement_interval', 86400)
        if not force and (time.time() - self.last_improvement_time) < improvement_interval:
            return {
                'status': 'skipped',
                'message': f"Next improvement scheduled in {int((self.last_improvement_time + improvement_interval - time.time()) / 60)} minutes"
            }
        
        logger.info("Running self-improvement routines")
        
        results = {
            'optimize_config': self._optimize_configuration(),
            'improve_performance': self._improve_performance(),
            'update_components': self._update_components() if self._is_online() else {'status': 'skipped', 'reason': 'offline'},
            'system_cleanup': self._perform_system_cleanup(),
            'timestamp': time.time()
        }
        
        # Update last improvement time
        self._update_last_improvement_time()
        
        # Log improvements
        improvement_log_file = os.path.join(self.data_dir, 'improvement_history.json')
        
        try:
            if os.path.exists(improvement_log_file):
                with open(improvement_log_file, 'r') as f:
                    improvement_history = json.load(f)
            else:
                improvement_history = {'improvements': []}
            
            # Add current improvement
            improvement_history['improvements'].append({
                'timestamp': time.time(),
                'results': results
            })
            
            # Limit history
            if len(improvement_history['improvements']) > 100:
                improvement_history['improvements'] = improvement_history['improvements'][-100:]
            
            with open(improvement_log_file, 'w') as f:
                json.dump(improvement_history, f)
                
        except Exception as e:
            logger.error(f"Error logging improvement history: {e}")
        
        return {
            'status': 'success',
            'results': results
        }
    
    def _optimize_configuration(self) -> Dict[str, Any]:
        """
        Optimize system configuration based on usage patterns
        
        Returns:
            Optimization results
        """
        optimizations = []
        
        try:
            # Load usage data
            with open(self.usage_data_file, 'r') as f:
                usage_data = json.load(f)
            
            # Load performance data
            with open(self.performance_file, 'r') as f:
                performance_data = json.load(f)
            
            # Analyze command usage patterns
            command_usage = usage_data.get('commands', {})
            
            # Example optimizations:
            
            # 1. Optimize AI model selection based on most common queries
            if 'llm query' in command_usage and command_usage['llm query']['count'] > 10:
                # If using LLM queries frequently, optimize the default engine
                avg_response_time = command_usage['llm query']['total_duration'] / command_usage['llm query']['count']
                
                if avg_response_time > 2.0:  # If response time is slow
                    # Check if a faster model configuration is available
                    if self.config['llm']['default_model'].get('llama.cpp', '') != 'tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf':
                        self.config['llm']['default_model']['llama.cpp'] = 'tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf'
                        optimizations.append({
                            'component': 'llm',
                            'change': 'Changed default llama.cpp model to TinyLlama for faster responses',
                            'reason': f'Average response time was {avg_response_time:.2f}s'
                        })
            
            # 2. Adjust context length based on memory usage
            memory_metrics = performance_data.get('memory_usage', [])
            if memory_metrics:
                recent_memory = [m['value'] for m in memory_metrics[-10:]]
                avg_memory = sum(recent_memory) / len(recent_memory) if recent_memory else 0
                
                if avg_memory > 400:  # If memory usage is high
                    current_context = self.config['llm'].get('context_length', 2048)
                    if current_context > 1024:
                        self.config['llm']['context_length'] = 1024
                        optimizations.append({
                            'component': 'llm',
                            'change': 'Reduced LLM context length to 1024',
                            'reason': f'Average memory usage was high at {avg_memory:.2f}MB'
                        })
            
            # Save optimized configuration if changes were made
            if optimizations:
                from src.config import save_config
                save_config(self.config)
                
                logger.info(f"Applied {len(optimizations)} configuration optimizations")
            
            return {
                'status': 'success',
                'optimizations': optimizations
            }
            
        except Exception as e:
            logger.error(f"Error optimizing configuration: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _improve_performance(self) -> Dict[str, Any]:
        """
        Improve system performance
        
        Returns:
            Performance improvement results
        """
        improvements = []
        
        try:
            # Load performance data
            with open(self.performance_file, 'r') as f:
                performance_data = json.load(f)
            
            # Load usage data for context
            with open(self.usage_data_file, 'r') as f:
                usage_data = json.load(f)
            
            # Analyze response times
            response_times = performance_data.get('response_times', [])
            if response_times:
                recent_times = [rt['value'] for rt in response_times[-20:]]
                avg_time = sum(recent_times) / len(recent_times) if recent_times else 0
                
                if avg_time > self.performance_thresholds['response_time']:
                    # Identify slow components and optimize
                    
                    # Look at command usage to identify slow commands
                    command_usage = usage_data.get('commands', {})
                    slow_commands = []
                    
                    for cmd, data in command_usage.items():
                        if data['count'] > 5:  # Only consider commands used multiple times
                            avg_cmd_time = data['total_duration'] / data['count']
                            if avg_cmd_time > 2.0:  # Threshold for slow command
                                slow_commands.append((cmd, avg_cmd_time))
                    
                    # Sort by average time (slowest first)
                    slow_commands.sort(key=lambda x: x[1], reverse=True)
                    
                    # Implement improvements for slow commands
                    for cmd, avg_time in slow_commands[:3]:  # Focus on top 3 slowest
                        if 'scan' in cmd:
                            # Optimize scanning parameters
                            if 'security' not in self.config:
                                self.config['security'] = {}
                            if 'scan' not in self.config['security']:
                                self.config['security']['scan'] = {}
                            
                            # Reduce scan thoroughness if it's too slow
                            self.config['security']['scan']['optimize_speed'] = True
                            self.config['security']['scan']['parallel_tasks'] = 5
                            
                            improvements.append({
                                'component': 'security.scan',
                                'change': 'Optimized scan parameters for better performance',
                                'reason': f'Average scan time was {avg_time:.2f}s'
                            })
                        
                        elif 'llm' in cmd:
                            # Optimize LLM parameters
                            if 'llm' not in self.config:
                                self.config['llm'] = {}
                            
                            # Reduce token count and use faster sampling
                            self.config['llm']['max_tokens'] = 256
                            self.config['llm']['optimize_inference'] = True
                            
                            improvements.append({
                                'component': 'llm',
                                'change': 'Reduced token count and optimized inference',
                                'reason': f'Average LLM query time was {avg_time:.2f}s'
                            })
            
            # Save optimized configuration if changes were made
            if improvements:
                from src.config import save_config
                save_config(self.config)
                
                logger.info(f"Applied {len(improvements)} performance improvements")
            
            return {
                'status': 'success',
                'improvements': improvements
            }
            
        except Exception as e:
            logger.error(f"Error improving performance: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _update_components(self) -> Dict[str, Any]:
        """
        Update system components when online
        
        Returns:
            Update results
        """
        if not self._is_online():
            return {
                'status': 'skipped',
                'reason': 'offline'
            }
        
        updates = []
        
        try:
            # Check for updates to internal modules
            update_log = {}
            
            # Self-update key internal libraries
            packages_to_update = ['openai', 'anthropic', 'flask', 'flask-socketio', 'requests']
            
            for package in packages_to_update:
                try:
                    # Check if package needs updating
                    check_process = subprocess.run(
                        [sys.executable, '-m', 'pip', 'list', '--outdated'],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    if package in check_process.stdout:
                        # Update the package
                        update_process = subprocess.run(
                            [sys.executable, '-m', 'pip', 'install', '--upgrade', package],
                            check=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                        
                        updates.append({
                            'component': package,
                            'status': 'updated',
                            'details': 'Package upgraded'
                        })
                        
                        update_log[package] = 'updated'
                    else:
                        update_log[package] = 'up-to-date'
                        
                except Exception as e:
                    logger.error(f"Error updating {package}: {e}")
                    update_log[package] = f'error: {str(e)}'
            
            # Log the update attempt
            update_history_file = os.path.join(self.data_dir, 'update_history.json')
            
            if os.path.exists(update_history_file):
                with open(update_history_file, 'r') as f:
                    update_history = json.load(f)
            else:
                update_history = {'updates': []}
            
            # Add current update
            update_history['updates'].append({
                'timestamp': time.time(),
                'results': update_log
            })
            
            # Limit history
            if len(update_history['updates']) > 50:
                update_history['updates'] = update_history['updates'][-50:]
            
            with open(update_history_file, 'w') as f:
                json.dump(update_history, f)
            
            return {
                'status': 'success',
                'updates': updates
            }
            
        except Exception as e:
            logger.error(f"Error updating components: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _perform_system_cleanup(self) -> Dict[str, Any]:
        """
        Perform system cleanup to maintain optimal performance
        
        Returns:
            Cleanup results
        """
        cleanup_actions = []
        
        try:
            # 1. Clean up temporary files
            temp_dir = self.config['paths']['temp_dir']
            if os.path.exists(temp_dir):
                before_size = self._get_dir_size(temp_dir)
                
                # Remove files older than 7 days
                cleanup_count = 0
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.exists(file_path):
                            file_age = time.time() - os.path.getmtime(file_path)
                            if file_age > (7 * 86400):  # 7 days
                                try:
                                    os.remove(file_path)
                                    cleanup_count += 1
                                except:
                                    pass
                
                after_size = self._get_dir_size(temp_dir)
                
                if cleanup_count > 0:
                    cleanup_actions.append({
                        'action': 'temp_cleanup',
                        'count': cleanup_count,
                        'space_freed': f"{(before_size - after_size) / (1024*1024):.2f} MB"
                    })
            
            # 2. Optimize database (if exists)
            db_file = os.path.join(self.config['paths']['data_dir'], 'g3r4ki.db')
            if os.path.exists(db_file):
                # Vacuum the SQLite database to optimize it
                try:
                    import sqlite3
                    conn = sqlite3.connect(db_file)
                    conn.execute("VACUUM")
                    conn.close()
                    
                    cleanup_actions.append({
                        'action': 'db_optimize',
                        'status': 'success'
                    })
                except Exception as e:
                    logger.error(f"Error optimizing database: {e}")
            
            # 3. Clean up old logs
            logs_dir = os.path.join(self.config['paths']['data_dir'], 'logs')
            if os.path.exists(logs_dir):
                before_size = self._get_dir_size(logs_dir)
                
                # Remove logs older than 30 days
                cleanup_count = 0
                for log_file in os.listdir(logs_dir):
                    if log_file.endswith('.log'):
                        file_path = os.path.join(logs_dir, log_file)
                        if os.path.exists(file_path):
                            file_age = time.time() - os.path.getmtime(file_path)
                            if file_age > (30 * 86400):  # 30 days
                                try:
                                    os.remove(file_path)
                                    cleanup_count += 1
                                except:
                                    pass
                
                after_size = self._get_dir_size(logs_dir)
                
                if cleanup_count > 0:
                    cleanup_actions.append({
                        'action': 'log_cleanup',
                        'count': cleanup_count,
                        'space_freed': f"{(before_size - after_size) / (1024*1024):.2f} MB"
                    })
            
            # 4. Compact JSON data files
            if os.path.exists(self.usage_data_file) and os.path.getsize(self.usage_data_file) > 1024*1024:  # > 1MB
                try:
                    with open(self.usage_data_file, 'r') as f:
                        usage_data = json.load(f)
                    
                    # Trim old command history
                    removed_entries = 0
                    if 'commands' in usage_data:
                        # Keep only commands used in the last 60 days
                        cutoff_time = time.time() - (60 * 86400)
                        commands_to_remove = []
                        
                        for cmd, data in usage_data['commands'].items():
                            if data.get('last_used', 0) < cutoff_time:
                                commands_to_remove.append(cmd)
                        
                        for cmd in commands_to_remove:
                            del usage_data['commands'][cmd]
                        
                        removed_entries = len(commands_to_remove)
                    
                    # Save compacted data
                    with open(self.usage_data_file, 'w') as f:
                        json.dump(usage_data, f)
                    
                    cleanup_actions.append({
                        'action': 'usage_data_compact',
                        'removed_entries': removed_entries
                    })
                except Exception as e:
                    logger.error(f"Error compacting usage data: {e}")
            
            return {
                'status': 'success',
                'cleanup_actions': cleanup_actions
            }
            
        except Exception as e:
            logger.error(f"Error performing system cleanup: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _get_dir_size(self, path: str) -> float:
        """
        Get directory size in bytes
        
        Args:
            path: Directory path
            
        Returns:
            Size in bytes
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        return total_size
    
    def _is_online(self) -> bool:
        """
        Check if system is online
        
        Returns:
            True if online, False otherwise
        """
        try:
            # Try to connect to a reliable server
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=1)
            return True
        except:
            return False
    
    def get_enhancement_stats(self) -> Dict[str, Any]:
        """
        Get enhancement statistics
        
        Returns:
            Statistics about self-improvement activities
        """
        stats = {
            'last_improvement': self.last_improvement_time,
            'next_improvement': self.last_improvement_time + self.config.get('enhancement', {}).get('improvement_interval', 86400),
            'cumulative_stats': {
                'optimizations': 0,
                'performance_improvements': 0,
                'updates': 0,
                'cleanup_actions': 0
            },
            'recent_activity': []
        }
        
        # Load improvement history
        improvement_log_file = os.path.join(self.data_dir, 'improvement_history.json')
        if os.path.exists(improvement_log_file):
            try:
                with open(improvement_log_file, 'r') as f:
                    improvement_history = json.load(f)
                
                # Count improvements
                for imp in improvement_history.get('improvements', []):
                    results = imp.get('results', {})
                    
                    # Count optimizations
                    opt_result = results.get('optimize_config', {})
                    if 'optimizations' in opt_result:
                        stats['cumulative_stats']['optimizations'] += len(opt_result['optimizations'])
                    
                    # Count performance improvements
                    perf_result = results.get('improve_performance', {})
                    if 'improvements' in perf_result:
                        stats['cumulative_stats']['performance_improvements'] += len(perf_result['improvements'])
                    
                    # Count updates
                    update_result = results.get('update_components', {})
                    if 'updates' in update_result:
                        stats['cumulative_stats']['updates'] += len(update_result['updates'])
                    
                    # Count cleanup actions
                    cleanup_result = results.get('system_cleanup', {})
                    if 'cleanup_actions' in cleanup_result:
                        stats['cumulative_stats']['cleanup_actions'] += len(cleanup_result['cleanup_actions'])
                
                # Get recent activity
                recent_improvements = improvement_history.get('improvements', [])[-5:]
                for imp in recent_improvements:
                    stats['recent_activity'].append({
                        'timestamp': imp.get('timestamp', 0),
                        'summary': self._summarize_improvement(imp.get('results', {}))
                    })
                    
            except Exception as e:
                logger.error(f"Error getting enhancement stats: {e}")
        
        return stats
    
    def _summarize_improvement(self, results: Dict[str, Any]) -> str:
        """
        Summarize improvement results
        
        Args:
            results: Improvement results
            
        Returns:
            Summary string
        """
        summary_parts = []
        
        # Optimizations
        opt_result = results.get('optimize_config', {})
        if 'optimizations' in opt_result and opt_result['optimizations']:
            summary_parts.append(f"{len(opt_result['optimizations'])} config optimizations")
        
        # Performance improvements
        perf_result = results.get('improve_performance', {})
        if 'improvements' in perf_result and perf_result['improvements']:
            summary_parts.append(f"{len(perf_result['improvements'])} performance improvements")
        
        # Updates
        update_result = results.get('update_components', {})
        if 'updates' in update_result and update_result['updates']:
            summary_parts.append(f"{len(update_result['updates'])} component updates")
        
        # Cleanup actions
        cleanup_result = results.get('system_cleanup', {})
        if 'cleanup_actions' in cleanup_result and cleanup_result['cleanup_actions']:
            summary_parts.append(f"{len(cleanup_result['cleanup_actions'])} cleanup actions")
        
        if not summary_parts:
            return "No significant improvements"
        
        return ", ".join(summary_parts)
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Get insights from learning data
        
        Returns:
            Insights extracted from learning data
        """
        insights = {
            'frequent_patterns': {},
            'optimization_suggestions': [],
            'workflow_recommendations': []
        }
        
        try:
            # Load learning data
            if os.path.exists(self.learning_file):
                with open(self.learning_file, 'r') as f:
                    learning_data = json.load(f)
                
                # Extract frequent patterns
                for op_type, patterns in learning_data.get('learned_patterns', {}).items():
                    if patterns:
                        # Count pattern occurrences
                        pattern_counts = {}
                        
                        for pattern in patterns:
                            # Create a simplified pattern key
                            if op_type == 'scan':
                                key = f"target:{pattern.get('target_type', 'unknown')}"
                            elif op_type == 'exploit':
                                key = f"vuln:{pattern.get('vulnerability_type', 'unknown')}|os:{pattern.get('target_os', 'unknown')}"
                            else:
                                continue
                            
                            if key not in pattern_counts:
                                pattern_counts[key] = 0
                            pattern_counts[key] += 1
                        
                        # Get top patterns
                        top_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                        insights['frequent_patterns'][op_type] = [
                            {'pattern': p[0], 'count': p[1]} for p in top_patterns
                        ]
                
                # Generate workflow recommendations based on successful workflows
                workflows = learning_data.get('successful_workflows', [])
                if workflows:
                    # Find recurring successful patterns
                    for workflow in workflows[-20:]:  # Look at recent workflows
                        op_type = workflow.get('type')
                        details = workflow.get('details', {})
                        outcome = workflow.get('outcome', {})
                        
                        if op_type == 'scan' and outcome.get('success') and len(outcome.get('findings', [])) > 5:
                            insights['workflow_recommendations'].append({
                                'type': 'scan',
                                'recommendation': f"Use {details.get('scan_type', 'standard')} scan with params: {str(details.get('options', {}))}",
                                'effectiveness': f"Found {len(outcome.get('findings', []))} issues"
                            })
                        elif op_type == 'exploit' and outcome.get('success'):
                            insights['workflow_recommendations'].append({
                                'type': 'exploit',
                                'recommendation': f"Try {details.get('vulnerability_type')} exploit against {details.get('target_os', 'unknown')} targets",
                                'effectiveness': "Successfully exploited target"
                            })
                
                # Limit to top 5 recommendations
                insights['workflow_recommendations'] = insights['workflow_recommendations'][:5]
                
        except Exception as e:
            logger.error(f"Error getting learning insights: {e}")
        
        return insights