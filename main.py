import requests
from config import ELEVENLABS_API_KEY, SPEECH_TO_TEXT_CONFIG
import os

def transcribe_audio_file(audio_file_path, custom_config=None):
    """
    Transcribe audio file using ElevenLabs Speech-to-Text API with direct requests
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
        custom_config (dict, optional): Custom configuration to override defaults
        
    Returns:
        dict: Transcription result with text, words, language info, etc.
    """
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY not found in environment variables. Please set it in your .env file.")
    
    # Merge custom config with default config
    config = SPEECH_TO_TEXT_CONFIG.copy()
    if custom_config:
        config.update(custom_config)
    
    # Filter out None values to avoid API errors
    config = {k: v for k, v in config.items() if v is not None}
    
    try:
        # Use direct requests API call (same as your working example)
        response = requests.post(
            "https://api.elevenlabs.io/v1/speech-to-text",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY
            },
            data=config,
            files={
                'file': (os.path.basename(audio_file_path), open(audio_file_path, 'rb'))
            }
        )
        
        # Check if request was successful
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

def transcribe_from_cloud_storage(cloud_storage_url, custom_config=None):
    """
    Transcribe audio from cloud storage URL using ElevenLabs Speech-to-Text API
    
    Args:
        cloud_storage_url (str): Valid AWS S3, Cloudflare R2 or Google Cloud Storage URL
        custom_config (dict, optional): Custom configuration to override defaults
        
    Returns:
        dict: Transcription result with text, words, language info, etc.
    """
    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY not found in environment variables. Please set it in your .env file.")
    
    # Merge custom config with default config
    config = SPEECH_TO_TEXT_CONFIG.copy()
    if custom_config:
        config.update(custom_config)
    
    # Add cloud storage URL to config
    config["cloud_storage_url"] = cloud_storage_url
    
    # Filter out None values to avoid API errors
    config = {k: v for k, v in config.items() if v is not None}
    
    try:
        # Use direct requests API call for cloud storage
        response = requests.post(
            "https://api.elevenlabs.io/v1/speech-to-text",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY
            },
            data=config
        )
        
        # Check if request was successful
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

def print_transcription_result(result):
    """
    Print transcription result in a formatted way
    
    Args:
        result (dict): Transcription result from ElevenLabs API
    """
    if not result:
        print("No transcription result to display")
        return
    
    print("\n=== TRANSCRIPTION RESULT ===")
    print(f"Language: {result.get('language_code', 'Unknown')} (confidence: {result.get('language_probability', 0):.2f})")
    print(f"Text: {result.get('text', 'No text')}")
    
    # Print words with speaker information if diarization is enabled
    words = result.get('words', [])
    if words:
        print("\nDetailed breakdown:")
        current_speaker = None
        for word in words:
            speaker_id = word.get('speaker_id')
            if speaker_id and speaker_id != current_speaker:
                current_speaker = speaker_id
                print(f"\n[{speaker_id.upper()}]: ", end="")
            
            word_text = word.get('text', '')
            if word.get('type') == 'audio_event':
                print(f"({word_text}) ", end="")
            else:
                print(f"{word_text} ", end="")
        print("\n")
    
    # Print additional formats if available
    additional_formats = result.get('additional_formats')
    if additional_formats:
        print("Additional formats generated:")
        for fmt in additional_formats:
            print(f"  - {fmt.get('requested_format', 'Unknown')} format")

if __name__ == "__main__":
    # Example usage
    audio_file = "path/to/your/audio/file.mp3"  # Replace with your audio file path
    
    print("Starting transcription with diarization enabled...")
    print("Note: Replace the audio_file path with your actual audio file")
    print()
    
    # Example with file upload
    # transcription = transcribe_audio_file(audio_file)
    # if transcription:
    #     print_transcription_result(transcription)
    # else:
    #     print("Transcription failed!")
    
    # Example with cloud storage URL
    # cloud_url = "https://your-bucket.s3.amazonaws.com/audio-file.mp3"
    # transcription = transcribe_from_cloud_storage(cloud_url)
    # if transcription:
    #     print_transcription_result(transcription)
    # else:
    #     print("Transcription failed!")
    
    print("To use this script:")
    print("1. Replace 'path/to/your/audio/file.mp3' with your actual audio file path")
    print("2. Uncomment the transcription lines in the code")
    print("3. Make sure your .env file contains your ElevenLabs API key")
    print("4. Run: python main.py")
