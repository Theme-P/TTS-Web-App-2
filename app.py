"""
Web Application for Thai-Chinese TTS with MeloTTS
"""

import os
from flask import Flask, render_template, request, jsonify

# Import services (now in the same directory)
from translation_service import TranslationService, TranslationError
from melo_tts_service import MeloTTSService, TTSError

app = Flask(__name__)

# Initialize services
# Output dir relative to WebApp static folder
current_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(current_dir, 'static', 'audio')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize with OUTPUT_DIR
translation_service = TranslationService()
tts_service = MeloTTSService(output_dir=OUTPUT_DIR)

@app.route('/')
def index():
    """Render main interface"""
    return render_template('index.html')

@app.route('/api/convert', methods=['POST'])
def convert():
    """
    Process: Thai Text -> Chinese Text -> Audio (MeloTTS)
    """
    data = request.json
    thai_text = data.get('text', '').strip()
    speed = data.get('speed', 1.0)  # Default speed 1.0
    
    # Validate speed range
    try:
        speed = float(speed)
        speed = max(0.5, min(2.0, speed))  # Clamp to 0.5-2.0
    except (ValueError, TypeError):
        speed = 1.0

    if not thai_text:
        return jsonify({'error': 'No text provided'}), 400

    # 1. Translate Thai -> Chinese
    try:
        chinese_text, mechanism = translation_service.translate(thai_text)
    except TranslationError as e:
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

    # 2. TTS with MeloTTS
    try:
         filepath = tts_service.generate_speech(chinese_text, speed=speed)
         filename = os.path.basename(filepath)
         
         # Return result
         return jsonify({
             'thai': thai_text,
             'chinese': chinese_text,
             'audio_url': f'/static/audio/{filename}',
             'translator': mechanism,
             'tts_engine': 'MeloTTS',
             'speed': speed
         })
         
    except TTSError as e:
        return jsonify({'error': f'TTS generation failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)