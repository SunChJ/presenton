import asyncio
from typing import Optional, Dict, Any

from .agent_response import AgentResponse
from ..memory.conversation_memory import ConversationMemory
from ..intent.recognizer import IntentRecognizer
from ..conversation.manager import ConversationManager


class PPTAgent:
    """PPT Agent core class"""
    
    def __init__(self):
        self.memory = ConversationMemory()
        self.intent_recognizer = IntentRecognizer()
        self.conversation_manager = ConversationManager()
        
    async def process_message(self, message: str, session_id: str) -> AgentResponse:
        """Process user message and return agent response"""
        try:
            # 1. Identify intent
            intent = await self.intent_recognizer.identify(message)
            
            # 2. Get conversation context
            context = await self.memory.get_context(session_id)
            
            # 3. Generate response
            response = await self.conversation_manager.generate_response(
                message, intent, context
            )
            
            # 4. Store interaction in memory
            await self.memory.store_interaction(
                session_id=session_id,
                user_message=message,
                agent_response=response.text,
                intent=intent.type.value,
                parameters=intent.parameters
            )
            
            return response
            
        except Exception as e:
            # Fallback response in case of errors
            return AgentResponse(
                text=f"抱歉，处理您的消息时遇到了问题。请重新尝试。",
                intent="ERROR",
                action_required=False,
                follow_up_question="您希望我帮您做什么？",
                extracted_params={},
                confidence=0.0
            )
        
    async def initialize(self):
        """Initialize agent components"""
        # Agent components are already initialized in __init__
        # This method is reserved for future use (e.g., loading models)
        pass