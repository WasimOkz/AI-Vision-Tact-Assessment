"""
Assessment API Router
Handles assessment sessions, reports, and agent orchestration
"""
from fastapi import APIRouter, HTTPException
from typing import List
import logging

from app.models.assessment import (
    AssessmentSession, AssessmentReport, StartAssessmentRequest,
    InterviewType, ChatMessage, MessageRole
)
from app.models.candidate import AssessmentStatus
from app.routers.candidates import candidates_db
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage (for demo)
sessions_db: dict[str, AssessmentSession] = {}
reports_db: dict[str, AssessmentReport] = {}

# Agent orchestrator
orchestrator = AgentOrchestrator()


@router.post("/start", response_model=AssessmentSession)
async def start_assessment(request: StartAssessmentRequest):
    """Start a new assessment session for a candidate"""
    candidate = candidates_db.get(request.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Create new session
    session = AssessmentSession(
        candidate_id=request.candidate_id,
        interview_type=request.interview_type,
        current_agent="profile_analyzer"
    )
    
    # Store session
    sessions_db[session.id] = session
    
    # Update candidate status
    candidate.status = AssessmentStatus.PROFILE_ANALYSIS
    
    # Get initial message from profile analyzer
    initial_message = await orchestrator.get_initial_message(
        session.id, 
        candidate
    )
    
    session.messages.append(ChatMessage(
        role=MessageRole.ASSISTANT,
        content=initial_message,
        agent_name="profile_analyzer"
    ))
    
    logger.info(f"Assessment session started: {session.id}")
    return session


@router.get("/session/{session_id}", response_model=AssessmentSession)
async def get_session(session_id: str):
    """Get assessment session by ID"""
    session = sessions_db.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/sessions", response_model=List[AssessmentSession])
async def list_sessions():
    """List all assessment sessions"""
    return list(sessions_db.values())


@router.post("/session/{session_id}/end")
async def end_session(session_id: str):
    """End an assessment session and generate report"""
    session = sessions_db.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.is_active = False
    
    # Generate final report
    candidate = candidates_db.get(session.candidate_id)
    report = await orchestrator.generate_final_report(session, candidate)
    reports_db[report.id] = report
    
    # Update candidate status
    if candidate:
        candidate.status = AssessmentStatus.HR_REVIEW
    
    logger.info(f"Assessment session ended: {session_id}")
    return {"message": "Session ended", "report_id": report.id}


@router.get("/report/{report_id}", response_model=AssessmentReport)
async def get_report(report_id: str):
    """Get assessment report by ID"""
    report = reports_db.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/candidate/{candidate_id}/reports", response_model=List[AssessmentReport])
async def get_candidate_reports(candidate_id: str):
    """Get all reports for a candidate"""
    reports = [r for r in reports_db.values() if r.candidate_id == candidate_id]
    return reports
