# AI Voice Detection API

This project provides a REST API to detect AI-generated voices in 5 supported languages (Tamil, English, Hindi, Malayalam, Telugu).

## Features
- **Strict API Key Authentication**
- **Base64 MP3 Audio Input**
- **Heuristic-based Voice Analysis** (Spectral Flatness, Pitch Stability)
- **JSON Response** with Confidence Score

## Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd voice-detection
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Running the API

Start the Flask server:
```bash
python app.py
```
The API will run on `http://localhost:5000`.

## API Usage

### Endpoint
`POST /api/voice-detection`

### Headers
- `Content-Type: application/json`
- `x-api-key: rocketdesk_test_4092002` (Default key for testing)

### Request Body
```json
{
  "language": "English",
  "audioFormat": "mp3",
  "audioBase64": "<BASE64_ENCODED_MP3_STRING>"
}
```

### Response
```json
{
  "status": "success",
  "language": "English",
  "classification": "HUMAN",
  "confidenceScore": 0.85,
  "explanation": "Natural pausing; High signal variance (Human-like)"
}
```

## Testing

Run the included test script:
```bash
python test_api.py
```

## Deployment

To deploy, ensure you set the `API_KEY` environment variable and use a production WSGI server like `gunicorn`:
```bash
gunicorn app:app
```
