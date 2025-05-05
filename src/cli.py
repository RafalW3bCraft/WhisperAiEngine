#!/usr/bin/env python3
# G3r4ki CLI interface

import os
import sys
import cmd
import argparse
import logging
import readline
import shlex
from datetime import datetime

from src.config import load_config, save_config
from src.system import check_system_requirements
from src.llm.manager import LLMManager
from src.voice.whisper_stt import WhisperSTT
from src.voice.piper_tts import PiperTTS
from src.voice.command_processor import VoiceCommandProcessor
from src.security.nmap_tools import NmapScanner
from src.security.recon import ReconScanner
from src.security.vuln_scan import VulnerabilityScanner
from src.security.tool_manager import ToolManager
from src.visualization.server import VisualizationServer
from src.visualization.data_processor import DataProcessor
from src.visualization.network_map import NetworkMap
from src.ai.ai_proxy import init_ai_proxy

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('g3r4ki.cli')

# Import agent system components
AGENT_SYSTEM_AVAILABLE = False
try:
    from src.agents.core import AgentManager
    from src.agents.types.recon_agent import ReconAgent
    from src.agents.types.security_agent import SecurityAgent
    AGENT_SYSTEM_AVAILABLE = True
except ImportError:
    logger.warning("Agent system components not available")

# Import NLP components
NLP_AVAILABLE = False
try:
    # Try both import approaches to ensure compatibility
    try:
        from src.nlp import CommandProcessor
    except ImportError:
        from src.nlp.command_processor import CommandProcessor
    NLP_AVAILABLE = True
    logger.info("Natural language processing available")
except ImportError as e:
    logger.warning(f"Natural language processing not available: {str(e)}")

