import os
import io
import base64
import json
import logging
import tempfile
from flask import Flask, request, jsonify
from model import VoiceDetector

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_KEY = "rocketdesk_test_4092002"  # In production, use os.environ.get("API_KEY")

detector = VoiceDetector()

@app.route('/api/voice-detection', methods=['POST'])
def detect_voice():
    try:
        # 1. API Key Validation
        api_key = request.headers.get('x-api-key')
        if not api_key or api_key != API_KEY:
            return jsonify({
                "status": "error",
                "message": "Invalid or missing API key"
            }), 401
        
        # 2. Request Parsing
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON body"}), 400
            
        language = data.get('language')
        audio_format = data.get('audioFormat')
        audio_base64 = data.get('audioBase64')
        
        # 3. Validation
        if not all([language, audio_format, audio_base64]):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
            
        if audio_format.lower() != 'mp3':
            return jsonify({"status": "error", "message": "Only mp3 format is supported"}), 400

        # 4. Decode Audio
        try:
            audio_bytes = base64.b64decode(audio_base64)
        except Exception:
            return jsonify({"status": "error", "message": "Invalid base64 string"}), 400

        # 5. Process Audio (Save to temp file for Librosa)
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
            temp_path = temp_audio.name
            temp_audio.write(audio_bytes)
            
        try:
            # 6. Analyze
            result = detector.predict(temp_path)
            
            # 7. Cleanup
            os.remove(temp_path)
            
            # 8. Response
            return jsonify({
                "status": "success",
                "language": language,
                "classification": result['classification'],
                "confidenceScore": result['confidenceScore'],
                "explanation": result['explanation']
            }), 200

        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error(f"Analysis error: {str(e)}")
            return jsonify({"status": "error", "message": f"Analysis failed: {str(e)}"}), 500

    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
