"""
Agent Orchestrator
LangGraph-based state machine for multi-agent orchestration
"""
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from enum import Enum
import logging
import operator

from app.agents.profile_analyzer import ProfileAnalyzerAgent
from app.agents.technical_interviewer import TechnicalInterviewerAgent
from app.agents.behavioral_interviewer import BehavioralInterviewerAgent
from app.agents.evaluation import EvaluationAgent
from app.agents.hr_handoff import HRHandoffAgent
from app.services.knowledge_base import KnowledgeBaseService
from app.models.assessment import AssessmentReport, ChatMessage, MessageRole

logger = logging.getLogger(__name__)


class AgentState(str, Enum):
    """Agent states in the interview flow"""
    PROFILE_ANALYSIS = "profile_analyzer"
    TECHNICAL_INTERVIEW = "technical_interviewer"
    BEHAVIORAL_INTERVIEW = "behavioral_interviewer"
    EVALUATION = "evaluation"
    HR_HANDOFF = "hr_handoff"
    COMPLETE = "complete"


class InterviewState(TypedDict):
    """State schema for the interview state machine"""
    candidate_id: str
    session_id: str
    current_agent: str
    messages: List[Dict[str, Any]]
    agent_evaluations: List[Dict[str, Any]]
    candidate_context: str
    is_complete: bool


