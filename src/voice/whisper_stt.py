#!/usr/bin/env python3
# G3r4ki Whisper Speech-to-Text integration

import os
import subprocess
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger('g3r4ki.voice.whisper')

class WhisperSTT:
    """Interface for OpenAI's Whisper speech-to-text"""
    
    def __init__(self, config):
        self.config = config
        self.whisper_dir = config['paths']['whisper_dir']
        self.model = config['voice']['whisper_model']
        
        # Check if whisper.cpp is installed
        if not os.path.exists(self.whisper_dir):
            logger.warning(f"Whisper directory not found at {self.whisper_dir}")
            logger.info("You may need to run setup_voice.sh to install Whisper")
    
    def is_available(self):
        """Check if Whisper is available"""
        whisper_main = os.path.join(self.whisper_dir, "main")
        return os.path.exists(whisper_main) and os.access(whisper_main, os.X_OK)
    
    def transcribe(self, audio_file):
        """
        Transcribe audio file to text using Whisper
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Transcribed text or error message
        """
        if not self.is_available():
            logger.error("Whisper is not available. Run setup_voice.sh to install it.")
            return "Error: Whisper is not installed or configured properly."
        
        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return f"Error: Audio file not found: {audio_file}"
        
        # Prepare command
        whisper_main = os.path.join(self.whisper_dir, "main")
        model_path = os.path.join(self.whisper_dir, f"models/ggml-{self.model}.bin")
        
        # Check if model exists, download if not
        if not os.path.exists(model_path):
            logger.info(f"Whisper model not found, downloading {self.model}...")
            model_dir = os.path.dirname(model_path)
            os.makedirs(model_dir, exist_ok=True)
            
            download_script = os.path.join(self.whisper_dir, "models/download-ggml-model.sh")
            if not os.path.exists(download_script):
                logger.error("Whisper model download script not found")
                return "Error: Whisper model download script not found"
            
            try:
                subprocess.run(
                    ["bash", download_script, self.model],
                    cwd=model_dir,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to download Whisper model: {e}")
                return f"Error: Failed to download Whisper model: {e}"
        
        # Create temp file for output
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            output_file = tmp.name
        
        try:
            # Run Whisper
            logger.info(f"Transcribing {audio_file} with Whisper...")
            subprocess.run(
                [
                    whisper_main,
                    "-m", model_path,
                    "-f", audio_file,
                    "-otxt",
                    "-of", output_file
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Read transcription
            with open(output_file, 'r') as f:
                transcription = f.read().strip()
            
            return transcription
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Whisper transcription failed: {e}")
            logger.error(f"STDERR: {e.stderr.decode('utf-8')}")
            return f"Error: Whisper transcription failed: {e.stderr.decode('utf-8')}"
        finally:
            # Clean up temp file
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def transcribe_microphone(self, duration=5):
        """
        Record audio from microphone and transcribe
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Transcribed text or error message
        """
        if not self.is_available():
            logger.error("Whisper is not available. Run setup_voice.sh to install it.")
            return "Error: Whisper is not installed or configured properly."
        
        # Check if we have arecord
        if not os.system("which arecord > /dev/null") == 0:
            logger.error("arecord not found. Install with: sudo apt install alsa-utils")
            return "Error: arecord not found. Install with: sudo apt install alsa-utils"
        
        # Create temp file for recording
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio_file = tmp.name
        
        try:
            # Record audio
            logger.info(f"Recording audio for {duration} seconds...")
            print(f"Recording for {duration} seconds...")
            
            subprocess.run(
                [
                    "arecord",
                    "-f", "cd",
                    "-d", str(duration),
                    audio_file
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            print("Recording complete, transcribing...")
            
            # Transcribe
            return self.transcribe(audio_file)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Recording or transcription failed: {e}")
            logger.error(f"STDERR: {e.stderr.decode('utf-8')}")
            return f"Error: Recording or transcription failed: {e.stderr.decode('utf-8')}"
        finally:
            # Clean up temp file
            if os.path.exists(audio_file):
                os.unlink(audio_file)
