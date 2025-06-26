#!/usr/bin/env python3
"""
Automated Transcription Script

This script monitors the /files folder for audio and video files and automatically
transcribes them if no corresponding transcript exists in /transcripts.
"""

import os
import json
from pathlib import Path
from main import transcribe_audio_file, print_transcription_result
from config import SPEECH_TO_TEXT_CONFIG
import argparse

# Define supported audio and video file extensions
SUPPORTED_MEDIA_EXTENSIONS = {
    # Audio
    '.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg', '.wma', '.aiff',
    # Video
    '.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v'
}

# Define supported transcript file extensions
TRANSCRIPT_EXTENSIONS = {
    '.txt', '.json', '.srt', '.vtt'
}

def get_media_files(media_folder):
    """
    Get all audio and video files from the media folder
    
    Args:
        media_folder (str): Path to the media folder
        
    Returns:
        list: List of media file paths
    """
    media_path = Path(media_folder)
    if not media_path.exists():
        print(f"Media folder '{media_folder}' does not exist. Creating it...")
        media_path.mkdir(parents=True, exist_ok=True)
        return []
    
    media_files = []
    for file_path in media_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_MEDIA_EXTENSIONS:
            media_files.append(file_path)
    
    return media_files

def get_transcript_files(transcripts_folder):
    """
    Get all transcript files from the transcripts folder
    
    Args:
        transcripts_folder (str): Path to the transcripts folder
        
    Returns:
        list: List of transcript file paths
    """
    transcripts_path = Path(transcripts_folder)
    if not transcripts_path.exists():
        print(f"Transcripts folder '{transcripts_folder}' does not exist. Creating it...")
        transcripts_path.mkdir(parents=True, exist_ok=True)
        return []
    
    transcript_files = []
    for file_path in transcripts_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in TRANSCRIPT_EXTENSIONS:
            transcript_files.append(file_path)
    
    return transcript_files

def has_transcript(media_file_path, transcript_files):
    """
    Check if a media file has a corresponding transcript
    
    Args:
        media_file_path (Path): Path to the media file
        transcript_files (list): List of transcript file paths
        
    Returns:
        bool: True if transcript exists, False otherwise
    """
    media_name = media_file_path.stem  # filename without extension
    
    for transcript_file in transcript_files:
        if transcript_file.stem == media_name:
            return True
    
    return False

