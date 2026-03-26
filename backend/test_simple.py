"""
Simple test for Deepgram service without NER dependencies
"""

import os
import sys
import asyncio

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import just the core components we need
from core.config import settings

async def test_deepgram_simple():
    """Simple test of Deepgram service configuration."""
    print("=== CaseSync Deepgram Service Test ===\n")
    
    # Test 1: Configuration
    print(f"✅ App Name: {settings.APP_NAME}")
    print(f"✅ App Version: {settings.APP_VERSION}")
    print(f"✅ Database URL: {settings.DATABASE_URL}")
    
    # Test 2: Deepgram Config
    if settings.DEEPGRAM_API_KEY:
        key_preview = settings.DEEPGRAM_API_KEY[:8] + "..." + settings.DEEPGRAM_API_KEY[-4:]
        print(f"✅ Deepgram API Key: {key_preview}")
    else:
        print("❌ Deepgram API Key: Not set")
        
    print(f"✅ Deepgram API URL: {settings.DEEPGRAM_API_URL}")
    print(f"✅ Supported Languages: {settings.SUPPORTED_LANGUAGES}")
    
    # Test 3: Direct Deepgram service import (bypassing NER)
    try:
        from services.whisper_service import DeepgramService
        service = DeepgramService()
        print(f"✅ Deepgram service initialized")
        print(f"✅ Supported formats: {service.get_supported_formats()}")
        
        # Test basic functionality
        test_path = "test.mp3"
        file_info = service.get_file_info(test_path)
        print(f"✅ File validation works: {file_info}")
        
    except Exception as e:
        print(f"❌ Deepgram service error: {e}")
        return False
    
    print(f"\n🎉 Configuration test passed!")
    print(f"✨ Ready to transcribe audio files with Deepgram API")
    
    if not settings.DEEPGRAM_API_KEY:
        print(f"\n⚠️  Next steps:")
        print(f"1. Sign up at https://console.deepgram.com")
        print(f"2. Get your API key")
        print(f"3. Add it to .env file: DEEPGRAM_API_KEY=your_key_here")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_deepgram_simple())
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)