from fastapi import APIRouter, HTTPException, Depends
from services.agent.memory.memory_manager import get_memory_manager
from services.agent.core.ppt_agent import PPTAgent
from ..endpoints.chat import get_agent_instance

AGENT_MEMORY_ROUTER = APIRouter(prefix="/memory", tags=["Agent Memory"])


@AGENT_MEMORY_ROUTER.get("/stats")
async def get_memory_stats():
    """Get memory system statistics"""
    try:
        manager = await get_memory_manager()
        stats = await manager.get_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get memory stats: {str(e)}"
        )


@AGENT_MEMORY_ROUTER.get("/sessions")
async def get_active_sessions():
    """Get list of active conversation sessions"""
    try:
        manager = await get_memory_manager()
        memory = await manager.get_memory_instance()
        
        if hasattr(memory, 'get_active_sessions'):
            sessions = await memory.get_active_sessions()
            return {
                "status": "success", 
                "active_sessions": sessions,
                "count": len(sessions)
            }
        else:
            return {
                "status": "success",
                "message": "Session listing not available for this memory backend",
                "active_sessions": [],
                "count": 0
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active sessions: {str(e)}"
        )


@AGENT_MEMORY_ROUTER.get("/sessions/{session_id}/context")
async def get_session_context(session_id: str, last_n: int = 10):
    """Get conversation context for a specific session"""
    try:
        manager = await get_memory_manager()
        memory = await manager.get_memory_instance()
        
        context = await memory.get_context(session_id, last_n=last_n)
        return {
            "status": "success",
            "session_id": session_id,
            "context": context,
            "interaction_count": len(context)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session context: {str(e)}"
        )


@AGENT_MEMORY_ROUTER.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear conversation history for a specific session"""
    try:
        manager = await get_memory_manager()
        memory = await manager.get_memory_instance()
        
        await memory.clear_session(session_id)
        return {
            "status": "success",
            "message": f"Session {session_id} cleared successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear session: {str(e)}"
        )


@AGENT_MEMORY_ROUTER.post("/cleanup")
async def cleanup_expired_sessions():
    """Manually trigger cleanup of expired sessions"""
    try:
        manager = await get_memory_manager()
        memory = await manager.get_memory_instance()
        
        if hasattr(memory, 'cleanup_expired_sessions'):
            await memory.cleanup_expired_sessions()
            return {
                "status": "success",
                "message": "Expired sessions cleanup completed"
            }
        else:
            return {
                "status": "success",
                "message": "Cleanup not needed for this memory backend"
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup sessions: {str(e)}"
        )


@AGENT_MEMORY_ROUTER.get("/health")
async def memory_health_check():
    """Check memory system health"""
    try:
        manager = await get_memory_manager()
        memory = await manager.get_memory_instance()
        
        # Test basic functionality
        test_session = "health_check_test"
        await memory.store_interaction(
            session_id=test_session,
            user_message="Health check test",
            agent_response="System is healthy"
        )
        
        context = await memory.get_context(test_session, last_n=1)
        await memory.clear_session(test_session)
        
        health_status = {
            "status": "healthy",
            "memory_type": "redis" if hasattr(memory, 'redis_client') and memory.redis_client else "in_memory",
            "can_store": len(context) > 0,
            "can_retrieve": len(context) > 0,
            "can_clear": True
        }
        
        if hasattr(memory, 'redis_client') and memory.redis_client:
            # Additional Redis-specific health checks
            try:
                await memory.redis_client.ping()
                health_status["redis_ping"] = True
            except:
                health_status["redis_ping"] = False
                health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Memory health check failed: {str(e)}"
        )