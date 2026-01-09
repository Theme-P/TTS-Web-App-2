"""
TTS Service - Edge TTS Speech Synthesis
Chinese text-to-speech with voice selection
"""

import edge_tts
import asyncio
import os
from datetime import datetime
from typing import List, Dict, Optional

class TTSService:
    """Chinese Text-to-Speech Service using Edge TTS"""
    
    # Available Chinese voices
    VOICES = {
        '1': {'name': 'zh-CN-XiaoxiaoNeural', 'label': 'Xiaoxiao (Female - Warm)'},
        '2': {'name': 'zh-CN-XiaoyiNeural', 'label': 'Xiaoyi (Female - Lively)'},
        '3': {'name': 'zh-CN-YunxiaNeural', 'label': 'Yunxia (Female - Cute)'},
        '4': {'name': 'zh-CN-YunxiNeural', 'label': 'Yunxi (Male - Sunshine)'},
        '5': {'name': 'zh-CN-YunjianNeural', 'label': 'Yunjian (Male - Passionate)'},
        '6': {'name': 'zh-CN-YunyangNeural', 'label': 'Yunyang (Male - Professional)'},
    }
    
    def __init__(self, output_dir: str = 'output'):
        """Initialize TTS service with output directory"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def get_voices(self) -> Dict[str, Dict[str, str]]:
        """Get available voices"""
        return self.VOICES
    
    def get_voice_labels(self) -> List[str]:
        """Get formatted voice labels for display"""
        return [f"{key}. {v['label']}" for key, v in self.VOICES.items()]
    
    def get_voice_name(self, choice: str) -> Optional[str]:
        """Get voice name from choice number"""
        if choice in self.VOICES:
            return self.VOICES[choice]['name']
        return None
    
    def is_valid_choice(self, choice: str) -> bool:
        """Check if voice choice is valid"""
        return choice in self.VOICES
    
    async def generate_speech_async(self, text: str, voice_name: str) -> str:
        """
        Generate speech from Chinese text.
        Returns: filepath to generated audio
        """
        if not text.strip():
            raise TTSError("Text cannot be empty")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"th_cn_tts_{timestamp}.mp3"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            communicate = edge_tts.Communicate(text, voice_name)
            await communicate.save(filepath)
            return filepath
        except Exception as e:
            raise TTSError(f"Failed to generate speech: {e}")
    
    def generate_speech(self, text: str, voice_name: str) -> str:
        """
        Synchronous wrapper for speech generation.
        Returns: filepath to generated audio
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.generate_speech_async(text, voice_name))
        finally:
            loop.close()
    
    def get_file_size_kb(self, filepath: str) -> float:
        """Get file size in KB"""
        return os.path.getsize(filepath) / 1024


class TTSError(Exception):
    """Custom exception for TTS errors"""
    pass

 