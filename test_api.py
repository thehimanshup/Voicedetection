import urllib.request
import json
import base64
import time
import sys

API_URL = "http://127.0.0.1:5000/api/voice-detection"
API_KEY = "rocketdesk_test_4092002"

def create_dummy_audio():
    # Create a minimal valid MP3 frame (silence) or just random bytes if we can't easily generate MP3
    # For now, let's try sending a WAV header and content, usually librosa/ffmpeg handles it even with wrong extension
    # RIFF header for WAV
    import wave
    import io
    
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(44100)
        wav_file.writeframes(b'\x00\x00' * 44100) # 1 second of silence
    
    return buffer.getvalue()

def test_api():
    print("Testing API...")
    
    audio_bytes = create_dummy_audio()
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    payload = {
        "language": "English",
        "audioFormat": "mp3",
        "audioBase64": audio_base64
    }
    
    data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(API_URL, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('x-api-key', API_KEY)
    
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            response_body = response.read().decode('utf-8')
            print(f"Status Code: {status_code}")
            print(f"Response: {response_body}")
            
            if status_code == 200:
                print("SUCCESS: API responded correctly.")
            else:
                print("FAILURE: Unexpected status code.")
                
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(e.read().decode('utf-8'))
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Wait for server to start if run immediately
    time.sleep(2) 
    test_api()
