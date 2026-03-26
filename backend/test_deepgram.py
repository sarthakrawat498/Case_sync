"""
Test script for Deepgram Speech-to-Text Service
Run this to verify the service is working correctly.

Requirements:
1. Set DEEPGRAM_API_KEY in .env file
2. Have an audio file to test with
3. Run: python test_deepgram.py
"""

import asyncio
import os
from pathlib import Path
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.whisper_service import whisper_service
from core.config import settings


async def test_deepgram_service():
    """Test the Deepgram service with validation."""
    print("=== Deepgram Service Test ===\n")
    
    # Check if API key is set
    if not settings.DEEPGRAM_API_KEY:
        print("❌ ERROR: DEEPGRAM_API_KEY not set in environment variables")
        print("Please set your Deepgram API key in .env file:")
        print("DEEPGRAM_API_KEY=your_actual_api_key_here")
        return False
    
    print(f"✓ Deepgram API Key: {'*' * 8}{settings.DEEPGRAM_API_KEY[-4:]}")
    print(f"✓ API URL: {settings.DEEPGRAM_API_URL}")
    
    # Check supported formats
    formats = whisper_service.get_supported_formats()
    print(f"✓ Supported formats: {', '.join(formats)}")
    
    # Look for test audio files
    test_files = []
    search_dirs = [
        Path("uploads"),
        Path("../uploads"), 
        Path("test_audio"),
        Path(".")
    ]
    
    for search_dir in search_dirs:
        if search_dir.exists():
            for ext in formats:
                test_files.extend(search_dir.glob(f"*{ext}"))
    
    if not test_files:
        print("\n⚠️  No audio files found for testing")
        print("Please add an audio file (.mp3, .wav, etc.) to test transcription")
        print("Supported formats:", ", ".join(formats))
        return True
    
    # Test transcription with first found file
    test_file = test_files[0]
    print(f"\n📁 Testing with file: {test_file.name}")
    
    # Get file info
    file_info = whisper_service.get_file_info(str(test_file))
    print(f"   Size: {file_info['size_mb']} MB")
    print(f"   Format: {file_info['extension']}")
    print(f"   Supported: {file_info['is_supported']}")
    
    if not file_info['is_supported']:
        print("❌ File format not supported")
        return False
    
    try:
        print(f"\n🎤 Starting transcription...")
        result = await whisper_service.transcribe(str(test_file))
        
        print(f"\n✅ Transcription successful!")
        print(f"   Language: {result['language']}")
        print(f"   Duration: {result['duration']:.1f}s")
        print(f"   Words: {result['word_count']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Service: {result['service']}")
        print(f"\n📝 Text (first 200 chars):")
        print(f"   {result['text'][:200]}{'...' if len(result['text']) > 200 else ''}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Transcription failed: {str(e)}")
        
        # Common error help
        if "401" in str(e) or "unauthorized" in str(e).lower():
            print("\n💡 This is likely an authentication error:")
            print("   - Check your DEEPGRAM_API_KEY is correct")
            print("   - Ensure your Deepgram account has credits")
            print("   - Visit https://console.deepgram.com/ to check your account")
        elif "403" in str(e) or "forbidden" in str(e).lower():
            print("\n💡 This might be a permissions or quota issue:")
            print("   - Check your Deepgram account limits")
            print("   - Ensure your API key has the right permissions")
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            print("\n💡 This looks like a network issue:")
            print("   - Check your internet connection") 
            print("   - Try again in a few moments")
        
        return False


def test_service_config():
    """Test service configuration."""
    print("=== Service Configuration Test ===\n")
    
    try:
        service = whisper_service
        print(f"✓ Service initialized: {service.__class__.__name__}")
        print(f"✓ API URL: {service.api_url}")
        print(f"✓ Supported languages: {service.supported_languages}")
        
        return True
        
    except Exception as e:
        print(f"❌ Service configuration error: {e}")
        return False


if __name__ == "__main__":
    async def main():
        """Main test function."""
        print("🔍 Testing CaseSync Deepgram Integration\n")
        
        # Test 1: Service Configuration
        config_ok = test_service_config()
        
        # Test 2: Deepgram API
        if config_ok:
            api_ok = await test_deepgram_service()
        else:
            api_ok = False
        
        # Summary
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        print(f"Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
        print(f"Deepgram API:  {'✅ PASS' if api_ok else '❌ FAIL'}")
        
        if config_ok and api_ok:
            print(f"\n🎉 All tests passed! Your Deepgram service is ready.")
            print(f"   You can now upload audio files for transcription.")
        else:
            print(f"\n⚠️  Some tests failed. Check the errors above.")
        
        return config_ok and api_ok
    
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)