class AgentOrchestrator:
    """
    LangGraph-style orchestrator for multi-agent interview system
    Manages state transitions and agent coordination
    """
    
    def __init__(self):
        # Initialize agents
        self.profile_analyzer = ProfileAnalyzerAgent()
        self.technical_interviewer = TechnicalInterviewerAgent()
        self.behavioral_interviewer = BehavioralInterviewerAgent()
        self.evaluation_agent = EvaluationAgent()
        self.hr_handoff = HRHandoffAgent()
        
        # Knowledge base service
        self.kb_service = KnowledgeBaseService()
        
        # Session states
        self._states: Dict[str, InterviewState] = {}
        
        # Agent transition map (state machine definition)
        self.transitions = {
            AgentState.PROFILE_ANALYSIS: AgentState.TECHNICAL_INTERVIEW,
            AgentState.TECHNICAL_INTERVIEW: AgentState.BEHAVIORAL_INTERVIEW,
            AgentState.BEHAVIORAL_INTERVIEW: AgentState.EVALUATION,
            AgentState.EVALUATION: AgentState.HR_HANDOFF,
            AgentState.HR_HANDOFF: AgentState.COMPLETE
        }
        
        logger.info("Agent Orchestrator initialized with 5 agents")
    
    def _get_agent(self, agent_name: str):
        """Get agent instance by name"""
        agents = {
            "profile_analyzer": self.profile_analyzer,
            "technical_interviewer": self.technical_interviewer,
            "behavioral_interviewer": self.behavioral_interviewer,
            "evaluation": self.evaluation_agent,
            "hr_handoff": self.hr_handoff
        }
        return agents.get(agent_name, self.profile_analyzer)
    
    async def initialize_session(
        self,
        session_id: str,
        candidate_id: str,
        candidate_context: str
    ) -> InterviewState:
        """Initialize a new interview session state"""
        state: InterviewState = {
            "candidate_id": candidate_id,
            "session_id": session_id,
            "current_agent": AgentState.PROFILE_ANALYSIS.value,
            "messages": [],
            "agent_evaluations": [],
            "candidate_context": candidate_context,
            "is_complete": False
        }
        self._states[session_id] = state
        logger.info(f"Session initialized: {session_id}")
        return state
    
    async def get_initial_message(self, session_id: str, candidate) -> str:
        """Get initial message from profile analyzer"""
        # Get candidate context
        context = await self.kb_service.get_candidate_context(candidate.id)
        
        # Initialize state if needed
        if session_id not in self._states:
            await self.initialize_session(session_id, candidate.id, context)
        
        # Generate initial message
        initial_msg = await self.profile_analyzer.generate_initial_message(
            context, 
            candidate.name
        )
        
        # Record message in state
        self._states[session_id]["messages"].append({
            "role": "assistant",
            "content": initial_msg,
            "agent": "profile_analyzer"
        })
        
        return initial_msg
    
    async def process_message(
        self,
        session_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Process user message through current agent
        Returns agent response and any state transitions
        """
        state = self._states.get(session_id)
        if not state:
            return {
                "error": "Session not found",
                "response": "I'm sorry, your session has expired. Please start a new assessment."
            }
        
        # Record user message
        state["messages"].append({
            "role": "user",
            "content": user_message
        })
        
        # Get current agent
        current_agent = self._get_agent(state["current_agent"])
        
        # Format conversation history
        conversation_history = [
            {"role": m["role"], "content": m["content"]}
            for m in state["messages"][-10:]  # Last 10 messages for context
        ]
        
        # Process through current agent
        result = await current_agent.process_response(
            state["candidate_context"],
            conversation_history,
            user_message
        )
        
        # Record agent response
        agent_response = result.get("response", "")
        state["messages"].append({
            "role": "assistant",
            "content": agent_response,
            "agent": state["current_agent"]
        })
        
        # Handle state transition
        if result.get("should_transition"):
            next_agent = result.get("next_agent")
            if next_agent:
                await self._transition_to_agent(session_id, next_agent)
                
                # Get transition message from new agent if not evaluation
                if next_agent not in ["evaluation", "hr_handoff"]:
                    new_agent = self._get_agent(next_agent)
                    transition_msg = await new_agent.generate_initial_question(
                        state["candidate_context"]
                    )
                    state["messages"].append({
                        "role": "assistant",
                        "content": transition_msg,
                        "agent": next_agent
                    })
                    agent_response = agent_response + "\n\n" + transition_msg
        
        return {
            "response": agent_response,
            "current_agent": state["current_agent"],
            "is_complete": state["is_complete"],
            "messages_count": len(state["messages"])
        }
    
    async def _transition_to_agent(self, session_id: str, next_agent: str):
        """Handle transition to next agent"""
        state = self._states.get(session_id)
        if not state:
            return
        
        # Store evaluation from current agent before transitioning
        current_agent = self._get_agent(state["current_agent"])
        if hasattr(current_agent, 'evaluate_performance'):
            evaluation = await current_agent.evaluate_performance(state["messages"])
            state["agent_evaluations"].append(evaluation)
        
        # Update state
        state["current_agent"] = next_agent
        logger.info(f"Session {session_id} transitioned to agent: {next_agent}")
        
        # Check if interview is complete
        if next_agent == "evaluation":
            state["is_complete"] = True
    
    async def generate_final_report(
        self,
        session,
        candidate
    ) -> AssessmentReport:
        """Generate final assessment report"""
        state = self._states.get(session.id)
        
        if state:
            # Collect any remaining evaluations
            for agent_name in ["profile_analyzer", "technical_interviewer", "behavioral_interviewer"]:
                agent = self._get_agent(agent_name)
                if hasattr(agent, 'evaluate_performance'):
                    # Check if we already have evaluation for this agent
                    existing = [e for e in state["agent_evaluations"] if e.get("agent") == agent_name]
                    if not existing:
                        evaluation = await agent.evaluate_performance(state["messages"])
                        state["agent_evaluations"].append(evaluation)
            
            context = state["candidate_context"]
            messages = state["messages"]
            evaluations = state["agent_evaluations"]
        else:
            context = await self.kb_service.get_candidate_context(candidate.id)
            messages = []
            evaluations = []
        
        # Generate report through evaluation agent
        report = await self.evaluation_agent.generate_final_report(
            candidate_id=candidate.id,
            session_id=session.id,
            candidate_context=context,
            conversation_history=messages,
            agent_evaluations=evaluations
        )
        
        # Prepare HR handoff
        await self.hr_handoff.prepare_handoff(
            candidate_id=candidate.id,
            assessment_report=report.model_dump(),
            conversation_history=messages
        )
        
        return report
    
    def get_session_state(self, session_id: str) -> Optional[InterviewState]:
        """Get current session state"""
        return self._states.get(session_id)
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agents"""
        return [
            "profile_analyzer",
            "technical_interviewer", 
            "behavioral_interviewer",
            "evaluation",
            "hr_handoff"
        ]
