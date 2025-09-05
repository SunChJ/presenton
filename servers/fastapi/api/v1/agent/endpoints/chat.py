from fastapi import APIRouter, HTTPException, Depends
from services.agent.core.ppt_agent import PPTAgent
from ..models import ChatRequest, ChatResponse

AGENT_CHAT_ROUTER = APIRouter(prefix="/chat", tags=["Agent Chat"])

# Global agent instance (in production, this should be managed differently)
_agent_instance = None


async def get_agent_instance() -> PPTAgent:
    """Get or create agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = PPTAgent()
        await _agent_instance.initialize()
    return _agent_instance


@AGENT_CHAT_ROUTER.post("/", response_model=ChatResponse)
async def agent_chat(
    request: ChatRequest,
    agent: PPTAgent = Depends(get_agent_instance)
):
    """Chat with PPT Agent"""
    try:
        # Process message with agent
        agent_response = await agent.process_message(
            message=request.message,
            session_id=request.session_id
        )
        
        # Convert to API response format
        return ChatResponse(
            response=agent_response.text,
            intent=agent_response.intent,
            action_required=agent_response.action_required,
            follow_up_question=agent_response.follow_up_question,
            extracted_params=agent_response.extracted_params,
            confidence=agent_response.confidence
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )