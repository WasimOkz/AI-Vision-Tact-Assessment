"""
Candidates API Router
Handles candidate creation, data ingestion, and profile retrieval
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Form
from typing import Optional
import logging
import base64

from app.models.candidate import (
    CandidateInput, CandidateProfile, CandidateResponse, 
    CandidateListResponse, AssessmentStatus
)
from app.services.ingestion import IngestionService
from app.services.knowledge_base import KnowledgeBaseService

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory storage (for demo - production would use database)
candidates_db: dict[str, CandidateProfile] = {}
ingestion_service = IngestionService()
kb_service = KnowledgeBaseService()


@router.post("/", response_model=CandidateResponse)
async def create_candidate(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    job_role: str = Form(default="Software Engineer"),
    linkedin_url: Optional[str] = Form(default=None),
    github_url: Optional[str] = Form(default=None),
    resume: Optional[UploadFile] = File(default=None)
):
    """
    Create a new candidate and trigger background data ingestion
    """
    logger.info(f"Creating candidate: {name} ({email})")
    
    # Handle resume upload
    resume_base64 = None
    if resume:
        content = await resume.read()
        resume_base64 = base64.b64encode(content).decode('utf-8')
    
    # Create candidate profile
    candidate = CandidateProfile(
        name=name,
        email=email,
        job_role=job_role,
        status=AssessmentStatus.DATA_INGESTION
    )
    
    # Store candidate
    candidates_db[candidate.id] = candidate
    
    # Trigger background ingestion
    background_tasks.add_task(
        process_candidate_data,
        candidate.id,
        linkedin_url,
        github_url,
        resume_base64
    )
    
    return CandidateResponse(
        id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        job_role=candidate.job_role,
        status=candidate.status,
        created_at=candidate.created_at,
        has_linkedin=linkedin_url is not None,
        has_github=github_url is not None,
        has_resume=resume is not None
    )


async def process_candidate_data(
    candidate_id: str,
    linkedin_url: Optional[str],
    github_url: Optional[str],
    resume_base64: Optional[str]
):
    """Background task to process candidate data from all sources"""
    logger.info(f"Starting data ingestion for candidate: {candidate_id}")
    
    candidate = candidates_db.get(candidate_id)
    if not candidate:
        logger.error(f"Candidate not found: {candidate_id}")
        return
    
    try:
        # Fetch LinkedIn data
        if linkedin_url:
            candidate.linkedin = await ingestion_service.fetch_linkedin_profile(linkedin_url)
            
        # Fetch GitHub data
        if github_url:
            candidate.github = await ingestion_service.fetch_github_profile(github_url)
            
        # Parse resume
        if resume_base64:
            candidate.resume = await ingestion_service.parse_resume(resume_base64)
        
        # Build unified profile
        await kb_service.build_unified_profile(candidate)
        
        # Update status
        candidate.status = AssessmentStatus.PROFILE_ANALYSIS
        logger.info(f"Data ingestion completed for candidate: {candidate_id}")
        
    except Exception as e:
        logger.error(f"Error processing candidate data: {e}")
        candidate.status = AssessmentStatus.PENDING


@router.get("/{candidate_id}", response_model=CandidateProfile)
async def get_candidate(candidate_id: str):
    """Get candidate profile by ID"""
    candidate = candidates_db.get(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.get("/", response_model=CandidateListResponse)
async def list_candidates():
    """List all candidates"""
    candidates = [
        CandidateResponse(
            id=c.id,
            name=c.name,
            email=c.email,
            job_role=c.job_role,
            status=c.status,
            created_at=c.created_at,
            has_linkedin=c.linkedin is not None,
            has_github=c.github is not None,
            has_resume=c.resume is not None
        )
        for c in candidates_db.values()
    ]
    return CandidateListResponse(candidates=candidates, total=len(candidates))


@router.delete("/{candidate_id}")
async def delete_candidate(candidate_id: str):
    """Delete a candidate"""
    if candidate_id not in candidates_db:
        raise HTTPException(status_code=404, detail="Candidate not found")
    del candidates_db[candidate_id]
    return {"message": "Candidate deleted successfully"}
