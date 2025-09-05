import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

# Redis dependencies - will be conditionally imported
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RedisConversationMemory:
    """Redis-based conversation memory storage"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", session_ttl: int = 3600):
        """
        Initialize Redis conversation memory
        
        Args:
            redis_url: Redis connection URL
            session_ttl: Session time-to-live in seconds (default: 1 hour)
        """
        self.redis_url = redis_url
        self.session_ttl = session_ttl
        self.redis_client = None
        self.logger = logging.getLogger(__name__)
        
        if not REDIS_AVAILABLE:
            self.logger.warning("Redis not available, falling back to in-memory storage")
            self._memory = {}  # Fallback to in-memory storage
    
    async def connect(self):
        """Connect to Redis"""
        if not REDIS_AVAILABLE:
            return
            
        try:
            self.redis_client = redis.from_url(
                self.redis_url, 
                decode_responses=True,
                health_check_interval=30
            )
            # Test connection
            await self.redis_client.ping()
            self.logger.info(f"Connected to Redis at {self.redis_url}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            self.logger.info("Falling back to in-memory storage")
            self.redis_client = None
            self._memory = {}
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.logger.info("Disconnected from Redis")
    
    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for session"""
        return f"ppt_agent:session:{session_id}"
    
    def _get_interaction_key(self, session_id: str, interaction_id: str) -> str:
        """Get Redis key for specific interaction"""
        return f"ppt_agent:session:{session_id}:interaction:{interaction_id}"
    
    async def store_interaction(
        self, 
        session_id: str, 
        user_message: str, 
        agent_response: str,
        intent: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ):
        """Store conversation interaction"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "agent_response": agent_response,
            "intent": intent,
            "parameters": parameters or {}
        }
        
        if self.redis_client:
            await self._store_interaction_redis(session_id, interaction)
        else:
            await self._store_interaction_memory(session_id, interaction)
    
    async def _store_interaction_redis(self, session_id: str, interaction: Dict):
        """Store interaction in Redis"""
        try:
            session_key = self._get_session_key(session_id)
            interaction_id = str(int(datetime.now().timestamp() * 1000))  # millisecond timestamp
            
            # Store the interaction
            interaction_data = json.dumps(interaction)
            await self.redis_client.lpush(session_key, interaction_data)
            
            # Keep only last 20 interactions per session
            await self.redis_client.ltrim(session_key, 0, 19)
            
            # Set expiration for the session
            await self.redis_client.expire(session_key, self.session_ttl)
            
            self.logger.debug(f"Stored interaction for session {session_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to store interaction in Redis: {e}")
            # Fallback to in-memory storage
            await self._store_interaction_memory(session_id, interaction)
    
    async def _store_interaction_memory(self, session_id: str, interaction: Dict):
        """Store interaction in memory (fallback)"""
        if not hasattr(self, '_memory'):
            self._memory = {}
            
        if session_id not in self._memory:
            self._memory[session_id] = []
            
        self._memory[session_id].append(interaction)
        
        # Keep only last 20 interactions
        if len(self._memory[session_id]) > 20:
            self._memory[session_id] = self._memory[session_id][-20:]
    
    async def get_context(self, session_id: str, last_n: int = 5) -> List[Dict]:
        """Get conversation context for session"""
        if self.redis_client:
            return await self._get_context_redis(session_id, last_n)
        else:
            return await self._get_context_memory(session_id, last_n)
    
    async def _get_context_redis(self, session_id: str, last_n: int) -> List[Dict]:
        """Get context from Redis"""
        try:
            session_key = self._get_session_key(session_id)
            
            # Get last N interactions (Redis LRANGE is 0-indexed)
            interactions_data = await self.redis_client.lrange(session_key, 0, last_n - 1)
            
            interactions = []
            for data in interactions_data:
                try:
                    interaction = json.loads(data)
                    interactions.append(interaction)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse interaction data: {e}")
            
            # Redis returns in reverse order (newest first), so reverse to get chronological order
            return list(reversed(interactions))
            
        except Exception as e:
            self.logger.error(f"Failed to get context from Redis: {e}")
            # Fallback to in-memory storage
            return await self._get_context_memory(session_id, last_n)
    
    async def _get_context_memory(self, session_id: str, last_n: int) -> List[Dict]:
        """Get context from memory (fallback)"""
        if not hasattr(self, '_memory'):
            self._memory = {}
            
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
        if self.redis_client:
            await self._clear_session_redis(session_id)
        else:
            await self._clear_session_memory(session_id)
    
    async def _clear_session_redis(self, session_id: str):
        """Clear session from Redis"""
        try:
            session_key = self._get_session_key(session_id)
            await self.redis_client.delete(session_key)
            self.logger.info(f"Cleared session {session_id} from Redis")
        except Exception as e:
            self.logger.error(f"Failed to clear session from Redis: {e}")
    
    async def _clear_session_memory(self, session_id: str):
        """Clear session from memory (fallback)"""
        if hasattr(self, '_memory') and session_id in self._memory:
            del self._memory[session_id]
    
    async def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        if self.redis_client:
            return await self._get_active_sessions_redis()
        else:
            return await self._get_active_sessions_memory()
    
    async def _get_active_sessions_redis(self) -> List[str]:
        """Get active sessions from Redis"""
        try:
            pattern = "ppt_agent:session:*"
            keys = await self.redis_client.keys(pattern)
            
            # Extract session IDs from keys
            session_ids = []
            for key in keys:
                # Key format: ppt_agent:session:{session_id}
                if key.count(':') == 2:  # Avoid interaction-specific keys
                    session_id = key.split(':')[2]
                    session_ids.append(session_id)
            
            return session_ids
        except Exception as e:
            self.logger.error(f"Failed to get active sessions from Redis: {e}")
            return []
    
    async def _get_active_sessions_memory(self) -> List[str]:
        """Get active sessions from memory (fallback)"""
        if hasattr(self, '_memory'):
            return list(self._memory.keys())
        return []
    
    async def cleanup_expired_sessions(self):
        """Cleanup expired sessions (mainly for in-memory fallback)"""
        if not self.redis_client and hasattr(self, '_memory'):
            # For in-memory storage, we'll implement a simple cleanup
            # In production, Redis handles expiration automatically
            current_time = datetime.now()
            expired_sessions = []
            
            for session_id, interactions in self._memory.items():
                if interactions:
                    last_interaction_time = datetime.fromisoformat(
                        interactions[-1]["timestamp"]
                    )
                    if current_time - last_interaction_time > timedelta(seconds=self.session_ttl):
                        expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self._memory[session_id]
                self.logger.info(f"Cleaned up expired session: {session_id}")
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        stats = {
            "redis_connected": self.redis_client is not None,
            "redis_url": self.redis_url if self.redis_client else None,
            "session_ttl": self.session_ttl,
            "storage_type": "redis" if self.redis_client else "memory"
        }
        
        if self.redis_client:
            try:
                info = await self.redis_client.info()
                stats.update({
                    "redis_version": info.get("redis_version"),
                    "used_memory_human": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients")
                })
            except Exception as e:
                self.logger.error(f"Failed to get Redis stats: {e}")
        else:
            if hasattr(self, '_memory'):
                stats.update({
                    "active_sessions": len(self._memory),
                    "total_interactions": sum(len(interactions) for interactions in self._memory.values())
                })
        
        return stats