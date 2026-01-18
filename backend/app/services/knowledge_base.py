"""
Knowledge Base Service
Handles building unified candidate profiles and RAG retrieval
"""
from typing import List, Dict, Any, Optional
import logging

from app.models.candidate import CandidateProfile

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """Service for building and querying candidate knowledge base"""
    
    def __init__(self):
        # In-memory knowledge store (production would use vector DB)
        self._knowledge_store: Dict[str, Dict[str, Any]] = {}
        self._embeddings_store: Dict[str, List[float]] = {}
    
    async def build_unified_profile(self, candidate: CandidateProfile) -> None:
        """
        Build unified profile from all candidate data sources
        Combines LinkedIn, GitHub, and Resume into a comprehensive profile
        """
        logger.info(f"Building unified profile for candidate: {candidate.id}")
        
        all_skills = set()
        experience_parts = []
        key_strengths = []
        
        # Process LinkedIn data
        if candidate.linkedin:
            all_skills.update(candidate.linkedin.skills)
            
            # Extract experience summary
            for exp in candidate.linkedin.experience:
                experience_parts.append(
                    f"{exp.get('title', '')} at {exp.get('company', '')} ({exp.get('duration', '')})"
                )
            
            if candidate.linkedin.headline:
                key_strengths.append(f"Professional: {candidate.linkedin.headline}")
        
        # Process GitHub data
        if candidate.github:
            all_skills.update(candidate.github.top_languages)
            
            if candidate.github.public_repos > 20:
                key_strengths.append(f"Active open source contributor ({candidate.github.public_repos} repos)")
            
            if candidate.github.contributions_last_year > 500:
                key_strengths.append(f"Consistent coding activity ({candidate.github.contributions_last_year} contributions)")
            
            # Add project experience
            for repo in candidate.github.repositories[:3]:
                experience_parts.append(f"Project: {repo.get('name')} - {repo.get('description', '')}")
        
        # Process Resume data
        if candidate.resume:
            all_skills.update(candidate.resume.skills)
        
        # Update candidate with unified data
        candidate.all_skills = list(all_skills)
        candidate.experience_summary = " | ".join(experience_parts[:5])
        candidate.key_strengths = key_strengths[:5]
        
        # Store in knowledge base
        self._knowledge_store[candidate.id] = {
            "profile": candidate.model_dump(),
            "skills": list(all_skills),
            "experience": experience_parts,
            "strengths": key_strengths
        }
        
        logger.info(f"Unified profile built with {len(all_skills)} skills")
    
    async def get_candidate_context(self, candidate_id: str) -> str:
        """
        Get formatted context string for candidate
        Used by agents for context-aware responses
        """
        knowledge = self._knowledge_store.get(candidate_id)
        if not knowledge:
            return "No candidate data available."
        
        profile = knowledge["profile"]
        
        context = f"""
CANDIDATE PROFILE:
- Name: {profile.get('name', 'Unknown')}
- Role Applied: {profile.get('job_role', 'Software Engineer')}

SKILLS:
{', '.join(knowledge.get('skills', [])[:15])}

EXPERIENCE:
{chr(10).join(['- ' + exp for exp in knowledge.get('experience', [])[:5]])}

KEY STRENGTHS:
{chr(10).join(['- ' + s for s in knowledge.get('strengths', [])])}
"""
        return context.strip()
    
    async def search_relevant_info(
        self, 
        candidate_id: str, 
        query: str
    ) -> List[str]:
        """
        Search for relevant information in candidate's knowledge base
        Simple keyword matching - production would use vector similarity
        """
        knowledge = self._knowledge_store.get(candidate_id)
        if not knowledge:
            return []
        
        results = []
        query_lower = query.lower()
        
        # Search in skills
        for skill in knowledge.get("skills", []):
            if skill.lower() in query_lower or query_lower in skill.lower():
                results.append(f"Skill: {skill}")
        
        # Search in experience
        for exp in knowledge.get("experience", []):
            if any(word in exp.lower() for word in query_lower.split()):
                results.append(f"Experience: {exp}")
        
        return results[:5]
    
    async def get_assessment_summary(self, candidate_id: str) -> Dict[str, Any]:
        """Get summary data for assessment generation"""
        knowledge = self._knowledge_store.get(candidate_id)
        if not knowledge:
            return {}
        
        return {
            "total_skills": len(knowledge.get("skills", [])),
            "top_skills": knowledge.get("skills", [])[:10],
            "experience_count": len(knowledge.get("experience", [])),
            "strengths": knowledge.get("strengths", []),
            "profile_completeness": self._calculate_completeness(knowledge)
        }
    
    def _calculate_completeness(self, knowledge: Dict[str, Any]) -> float:
        """Calculate profile completeness percentage"""
        score = 0
        if knowledge.get("skills"):
            score += 30
        if knowledge.get("experience"):
            score += 40
        if knowledge.get("strengths"):
            score += 30
        return min(score, 100)
