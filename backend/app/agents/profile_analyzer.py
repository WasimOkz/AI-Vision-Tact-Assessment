"""
Profile Analyzer Agent
Analyzes candidate's combined profile data and identifies key strengths
"""
from typing import Dict, Any, List
import logging

from app.services.llm_service import get_llm_service
from app.services.knowledge_base import KnowledgeBaseService

logger = logging.getLogger(__name__)


class ProfileAnalyzerAgent:
    """Agent for analyzing candidate profiles"""
    
    def __init__(self):
        self.name = "profile_analyzer"
        self.llm = get_llm_service()
        self.kb = KnowledgeBaseService()
        
        self.system_prompt = """You are a Profile Analyzer Agent for an AI-powered candidate assessment platform.
Your role is to:
1. Analyze the candidate's complete profile (LinkedIn, GitHub, Resume)
2. Identify key strengths and potential areas of concern
3. Generate insightful questions to understand the candidate better
4. Provide an initial assessment of the candidate's fit for the role

Be professional, thorough, and objective in your analysis.
Focus on understanding the candidate's experience, skills, and potential."""
    
    async def analyze_profile(self, candidate_context: str) -> Dict[str, Any]:
        """Perform initial profile analysis"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""Analyze this candidate's profile with scrutiny.

CANDIDATE CONTEXT:
{candidate_context}

OUTPUT REQUIRED (Markdown):
1. **Executive Summary**: 2 sentences on their strongest selling point.
2. **Key Signals**:
   - Technical Stack Match: (High/Medium/Low)
   - Experience Level: (Junior/Mid/Senior)
   - Notable Achievements: List 2 specific items.
3. **Risk Factors**: What skills look claimed but unproven?
4. **Interview Strategy**: Suggest 2 specific deep-dive topics for the technical interviewer.

Be critical and insight-driven."""}
        ]
        
        response = await self.llm.generate_response(messages)
        return {
            "agent": self.name,
            "analysis": response,
            "status": "complete"
        }
    
    async def generate_initial_message(self, candidate_context: str, candidate_name: str) -> str:
        """Generate the initial greeting and question"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""Generate a personalized welcome for {candidate_name}.

CANDIDATE PROFILE:
{candidate_context}

INSTRUCTIONS:
1. Warmly welcome them to the "AI Engineering Assessment".
2. Mention **one specific impressive detail** from their resume (e.g., "I was impressed by your work on X").
3. Ask an open-ended icebreaker related to their most recent role.
4. Keep it under 3 sentences. Professional tone.
"""}
        ]
        
        response = await self.llm.generate_response(messages, temperature=0.8)
        return response
    
    async def process_response(
        self, 
        candidate_context: str,
        conversation_history: List[Dict[str, str]],
        user_message: str
    ) -> Dict[str, Any]:
        """Process user response and determine next steps"""
        messages = [
            {"role": "system", "content": self.system_prompt + """
You are currently chatting with the candidate.
Goal: Validate their background briefly before technical assessment.

DECISION LOGIC:
1. If the user's answer is brief/standard -> Move to technical.
2. If the user asks a question -> Answer briefly, then move to technical.
3. If the user's answer is very detailed -> Acknowledge one point, then move to technical.

To move to technical interview, say:
"That's great context. Let's dive into the technical assessment now to explore your skills further. [TRANSITION:technical]"

Do NOT ask endless profile questions. max 1-2 exchanges.
"""},
            {"role": "user", "content": f"CANDIDATE PROFILE:\n{candidate_context}"}
        ]
        
        # Add conversation history
        messages.extend(conversation_history[-6:])
        messages.append({"role": "user", "content": user_message})
        
        response = await self.llm.generate_response(messages)
        
        # Check for transition signal
        should_transition = "[TRANSITION:technical]" in response
        clean_response = response.replace("[TRANSITION:technical]", "").replace("[CONTINUE]", "").strip()
        
        return {
            "agent": self.name,
            "response": clean_response,
            "should_transition": should_transition,
            "next_agent": "technical_interviewer" if should_transition else None
        }
    
    def get_score(self, analysis: str) -> Dict[str, Any]:
        """Extract scoring from analysis"""
        return {
            "agent": self.name,
            "category": "Profile Completeness",
            "score": 75,  # Would be computed from actual analysis
            "feedback": "Candidate has a well-rounded profile with strong technical background"
        }
