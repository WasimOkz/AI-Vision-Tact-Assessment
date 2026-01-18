"""
HR Handoff Agent
Handles human-in-the-loop transitions and HR communications
"""
from typing import Dict, Any, List, Optional
import logging

from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class HRHandoffAgent:
    """Agent for managing HR handoff and HITL processes"""
    
    def __init__(self):
        self.name = "hr_handoff"
        self.llm = get_llm_service()
        
        self.system_prompt = """You are an HR Handoff Agent responsible for:
1. Preparing assessment summaries for HR review
2. Flagging candidates that need special attention
3. Generating notifications for HR team
4. Managing the handoff process from AI to human review

You ensure smooth transition from automated assessment to human decision-making."""
    
    async def prepare_handoff(
        self,
        candidate_id: str,
        assessment_report: Dict[str, Any],
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Prepare materials for HR handoff"""
        
        # Determine urgency/priority
        priority = self._calculate_priority(assessment_report)
        
        # Generate HR notification
        notification = await self._generate_hr_notification(
            assessment_report,
            priority
        )
        
        # Identify key discussion points
        discussion_points = await self._identify_discussion_points(
            assessment_report,
            conversation_history
        )
        
        return {
            "agent": self.name,
            "candidate_id": candidate_id,
            "priority": priority,
            "notification": notification,
            "discussion_points": discussion_points,
            "requires_immediate_review": priority == "high",
            "handoff_complete": True
        }
    
    def _calculate_priority(self, report: Dict[str, Any]) -> str:
        """Calculate review priority based on assessment"""
        overall_score = report.get("overall_score", 0)
        risks = report.get("risks", [])
        
        # High priority: exceptional candidates or concerning flags
        if overall_score >= 85:
            return "high"  # Excellent candidate - fast-track
        elif overall_score < 50:
            return "high"  # Concerning - needs review
        elif len(risks) >= 3:
            return "medium"  # Multiple risks to consider
        else:
            return "normal"
    
    async def _generate_hr_notification(
        self,
        report: Dict[str, Any],
        priority: str
    ) -> str:
        """Generate notification message for HR"""
        score = report.get("overall_score", 0)
        recommendation = report.get("recommendation", "No recommendation available")
        
        priority_labels = {
            "high": "🔴 HIGH PRIORITY",
            "medium": "🟡 MEDIUM PRIORITY",
            "normal": "🟢 NORMAL"
        }
        
        notification = f"""
{priority_labels.get(priority, 'NORMAL')}

Assessment Complete for Candidate
Overall Score: {score:.1f}/100

Summary: {report.get('executive_summary', 'No summary available')[:200]}...

Recommendation: {recommendation}

Key Strengths:
{chr(10).join(['• ' + s for s in report.get('key_strengths', [])[:3]])}

Risks to Consider:
{chr(10).join(['• ' + r for r in report.get('risks', [])[:2]])}

Please review the full assessment report and make your decision.
"""
        return notification.strip()
    
    async def _identify_discussion_points(
        self,
        report: Dict[str, Any],
        conversation_history: List[Dict[str, str]]
    ) -> List[str]:
        """Identify key points for HR to discuss with hiring manager"""
        points = []
        
        # Based on scores
        if report.get("technical_score", 0) > report.get("behavioral_score", 0) + 15:
            points.append("Strong technical skills but behavioral scores are relatively lower - consider team dynamics")
        
        if report.get("behavioral_score", 0) > report.get("technical_score", 0) + 15:
            points.append("Excellent soft skills - may benefit from technical mentorship")
        
        # Based on risks
        for risk in report.get("risks", [])[:2]:
            points.append(f"Risk to address: {risk}")
        
        # Default points
        if not points:
            points = [
                "Review overall fit with team culture",
                "Discuss growth potential and career path",
                "Confirm compensation expectations alignment"
            ]
        
        return points
    
    async def process_hr_decision(
        self,
        candidate_id: str,
        decision: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process HR's final decision"""
        logger.info(f"Processing HR decision for candidate {candidate_id}: {decision}")
        
        # Generate candidate notification (for future implementation)
        if decision == "approve":
            next_steps = "Schedule final interview or send offer"
        elif decision == "reject":
            next_steps = "Send rejection notification"
        else:  # hold
            next_steps = "Schedule follow-up review in 1 week"
        
        return {
            "agent": self.name,
            "candidate_id": candidate_id,
            "decision": decision,
            "notes": notes,
            "next_steps": next_steps,
            "processed": True
        }
    
    async def generate_closing_message(self, candidate_name: str) -> str:
        """Generate closing message for candidate after interview"""
        return f"""Thank you so much for taking the time to speak with us today, {candidate_name}. 

We really appreciated learning more about your experience and background. Our HR team will review your assessment and get back to you within the next few business days.

If you have any questions in the meantime, please don't hesitate to reach out. We wish you the best!"""
