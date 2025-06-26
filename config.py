import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Speech-to-Text Model Configuration
# All parameters from https://elevenlabs.io/docs/api-reference/speech-to-text/convert
SPEECH_TO_TEXT_CONFIG = {
    # Required parameters
    "model_id": "scribe_v1",  # Options: 'scribe_v1', 'scribe_v1_experimental'
    
    # Optional parameters with defaults
    "language_code": None,  # ISO-639-1 or ISO-639-3 language code (e.g., "en", "fr", "es")
    "tag_audio_events": True,  # Tag audio events like (laughter), (footsteps), etc.
    "num_speakers": None,  # Maximum number of speakers (1-32), None = auto-detect
    "timestamps_granularity": "word",  # Options: 'none', 'word', 'character'
    "diarize": True,  # Enable speaker diarization (identify who is speaking)
    "file_format": "other",  # Options: 'pcm_s16le_16', 'other'
    "webhook": False,  # Send results to configured webhooks (async processing)
    "temperature": None,  # Controls randomness (0.0-2.0), None = model default
    "enable_logging": True,  # Enable request logging (enterprise feature)
    
    # Additional export formats (optional) - set to None to avoid API errors
    "additional_formats": None,  # List of export format objects
}

# Available models for reference
AVAILABLE_MODELS = {
    "scribe_v1": "Standard transcription model",
    "scribe_v1_experimental": "Experimental transcription model with enhanced features"
}

# Available timestamps granularity options
TIMESTAMPS_GRANULARITY_OPTIONS = {
    "none": "No timestamps",
    "word": "Word-level timestamps",
    "character": "Character-level timestamps per word"
}

# Available file format options
FILE_FORMAT_OPTIONS = {
    "pcm_s16le_16": "16-bit PCM at 16kHz, mono, little-endian (lower latency)",
    "other": "All other audio/video formats"
}

# Additional export format templates
EXPORT_FORMATS = {
    "segmented_json": {
        "format": "segmented_json",
        "include_speakers": True,
        "include_timestamps": True,
        "segment_on_silence_longer_than_s": None,
        "max_segment_duration_s": None,
        "max_segment_chars": None
    },
    "docx": {
        "format": "docx",
        "include_speakers": True,
        "include_timestamps": True,
        "segment_on_silence_longer_than_s": None,
        "max_segment_duration_s": None,
        "max_segment_chars": None
    },
    "pdf": {
        "format": "pdf",
        "include_speakers": True,
        "include_timestamps": True,
        "segment_on_silence_longer_than_s": None,
        "max_segment_duration_s": None,
        "max_segment_chars": None
    },
    "txt": {
        "format": "txt",
        "max_characters_per_line": 100,
        "include_speakers": True,
        "include_timestamps": True,
        "segment_on_silence_longer_than_s": None,
        "max_segment_duration_s": None,
        "max_segment_chars": None
    },
    "html": {
        "format": "html",
        "include_speakers": True,
        "include_timestamps": True,
        "segment_on_silence_longer_than_s": None,
        "max_segment_duration_s": None,
        "max_segment_chars": None
    },
    "srt": {
        "format": "srt",
        "max_characters_per_line": 50,
        "include_speakers": False,
        "include_timestamps": True,
        "segment_on_silence_longer_than_s": 0.6,
        "max_segment_duration_s": 5,
        "max_segment_chars": 90
    }
}

# Common language codes for reference
LANGUAGE_CODES = {
    "en": "English",
    "es": "Spanish", 
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "hi": "Hindi",
    "nl": "Dutch",
    "sv": "Swedish",
    "no": "Norwegian",
    "da": "Danish",
    "fi": "Finnish",
    "pl": "Polish",
    "tr": "Turkish",
    "he": "Hebrew"
} 