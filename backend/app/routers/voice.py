"""
Voice Interview API Router
Handles voice-based assessment sessions with STT/TTS
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import uuid

from app.services.voice_service import VoiceService

router = APIRouter()
logger = logging.getLogger(__name__)

# Voice service instance
voice_service = VoiceService()

# In-memory voice sessions
voice_sessions: dict[str, dict] = {}


class VoiceSessionRequest(BaseModel):
    """Request to start a voice session"""
    candidate_id: str
    session_id: str  # Chat session ID to link with


class VoiceSessionResponse(BaseModel):
    """Voice session response"""
    voice_session_id: str
    candidate_id: str
    session_id: str
    avatar_url: Optional[str] = None
    status: str = "ready"


class TranscriptionRequest(BaseModel):
    """Request for speech-to-text"""
    audio_base64: str
    voice_session_id: str


class SynthesisRequest(BaseModel):
    """Request for text-to-speech"""
    text: str
    voice_session_id: str


@router.post("/start", response_model=VoiceSessionResponse)
async def start_voice_session(request: VoiceSessionRequest):
    """Start a new voice interview session"""
    voice_session_id = str(uuid.uuid4())
    
    # Create voice session
    voice_sessions[voice_session_id] = {
        "candidate_id": request.candidate_id,
        "session_id": request.session_id,
        "status": "ready"
    }
    
    logger.info(f"Voice session started: {voice_session_id}")
    
    return VoiceSessionResponse(
        voice_session_id=voice_session_id,
        candidate_id=request.candidate_id,
        session_id=request.session_id,
        avatar_url="/avatars/interviewer.png",
        status="ready"
    )


@router.post("/transcribe")
async def transcribe_audio(request: TranscriptionRequest):
    """Convert speech to text"""
    session = voice_sessions.get(request.voice_session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Voice session not found")
    
    try:
        text = await voice_service.speech_to_text(request.audio_base64)
        return {"text": text, "success": True}
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return {"text": "", "success": False, "error": str(e)}


@router.post("/synthesize")
async def synthesize_speech(request: SynthesisRequest):
    """Convert text to speech"""
    session = voice_sessions.get(request.voice_session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Voice session not found")
    
    try:
        audio_base64 = await voice_service.text_to_speech(request.text)
        return {"audio_base64": audio_base64, "success": True}
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        return {"audio_base64": "", "success": False, "error": str(e)}


@router.post("/{voice_session_id}/end")
async def end_voice_session(voice_session_id: str):
    """End a voice session"""
    if voice_session_id not in voice_sessions:
        raise HTTPException(status_code=404, detail="Voice session not found")
    
    del voice_sessions[voice_session_id]
    logger.info(f"Voice session ended: {voice_session_id}")
    
    return {"message": "Voice session ended"}


@router.get("/{voice_session_id}/status")
async def get_voice_session_status(voice_session_id: str):
    """Get voice session status"""
    session = voice_sessions.get(voice_session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Voice session not found")
    
    return {"voice_session_id": voice_session_id, **session}
