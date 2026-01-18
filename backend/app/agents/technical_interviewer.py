"""
Technical Interviewer Agent
Conducts technical assessment based on candidate's skills and experience
"""
from typing import Dict, Any, List
import logging

from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class TechnicalInterviewerAgent:
    """Agent for conducting technical interviews"""
    
    def __init__(self):
        self.name = "technical_interviewer"
        self.llm = get_llm_service()
        self.questions_asked = 0
        self.max_questions = 4  # Reduced count for higher quality deep-dives
        
        self.system_prompt = """You are an expert Senior Technical Interviewer at a top-tier tech company.
Your goal is to accurately assess the candidate's TRUE engineering depth.

CORE BEHAVIORS:
1. **Adaptive Difficulty**: Start with a standard question. If they answer well, immediately escalate complexity. If they struggle, pivot to a simpler related concept.
2. **Deep Diving**: Do NOT accept surface-level definitions. Ask "Why?", "How would that scale?", "What are the trade-offs?".
3. **Context-Aware**: Reference their specific projects/skills from their profile. E.g., "I see you used Redis in Project X..."
4. **Code-Oriented**: Ask for brief code snippets or architectural explanations where appropriate.
5. **No Fluff**: Be concise, professional, and direct. Avoid excessive praise like "Great answer!".

INTERVIEW STAGES:
- Question 1: System Design / Architecture (based on their strongest claim)
- Question 2: Coding/Algorithm concept (complexity, optimization)
- Question 3: Debugging/Production Engineering (scalability, reliability)
- Question 4: Specific technology deep-dive (language/framework specific)

Your persona: Experienced, fair, curious, but rigorous. You are NOT a checklist reader."""
    
    async def generate_initial_question(self, candidate_context: str) -> str:
        """Generate the first technical question"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""Generate the first system design question for this candidate.

CANDIDATE CONTEXT:
{candidate_context}

INSTRUCTIONS:
1. Identify their most impressive claimed project or skill.
2. Ask a System Design question related to it.
3. START directly with the question. Do not say "Let's start".
4. Example: "You mentioned building a real-time chat app. How did you handle message persistence and varying network latency?"
"""}
        ]
        
        response = await self.llm.generate_response(messages, temperature=0.7)
        self.questions_asked = 1
        return response
    
    async def process_response(
        self,
        candidate_context: str,
        conversation_history: List[Dict[str, str]],
        user_message: str
    ) -> Dict[str, Any]:
        """Process candidate's technical response"""
        self.questions_asked += 1
        
        # Determine strict state
        is_last_question = self.questions_asked >= self.max_questions
        
        # Dynamic Prompt Construction based on interview progress
        if is_last_question:
            instruction = """
This is the final technical interaction.
1. Briefly acknowledge their answer (1 sentence).
2. Do NOT ask another question.
3. Say exactly: "Thank you, that covers the technical portion. I'll now pass you to my colleague for the behavioral interview. [TRANSITION:behavioral]"
"""
        else:
            instruction = f"""
ANALYZE their response to the previous question:
- Is it correct?
- Is it deep or superficial?

DECISION LOGIC:
A) If **VAGUE/SUPERFICIAL**: Ask a follow-up probe. "Could you be more specific about...?" or "What happens if that service fails?"
B) If **WRONG**: Gently correct them and ask a simpler variable. "Actually, typically X happens. But let's look at..."
C) If **GOOD**: Move to the next topic (Coding, Debugging, or Tech Stack).

CURRENT QUESTION NUMBER: {self.questions_asked}/{self.max_questions}

Generate ONLY the response (Evaluation + Next Question/Follow-up).
"""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"CANDIDATE PROFILE:\n{candidate_context}"}
        ]
        
        # Add limited history to maintain focus but keep context
        messages.extend(conversation_history[-8:])
        messages.append({"role": "user", "content": user_message})
        messages.append({"role": "system", "content": instruction})
        
        response = await self.llm.generate_response(messages)
        
        should_transition = "[TRANSITION:behavioral]" in response
        clean_response = response.replace("[TRANSITION:behavioral]", "").strip()
        
        return {
            "agent": self.name,
            "response": clean_response,
            "should_transition": should_transition,
            "next_agent": "behavioral_interviewer" if should_transition else None,
            "questions_asked": self.questions_asked
        }
    
    async def evaluate_performance(
        self, 
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Evaluate overall technical performance"""
        messages = [
            {"role": "system", "content": """You are a Lead Engineer evaluating a technical interview.
Output valid JSON only.

Schema:
{
    "score": int (0-100),
    "feedback": "string (executive summary)",
    "strengths": ["string", "string"],
    "areas_for_improvement": ["string", "string"],
    "technical_level": "Junior" | "Mid" | "Senior" | "Staff"
}
"""},
            {"role": "user", "content": f"""Evaluate this conversation history based on:
1. Depth of technical understanding
2. System design capability
3. Communication clarity

HISTORY:
{self._format_history(conversation_history)}"""}
        ]
        
        try:
            # Use structured output capability logic if available, otherwise parse text
            response_text = await self.llm.generate_response(messages)
            # Basic cleaning to ensure JSON
            import json
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            data = json.loads(response_text[start:end])
            
            return {
                "agent": self.name,
                "category": "Technical Skills",
                "score": data.get("score", 70),
                "feedback": data.get("feedback", "Technical assessment completed."),
                "strengths": data.get("strengths", []),
                "areas_for_improvement": data.get("areas_for_improvement", [])
            }
        except:
            # Fallback
            return {
                "agent": self.name,
                "category": "Technical Skills",
                "score": 75,
                "feedback": "Technical interview completed. Candidate demonstrated reasonable knowledge.",
                "strengths": ["Communication"],
                "areas_for_improvement": ["Depth in specific areas"]
            }

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """Format conversation history for evaluation"""
        formatted = []
        for msg in history:
            role = "Interviewer" if msg.get("role") == "assistant" else "Candidate"
            formatted.append(f"{role}: {msg.get('content', '')}")
        return "\n\n".join(formatted)
