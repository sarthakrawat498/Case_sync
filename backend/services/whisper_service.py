"""
Deepgram Speech-to-Text Service
Handles audio transcription using Deepgram's AI Speech API.
Supports Hindi and English languages with high accuracy.

Production Implementation:
- Uses Deepgram REST API for cloud-based transcription
- Automatic language detection
- Real-time processing with professional accuracy
- Returns transcript text and detected language
"""

import os
import aiohttp
import json
from typing import Dict, Any, Optional
from pathlib import Path

from core.config import settings


class DeepgramService:
    """
    Speech-to-text service using Deepgram API.
    Supports Hindi and English audio transcription with professional accuracy.
    """
    
    def __init__(self):
        """Initialize Deepgram service."""
        self.api_key = settings.DEEPGRAM_API_KEY
        self.api_url = settings.DEEPGRAM_API_URL
        self.supported_languages = settings.SUPPORTED_LANGUAGES
        
        if not self.api_key:
            raise ValueError("DEEPGRAM_API_KEY environment variable is required")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Deepgram API request."""
        return {
            'Authorization': f'Token {self.api_key}'
        }
    
    
    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio file to text using Deepgram API.
        
        Args:
            audio_path: Path to the audio file
            language: Optional language code ('hi' or 'en'). If None, auto-detects.
            
        Returns:
            Dict containing:
            - text: Transcribed text
            - language: Detected/specified language code
            - confidence: Transcription confidence score
            - duration: Audio duration in seconds
            - word_count: Number of words transcribed
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if not self.validate_audio_file(audio_path):
            raise ValueError(f"Unsupported audio format: {Path(audio_path).suffix}")
        
        print(f"Transcribing audio file: {Path(audio_path).name}")
        
        # Prepare Deepgram request parameters
        params = {
            'model': 'nova-2',  # Latest Deepgram model
            'smart_format': 'true',  # Auto-formatting
            'punctuate': 'true',  # Add punctuation
            'diarize': 'false',  # Single speaker
            'utterances': 'true',  # Get confidence scores
        }
        
        # Add language parameter if specified
        if language and language in self.supported_languages:
            if language == 'hi':
                params['language'] = 'hi'  # Hindi
            else:
                params['language'] = 'en-IN'  # Indian English
        else:
            # Auto-detect language between Hindi and English
            params['detect_language'] = 'true'
        
        try:
            async with aiohttp.ClientSession() as session:
                # Read audio file
                with open(audio_path, 'rb') as audio_file:
                    audio_data = audio_file.read()
                
                # Prepare headers with audio content type
                headers = self._get_headers()
                
                # Determine content type based on file extension
                file_ext = Path(audio_path).suffix.lower()
                content_type_map = {
                    '.mp3': 'audio/mpeg',
                    '.wav': 'audio/wav',
                    '.m4a': 'audio/mp4',
                    '.flac': 'audio/flac',
                    '.ogg': 'audio/ogg',
                    '.opus': 'audio/opus',
                    '.webm': 'audio/webm',
                    '.mp4': 'audio/mp4',
                    '.aac': 'audio/aac'
                }
                headers['Content-Type'] = content_type_map.get(file_ext, 'audio/wav')
                
                # Make API request to Deepgram
                async with session.post(
                    self.api_url,
                    headers=headers,
                    params=params,
                    data=audio_data
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Deepgram API error ({response.status}): {error_text}")
                    
                    result = await response.json()
                    
                    return self._process_deepgram_response(result)
        
        except aiohttp.ClientError as e:
            raise Exception(f"Network error during transcription: {str(e)}")
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def _process_deepgram_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Deepgram API response and extract relevant information.
        
        Args:
            response: Raw Deepgram API response
            
        Returns:
            Processed transcription result
        """
        try:
            # Extract main transcript
            channels = response.get('results', {}).get('channels', [])
            if not channels:
                raise Exception("No transcription channels found in response")
            
            alternatives = channels[0].get('alternatives', [])
            if not alternatives:
                raise Exception("No transcription alternatives found")
            
            main_result = alternatives[0]
            transcript_text = main_result.get('transcript', '').strip()
            
            if not transcript_text:
                raise Exception("Empty transcription result")
            
            # Extract metadata
            metadata = response.get('metadata', {})
            duration = metadata.get('duration', 0.0)
            
            # Detect language from response or transcript content
            detected_language = self._detect_language_from_response(response, transcript_text)
            
            # Calculate confidence score
            confidence = main_result.get('confidence', 0.0)
            
            # Count words
            word_count = len(transcript_text.split())
            
            print(f"✓ Transcription successful:")
            print(f"  Language: {detected_language}")
            print(f"  Duration: {duration:.1f}s")
            print(f"  Words: {word_count}")
            print(f"  Confidence: {confidence:.2f}")
            print(f"  Text preview: {transcript_text[:100]}{'...' if len(transcript_text) > 100 else ''}")
            
            return {
                'text': transcript_text,
                'language': detected_language,
                'confidence': confidence,
                'duration': duration,
                'word_count': word_count,
                'is_real': True,
                'service': 'deepgram'
            }
            
        except Exception as e:
            raise Exception(f"Failed to process Deepgram response: {str(e)}")
    
    def _detect_language_from_response(self, response: Dict[str, Any], text: str) -> str:
        """
        Detect language from Deepgram response or text content.
        
        Args:
            response: Deepgram API response
            text: Transcribed text
            
        Returns:
            Language code ('hi' or 'en')
        """
        # Try to get language from Deepgram metadata
        try:
            metadata = response.get('metadata', {})
            detected_lang = metadata.get('detected_language')
            
            if detected_lang:
                if detected_lang.startswith('hi'):
                    return 'hi'
                elif detected_lang.startswith('en'):
                    return 'en'
        except:
            pass
        
        # Fallback: Simple text-based detection
        # Check for Devanagari script (Hindi)
        hindi_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')
        if hindi_chars > len(text) * 0.1:  # If >10% Hindi characters
            return 'hi'
        
        # Default to English
        return 'en'
    
    def get_supported_formats(self) -> list:
        """Return list of supported audio formats for Deepgram."""
        return ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.opus', '.webm', '.mp4', '.3gp', '.aac']
    
    def validate_audio_file(self, filepath: str) -> bool:
        """
        Validate if the audio file format is supported by Deepgram.
        
        Args:
            filepath: Path to the audio file
            
        Returns:
            bool: True if format is supported
        """
        ext = Path(filepath).suffix.lower()
        return ext in self.get_supported_formats()
    
    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """
        Get basic information about the audio file.
        
        Args:
            filepath: Path to the audio file
            
        Returns:
            Dict with file information
        """
        path_obj = Path(filepath)
        file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        
        return {
            'filename': path_obj.name,
            'extension': path_obj.suffix.lower(),
            'size_bytes': file_size,
            'size_mb': round(file_size / (1024 * 1024), 2),
            'is_supported': self.validate_audio_file(filepath)
        }


# Create service instance with new name for backward compatibility
class WhisperService(DeepgramService):
    """Backward compatibility alias for DeepgramService."""
    pass


# Singleton instance
whisper_service = WhisperService()
