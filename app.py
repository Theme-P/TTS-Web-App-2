"""
Web Application for Thai-Chinese TTS
"""

import os
from flask import Flask, render_template, request, jsonify

# Import services (now in the same directory)
from translation_service import TranslationService, TranslationError
from tts_service import TTSService, TTSError

app = Flask(__name__)

# Initialize services
# Output dir relative to WebApp static folder
current_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(current_dir, 'static', 'audio')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize with OUTPUT_DIR
translation_service = TranslationService()
tts_service = TTSService(output_dir=OUTPUT_DIR)

@app.route('/')
def index():
    """Render main interface"""
    return render_template('index.html')

@app.route('/api/voices')
def get_voices():
    """Get available Chinese voices"""
    voices = []
    for key, data in tts_service.get_voices().items():
        voices.append({
            'id': key,
            'name': data['name'],
            'label': data['label']
        })
    return jsonify(voices)

@app.route('/api/convert', methods=['POST'])
def convert():
    """
    Process: Thai Text -> Chinese Text -> Audio
    """
    data = request.json
    thai_text = data.get('text', '').strip()
    voice_choice = data.get('voice', '1') # Default to first voice

    if not thai_text:
        return jsonify({'error': 'No text provided'}), 400

    # 1. Translate
    try:
        chinese_text, mechanism = translation_service.translate(thai_text)
    except TranslationError as e:
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

    # 2. TTS
    voice_name = tts_service.get_voice_name(voice_choice)
    if not voice_name:
        voice_name = 'zh-CN-XiaoxiaoNeural' # Fallback

    try:
         filepath = tts_service.generate_speech(chinese_text, voice_name)
         filename = os.path.basename(filepath)
         
         # Return result
         return jsonify({
             'thai': thai_text,
             'chinese': chinese_text,
             'audio_url': f'/static/audio/{filename}',
             'translator': mechanism
         })
         
    except TTSError as e:
        return jsonify({'error': f'TTS generation failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    