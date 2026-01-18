"""
HR Dashboard API Router
Handles HR review, candidate overview, and decision management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import logging

from app.models.assessment import AssessmentReport
from app.models.candidate import CandidateProfile, AssessmentStatus
from app.routers.candidates import candidates_db
from app.routers.assessment import reports_db, sessions_db

router = APIRouter()
logger = logging.getLogger(__name__)


class HRDecision(BaseModel):
    """HR decision model"""
    decision: str  # "approve", "reject", "hold"
    notes: Optional[str] = None


class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_candidates: int
    pending_review: int
    approved: int
    rejected: int
    in_progress: int


class CandidateWithAssessment(BaseModel):
    """Candidate with their latest assessment"""
    candidate: CandidateProfile
    latest_report: Optional[AssessmentReport] = None
    sessions_count: int = 0


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get HR dashboard statistics"""
    candidates = list(candidates_db.values())
    
    pending_review = sum(1 for c in candidates if c.status == AssessmentStatus.HR_REVIEW)
    completed = sum(1 for c in candidates if c.status == AssessmentStatus.COMPLETED)
    in_progress = sum(1 for c in candidates if c.status not in [
        AssessmentStatus.HR_REVIEW, AssessmentStatus.COMPLETED, AssessmentStatus.PENDING
    ])
    
    # Count approved/rejected from reports
    approved = sum(1 for r in reports_db.values() if r.hr_decision == "approve")
    rejected = sum(1 for r in reports_db.values() if r.hr_decision == "reject")
    
    return DashboardStats(
        total_candidates=len(candidates),
        pending_review=pending_review,
        approved=approved,
        rejected=rejected,
        in_progress=in_progress
    )


@router.get("/candidates", response_model=List[CandidateWithAssessment])
async def get_all_candidates_with_assessments():
    """Get all candidates with their assessment data"""
    result = []
    
    for candidate in candidates_db.values():
        # Find latest report for this candidate
        candidate_reports = [r for r in reports_db.values() if r.candidate_id == candidate.id]
        latest_report = max(candidate_reports, key=lambda r: r.created_at) if candidate_reports else None
        
        # Count sessions
        sessions_count = sum(1 for s in sessions_db.values() if s.candidate_id == candidate.id)
        
        result.append(CandidateWithAssessment(
            candidate=candidate,
            latest_report=latest_report,
            sessions_count=sessions_count
        ))
    
    return result


@router.get("/candidates/pending")
async def get_pending_review():
    """Get candidates pending HR review"""
    pending = [
        c for c in candidates_db.values() 
        if c.status == AssessmentStatus.HR_REVIEW
    ]
    return pending


@router.post("/decision/{report_id}")
async def make_hr_decision(report_id: str, decision: HRDecision):
    """Make HR decision on a candidate assessment"""
    report = reports_db.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Update report
    report.hr_reviewed = True
    report.hr_decision = decision.decision
    report.hr_notes = decision.notes
    
    # Update candidate status
    candidate = candidates_db.get(report.candidate_id)
    if candidate:
        candidate.status = AssessmentStatus.COMPLETED
    
    logger.info(f"HR decision made for report {report_id}: {decision.decision}")
    
    return {
        "message": "Decision recorded",
        "report_id": report_id,
        "decision": decision.decision
    }


@router.get("/report/{report_id}/detailed", response_model=AssessmentReport)
async def get_detailed_report(report_id: str):
    """Get detailed assessment report for HR review"""
    report = reports_db.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/override/{candidate_id}")
async def override_assessment(candidate_id: str, decision: HRDecision):
    """HR override for candidate assessment without report"""
    candidate = candidates_db.get(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Create override report if none exists
    from app.models.assessment import AssessmentReport
    
    report = AssessmentReport(
        candidate_id=candidate_id,
        session_id="hr_override",
        hr_reviewed=True,
        hr_decision=decision.decision,
        hr_notes=decision.notes,
        executive_summary=f"HR Override: {decision.notes or 'No notes provided'}"
    )
    
    reports_db[report.id] = report
    candidate.status = AssessmentStatus.COMPLETED
    
    logger.info(f"HR override for candidate {candidate_id}: {decision.decision}")
    
    return {
        "message": "Override recorded",
        "candidate_id": candidate_id,
        "report_id": report.id,
        "decision": decision.decision
    }
