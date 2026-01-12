"""
Simple test script for MeloTTS Chinese TTS
"""
import os
import sys

# Fix OpenMP conflict on Windows
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Add MeloTTS to path
MELOTTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'MeloTTS')
sys.path.insert(0, MELOTTS_PATH)

print("Loading MeloTTS...")
from melo.api import TTS

# Initialize model
print("Initializing Chinese model...")
model = TTS(language='ZH', device='cpu')

# Get speaker
speaker_ids = model.hps.data.spk2id
print(f"Available speakers: {speaker_ids}")

# Test TTS
test_text = "你好，欢迎光临"  # Hello, welcome
output_path = "test_output.wav"

print(f"Generating speech for: {test_text}")
try:
    model.tts_to_file(test_text, speaker_ids['ZH'], output_path, speed=1.0, quiet=True)
    print(f"Success! Audio saved to: {output_path}")
    print(f"File size: {os.path.getsize(output_path)} bytes")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