def save_transcript(transcript_data, output_path, format_type="json"):
    """
    Save transcript data to file
    
    Args:
        transcript_data (dict): Transcription result from API
        output_path (Path): Path where to save the transcript
        format_type (str): Format type for saving
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if format_type == "json":
        # Save as JSON with full API response
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, indent=2, ensure_ascii=False)
    
    elif format_type == "txt":
        # Save as plain text
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Language: {transcript_data.get('language_code', 'Unknown')}\n")
            f.write(f"Confidence: {transcript_data.get('language_probability', 0):.2f}\n")
            f.write(f"Transcription:\n{transcript_data.get('text', 'No text')}\n")
            
            # Add speaker information if diarization is enabled
            words = transcript_data.get('words', [])
            if words and any(word.get('speaker_id') for word in words):
                f.write("\nDetailed breakdown with speakers:\n")
                current_speaker = None
                for word in words:
                    speaker_id = word.get('speaker_id')
                    if speaker_id and speaker_id != current_speaker:
                        current_speaker = speaker_id
                        f.write(f"\n[{speaker_id.upper()}]: ")
                    
                    word_text = word.get('text', '')
                    if word.get('type') == 'audio_event':
                        f.write(f"({word_text}) ")
                    else:
                        f.write(f"{word_text} ")
    
    elif format_type == "srt":
        # Save as SRT subtitle format
        with open(output_path, 'w', encoding='utf-8') as f:
            words = transcript_data.get('words', [])
            if words:
                subtitle_index = 1
                current_speaker = None
                subtitle_text = ""
                start_time = None
                end_time = None
                
                for word in words:
                    speaker_id = word.get('speaker_id')
                    word_text = word.get('text', '')
                    word_start = word.get('start')
                    word_end = word.get('end')
                    
                    # Start new subtitle if speaker changes or time gap is large
                    if (speaker_id != current_speaker or 
                        (start_time is not None and word_start and word_start - end_time > 1.0)):
                        
                        # Write previous subtitle if exists
                        if subtitle_text and start_time is not None and end_time is not None:
                            f.write(f"{subtitle_index}\n")
                            f.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
                            f.write(f"{subtitle_text.strip()}\n\n")
                            subtitle_index += 1
                        
                        # Start new subtitle
                        current_speaker = speaker_id
                        subtitle_text = word_text
                        start_time = word_start
                        end_time = word_end
                    else:
                        # Continue current subtitle
                        subtitle_text += f" {word_text}"
                        if word_end:
                            end_time = word_end
                
                # Write final subtitle
                if subtitle_text and start_time is not None and end_time is not None:
                    f.write(f"{subtitle_index}\n")
                    f.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
                    f.write(f"{subtitle_text.strip()}\n")

def format_time(seconds):
    """Format seconds to SRT time format (HH:MM:SS,mmm)"""
    if seconds is None:
        return "00:00:00,000"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def process_media_files(media_folder="files", transcripts_folder="transcripts", 
                       output_format="json", custom_config=None):
    """
    Process all audio and video files that don't have corresponding transcripts
    
    Args:
        media_folder (str): Path to media folder
        transcripts_folder (str): Path to transcripts folder
        output_format (str): Output format ('json', 'txt', 'srt')
        custom_config (dict): Custom configuration for transcription
    """
    print("🎵 Automated Transcription System (Audio & Video)")
    print("=" * 50)
    
    # Get media and transcript files
    media_files = get_media_files(media_folder)
    transcript_files = get_transcript_files(transcripts_folder)
    
    print(f"📁 Found {len(media_files)} audio/video files in '{media_folder}'")
    print(f"📄 Found {len(transcript_files)} transcript files in '{transcripts_folder}'")
    print()
    
    if not media_files:
        print("No audio or video files found. Please add files to the 'files' folder.")
        return
    
    # Find files that need transcription
    files_to_process = []
    for media_file in media_files:
        if not has_transcript(media_file, transcript_files):
            files_to_process.append(media_file)
    
    print(f"🔄 Found {len(files_to_process)} files that need transcription:")
    for file in files_to_process:
        print(f"   - {file.name}")
    print()
    
    if not files_to_process:
        print("✅ All audio/video files already have transcripts!")
        return
    
    # Process each file
    successful_transcriptions = 0
    failed_transcriptions = 0
    
    for i, media_file in enumerate(files_to_process, 1):
        print(f"🎯 Processing {i}/{len(files_to_process)}: {media_file.name}")
        
        try:
            # Transcribe the media file
            result = transcribe_audio_file(str(media_file), custom_config)
            
            if result:
                # Create output filename
                output_filename = f"{media_file.stem}.{output_format}"
                output_path = Path(transcripts_folder) / output_filename
                
                # Save the transcript
                save_transcript(result, output_path, output_format)
                
                print(f"   ✅ Successfully transcribed and saved to: {output_path}")
                print(f"   📝 Language: {result.get('language_code', 'Unknown')} "
                      f"(confidence: {result.get('language_probability', 0):.2f})")
                print(f"   🗣️  Text: {result.get('text', 'No text')[:100]}{'...' if len(result.get('text', '')) > 100 else ''}")
                
                successful_transcriptions += 1
            else:
                print(f"   ❌ Failed to transcribe {media_file.name}")
                failed_transcriptions += 1
                
        except Exception as e:
            print(f"   ❌ Error processing {media_file.name}: {e}")
            failed_transcriptions += 1
        
        print()
    
    # Summary
    print("=" * 50)
    print("📊 TRANSCRIPTION SUMMARY")
    print(f"✅ Successful: {successful_transcriptions}")
    print(f"❌ Failed: {failed_transcriptions}")
    print(f"📁 Total processed: {len(files_to_process)}")
    
    if successful_transcriptions > 0:
        print(f"\n📂 Transcripts saved in: {transcripts_folder}/")

def main():
    print("🚀 Starting automated transcription...\n")
    parser = argparse.ArgumentParser(description="Automated Transcription Script")
    parser.add_argument('--input', type=str, help='Path to a single audio/video file to transcribe')
    parser.add_argument('--output_dir', type=str, default="transcripts", help='Directory to save transcripts')
    parser.add_argument('--output_format', type=str, default="json", help='Transcript format: json, txt, srt')
    args = parser.parse_args()

    custom_config = {}

    if args.input:
        # Single file mode
        from pathlib import Path
        media_file = Path(args.input)
        if not media_file.exists():
            print(f"File {args.input} does not exist.")
            return
        print(f"Transcribing single file: {media_file}")
        result = transcribe_audio_file(str(media_file), custom_config)
        if result:
            output_filename = f"{media_file.stem}.{args.output_format}"
            output_path = Path(args.output_dir) / output_filename
            save_transcript(result, output_path, args.output_format)
            print(f"✅ Successfully transcribed and saved to: {output_path}")
        else:
            print("❌ Transcription failed.")
    else:
        # Batch mode (original)
        process_media_files(
            media_folder="files",
            transcripts_folder=args.output_dir,
            output_format=args.output_format,
            custom_config=custom_config
        )

if __name__ == "__main__":
    main() 