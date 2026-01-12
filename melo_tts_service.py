"""
TTS Service - MeloTTS Speech Synthesis
Chinese text-to-speech with voice selection using MeloTTS
"""

import os
import sys

# Fix OpenMP conflict on Windows
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from datetime import datetime
from typing import Dict, Optional, List

from melo.api import TTS


class MeloTTSService:
    """Chinese Text-to-Speech Service using MeloTTS"""
    
    def __init__(self, output_dir: str = 'output', device: str = 'auto'):
        """
        Initialize MeloTTS service
        
        Args:
            output_dir: Directory to save audio files
            device: 'auto', 'cpu', 'cuda', or 'mps'
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize MeloTTS model for Chinese
        print("Loading MeloTTS Chinese model...")
        self._model = TTS(language='ZH', device=device)
        
        # Get available speakers from model
        self._speaker_ids = self._model.hps.data.spk2id
        self._speakers = list(self._speaker_ids.keys())
        
        # Create voice mapping for API compatibility
        self._voices = self._build_voice_mapping()
        print(f"MeloTTS loaded. Available speakers: {self._speakers}")
    
    def _build_voice_mapping(self) -> Dict[str, Dict[str, str]]:
        """Build voice mapping from MeloTTS speakers"""
        voices = {}
        labels = {
            'ZH': 'Chinese Female',
        }
        
        for idx, speaker in enumerate(self._speakers, 1):
            key = str(idx)
            label = labels.get(speaker, speaker)
            voices[key] = {
                'name': speaker,
                'label': label,
                'speaker_id': self._speaker_ids[speaker]
            }
        
        return voices
    
    def get_voices(self) -> Dict[str, Dict[str, str]]:
        """Get available voices"""
        return self._voices
    
    def get_voice_labels(self) -> List[str]:
        """Get formatted voice labels for display"""
        return [f"{key}. {v['label']}" for key, v in self._voices.items()]
    
    def get_voice_name(self, choice: str) -> Optional[str]:
        """Get voice name from choice number"""
        if choice in self._voices:
            return self._voices[choice]['name']
        return None
    
    def get_speaker_id(self, choice: str) -> Optional[int]:
        """Get speaker ID from choice number"""
        if choice in self._voices:
            return self._voices[choice]['speaker_id']
        return None
    
    def is_valid_choice(self, choice: str) -> bool:
        """Check if voice choice is valid"""
        return choice in self._voices
    
    def generate_speech(self, text: str, speed: float = 1.0) -> str:
        """
        Generate speech from Chinese text using MeloTTS.
        
        Args:
            text: Chinese text to synthesize
            speed: Speech speed (0.5-2.0)
        
        Returns:
            filepath to generated audio (WAV format)
        """
        if not text.strip():
            raise TTSError("Text cannot be empty")
        
        # Use first (and only) Chinese speaker
        speaker_id = self._speaker_ids[self._speakers[0]]
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"melo_tts_{timestamp}.wav"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # Generate speech with MeloTTS
            self._model.tts_to_file(
                text=text,
                speaker_id=speaker_id,
                output_path=filepath,
                speed=speed,
                quiet=True
            )
            return filepath
        except Exception as e:
            raise TTSError(f"Failed to generate speech: {e}")
    
    def get_file_size_kb(self, filepath: str) -> float:
        """Get file size in KB"""
        return os.path.getsize(filepath) / 1024


class TTSError(Exception):
    """Custom exception for TTS errors"""
    pass
