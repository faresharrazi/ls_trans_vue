# Audio/Video Transcription Tool

Modern web application for transcribing audio and video files using ElevenLabs Speech-to-Text API with interactive playback features.

## Features

- 🎨 **Modern Vue.js Frontend** - Beautiful, responsive UI
- 🔑 **Secure API Key Management** - Password-style input with local storage
- 📁 **Drag & Drop Upload** - Easy file upload with visual feedback
- 🎬 **Interactive Media Player** - Built-in audio/video player with transcript sync
- 📝 **Real-time Transcription** - Live progress tracking
- 🎯 **Click to Seek** - Click any sentence to jump to that moment in the media
- ✨ **Live Highlighting** - Transcript highlights in sync with media playback
- 📥 **Multiple Export Formats** - JSON, TXT, SRT downloads
- ⚡ **Fast Processing** - Optimized backend with Flask

## Quick Start

### Option 1: One-Command Setup

```bash
./start.sh
```

### Option 2: Manual Setup

1. **Install Dependencies**

   ```bash
   # Backend dependencies
   pip install -r requirements.txt

   # Frontend dependencies
   cd frontend
   npm install
   ```

2. **Start Backend**

   ```bash
   python api.py
   ```

3. **Start Frontend**

   ```bash
   cd frontend
   npm run dev
   ```

4. **Open Application**
   - Frontend: http://localhost:5173
   - Backend: http://localhost:5000

## How to Use

1. **Enter API Key** - Add your ElevenLabs API key in the secure input field
2. **Upload Media** - Drag & drop or click to upload audio/video files
3. **Generate Transcript** - Click the generate button to start transcription
4. **Interactive Playback** - Play the media and watch the transcript highlight in real-time
5. **Click to Seek** - Click any sentence in the transcript to jump to that moment
6. **Download** - Export in JSON, TXT, or SRT formats

## Interactive Features

- **Real-time Highlighting**: As the media plays, the current sentence is highlighted in blue
- **Click to Seek**: Click any sentence to jump directly to that timestamp in the media
- **Sentence Segmentation**: Transcript is automatically split by full stops for easy navigation

## Supported Formats

- **Audio**: MP3, WAV, M4A, FLAC, AAC, OGG
- **Video**: MP4, AVI, MOV, MKV, WebM, FLV

## Project Structure

```
ls_trans_vue/
├── api.py                 # Flask backend API
├── main.py               # Core transcription functions
├── config.py             # API configuration
├── auto_transcribe.py    # Batch processing script
├── requirements.txt      # Python dependencies
├── start.sh             # Startup script
├── files/               # Uploaded media files
├── transcripts/         # Generated transcripts
└── frontend/            # Vue.js frontend
    ├── src/
    │   ├── components/
    │   │   └── TranscriptionApp.vue  # Main app component
    │   └── App.vue
    └── package.json
```

## API Endpoints

- `POST /api/transcribe` - Upload and transcribe media files
- `POST /api/save-transcript` - Save transcript to backend
- `GET /api/health` - Health check endpoint

## Configuration

Edit `config.py` to customize:

- Language detection
- Speaker diarization
- Output formats
- Model selection

## Development

### Backend Development

```bash
python api.py
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Build for Production

```bash
cd frontend
npm run build
```

## Requirements

- Python 3.8+
- Node.js 16+
- ElevenLabs API key
