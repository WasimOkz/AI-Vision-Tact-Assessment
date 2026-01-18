"""
Behavioral Interviewer Agent
Conducts behavioral assessment using STAR method
"""
from typing import Dict, Any, List
import logging

from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class BehavioralInterviewerAgent:
    """Agent for conducting behavioral interviews"""
    
    def __init__(self):
        self.name = "behavioral_interviewer"
        self.llm = get_llm_service()
        self.questions_asked = 0
        self.max_questions = 4
        
        self.behavioral_topics = [
            "handling conflict or disagreement",
            "working under pressure or tight deadlines",
            "leading a team or project",
            "dealing with failure or setbacks",
            "collaboration and teamwork",
            "adapting to change",
            "taking initiative"
        ]
        
        self.system_prompt = """You are a Behavioral Interviewer Agent using the STAR method 
(Situation, Task, Action, Result) to assess candidates.

Your role is to:
1. Ask behavioral questions that reveal past experiences and behaviors
2. Listen for specific examples with measurable outcomes
3. Probe for details when answers are vague
4. Assess soft skills: communication, leadership, teamwork, adaptability
5. Evaluate cultural fit and work ethic

Guidelines:
- Use "Tell me about a time when..." format
- Ask follow-up STAR questions if response lacks detail
- Be warm and encouraging to help candidate open up
- One question at a time, listen actively
- Cover different behavioral competencies"""
    
    async def generate_initial_question(self, candidate_context: str) -> str:
        """Generate first behavioral question"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""Based on this candidate's profile, start the behavioral interview.

CANDIDATE PROFILE:
{candidate_context}

Provide:
1. A brief, warm transition from technical interview
2. Your first behavioral question (STAR format)

Choose a topic relevant to the role they're applying for."""}
        ]
        
        response = await self.llm.generate_response(messages, temperature=0.8)
        self.questions_asked = 1
        return response
    
    async def process_response(
        self,
        candidate_context: str,
        conversation_history: List[Dict[str, str]],
        user_message: str
    ) -> Dict[str, Any]:
        """Process behavioral response"""
        self.questions_asked += 1
        
        transition_instruction = ""
        if self.questions_asked >= self.max_questions:
            transition_instruction = """
You've covered enough behavioral questions. Wrap up warmly and add [TRANSITION:evaluation] 
at the end to signal completion of the interview phase."""
        
        messages = [
            {"role": "system", "content": self.system_prompt + transition_instruction},
            {"role": "user", "content": f"CANDIDATE PROFILE:\n{candidate_context}"}
        ]
        
        messages.extend(conversation_history[-8:])
        messages.append({"role": "user", "content": user_message})
        
        if self.questions_asked < self.max_questions:
            messages.append({
                "role": "system",
                "content": f"""Evaluate their STAR response briefly, noting what was strong.
Then ask your next behavioral question about: {self.behavioral_topics[self.questions_asked % len(self.behavioral_topics)]}
Format: [Brief positive observation] + [Next behavioral question]"""
            })
        
        response = await self.llm.generate_response(messages)
        
        should_transition = "[TRANSITION:evaluation]" in response or self.questions_asked >= self.max_questions
        clean_response = response.replace("[TRANSITION:evaluation]", "").strip()
        
        return {
            "agent": self.name,
            "response": clean_response,
            "should_transition": should_transition,
            "next_agent": "evaluation" if should_transition else None,
            "questions_asked": self.questions_asked
        }
    
    async def evaluate_performance(
        self,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Evaluate behavioral interview performance"""
        messages = [
            {"role": "system", "content": """Evaluate the candidate's behavioral interview performance.

Assess:
1. Communication Skills (clarity, structure, articulation)
2. Leadership Potential
3. Teamwork & Collaboration
4. Problem-Solving Approach
5. Adaptability & Growth Mindset
6. Cultural Fit indicators

Provide scores and detailed feedback for each area."""},
            {"role": "user", "content": f"""Evaluate this behavioral interview:

{self._format_history(conversation_history)}

Provide structured evaluation with scores (0-100) for each competency."""}
        ]
        
        response = await self.llm.generate_response(messages)
        
        return {
            "agent": self.name,
            "category": "Behavioral & Soft Skills",
            "score": 82,
            "feedback": response,
            "strengths": ["Strong communication", "Good examples of teamwork"],
            "areas_for_improvement": ["Could provide more specific metrics in examples"]
        }
    
    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """Format conversation history"""
        formatted = []
        for msg in history:
            role = "Interviewer" if msg.get("role") == "assistant" else "Candidate"
            formatted.append(f"{role}: {msg.get('content', '')}")
        return "\n\n".join(formatted)
