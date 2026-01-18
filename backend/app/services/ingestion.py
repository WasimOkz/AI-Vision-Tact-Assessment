"""
Data Ingestion Service
Handles fetching and parsing data from LinkedIn, GitHub, and Resume
"""
import base64
import json
import re
from typing import Optional
import logging

from app.models.candidate import LinkedInProfile, GitHubProfile, ResumeData

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for ingesting candidate data from various sources"""
    
    async def fetch_linkedin_profile(self, url: str) -> LinkedInProfile:
        """
        Fetch and parse LinkedIn profile data
        NOTE: This is a MOCK implementation as LinkedIn requires authentication
        In production, use LinkedIn API with OAuth or scraping services
        """
        logger.info(f"Fetching LinkedIn profile: {url}")
        
        # Extract username from URL for mock purposes
        username = url.split("/in/")[-1].strip("/") if "/in/" in url else "candidate"
        
        # Mock LinkedIn data - simulates what would be fetched
        mock_profile = LinkedInProfile(
            name=f"{username.replace('-', ' ').title()}",
            headline="Senior Software Engineer | AI/ML Enthusiast",
            summary="Experienced software engineer with 5+ years of experience in building scalable systems. Passionate about AI and machine learning applications.",
            experience=[
                {
                    "title": "Senior Software Engineer",
                    "company": "Tech Company Inc.",
                    "duration": "2021 - Present",
                    "description": "Leading development of microservices architecture, mentoring junior developers, and implementing CI/CD pipelines."
                },
                {
                    "title": "Software Engineer",
                    "company": "Startup Corp",
                    "duration": "2019 - 2021",
                    "description": "Full-stack development using React and Python. Built RESTful APIs and integrated third-party services."
                }
            ],
            education=[
                {
                    "degree": "B.S. Computer Science",
                    "institution": "State University",
                    "year": "2019"
                }
            ],
            skills=[
                "Python", "JavaScript", "React", "Node.js", "AWS", 
                "Docker", "Kubernetes", "Machine Learning", "SQL", "Git"
            ],
            certifications=["AWS Solutions Architect", "Google Cloud Professional"]
        )
        
        logger.info(f"LinkedIn profile fetched successfully for: {username}")
        return mock_profile
    
    async def fetch_github_profile(self, url: str) -> GitHubProfile:
        """
        Fetch and parse GitHub profile data
        NOTE: This is a MOCK implementation
        In production, use GitHub API for real data
        """
        logger.info(f"Fetching GitHub profile: {url}")
        
        # Extract username from URL
        username = url.rstrip("/").split("/")[-1]
        
        # Mock GitHub data
        mock_profile = GitHubProfile(
            username=username,
            bio="Full-stack developer passionate about open source",
            public_repos=42,
            followers=156,
            following=89,
            top_languages=["Python", "JavaScript", "TypeScript", "Go"],
            repositories=[
                {
                    "name": "ml-pipeline",
                    "description": "End-to-end machine learning pipeline framework",
                    "stars": 234,
                    "language": "Python",
                    "topics": ["machine-learning", "mlops", "pipeline"]
                },
                {
                    "name": "react-dashboard",
                    "description": "Modern admin dashboard built with React and TypeScript",
                    "stars": 89,
                    "language": "TypeScript",
                    "topics": ["react", "dashboard", "admin"]
                },
                {
                    "name": "api-gateway",
                    "description": "Lightweight API gateway with rate limiting",
                    "stars": 156,
                    "language": "Go",
                    "topics": ["api", "gateway", "microservices"]
                }
            ],
            contributions_last_year=847
        )
        
        logger.info(f"GitHub profile fetched successfully for: {username}")
        return mock_profile
    
    async def parse_resume(self, resume_base64: str) -> ResumeData:
        """
        Parse PDF resume into structured data
        Uses basic PDF extraction - in production, use advanced parsing
        """
        logger.info("Parsing resume PDF")
        
        try:
            # Decode base64 PDF
            pdf_bytes = base64.b64decode(resume_base64)
            
            # Extract text using PyMuPDF if available
            raw_text = await self._extract_pdf_text(pdf_bytes)
            
            # Parse structured data from text
            resume_data = await self._parse_resume_text(raw_text)
            
            logger.info("Resume parsed successfully")
            return resume_data
            
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            # Return empty resume data on error
            return ResumeData()
    
    async def _extract_pdf_text(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes"""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except ImportError:
            logger.warning("PyMuPDF not available, using mock text")
            return "Sample resume text - PyMuPDF not installed"
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return ""
    
    async def _parse_resume_text(self, text: str) -> ResumeData:
        """Parse resume text into structured format"""
        # Simple parsing logic - in production use NER or LLM
        skills = []
        skill_keywords = [
            "Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust",
            "React", "Vue", "Angular", "Node.js", "Django", "FastAPI", "Flask",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
            "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
            "SQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch"
        ]
        
        for skill in skill_keywords:
            if skill.lower() in text.lower():
                skills.append(skill)
        
        return ResumeData(
            raw_text=text[:5000],  # Limit text length
            skills=skills,
            experience=[],  # Would need more advanced parsing
            education=[],
            projects=[],
            certifications=[]
        )
