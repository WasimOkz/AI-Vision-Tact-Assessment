"""
WebSocket Voice Handler
Real-time voice communication for AI interview with STT/TTS
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import logging
import json
import base64

from app.services.voice_service import VoiceService
from app.agents.orchestrator import AgentOrchestrator
from app.routers.candidates import candidates_db
from app.routers.assessment import sessions_db

router = APIRouter()
logger = logging.getLogger(__name__)


class VoiceConnectionManager:
    """Manage voice WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.voice_service = VoiceService()
        self.orchestrator = AgentOrchestrator()
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"Voice WebSocket connected: {session_id}")
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"Voice WebSocket disconnected: {session_id}")
    
    async def send_message(self, session_id: str, message: dict):
        websocket = self.active_connections.get(session_id)
        if websocket:
            await websocket.send_json(message)


voice_manager = VoiceConnectionManager()


@router.websocket("/ws/voice/{session_id}")
async def websocket_voice(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time voice interview
    
    Message format (client -> server):
    {
        "type": "audio",
        "audio_base64": "base64 encoded audio data",
        "format": "webm"  // or "wav"
    }
    
    Response format (server -> client):
    {
        "type": "response",
        "text": "AI response text",
        "audio_base64": "base64 encoded TTS audio",
        "avatar_state": "speaking" | "idle"
    }
    """
    await voice_manager.connect(websocket, session_id)
    
    try:
        # Get session info
        session = sessions_db.get(session_id)
        candidate = None
        if session:
            candidate = candidates_db.get(session.candidate_id)
            if candidate:
                from app.services.knowledge_base import KnowledgeBaseService
                kb = KnowledgeBaseService()
                context = await kb.get_candidate_context(candidate.id)
                await voice_manager.orchestrator.initialize_session(
                    session_id,
                    candidate.id,
                    context
                )
        
        # Send ready message with initial greeting
        initial_greeting = "Hello! I'm your AI interviewer. I can see your profile and I'm excited to learn more about you. Please click the microphone button to start speaking."
        
        # Generate TTS for greeting
        greeting_audio = await voice_manager.voice_service.text_to_speech(initial_greeting)
        
        await voice_manager.send_message(session_id, {
            "type": "ready",
            "message": initial_greeting,
            "audio_base64": greeting_audio,
            "avatar_state": "speaking"
        })
        
        while True:
            # Receive audio from client
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                message_type = message_data.get("type", "audio")
                
                if message_type == "audio":
                    audio_base64 = message_data.get("audio_base64", "")
                    
                    if audio_base64:
                        # Update avatar state to listening
                        await voice_manager.send_message(session_id, {
                            "type": "status",
                            "avatar_state": "listening",
                            "message": "Processing your speech..."
                        })
                        
                        # Speech-to-Text
                        transcribed_text = await voice_manager.voice_service.speech_to_text(
                            audio_base64
                        )
                        
                        if transcribed_text:
                            # Send transcription
                            await voice_manager.send_message(session_id, {
                                "type": "transcription",
                                "text": transcribed_text
                            })
                            
                            # Process through AI (update avatar to thinking)
                            await voice_manager.send_message(session_id, {
                                "type": "status",
                                "avatar_state": "thinking",
                                "message": "Thinking..."
                            })
                            
                            # Get AI response
                            result = await voice_manager.orchestrator.process_message(
                                session_id,
                                transcribed_text
                            )
                            
                            ai_response = result.get("response", "")
                            
                            # Generate TTS
                            response_audio = await voice_manager.voice_service.text_to_speech(
                                ai_response
                            )
                            
                            # Send response with audio
                            await voice_manager.send_message(session_id, {
                                "type": "response",
                                "text": ai_response,
                                "audio_base64": response_audio,
                                "agent": result.get("current_agent", "assistant"),
                                "avatar_state": "speaking",
                                "is_complete": result.get("is_complete", False)
                            })
                            
                            # After speaking, set avatar to idle
                            await voice_manager.send_message(session_id, {
                                "type": "status",
                                "avatar_state": "idle"
                            })
                        else:
                            await voice_manager.send_message(session_id, {
                                "type": "error",
                                "message": "Could not transcribe audio. Please try speaking again.",
                                "avatar_state": "idle"
                            })
                
                elif message_type == "end":
                    await voice_manager.send_message(session_id, {
                        "type": "session_ended",
                        "message": "Voice interview has ended. Thank you!",
                        "avatar_state": "idle"
                    })
                    break
                    
            except json.JSONDecodeError:
                await voice_manager.send_message(session_id, {
                    "type": "error",
                    "message": "Invalid message format"
                })
                
    except WebSocketDisconnect:
        voice_manager.disconnect(session_id)
        logger.info(f"Client disconnected from voice: {session_id}")
    except Exception as e:
        logger.error(f"Voice WebSocket error: {e}")
        voice_manager.disconnect(session_id)
