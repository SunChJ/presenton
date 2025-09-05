from typing import Optional, Dict, Any
from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    session_id: str


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    intent: Optional[str] = None
    action_required: bool = False
    follow_up_question: Optional[str] = None
    extracted_params: Dict[str, Any] = {}
    confidence: float = 0.0