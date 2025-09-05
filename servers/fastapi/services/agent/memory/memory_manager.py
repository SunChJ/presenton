import os
import logging
from typing import Optional, Union
from .conversation_memory import ConversationMemory
from .redis_conversation_memory import RedisConversationMemory


class MemoryManager:
    """Memory manager that handles different storage backends"""
    
    def __init__(
        self, 
        redis_url: Optional[str] = None,
        use_redis: bool = True,
        session_ttl: int = 3600
    ):
        """
        Initialize memory manager
        
        Args:
            redis_url: Redis connection URL (auto-detected from env if None)
            use_redis: Whether to prefer Redis over in-memory storage
            session_ttl: Session time-to-live in seconds
        """
        self.logger = logging.getLogger(__name__)
        self.use_redis = use_redis
        self.session_ttl = session_ttl
        
        # Auto-detect Redis URL from environment
        if redis_url is None:
            redis_url = self._detect_redis_url()
        
        self.redis_url = redis_url
        self._memory_instance = None
    
    def _detect_redis_url(self) -> Optional[str]:
        """Auto-detect Redis URL from environment variables"""
        # Check common Redis environment variables
        redis_vars = [
            "REDIS_URL",
            "REDIS_CONNECTION_STRING", 
            "CACHE_URL",
            "REDISCLOUD_URL",
            "REDISTOGO_URL"
        ]
        
        for var in redis_vars:
            url = os.getenv(var)
            if url:
                self.logger.info(f"Found Redis URL from {var}")
                return url
        
        # Check individual Redis components
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = os.getenv("REDIS_PORT", "6379")
        redis_password = os.getenv("REDIS_PASSWORD")
        redis_db = os.getenv("REDIS_DB", "0")
        
        # Build Redis URL
        if redis_password:
            url = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"
        else:
            url = f"redis://{redis_host}:{redis_port}/{redis_db}"
        
        # Check if this looks like a real Redis setup (not just defaults)
        if redis_host != "localhost" or redis_password or redis_db != "0":
            self.logger.info(f"Built Redis URL from environment components")
            return url
        
        # Check if Redis is available locally
        if redis_host == "localhost" and redis_port == "6379":
            self.logger.info("Using default local Redis configuration")
            return url
        
        return None
    
    async def get_memory_instance(self) -> Union[RedisConversationMemory, ConversationMemory]:
        """Get the appropriate memory instance"""
        if self._memory_instance is None:
            await self._initialize_memory()
        
        return self._memory_instance
    
    async def _initialize_memory(self):
        """Initialize the memory backend"""
        if self.use_redis and self.redis_url:
            # Try Redis first
            try:
                self.logger.info("Attempting to initialize Redis memory...")
                redis_memory = RedisConversationMemory(
                    redis_url=self.redis_url,
                    session_ttl=self.session_ttl
                )
                
                await redis_memory.connect()
                
                if redis_memory.redis_client:
                    self.logger.info("Successfully initialized Redis memory")
                    self._memory_instance = redis_memory
                    return
                else:
                    self.logger.warning("Redis connection failed, falling back to in-memory")
                    
            except Exception as e:
                self.logger.error(f"Redis initialization failed: {e}")
                self.logger.info("Falling back to in-memory storage")
        
        # Fallback to in-memory storage
        self.logger.info("Initializing in-memory conversation storage")
        self._memory_instance = ConversationMemory()
    
    async def cleanup(self):
        """Cleanup memory resources"""
        if self._memory_instance:
            if hasattr(self._memory_instance, 'disconnect'):
                await self._memory_instance.disconnect()
            elif hasattr(self._memory_instance, 'cleanup_expired_sessions'):
                await self._memory_instance.cleanup_expired_sessions()
    
    async def get_stats(self) -> dict:
        """Get memory statistics"""
        if self._memory_instance is None:
            return {"status": "not_initialized"}
        
        if hasattr(self._memory_instance, 'get_session_stats'):
            return await self._memory_instance.get_session_stats()
        else:
            return {
                "storage_type": "basic_memory",
                "status": "initialized"
            }


# Global memory manager instance
_memory_manager = None


async def get_memory_manager(
    redis_url: Optional[str] = None,
    use_redis: bool = True,
    session_ttl: int = 3600
) -> MemoryManager:
    """Get or create the global memory manager instance"""
    global _memory_manager
    
    if _memory_manager is None:
        _memory_manager = MemoryManager(
            redis_url=redis_url,
            use_redis=use_redis, 
            session_ttl=session_ttl
        )
    
    return _memory_manager


async def get_conversation_memory() -> Union[RedisConversationMemory, ConversationMemory]:
    """Get the conversation memory instance"""
    manager = await get_memory_manager()
    return await manager.get_memory_instance()