from typing import Optional, Dict, Any, AsyncGenerator
from pydantic import BaseModel


class AgentResponse(BaseModel):
    """Agent response model"""
    text: str
    intent: Optional[str] = None
    action_required: bool = False
    follow_up_question: Optional[str] = None
    extracted_params: Dict[str, Any] = {}
    confidence: float = 0.0
    is_streaming: bool = False
    
    class Config:
        arbitrary_types_allowed = True


class StreamingAgentResponse:
    """Streaming agent response for GPTs-style interaction"""
    
    def __init__(
        self,
        intent: Optional[str] = None,
        action_required: bool = False,
        extracted_params: Dict[str, Any] = None,
        confidence: float = 0.0,
        stream_generator: Optional[AsyncGenerator[str, None]] = None
    ):
        self.intent = intent
        self.action_required = action_required
        self.extracted_params = extracted_params or {}
        self.confidence = confidence
        self.stream_generator = stream_generator
    
    async def stream_response(self) -> AsyncGenerator[str, None]:
        """Stream response content"""
        if self.stream_generator:
            async for chunk in self.stream_generator:
                yield chunk
        else:
            yield "抱歉，没有可用的响应内容。"