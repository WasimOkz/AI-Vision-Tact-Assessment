"""
Pydantic models for Candidate data
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class AssessmentStatus(str, Enum):
    """Assessment status enum"""
    PENDING = "pending"
    DATA_INGESTION = "data_ingestion"
    PROFILE_ANALYSIS = "profile_analysis"
    TECHNICAL_INTERVIEW = "technical_interview"
    BEHAVIORAL_INTERVIEW = "behavioral_interview"
    EVALUATION = "evaluation"
    HR_REVIEW = "hr_review"
    COMPLETED = "completed"


class CandidateInput(BaseModel):
    """Input model for creating a candidate"""
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    resume_base64: Optional[str] = None  # Base64 encoded PDF
    job_role: str = Field(default="Software Engineer")


class LinkedInProfile(BaseModel):
    """LinkedIn profile data"""
    name: str = ""
    headline: str = ""
    summary: str = ""
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    skills: List[str] = []
    certifications: List[str] = []


class GitHubProfile(BaseModel):
    """GitHub profile data"""
    username: str = ""
    bio: str = ""
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    top_languages: List[str] = []
    repositories: List[Dict[str, Any]] = []
    contributions_last_year: int = 0


class ResumeData(BaseModel):
    """Parsed resume data"""
    raw_text: str = ""
    skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []
    certifications: List[str] = []


class CandidateProfile(BaseModel):
    """Unified candidate profile"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    job_role: str
    linkedin: Optional[LinkedInProfile] = None
    github: Optional[GitHubProfile] = None
    resume: Optional[ResumeData] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: AssessmentStatus = AssessmentStatus.PENDING
    
    # Unified data
    all_skills: List[str] = []
    experience_summary: str = ""
    key_strengths: List[str] = []


class CandidateResponse(BaseModel):
    """Response model for candidate"""
    id: str
    name: str
    email: str
    job_role: str
    status: AssessmentStatus
    created_at: datetime
    has_linkedin: bool
    has_github: bool
    has_resume: bool


class CandidateListResponse(BaseModel):
    """Response model for candidate list"""
    candidates: List[CandidateResponse]
    total: int
