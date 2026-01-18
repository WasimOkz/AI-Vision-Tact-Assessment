"""
WebSocket Chat Handler
Real-time chat communication for AI assessment
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import logging
import json

from app.agents.orchestrator import AgentOrchestrator
from app.routers.candidates import candidates_db
from app.routers.assessment import sessions_db

router = APIRouter()
logger = logging.getLogger(__name__)

# Connection manager
class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.orchestrator = AgentOrchestrator()
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected: {session_id}")
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_message(self, session_id: str, message: dict):
        websocket = self.active_connections.get(session_id)
        if websocket:
            await websocket.send_json(message)
    
    async def broadcast_to_session(self, session_id: str, message: dict):
        await self.send_message(session_id, message)


manager = ConnectionManager()


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time chat assessment
    
    Message format (client -> server):
    {
        "type": "message",
        "content": "user message text",
        "candidate_id": "optional-candidate-id"
    }
    
    Response format (server -> client):
    {
        "type": "response",
        "content": "AI response text",
        "agent": "current_agent_name",
        "is_complete": false
    }
    """
    await manager.connect(websocket, session_id)
    
    try:
        # Get session info
        session = sessions_db.get(session_id)
        if session:
            candidate = candidates_db.get(session.candidate_id)
            if candidate:
                # Initialize orchestrator for this session
                from app.services.knowledge_base import KnowledgeBaseService
                kb = KnowledgeBaseService()
                context = await kb.get_candidate_context(candidate.id)
                await manager.orchestrator.initialize_session(
                    session_id, 
                    candidate.id, 
                    context
                )
        
        # Send ready message
        await manager.send_message(session_id, {
            "type": "ready",
            "message": "Connected to assessment chat",
            "session_id": session_id
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
                message_type = message_data.get("type", "message")
                content = message_data.get("content", "")
                
                if message_type == "message" and content:
                    # Send typing indicator
                    await manager.send_message(session_id, {
                        "type": "typing",
                        "agent": manager.orchestrator.get_session_state(session_id).get("current_agent", "assistant") if manager.orchestrator.get_session_state(session_id) else "assistant"
                    })
                    
                    # Process through orchestrator
                    result = await manager.orchestrator.process_message(
                        session_id,
                        content
                    )
                    
                    # Send response
                    await manager.send_message(session_id, {
                        "type": "response",
                        "content": result.get("response", ""),
                        "agent": result.get("current_agent", "assistant"),
                        "is_complete": result.get("is_complete", False),
                        "messages_count": result.get("messages_count", 0)
                    })
                    
                elif message_type == "end":
                    # End session
                    await manager.send_message(session_id, {
                        "type": "session_ended",
                        "message": "Assessment session has ended. Thank you!"
                    })
                    break
                    
            except json.JSONDecodeError:
                await manager.send_message(session_id, {
                    "type": "error",
                    "message": "Invalid message format"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"Client disconnected from chat: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(session_id)
