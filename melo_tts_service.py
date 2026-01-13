"""
TTS Service - MeloTTS Speech Synthesis
Chinese text-to-speech with voice selection using MeloTTS
Optimized with lazy loading and automatic cleanup
"""

import os
import sys
import io
from pathlib import Path

# Fix OpenMP conflict on Windows
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from typing import Dict, Optional, List

from melo.api import TTS


class MeloTTSService:
    """Chinese Text-to-Speech Service using MeloTTS with Lazy Loading"""
    
    def __init__(self, device: str = 'auto'):
        """
        Initialize MeloTTS service
        
        Args:
            device: 'auto', 'cpu', 'cuda', or 'mps'
        """
        self.device = device
        
        # Lazy initialization
        self._model = None
        self._speaker_ids = None
        self._speakers = None
        self._voices = None
    
    @property
    def model(self):
        """Lazy initialization of MeloTTS model"""
        if self._model is None:
            print("Loading MeloTTS Chinese model...")
            self._model = TTS(language='ZH', device=self.device)
            
            # Get available speakers from model
            self._speaker_ids = self._model.hps.data.spk2id
            self._speakers = list(self._speaker_ids.keys())
            
            # Create voice mapping for API compatibility
            self._voices = self._build_voice_mapping()
            print(f"MeloTTS loaded. Available speakers: {self._speakers}")
        return self._model
    
    def _build_voice_mapping(self) -> Dict[str, Dict[str, str]]:
        """Build voice mapping from MeloTTS speakers"""
        if self._speaker_ids is None:
            # Trigger model loading
            _ = self.model
        
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
        if self._voices is None:
            # Trigger model loading
            _ = self.model
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
        if self._voices is None:
            _ = self.model
        return choice in self._voices
    
    def generate_speech(self, text: str, speed: float = 1.0) -> bytes:
        """
        Generate speech from Chinese text using MeloTTS.
        
        Args:
            text: Chinese text to synthesize
            speed: Speech speed (0.5-2.0)
        
        Returns:
            Audio data as bytes (WAV format)
        """
        if not text.strip():
            raise TTSError("Text cannot be empty")
        
        # Trigger model loading if needed
        model = self.model
        
        # Use first (and only) Chinese speaker
        speaker_id = self._speaker_ids[self._speakers[0]]
        
        # Create temporary file in memory
        import tempfile
        try:
            # Create a temporary file to capture MeloTTS output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            # Generate speech with MeloTTS to temp file
            model.tts_to_file(
                text=text,
                speaker_id=speaker_id,
                output_path=tmp_path,
                speed=speed,
                quiet=True
            )
            
            # Read the audio file into memory
            with open(tmp_path, 'rb') as f:
                audio_bytes = f.read()
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            return audio_bytes
        except Exception as e:
            # Clean up temp file on error
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise TTSError(f"Failed to generate speech: {e}")
    
    def shutdown(self):
        """Cleanup resources"""
        # Clear model from memory
        self._model = None
        self._speaker_ids = None
        self._speakers = None
        self._voices = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.shutdown()
        return False


class TTSError(Exception):
    """Custom exception for TTS errors"""
    pass
