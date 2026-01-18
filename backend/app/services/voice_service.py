"""
Voice Service
Handles Speech-to-Text and Text-to-Speech operations
Using browser-based fallback (Web Speech API on frontend)
"""
import base64
import logging
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class VoiceService:
    """Service for voice processing (STT/TTS) - Browser-based fallback"""
    
    def __init__(self):
        logger.info("Voice service initialized (using browser-based fallback)")
    
    async def speech_to_text(self, audio_base64: str) -> str:
        """
        Convert speech to text
        Note: Primary STT is done on frontend using Web Speech API
        This endpoint is for future server-side STT integration
        """
        logger.info("Processing speech-to-text (mock - frontend uses Web Speech API)")
        
        # Return mock transcription - actual STT happens on frontend
        # In production, integrate with Google Cloud Speech-to-Text or Whisper
        return "This is a mock transcription. The frontend uses Web Speech API for real-time STT."
    
    async def text_to_speech(self, text: str, voice: str = "default") -> str:
        """
        Convert text to speech
        Note: Primary TTS is done on frontend using Web Speech API
        This returns empty to signal frontend to use browser TTS
        """
        logger.info(f"Text-to-speech requested: {text[:50]}...")
        
        # Return empty - frontend will use browser's speechSynthesis API
        # In production, integrate with Google Cloud Text-to-Speech or ElevenLabs
        return ""
    
    async def get_avatar_animation(self, audio_base64: str) -> Optional[str]:
        """
        Get avatar animation for given audio
        Returns avatar URL for animation states
        """
        logger.info("Avatar animation requested")
        return "/avatars/interviewer_speaking.gif"
