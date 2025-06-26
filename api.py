from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
from main import transcribe_audio_file
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Ensure directories exist
FILES_DIR = Path("files")
TRANSCRIPTS_DIR = Path("transcripts")
FILES_DIR.mkdir(exist_ok=True)
TRANSCRIPTS_DIR.mkdir(exist_ok=True)

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    """Handle file upload and transcription"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get API key from headers
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'API key required'}), 401
        
        api_key = auth_header.split(' ')[1]
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            file.save(tmp_file.name)
            temp_path = tmp_file.name
        
        try:
            # Set API key in environment for this request
            os.environ['ELEVENLABS_API_KEY'] = api_key
            
            # Transcribe the file
            result = transcribe_audio_file(temp_path)
            
            if result:
                # Save file to files directory
                file_path = FILES_DIR / file.filename
                with open(file_path, 'wb') as f:
                    file.seek(0)  # Reset file pointer
                    f.write(file.read())
                
                return jsonify(result)
            else:
                return jsonify({'error': 'Transcription failed'}), 500
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-transcript', methods=['POST'])
def save_transcript():
    """Save transcript to backend"""
    try:
        data = request.json
        filename = data.get('filename')
        transcript = data.get('transcript')
        
        if not filename or not transcript:
            return jsonify({'error': 'Missing filename or transcript'}), 400
        
        # Save transcript as JSON
        transcript_filename = os.path.splitext(filename)[0] + '.json'
        transcript_path = TRANSCRIPTS_DIR / transcript_filename
        
        with open(transcript_path, 'w', encoding='utf-8') as f:
            json.dump(transcript, f, indent=2, ensure_ascii=False)
        
        return jsonify({'message': 'Transcript saved successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Transcription API is running'})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 