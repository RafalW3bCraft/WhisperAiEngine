#!/usr/bin/env python3
# G3r4ki Piper Text-to-Speech integration

import os
import subprocess
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger('g3r4ki.voice.piper')

class PiperTTS:
    """Interface for Piper text-to-speech"""
    
    def __init__(self, config):
        self.config = config
        self.piper_dir = config['paths']['piper_dir']
        self.model = config['voice']['piper_model']
        
        # Check if piper is installed
        if not os.path.exists(self.piper_dir):
            logger.warning(f"Piper directory not found at {self.piper_dir}")
            logger.info("You may need to run setup_voice.sh to install Piper")
    
    def is_available(self):
        """Check if Piper is available"""
        piper_executable = os.path.join(self.piper_dir, "piper")
        return os.path.exists(piper_executable) and os.access(piper_executable, os.X_OK)
    
    def synthesize(self, text, output_file, model=None):
        """
        Synthesize text to speech using Piper
        
        Args:
            text: Text to synthesize
            output_file: Path to save audio file
            model: Optional model name (defaults to config)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.error("Piper is not available. Run setup_voice.sh to install it.")
            return False
        
        if not text:
            logger.error("No text provided for synthesis")
            return False
        
        # Use provided model or default from config
        model_name = model if model else self.model
        
        # Prepare paths
        piper_executable = os.path.join(self.piper_dir, "piper")
        model_dir = os.path.join(self.piper_dir, "voices")
        model_path = os.path.join(model_dir, f"{model_name}.onnx")
        model_json = os.path.join(model_dir, f"{model_name}.onnx.json")
        
        # Check if model exists
        if not (os.path.exists(model_path) and os.path.exists(model_json)):
            logger.error(f"Piper model not found: {model_name}")
            logger.info("Available models:")
            
            if os.path.exists(model_dir):
                for file in os.listdir(model_dir):
                    if file.endswith('.onnx'):
                        logger.info(f"  - {file[:-5]}")
            
            return False
        
        # Create temp file for text
        with tempfile.NamedTemporaryFile(mode='w', suffix=".txt", delete=False) as tmp:
            tmp.write(text)
            text_file = tmp.name
        
        try:
            # Run Piper
            logger.info(f"Synthesizing speech with Piper model {model_name}...")
            subprocess.run(
                [
                    piper_executable,
                    "--model", model_path,
                    "--output-raw",
                    "--text-file", text_file,
                    "--output-file", output_file
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info(f"Speech synthesized to {output_file}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Piper synthesis failed: {e}")
            logger.error(f"STDERR: {e.stderr.decode('utf-8')}")
            return False
        finally:
            # Clean up temp file
            if os.path.exists(text_file):
                os.unlink(text_file)
    
    def list_models(self):
        """List available Piper models
        
        Returns:
            List of available model names
        """
        if not self.is_available():
            logger.error("Piper is not available. Run setup_voice.sh to install it.")
            return []
        
        model_dir = os.path.join(self.piper_dir, "voices")
        
        if not os.path.exists(model_dir):
            logger.warning(f"Piper voices directory not found: {model_dir}")
            return []
        
        models = []
        for file in os.listdir(model_dir):
            if file.endswith('.onnx'):
                models.append(file[:-5])
        
        return models
    
    def speak(self, text, model=None):
        """
        Synthesize and play speech
        
        Args:
            text: Text to speak
            model: Optional model name (defaults to config)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.error("Piper is not available. Run setup_voice.sh to install it.")
            return False
        
        # Check if we have play command
        if not os.system("which play > /dev/null") == 0:
            logger.error("play command not found. Install with: sudo apt install sox")
            return False
        
        # Create temp file for audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio_file = tmp.name
        
        try:
            # Synthesize speech
            success = self.synthesize(text, audio_file, model)
            
            if not success:
                logger.error("Failed to synthesize speech")
                return False
            
            # Play audio
            logger.info("Playing synthesized speech...")
            subprocess.run(
                ["play", audio_file],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to play audio: {e}")
            return False
        finally:
            # Clean up temp file
            if os.path.exists(audio_file):
                os.unlink(audio_file)
