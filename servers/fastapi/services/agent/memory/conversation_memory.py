import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

# TODO: Add Redis dependency later
# import redis


class ConversationMemory:
    """In-memory conversation storage (will be replaced with Redis)"""
    
    def __init__(self):
        # Temporary in-memory storage
        self._memory: Dict[str, List[Dict]] = {}
        
    async def store_interaction(
        self, 
        session_id: str, 
        user_message: str, 
        agent_response: str,
        intent: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """Store conversation interaction"""
        if session_id not in self._memory:
            self._memory[session_id] = []
            
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "agent_response": agent_response,
            "intent": intent,
            "parameters": parameters or {}
        }
        
        self._memory[session_id].append(interaction)
        
        # Keep only last 20 interactions to prevent memory overflow
        if len(self._memory[session_id]) > 20:
            self._memory[session_id] = self._memory[session_id][-20:]
    
    async def get_context(self, session_id: str, last_n: int = 5) -> List[Dict]:
        """Get conversation context for session"""
        if session_id not in self._memory:
            return []
            
        interactions = self._memory[session_id]
        return interactions[-last_n:] if interactions else []
    
    async def get_recent_intent(self, session_id: str) -> Optional[str]:
        """Get the most recent intent from conversation"""
        context = await self.get_context(session_id, last_n=1)
        if context and context[0].get("intent"):
            return context[0]["intent"]
        return None
    
    async def clear_session(self, session_id: str):
        """Clear conversation history for session"""
        if session_id in self._memory:
            del self._memory[session_id]