from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel


class IntentType(str, Enum):
    """Intent types for PPT Agent"""
    CREATE_PRESENTATION = "CREATE_PRESENTATION"
    MODIFY_SLIDE = "MODIFY_SLIDE"
    ADD_CONTENT = "ADD_CONTENT"
    EXPORT_PRESENTATION = "EXPORT_PRESENTATION"
    ANALYZE_CONTENT = "ANALYZE_CONTENT"
    CHAT_QUESTION = "CHAT_QUESTION"
    UNKNOWN = "UNKNOWN"


class Intent(BaseModel):
    """Intent model"""
    type: IntentType
    confidence: float
    parameters: Dict[str, Any] = {}
    
    class Config:
        use_enum_values = True