class G3r4kiCLI(cmd.Cmd):
    """Command-line interface for G3r4ki"""
    
    intro = r"""
  __ _____  _ _   _    _ 
 / _|__ / || | | | | _(_)
| |_ |_ \| || |_| |/ / |
|  _|__) |__   _|   <| |
|_| |___/   |_| |_|\_\_|

AI-powered cybersecurity operations
Type 'help' or '?' to list commands.
"""
    prompt = "g3r4ki> "
    
    def __init__(self, config=None):
        super().__init__()
        
        # Load configuration
        self.config = config if config else load_config()
        
        # Set debug level based on config
        if self.config.get('debug', False):
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled")
        
        # Initialize components
        self.llm_manager = LLMManager(self.config)
        self.whisper = WhisperSTT(self.config)
        self.piper = PiperTTS(self.config)
        self.nmap = NmapScanner(self.config)
        self.recon = ReconScanner(self.config)
        self.vuln_scanner = VulnerabilityScanner(self.config)
        self.tool_manager = ToolManager(self.config)
        
        # Initialize AI Proxy system (unified cloud + local LLMs)
        self.ai_proxy = init_ai_proxy(self.config)
        
        # Initialize voice command processor after CLI is ready (pass self reference)
        self.voice_cmd = VoiceCommandProcessor(self.config, self)
        
        # Initialize NLP components if available
        self.nlp_processor = None
        if NLP_AVAILABLE and self.config.get('nlp', {}).get('enabled', True):
            try:
                self.nlp_processor = CommandProcessor(config=self.config)
                logger.info("NLP command processor initialized")
                
                # Register command handlers
                self.nlp_processor.register_command_handler("scan", self.do_scan)
                self.nlp_processor.register_command_handler("recon", self.do_recon)
                self.nlp_processor.register_command_handler("vuln", self.do_vuln)
                self.nlp_processor.register_command_handler("llm", self.do_llm)
                self.nlp_processor.register_command_handler("help", self.do_help)
                self.nlp_processor.register_command_handler("exit", self.do_exit)
                self.nlp_processor.register_command_handler("tools", self.do_tools)
            except Exception as e:
                logger.error(f"Error initializing NLP processor: {str(e)}")
        
        # Initialize visualization components
        self.data_processor = DataProcessor()
        self.network_map = NetworkMap()
        self.vis_server = VisualizationServer(self.config)
        
        # Initialize agent system if available
        self.agent_manager = None
        if AGENT_SYSTEM_AVAILABLE:
            try:
                self.agent_manager = AgentManager(self.config)
                
                # Register agent types
                self.agent_manager.register_agent_type("recon", ReconAgent)
                self.agent_manager.register_agent_type("security", SecurityAgent)
                
                # Register penetration testing agent if available
                try:
                    from src.agents.types.pentest_agent import PentestAgent
                    self.agent_manager.register_agent_type("pentest", PentestAgent)
                    logger.info("Pentest agent registered")
                except Exception as e:
                    logger.warning(f"Failed to register pentest agent: {str(e)}")
                
                logger.info("Agent system initialized")
            except Exception as e:
                logger.error(f"Error initializing agent system: {str(e)}")
        
        # Initialize penetration testing tools
        try:
            from src.pentest.utils.cli import add_cli_commands
            add_cli_commands(self)
            logger.info("Penetration testing tools initialized")
        except Exception as e:
            logger.error(f"Error initializing penetration testing tools: {str(e)}")
        
        # Auto-start visualization server if configured
        if self.config.get('visualization', {}).get('auto_start', False):
            if self.vis_server.is_available():
                self.vis_server.start(debug=self.config.get('debug', False))
                logger.info(f"Visualization server started at http://{self.config['visualization']['host']}:{self.config['visualization']['port']}")
            else:
                logger.warning("Visualization server dependencies not available. Install Flask and Flask-SocketIO.")
        
        # Command history file
        self.history_file = os.path.expanduser("~/.g3r4ki_history")
        
        # Try to load history file
        try:
            readline.read_history_file(self.history_file)
        except FileNotFoundError:
            pass
        
        # Set history file size
        readline.set_history_length(1000)
    
    def preloop(self):
        """Hook method executed once when the cmdloop() method is called."""
        print(self.intro)
    
    def postloop(self):
        """Hook method executed once when the cmdloop() method is about to return."""
        readline.write_history_file(self.history_file)
        print("Goodbye!")
    
    def emptyline(self):
        """Called when an empty line is entered."""
        return False  # Don't repeat last command
    
    def default(self, line):
        """Called when the command prefix is not recognized."""
        if line.startswith('!'):
            # Execute as shell command
            os.system(line[1:])
        elif self.nlp_processor and self.config.get('nlp', {}).get('enabled', True):
            # Use NLP processor to handle natural language commands
            try:
                result = self.nlp_processor.process_and_execute(line)
                
                if result.get('success'):
                    execution = result.get('execution', {})
                    if execution.get('success'):
                        if 'result' in execution:
                            print(execution.get('result', ''))
                        print(execution.get('message', 'Command executed successfully.'))
                    else:
                        print(f"Error executing command: {execution.get('message', 'Unknown error')}")
                else:
                    print(f"Could not understand command: {line}")
                    print("Try rephrasing or use standard command syntax.")
                    print("Type 'help' or '?' for a list of available commands.")
                    
                    # Provide reasoning if available
                    if 'reasoning' in result:
                        print(f"\nAnalysis: {result['reasoning']}")
            except Exception as e:
                logger.error(f"Error in NLP processing: {str(e)}")
                print(f"Error processing natural language command: {str(e)}")
                print("Type 'help' or '?' to list available commands.")
        else:
            print(f"Unknown command: {line}")
            print("Type 'help' or '?' to list available commands.")
    
    def start_interactive_mode(self):
        """Start the interactive command shell"""
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            readline.write_history_file(self.history_file)
    
    def handle_llm_command(self, args):
        """Handle LLM-related commands from command line arguments"""
        if not hasattr(args, "llm_command") or args.llm_command is None:
            print("No llm subcommand specified. Use --help for usage.")
            return
        
        if args.llm_command == "list":
            engines, models = self.llm_manager.list_models()
            print("Available LLM engines:")
            for engine in engines:
                print(f"  - {engine}")
                if engine in models and models[engine]:
                    for model in models[engine]:
                        print(f"    - {model}")
            
            # Also show AI providers
            providers = self.ai_proxy.get_available_providers()
            if providers:
                print("\nAI Providers (use 'llm ai' command):")
                for provider in providers:
                    print(f"  - {provider['name']} ({provider['type']})")
        
        elif args.llm_command == "download":
            provider = args.provider
            model = args.model
            
            print(f"Downloading model '{model}' for provider '{provider}'...")
            
            try:
                from src.llm.local_ai import LocalAIManager
            except ImportError as e:
                print(f"Error importing LocalAIManager: {e}")
                return
            
            local_ai = LocalAIManager()
            
            success = local_ai.download_model(provider, model)
            
            if success:
                print(f"Model '{model}' downloaded successfully for provider '{provider}'.")
            else:
                print(f"Failed to download model '{model}' for provider '{provider}'.")
        
        elif args.llm_command == "query":
            engine = args.engine if args.engine else self.config['llm']['default_engine']
            model = args.model if args.model else self.config['llm']['default_model'][engine]
            
            print(f"Querying {engine} with model {model}...")
            response = self.llm_manager.query(args.text, engine, model)
            
            print("\nResponse:")
            print(response)
        
        elif args.llm_command == "ai":
            text = args.text
            provider_id = args.provider
            system_prompt = args.system if hasattr(args, 'system') else ""
            
            providers = self.ai_proxy.get_available_providers()
            if not providers:
                print("No AI providers are available.")
                print("Please ensure you have API keys for cloud providers or")
                print("run the setup scripts to install local LLM components:")
                print("  bash scripts/setup_llms.sh")
                return
            
            if not provider_id:
                recommended = self.ai_proxy.get_recommended_provider()
                if recommended:
                    provider_id = recommended['id']
                    print(f"Using recommended provider: {recommended['name']}")
                else:
                    provider_id = providers[0]['id']
                    print(f"Using available provider: {providers[0]['name']}")
            
            if not self.ai_proxy.is_provider_available(provider_id):
                print(f"Error: Provider '{provider_id}' is not available.")
                print("Available providers:")
                for p in providers:
                    print(f"  - {p['name']} (id: {p['id']})")
                return
            
            print(f"Querying provider: {provider_id}...")
            if system_prompt:
                print(f"Using system prompt: {system_prompt}")
            
            try:
                result = self.ai_proxy.query(provider_id, text, system_prompt)
                print(f"\nResponse from {result['provider_name']} (took {result['time_taken']}s):")
                print(result['response'])
            except Exception as e:
                print(f"Error querying AI provider: {str(e)}")
        
        elif args.llm_command == "best":
            text = args.text
            system_prompt = args.system if hasattr(args, 'system') else ""
            
            print("Querying best available AI provider...")
            if system_prompt:
                print(f"Using system prompt: {system_prompt}")
            
            try:
                result = self.ai_proxy.query_with_reasoning(text, system_prompt)
                print(f"\nResponse from {result['provider_name']} (took {result['time_taken']}s):")
                print(result['response'])
            except Exception as e:
                print(f"Error querying AI: {str(e)}")
        
        elif args.llm_command == "providers":
            providers = self.ai_proxy.get_available_providers()
            if not providers:
                print("No AI providers are currently available.")
                print("Please ensure you have API keys for cloud providers or")
                print("run the setup scripts to install local LLM components:")
                print("  bash scripts/setup_llms.sh")
                return
            
            print("Available AI Providers:")
            cloud_providers = [p for p in providers if p['type'] == 'cloud']
            local_providers = [p for p in providers if p['type'] == 'local']
            
            if cloud_providers:
                print("\nCloud Providers:")
                for provider in cloud_providers:
                    print(f"  - {provider['name']} (id: {provider['id']})")
            
            if local_providers:
                print("\nLocal Providers:")
                for provider in local_providers:
                    model_count = provider.get('model_count', 0)
                    print(f"  - {provider['name']} (id: {provider['id']}) - {model_count} models")
            
            recommended = self.ai_proxy.get_recommended_provider()
            if recommended:
                print(f"\nRecommended provider: {recommended['name']} ({recommended['type']})")
        
        elif args.llm_command == "engines":
            engines = self.llm_manager.get_available_engines()
            if not engines:
                print("No LLM engines are currently available.")
                print("Please run the setup scripts to install LLM components:")
                print("  bash scripts/setup_llms.sh")
                return
            
            print("Available LLM engines:")
            for engine in engines:
                print(f"  - {engine}")
        
        else:
            print("Unknown llm command. Use: list|query|download|ai|best|providers|engines")
    
    def handle_voice_command(self, args):
        """Handle voice-related commands from command line arguments"""
        if args.stt:
            # Check if Whisper is available
            if not self.whisper.is_available():
                print("Error: Whisper speech-to-text is not available.")
                print("Please run the setup scripts to install voice components:")
                print("  bash scripts/setup_voice.sh")
                return
                
            if not os.path.exists(args.stt):
                print(f"Error: Audio file not found: {args.stt}")
                return
            
            print(f"Transcribing audio from {args.stt}...")
            try:
                text = self.whisper.transcribe(args.stt)
                print("\nTranscription:")
                print(text)
            except Exception as e:
                print(f"Error during transcription: {str(e)}")
                print("This could be due to missing Whisper models or configuration issues.")
        
        elif args.tts:
            # Check if Piper is available
            if not self.piper.is_available():
                print("Error: Piper text-to-speech is not available.")
                print("Please run the setup scripts to install voice components:")
                print("  bash scripts/setup_voice.sh")
                return
                
            output = args.output if args.output else "output.wav"
            
            print(f"Generating speech for: {args.tts}")
            print(f"Output file: {output}")
            
            try:
                success = self.piper.synthesize(args.tts, output)
                if success:
                    print(f"Speech generated successfully: {output}")
                else:
                    print("Failed to generate speech")
            except Exception as e:
                print(f"Error generating speech: {str(e)}")
                print("This could be due to missing Piper models or configuration issues.")
        
        elif args.command:
            # Check if voice command processing is available
            if not self.voice_cmd.is_available():
                print("Error: Voice command processing is not available.")
                print("Please run the setup scripts to install voice components:")
                print("  bash scripts/setup_voice.sh")
                return
                
            if not os.path.exists(args.command):
                print(f"Error: Audio file not found: {args.command}")
                return
                
            print(f"Processing voice command from {args.command}...")
            
            try:
                command, response, success = self.voice_cmd.process_audio_file(args.command)
                print(f"\nTranscribed command: {command}")
                print(f"Response: {response}")
                
                # Speak the response if requested
                if args.speak:
                    print("Speaking response...")
                    self.voice_cmd.speak_response(response)
            except Exception as e:
                print(f"Error processing voice command: {str(e)}")
                print("This could be due to missing voice components or configuration issues.")
        
        elif args.listen:
            # Check if voice command processing is available
            if not self.voice_cmd.is_available():
                print("Error: Voice command processing is not available.")
                print("Please run the setup scripts to install voice components:")
                print("  bash scripts/setup_voice.sh")
                return
                
            # Get duration if specified
            duration = args.duration if hasattr(args, 'duration') and args.duration else 5
            
            print(f"Listening for voice command for {duration} seconds...")
            
            try:
                command, response, success = self.voice_cmd.process_mic_input(duration)
                print(f"\nTranscribed command: {command}")
                print(f"Response: {response}")
                
                # Speak the response if requested
                if args.speak:
                    print("Speaking response...")
                    self.voice_cmd.speak_response(response)
            except Exception as e:
                print(f"Error processing voice command: {str(e)}")
                print("This could be due to missing voice components or configuration issues.")
    
    def handle_security_command(self, args):
        """Handle security-related commands from command line arguments"""
        if args.scan:
            print(f"Scanning target: {args.scan}")
            results = self.nmap.scan(args.scan)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(results)
                print(f"Scan results saved to {args.output}")
            else:
                print("\nScan Results:")
                print(results)
        
        elif args.recon:
            print(f"Performing reconnaissance on target: {args.recon}")
            results = self.recon.scan(args.recon)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(results)
                print(f"Reconnaissance results saved to {args.output}")
            else:
                print("\nReconnaissance Results:")
                print(results)
        
        elif args.vuln:
            print(f"Performing vulnerability scan on target: {args.vuln}")
            results = self.vuln_scanner.scan(args.vuln)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(results)
                print(f"Vulnerability scan results saved to {args.output}")
            else:
                print("\nVulnerability Scan Results:")
                print(results)
                
        # Handle tool management operations
        elif hasattr(args, 'tools_list') and args.tools_list:
            print("Scanning for available security tools...")
            available_tools = self.tool_manager.scan_available_tools()
            
            print("\nAvailable Security Tools:")
            for category, tools in available_tools.items():
                print(f"\n== {category.upper()} ==")
                for tool_name, is_available in tools.items():
                    status = "✓" if is_available else "✗"
                    print(f"  {status} {tool_name}")
        
        elif hasattr(args, 'tools_scan') and args.tools_scan:
            print("Performing a comprehensive scan of available tools...")
            available_tools = self.tool_manager.scan_available_tools()
            
            installed_count = 0
            missing_count = 0
            
            for category, tools in available_tools.items():
                for tool_name, is_available in tools.items():
                    if is_available:
                        installed_count += 1
                    else:
                        missing_count += 1
            
            print(f"\nScan complete: {installed_count} tools installed, {missing_count} tools missing")
            print("Use 'g3r4ki sec --tools-list' for details or 'g3r4ki sec --tools-install CATEGORY' to install tools")
        
        elif hasattr(args, 'tools_info') and args.tools_info:
            tool_name = args.tools_info
            print(f"Getting information for tool: {tool_name}")
            
            tool_info = self.tool_manager.get_tool_info(tool_name)
            
            print(f"\n=== {tool_info['name']} ===")
            print(f"Installed: {'Yes' if tool_info['installed'] else 'No'}")
            
            if tool_info['installed'] and tool_info['path']:
                print(f"Path: {tool_info['path']}")
            
            if tool_info['categories']:
                print(f"Categories: {', '.join(tool_info['categories'])}")
            
            if tool_info.get('package'):
                print(f"Package name: {tool_info['package']}")
            
            if tool_info.get('python_package'):
                print(f"Python package: {tool_info['python_package']}")
            
            if tool_info.get('github_repo'):
                print(f"GitHub repository: {tool_info['github_repo']}")
        
        elif hasattr(args, 'tools_install') and args.tools_install:
            target = args.tools_install
            force = hasattr(args, 'force') and args.force
            
            # Check if it's a category
            if target in self.tool_manager.TOOL_CATEGORIES:
                print(f"Installing tools for category: {target}")
                results = self.tool_manager.install_category(target)
                
                print("\nInstallation Results:")
                for tool_name, success in results.items():
                    status = "✓" if success else "✗"
                    print(f"  {status} {tool_name}")
            else:
                # Try to install as a tool
                print(f"Installing tool: {target}")
                success = self.tool_manager.install_tool(target, force=force)
                
                if success:
                    print(f"Tool '{target}' installed successfully")
                else:
                    print(f"Failed to install tool '{target}'")
                    print("Make sure the tool name is correct or try with a category name")
        
        elif hasattr(args, 'tools_categories') and args.tools_categories:
            print("Available tool categories:")
            for category, tools in self.tool_manager.TOOL_CATEGORIES.items():
                tool_count = len(tools)
                print(f"  {category}: {tool_count} tools")
                # Show tools in the category
                print(f"    Tools: {', '.join(tools)}")
    
    # Command definitions for interactive mode
    def do_exit(self, arg):
        """Exit the program"""
        return True
    
    def do_quit(self, arg):
        """Exit the program"""
        return True
    
    def do_config(self, arg):
        """Show or edit configuration
        Usage: config [show|edit|reload|save]"""
        args = shlex.split(arg)
        if not args or args[0] == "show":
            import pprint
            pprint.pprint(self.config)
        elif args[0] == "edit":
            editor = os.environ.get("EDITOR", "nano")
            os.system(f"{editor} {os.path.expanduser('~/.config/g3r4ki/config.yaml')}")
        elif args[0] == "reload":
            self.config = load_config()
            print("Configuration reloaded")
        elif args[0] == "save":
            save_config(self.config)
            print("Configuration saved")
        else:
            print("Unknown config command. Use: config [show|edit|reload|save]")
    
    def do_system(self, arg):
        """System utilities
        Usage: system [check|info]"""
        args = shlex.split(arg)
        if not args or args[0] == "check":
            check_system_requirements()
        elif args[0] == "info":
            from src.system import get_hardware_info
            hw_info = get_hardware_info()
            
            print("\nSystem Information:")
            print(f"CPU: {hw_info['cpu']['model']} ({hw_info['cpu']['cores']} cores)")
            print(f"Memory: {hw_info['memory']['total_gb']} GB")
            print(f"GPU: {hw_info['gpu']['model']}")
            print(f"CUDA: {hw_info['gpu']['cuda_version'] or 'Not available'}")
        else:
            print("Unknown system command. Use: system [check|info]")
    
    def do_visualize(self, arg):
        """Visualization operations
        Usage: visualize start
               visualize stop
               visualize status
               visualize url"""
        args = shlex.split(arg)
        if not args:
            print("Usage: visualize start|stop|status|url")
            return
        
        # Check if visualization server is available
        if not self.vis_server.is_available() and args[0] != "status":
            print("Error: Visualization server is not available.")
            print("Please install the required packages:")
            print("  pip install flask flask-socketio networkx")
            return
        
        if args[0] == "start":
            if self.vis_server.start(debug=self.config.get('debug', False)):
                host = self.config['visualization']['host']
                port = self.config['visualization']['port']
                print(f"Visualization server started at http://{host}:{port}")
            else:
                print("Failed to start visualization server.")
        
        elif args[0] == "stop":
            self.vis_server.stop()
            print("Visualization server stopped.")
        
        elif args[0] == "status":
            if not self.vis_server.is_available():
                print("Visualization server is not available (missing dependencies).")
            elif hasattr(self.vis_server, 'running') and self.vis_server.running:
                host = self.config['visualization']['host']
                port = self.config['visualization']['port']
                print(f"Visualization server is running at http://{host}:{port}")
            else:
                print("Visualization server is not running.")
        
        elif args[0] == "url":
            host = self.config['visualization']['host']
            port = self.config['visualization']['port']
            print(f"Visualization URL: http://{host}:{port}")
        
        else:
            print("Unknown visualize command. Use: visualize start|stop|status|url")
    
    def do_llm(self, arg):
        """LLM operations
        Usage: llm list
               llm engines
               llm query <text> [--engine <engine>] [--model <model>]
               llm ai <text> [--provider <provider>] [--system <system_prompt>]
               llm providers
               llm best <text> [--system <system_prompt>]"""
        args = shlex.split(arg)
        if not args:
            print("Usage: llm list|engines|query|ai|providers|best")
            return
        
        # Check if any LLM engines are available
        available_engines = self.llm_manager.get_available_engines()
        
        if args[0] == "list":
            try:
                engines, models = self.llm_manager.list_models()
                
                if not engines:
                    print("No LLM engines are currently available.")
                    print("Please run the setup scripts to install LLM components:")
                    print("  bash scripts/setup_llms.sh")
                    return
                    
                print("Available LLM engines and models:")
                for engine in engines:
                    print(f"  - {engine}")
                    if engine in models and models[engine]:
                        for model in models[engine]:
                            print(f"    - {model}")
                    else:
                        print(f"    (No models found for {engine})")
            except Exception as e:
                print(f"Error listing models: {str(e)}")
                print("This may be due to missing LLM components.")
                print("Please run: bash scripts/setup_llms.sh")
        
        elif args[0] == "engines":
            if not available_engines:
                print("No LLM engines are currently available.")
                print("Please run the setup scripts to install LLM components:")
                print("  bash scripts/setup_llms.sh")
                return
                
            print("Available LLM engines:")
            for engine in available_engines:
                print(f"  - {engine}")
        
        elif args[0] == "providers":
            # List all AI providers (both cloud and local)
            providers = self.ai_proxy.get_available_providers()
            
            if not providers:
                print("No AI providers are currently available.")
                print("Please ensure you have API keys for cloud providers or")
                print("run the setup scripts to install local LLM components:")
                print("  bash scripts/setup_llms.sh")
                return
            
            print("Available AI Providers:")
            
            # Group by type
            cloud_providers = [p for p in providers if p['type'] == 'cloud']
            local_providers = [p for p in providers if p['type'] == 'local']
            
            if cloud_providers:
                print("\nCloud Providers:")
                for provider in cloud_providers:
                    print(f"  - {provider['name']} (id: {provider['id']})")
            
            if local_providers:
                print("\nLocal Providers:")
                for provider in local_providers:
                    model_count = provider.get('model_count', 0)
                    print(f"  - {provider['name']} (id: {provider['id']}) - {model_count} models")
            
            # Show recommended provider
            recommended = self.ai_proxy.get_recommended_provider()
            if recommended:
                print(f"\nRecommended provider: {recommended['name']} ({recommended['type']})")
        
        elif args[0] == "query":
            if len(args) < 2:
                print("Usage: llm query <text> [--engine <engine>] [--model <model>]")
                return
            
            if not available_engines:
                print("No LLM engines are currently available.")
                print("Please run the setup scripts to install LLM components:")
                print("  bash scripts/setup_llms.sh")
                return
            
            # Parse arguments
            query_text = args[1]
            engine = self.config['llm']['default_engine']
            model = None
            
            i = 2
            while i < len(args):
                if args[i] == "--engine" and i + 1 < len(args):
                    engine = args[i + 1]
                    i += 2
                elif args[i] == "--model" and i + 1 < len(args):
                    model = args[i + 1]
                    i += 2
                else:
                    query_text += " " + args[i]
                    i += 1
            
            # Check if the specified engine is available
            if engine not in available_engines:
                print(f"Error: Engine '{engine}' is not available.")
                print(f"Available engines: {', '.join(available_engines) if available_engines else 'none'}")
                print("Please run the setup scripts to install LLM components:")
                print("  bash scripts/setup_llms.sh")
                return
            
            if not model:
                model = self.config['llm']['default_model'][engine]
            
            print(f"Querying {engine} (model: {model})...")
            
            try:
                response = self.llm_manager.query(query_text, engine, model)
                print("\nResponse:")
                print(response)
            except Exception as e:
                print(f"Error querying LLM: {str(e)}")
                print("This could be due to missing models or configuration issues.")
        
        elif args[0] == "ai":
            if len(args) < 2:
                print("Usage: llm ai <text> [--provider <provider>] [--system <system_prompt>]")
                return
            
            # Get available providers
            providers = self.ai_proxy.get_available_providers()
            
            if not providers:
                print("No AI providers are available.")
                print("Please ensure you have API keys for cloud providers or")
                print("run the setup scripts to install local LLM components:")
                print("  bash scripts/setup_llms.sh")
                return
            
            # Parse arguments
            query_text = args[1]
            provider_id = None
            system_prompt = ""
            
            i = 2
            while i < len(args):
                if args[i] == "--provider" and i + 1 < len(args):
                    provider_id = args[i + 1]
                    i += 2
                elif args[i] == "--system" and i + 1 < len(args):
                    system_prompt = args[i + 1]
                    i += 2
                else:
                    query_text += " " + args[i]
                    i += 1
            
            # If no provider specified, use recommended
            if not provider_id:
                recommended = self.ai_proxy.get_recommended_provider()
                if recommended:
                    provider_id = recommended['id']
                    print(f"Using recommended provider: {recommended['name']}")
                else:
                    # Use first available provider
                    provider_id = providers[0]['id']
                    print(f"Using available provider: {providers[0]['name']}")
            
            # Check if provider is available
            if not self.ai_proxy.is_provider_available(provider_id):
                print(f"Error: Provider '{provider_id}' is not available.")
                print("Available providers:")
                for p in providers:
                    print(f"  - {p['name']} (id: {p['id']})")
                return
                
            # Query the provider
            print(f"Querying provider: {provider_id}...")
            if system_prompt:
                print(f"Using system prompt: {system_prompt}")
                
            try:
                result = self.ai_proxy.query(provider_id, query_text, system_prompt)
                
                print(f"\nResponse from {result['provider_name']} (took {result['time_taken']}s):")
                print(result['response'])
            except Exception as e:
                print(f"Error querying AI provider: {str(e)}")
        
        elif args[0] == "best":
            if len(args) < 2:
                print("Usage: llm best <text> [--system <system_prompt>]")
                return
            
            # Parse arguments
            query_text = args[1]
            system_prompt = ""
            
            i = 2
            while i < len(args):
                if args[i] == "--system" and i + 1 < len(args):
                    system_prompt = args[i + 1]
                    i += 2
                else:
                    query_text += " " + args[i]
                    i += 1
            
            print("Querying best available AI provider...")
            if system_prompt:
                print(f"Using system prompt: {system_prompt}")
            
            try:
                result = self.ai_proxy.query_with_reasoning(query_text, system_prompt)
                
                print(f"\nResponse from {result['provider_name']} (took {result['time_taken']}s):")
                print(result['response'])
            except Exception as e:
                print(f"Error querying AI: {str(e)}")
        
        else:
            print("Unknown llm command. Use: llm list|engines|query|ai|providers|best")
    
    def do_voice(self, arg):
        """Voice operations
        Usage: voice stt <audio_file>
               voice tts <text> [--output <output_file>]
               voice command <audio_file> [--speak]
               voice listen [<duration>] [--speak]
               voice start
               voice stop"""
        args = shlex.split(arg)
        if not args:
            print("Usage: voice stt|tts|command|listen|start|stop")
            return
        
        if args[0] == "stt":
            if len(args) < 2:
                print("Usage: voice stt <audio_file>")
                return
            
            # Check if Whisper is available
            if not self.whisper.is_available():
                print("Error: Whisper speech-to-text is not available.")
                print("Please run the setup scripts to install voice components:")
                print("  bash scripts/setup_voice.sh")
                return
            
            audio_file = args[1]
            if not os.path.exists(audio_file):
                print(f"Error: Audio file not found: {audio_file}")
                return
            
            print(f"Transcribing audio from {audio_file}...")
            
            try:
                text = self.whisper.transcribe(audio_file)
                print("\nTranscription:")
                print(text)
            except Exception as e:
                print(f"Error during transcription: {str(e)}")
                print("This could be due to missing Whisper models or configuration issues.")
        
        elif args[0] == "tts":
            if len(args) < 2:
                print("Usage: voice tts <text> [--output <output_file>]")
                return
            
            # Check if Piper is available
            if not self.piper.is_available():
                print("Error: Piper text-to-speech is not available.")
                print("Please run the setup scripts to install voice components:")
                print("  bash scripts/setup_voice.sh")
                return
            
            # Parse arguments
            text = args[1]
            output_file = "output.wav"
            
            i = 2
            while i < len(args):
                if args[i] == "--output" and i + 1 < len(args):
                    output_file = args[i + 1]
                    i += 2
                else:
                    text += " " + args[i]
                    i += 1
            
            print(f"Generating speech for: {text}")
            print(f"Output file: {output_file}")
            
            try:
                success = self.piper.synthesize(text, output_file)
                
                if success:
                    print(f"Speech generated successfully: {output_file}")
                else:
                    print("Failed to generate speech. Check Piper configuration.")
            except Exception as e:
                print(f"Error generating speech: {str(e)}")
                print("This could be due to missing Piper models or configuration issues.")
        
        elif args[0] == "command":
            if len(args) < 2:
                print("Usage: voice command <audio_file> [--speak]")
                return
            
            # Check if voice command processing is available
            if not self.voice_cmd.is_available():
                print("Error: Voice command processing is not available.")
                print("Please run the setup scripts to install voice components:")
                print("  bash scripts/setup_voice.sh")
                return
            
            audio_file = args[1]
            if not os.path.exists(audio_file):
                print(f"Error: Audio file not found: {audio_file}")
                return
            
            print(f"Processing voice command from {audio_file}...")
            
            try:
                command, response, success = self.voice_cmd.process_audio_file(audio_file)
                print(f"\nTranscribed command: {command}")
                print(f"Response: {response}")
                
                # Speak the response if requested
                if "--speak" in args:
                    print("Speaking response...")
                    self.voice_cmd.speak_response(response)
            except Exception as e:
                print(f"Error processing voice command: {str(e)}")
        
        elif args[0] == "listen":
            # Check if voice command processing is available
            if not self.voice_cmd.is_available():
                print("Error: Voice command processing is not available.")
                print("Please run the setup scripts to install voice components:")
                print("  bash scripts/setup_voice.sh")
                return
            
            # Default duration is 5 seconds
            duration = 5
            speak_response = False
            
            # Parse args
            for i in range(1, len(args)):
                if args[i] == "--speak":
                    speak_response = True
                elif args[i].isdigit():
                    duration = int(args[i])
            
            print(f"Listening for {duration} seconds...")
            
            try:
                command, response, success = self.voice_cmd.process_mic_input(duration)
                print(f"\nTranscribed command: {command}")
                print(f"Response: {response}")
                
                # Speak the response if requested
                if speak_response:
                    print("Speaking response...")
                    self.voice_cmd.speak_response(response)
            except Exception as e:
                print(f"Error processing voice command: {str(e)}")
        
        elif args[0] == "start":
            # Check if voice command processing is available
            if not self.voice_cmd.is_available():
                print("Error: Voice command processing is not available.")
                print("Please run the setup scripts to install voice components:")
                print("  bash scripts/setup_voice.sh")
                return
            
            if self.voice_cmd.start():
                print("Voice command processor started")
                print("Voice commands will be processed in the background")
                print("Use 'voice stop' to stop the processor")
            else:
                print("Failed to start voice command processor")
        
        elif args[0] == "stop":
            self.voice_cmd.stop()
            print("Voice command processor stopped")
        
        else:
            print("Unknown voice command. Use: voice stt|tts|command|listen|start|stop")
    
    def do_scan(self, arg):
        """Perform network scan
        Usage: scan <target> [--output <output_file>]"""
        args = shlex.split(arg)
        if not args:
            print("Usage: scan <target> [--output <output_file>]")
            return
        
        # Check if Nmap is available
        if not self.nmap.is_available():
            print("Error: Nmap is not available.")
            print("Please install Nmap with: bash scripts/install_deps.sh")
            return
            
        target = args[0]
        output_file = None
        
        i = 1
        while i < len(args):
            if args[i] == "--output" and i + 1 < len(args):
                output_file = args[i + 1]
                i += 2
            else:
                i += 1
        
        print(f"Scanning target: {target}")
        
        try:
            results = self.nmap.scan(target)
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(results)
                print(f"Scan results saved to {output_file}")
            else:
                print("\nScan Results:")
                print(results)
        except Exception as e:
            print(f"Error during scan: {str(e)}")
            print("This could be due to network connectivity issues or insufficient permissions.")
    
    def do_recon(self, arg):
        """Perform reconnaissance
        Usage: recon <target> [--output <output_file>]"""
        args = shlex.split(arg)
        if not args:
            print("Usage: recon <target> [--output <output_file>]")
            return
        
        # Check if required tools are available
        if not self.recon.is_available():
            print("Error: Reconnaissance tools are not available.")
            print("Please run the setup scripts to install required tools:")
            print("  bash scripts/install_deps.sh")
            print("\nRequired tools:")
            print("  - whois: WHOIS domain lookup")
            print("  - dig: DNS lookup utility (dnsutils package)")
            print("  - nmap: Network scanner")
            print("\nOptional tools:")
            print("  - amass: Advanced subdomain enumeration")
            print("  - subfinder: Subdomain discovery tool")
            print("  - whatweb: Web technology identifier")
            return
        
        target = args[0]
        output_file = None
        
        i = 1
        while i < len(args):
            if args[i] == "--output" and i + 1 < len(args):
                output_file = args[i + 1]
                i += 2
            else:
                i += 1
        
        print(f"Performing reconnaissance on target: {target}")
        
        try:
            results = self.recon.scan(target)
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(results)
                print(f"Reconnaissance results saved to {output_file}")
            else:
                print("\nReconnaissance Results:")
                print(results)
        except Exception as e:
            print(f"Error during reconnaissance: {str(e)}")
            print("This could be due to network connectivity issues or target unavailability.")
    
    def do_vuln(self, arg):
        """Perform vulnerability scan
        Usage: vuln <target> [--output <output_file>]"""
        args = shlex.split(arg)
        if not args:
            print("Usage: vuln <target> [--output <output_file>]")
            return
        
        # Check if required tools are available
        if not self.vuln_scanner.is_available():
            print("Error: Vulnerability scanning tools are not available.")
            print("Please run the setup scripts to install required tools:")
            print("  bash scripts/install_deps.sh")
            print("\nRequired tools:")
            print("  - nmap: Network mapper and vulnerability scanner")
            print("\nOptional tools:")
            print("  - nikto: Web server vulnerability scanner")
            print("  - sslscan: SSL/TLS configuration analyzer")
            return
            
        target = args[0]
        output_file = None
        
        i = 1
        while i < len(args):
            if args[i] == "--output" and i + 1 < len(args):
                output_file = args[i + 1]
                i += 2
            else:
                i += 1
        
        print(f"Performing vulnerability scan on target: {target}")
        
        try:
            results = self.vuln_scanner.scan(target)
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(results)
                print(f"Vulnerability scan results saved to {output_file}")
            else:
                print("\nVulnerability Scan Results:")
                print(results)
        except Exception as e:
            print(f"Error during vulnerability scan: {str(e)}")
            print("This could be due to network connectivity issues or target unavailability.")
    
    def do_tools(self, arg):
        """Tool management operations
        Usage: tools list
               tools scan
               tools info <tool_name>
               tools install <tool_name|category>
               tools categories"""
               
    def do_agent(self, arg):
        """Agent system operations
        Usage: agent status
               agent create <type> <name> <target>
               agent list
               agent run <agent_id>
               agent stop <agent_id>
               agent report <agent_id>"""
        args = shlex.split(arg)
        if not args:
            print("Usage: agent status|create|list|run|stop|report")
            return
            
        # Check if agent system is available
        if not AGENT_SYSTEM_AVAILABLE or not self.agent_manager:
            print("Error: Agent system is not available")
            print("Please check that all agent components are properly installed")
            return
            
        if args[0] == "status":
            # Show agent system status
            print("Agent System Status:")
            print(f"Available: {'Yes' if AGENT_SYSTEM_AVAILABLE else 'No'}")
            
            if self.agent_manager:
                agent_count = len(self.agent_manager.list_agents())
                print(f"Active Agents: {agent_count}")
                print(f"Agent Types: recon, security")
            
        elif args[0] == "list":
            # List all agents
            agents = self.agent_manager.list_agents()
            
            if not agents:
                print("No active agents found")
                return
                
            print(f"Found {len(agents)} active agents:")
            for agent in agents:
                print(f"  ID: {agent['id']}")
                print(f"  Name: {agent['name']}")
                print(f"  Description: {agent['description']}")
                print(f"  Status: {agent['status']}")
                print(f"  Created: {agent['created_at']}")
                print()
        
        elif args[0] == "create" and len(args) >= 4:
            # Create a new agent
            agent_type = args[1]
            agent_name = args[2]
            target = args[3]
            
            # Validate agent type
            if agent_type not in ["recon", "security"]:
                print(f"Error: Unknown agent type '{agent_type}'")
                print("Available types: recon, security")
                return
            
            print(f"Creating {agent_type} agent '{agent_name}' targeting {target}...")
            
            description = f"Auto-generated {agent_type} agent for target {target}"
            
            try:
                # Create the agent
                agent = None
                if agent_type == "recon":
                    agent = self.agent_manager.create_agent(
                        agent_type="recon",
                        name=agent_name,
                        description=description
                    )
                    
                    # Set target using the ReconAgent specific method
                    if agent:
                        agent.set_target(target)
                        
                elif agent_type == "security":
                    agent = self.agent_manager.create_agent(
                        agent_type="security",
                        name=agent_name,
                        description=description
                    )
                    
                    # Set target using the SecurityAgent specific method
                    if agent:
                        agent.set_target(target)
                
                if agent:
                    print(f"Agent created successfully with ID: {agent.agent_id}")
                    print("Use 'agent run <agent_id>' to execute the agent")
                else:
                    print("Failed to create agent")
            except Exception as e:
                print(f"Error creating agent: {str(e)}")
        
        elif args[0] == "run" and len(args) > 1:
            # Run an agent
            agent_id = args[1]
            agent = self.agent_manager.get_agent(agent_id)
            
            if not agent:
                print(f"Error: Agent not found with ID {agent_id}")
                print("Use 'agent list' to see available agents")
                return
                
            print(f"Running agent '{agent.name}' ({agent_id})...")
            print("This may take some time depending on the agent's tasks")
            
            # Run in async mode by default
            async_run = True
            if len(args) > 2 and args[2] == "--sync":
                async_run = False
                print("Running in synchronous mode")
            
            try:
                result = self.agent_manager.run_agent(agent_id, async_run=async_run)
                
                if async_run:
                    print(f"Agent is running in the background")
                    print("Use 'agent status' to check progress")
                else:
                    success = result
                    print(f"Agent execution {'completed successfully' if success else 'failed'}")
                    print("Check 'results/' directory for output files")
            except Exception as e:
                print(f"Error running agent: {str(e)}")
        
        elif args[0] == "stop" and len(args) > 1:
            # Stop an agent
            agent_id = args[1]
            
            print(f"Stopping agent {agent_id}...")
            
            try:
                success = self.agent_manager.stop_agent(agent_id)
                if success:
                    print(f"Agent stopped successfully")
                else:
                    print(f"Failed to stop agent")
            except Exception as e:
                print(f"Error stopping agent: {str(e)}")
        
        elif args[0] == "report" and len(args) > 1:
            # Generate report from agent
            agent_id = args[1]
            agent = self.agent_manager.get_agent(agent_id)
            
            if not agent:
                print(f"Error: Agent not found with ID {agent_id}")
                print("Use 'agent list' to see available agents")
                return
            
            print(f"Generating report for agent '{agent.name}' ({agent_id})...")
            
            try:
                # Check if agent has a generate_report method
                if hasattr(agent, 'generate_report') and callable(getattr(agent, 'generate_report')):
                    report = agent.generate_report()
                    
                    if "error" in report:
                        print(f"Error generating report: {report['error']}")
                    else:
                        print("Report generated successfully")
                        
                        if "saved_to" in report:
                            print(f"Report saved to: {report['saved_to']}")
                            
                        # Print summary if available
                        if "executive_summary" in report and "summary" in report["executive_summary"]:
                            print("\nExecutive Summary:")
                            print(report["executive_summary"]["summary"])
                else:
                    print(f"Error: Agent type '{agent.__class__.__name__}' does not support report generation")
            except Exception as e:
                print(f"Error generating report: {str(e)}")
        
        else:
            print("Unknown agent command or missing parameters")
            print("Usage: agent status|create|list|run|stop|report")
    
    def do_help(self, arg):
        """List available commands with 'help' or detailed help with 'help cmd'"""
        if arg:
            # Display help for specific command
            super().do_help(arg)
        else:
            # Display categorized help
            print("\nAvailable Commands:")
            
            print("\nSystem Commands:")
            print("  config       - Show or edit configuration")
            print("  system       - System utilities and information")
            print("  exit/quit    - Exit the program")
            
            print("\nLLM Commands:")
            print("  llm list     - List available LLM engines and models")
            print("  llm engines  - List available LLM engines")
            print("  llm query    - Query an LLM")
            
            print("\nVoice Commands:")
            print("  voice stt    - Speech to text conversion")
            print("  voice tts    - Text to speech conversion")
            
            print("\nSecurity Commands:")
            print("  scan         - Perform network scan")
            print("  recon        - Perform reconnaissance")
            print("  vuln         - Perform vulnerability scan")
            print("  tools        - Manage security tools")
            print("  agent        - Control autonomous agent system")
            
            print("\nFor detailed help on a specific command, type: help <command>")
