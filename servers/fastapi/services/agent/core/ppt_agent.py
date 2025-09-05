import asyncio
from typing import Optional, Dict, Any

from .agent_response import AgentResponse, StreamingAgentResponse
from .ppt_executor import PPTExecutor
from ..memory.conversation_memory import ConversationMemory
from ..intent.recognizer import IntentRecognizer
from ..conversation.manager import ConversationManager
from ..intent.intent_types import IntentType


class PPTAgent:
    """PPT Agent core class"""
    
    def __init__(self):
        self.memory = ConversationMemory()
        self.intent_recognizer = IntentRecognizer()
        self.conversation_manager = ConversationManager()
        self.executor = PPTExecutor()
        
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
    
    async def process_message_streaming(
        self, 
        message: str, 
        session_id: str
    ) -> StreamingAgentResponse:
        """Process user message and return streaming response (GPTs style)"""
        try:
            # 1. Identify intent
            intent = await self.intent_recognizer.identify(message)
            
            # 2. Get conversation context
            context = await self.memory.get_context(session_id)
            
            # 3. Check if action should be executed
            if intent.type in [IntentType.CREATE_PRESENTATION, IntentType.MODIFY_SLIDE, IntentType.EXPORT_PRESENTATION]:
                # Execute action with streaming updates
                stream_generator = self.executor.execute_action(intent, message, session_id)
                
                # Store interaction start in memory
                await self.memory.store_interaction(
                    session_id=session_id,
                    user_message=message,
                    agent_response=f"正在执行: {intent.type.value}",
                    intent=intent.type.value,
                    parameters=intent.parameters
                )
                
                return StreamingAgentResponse(
                    intent=intent.type.value,
                    action_required=True,
                    extracted_params=intent.parameters,
                    confidence=intent.confidence,
                    stream_generator=stream_generator
                )
            else:
                # Generate conversational response
                response = await self.conversation_manager.generate_response(
                    message, intent, context
                )
                
                # Store interaction in memory
                await self.memory.store_interaction(
                    session_id=session_id,
                    user_message=message,
                    agent_response=response.text,
                    intent=intent.type.value,
                    parameters=intent.parameters
                )
                
                # Create streaming response for text-only reply
                async def text_generator():
                    yield response.text
                    if response.follow_up_question:
                        yield f"\n\n{response.follow_up_question}"
                
                return StreamingAgentResponse(
                    intent=intent.type.value,
                    action_required=False,
                    extracted_params=intent.parameters,
                    confidence=intent.confidence,
                    stream_generator=text_generator()
                )
                
        except Exception as e:
            # Fallback streaming response
            async def error_generator():
                yield f"抱歉，处理您的消息时遇到了问题：{str(e)}"
                yield "\n\n请重新尝试或提供更多详细信息。"
            
            return StreamingAgentResponse(
                intent="ERROR",
                action_required=False,
                extracted_params={},
                confidence=0.0,
                stream_generator=error_generator()
            )
        
    async def initialize(self):
        """Initialize agent components"""
        # Agent components are already initialized in __init__
        # This method is reserved for future use (e.g., loading models)
        pass