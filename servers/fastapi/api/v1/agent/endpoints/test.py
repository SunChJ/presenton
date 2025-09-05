from fastapi import APIRouter, Depends
from services.agent.core.ppt_agent import PPTAgent
from ..endpoints.chat import get_agent_instance

AGENT_TEST_ROUTER = APIRouter(prefix="/test", tags=["Agent Test"])


@AGENT_TEST_ROUTER.get("/intent")
async def test_intent_recognition(
    message: str = "创建一个关于机器学习的10页PPT",
    agent: PPTAgent = Depends(get_agent_instance)
):
    """Test intent recognition"""
    intent = await agent.intent_recognizer.identify(message)
    
    return {
        "message": message,
        "intent_type": intent.type.value,
        "confidence": intent.confidence,
        "parameters": intent.parameters
    }


@AGENT_TEST_ROUTER.get("/health")
async def test_agent_health(
    agent: PPTAgent = Depends(get_agent_instance)
):
    """Test agent health"""
    return {
        "status": "healthy",
        "components": {
            "memory": "initialized" if agent.memory else "not_initialized",
            "intent_recognizer": "initialized" if agent.intent_recognizer else "not_initialized",
            "conversation_manager": "initialized" if agent.conversation_manager else "not_initialized",
            "executor": "initialized" if agent.executor else "not_initialized"
        }
    }