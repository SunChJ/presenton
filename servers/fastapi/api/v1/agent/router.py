from fastapi import APIRouter
from .endpoints.chat import AGENT_CHAT_ROUTER
from .endpoints.test import AGENT_TEST_ROUTER

AGENT_ROUTER = APIRouter(prefix="/agent", tags=["Agent"])

# Include all agent endpoints
AGENT_ROUTER.include_router(AGENT_CHAT_ROUTER)
AGENT_ROUTER.include_router(AGENT_TEST_ROUTER)