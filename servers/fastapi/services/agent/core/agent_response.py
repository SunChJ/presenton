from typing import Optional, Dict, Any
from pydantic import BaseModel


class AgentResponse(BaseModel):
    """Agent response model"""
    text: str
    intent: Optional[str] = None
    action_required: bool = False
    follow_up_question: Optional[str] = None
    extracted_params: Dict[str, Any] = {}
    confidence: float = 0.0
    
    class Config:
        arbitrary_types_allowed = True