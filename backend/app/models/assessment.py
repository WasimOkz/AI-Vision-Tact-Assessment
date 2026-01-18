"""
Pydantic models for Assessment data
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class InterviewType(str, Enum):
    """Interview type enum"""
    CHAT = "chat"
    VOICE = "voice"


class MessageRole(str, Enum):
    """Message role enum"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Chat message model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_name: Optional[str] = None  # Which agent sent this message


class AssessmentSession(BaseModel):
    """Assessment session model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    candidate_id: str
    interview_type: InterviewType
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    messages: List[ChatMessage] = []
    current_agent: str = "profile_analyzer"
    is_active: bool = True


class AgentScore(BaseModel):
    """Score from an individual agent"""
    agent_name: str
    category: str
    score: float = Field(..., ge=0, le=100)
    feedback: str
    strengths: List[str] = []
    areas_for_improvement: List[str] = []


class AssessmentReport(BaseModel):
    """Final assessment report"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    candidate_id: str
    session_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Scores
    technical_score: float = 0
    behavioral_score: float = 0
    communication_score: float = 0
    overall_score: float = 0
    
    # Agent evaluations
    agent_scores: List[AgentScore] = []
    
    # Summary
    executive_summary: str = ""
    key_strengths: List[str] = []
    risks: List[str] = []
    recommendation: str = ""
    
    # HR fields
    hr_reviewed: bool = False
    hr_decision: Optional[str] = None
    hr_notes: Optional[str] = None


class StartAssessmentRequest(BaseModel):
    """Request to start an assessment"""
    candidate_id: str
    interview_type: InterviewType = InterviewType.CHAT


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    session_id: str


class ChatResponse(BaseModel):
    """Chat response model"""
    message: ChatMessage
    session_id: str
    current_agent: str
