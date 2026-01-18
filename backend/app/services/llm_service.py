"""
LLM Service
Handles all LLM interactions using Groq via OpenAI SDK
With Smart Fallback for robust demos
"""
from typing import List, Dict, Any, Optional
import logging
import json
import random

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMService:
    """Service for LLM interactions using Groq"""
    
    def __init__(self):
        self.client = None
        self.model_name = settings.LLM_MODEL
        self._init_client()
    
    def _init_client(self):
        """Initialize OpenAI client configured for Groq"""
        if settings.GROQ_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=settings.GROQ_API_KEY,
                    base_url=settings.GROQ_BASE_URL
                )
                logger.info(f"Groq client initialized with model: {self.model_name}")
            except ImportError:
                logger.error("openai package not installed")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        else:
            logger.warning("GROQ_API_KEY not set - using mock responses")
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate a response from Groq"""
        if not self.client:
            return self._get_smart_mock_response(messages)
        
        try:
            # Force system message for better instruction adherence
            system_instruction = "You are a helpful AI assistant."
            if messages and messages[0]['role'] == 'system':
                system_instruction = messages[0]['content']
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            # Fallback to smart mock on error so demo doesn't break
            return self._get_smart_mock_response(messages)
    
    async def generate_structured_response(
        self,
        messages: List[Dict[str, str]],
        response_format: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a structured JSON response"""
        if not self.client:
             return {"response": self._get_smart_mock_response(messages)}

        try:
            # Force JSON mode instruction
            messages_with_json = messages.copy()
            messages_with_json.append({
                "role": "system", 
                "content": "You must respond with valid JSON only."
            })
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages_with_json,
                temperature=0.1,  # Lower temp for structured data
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"JSON parsing error or API error: {e}")
            # Fallback
            return {"response": "Error generating structured data, proceeding with standard flow."}

    def _get_smart_mock_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate intelligent mock responses based on context"""
        full_context = " ".join([m.get("content", "") for m in messages]).lower()
        system_prompt = messages[0]["content"].lower() if messages else ""
        
        # Profile Analyzer
        if "profile" in system_prompt:
            if "hello" in full_context or "hi" in full_context: 
                return "Hello! I'm your AI Profile Analyzer. I've reviewed your resume and profiles. Could you briefly introduce yourself and highlight your key technical strengths?"
            return "Thank you. Your background aligns well with our requirements. I'd like to proceed to the technical assessment. [TRANSITION:technical]"
            
        # Technical Interviewer
        elif "technical" in system_prompt:
             if "design" in full_context:
                 return "That's a solid architectural choice. How would you verify the scalability of that solution using load testing?"
             return "Good answer. Now, let's move to the behavioral section to understand your work style better. [TRANSITION:behavioral]"
            
        # Behavioral Interviewer
        elif "behavioral" in system_prompt:
             if "conflict" in full_context:
                 return "Handling conflict constructively is key. Can you share an example of a time you had to persuade a stakeholder to change their mind?"
             return "Excellent examples. I have gathered enough information to form a comprehensive evaluation. [TRANSITION:evaluation]"
        
        # Default
        return "I understand. That's a valid point. Please continue."


# Singleton instance
_llm_service: Optional[LLMService] = None

def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
