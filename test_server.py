#!/usr/bin/env python3
"""
Simplified test server for Agent verification
"""
import sys
import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn

# Add FastAPI path to sys.path
sys.path.insert(0, os.path.join(os.getcwd(), "servers", "fastapi"))

# Set required environment variables
os.environ["APP_DATA_DIRECTORY"] = "./app_data"
os.environ["TEMP_DIRECTORY"] = "./tmp/presenton"
os.environ["DATABASE_URL"] = "sqlite:///./app_data/presenton.db"

# Import our agent classes
try:
    from services.agent.core.ppt_agent import PPTAgent
    from services.agent.intent.recognizer import IntentRecognizer
    from services.agent.memory.conversation_memory import ConversationMemory
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

app = FastAPI(title="PPT Agent Test Server", version="1.0.0")

# Global agent instance
_agent_instance = None

async def get_agent_instance() -> PPTAgent:
    """Get or create agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = PPTAgent()
        await _agent_instance.initialize()
    return _agent_instance

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "PPT Agent Test Server is running"}

@app.get("/agent/test/health")
async def test_agent_health():
    """Test agent health"""
    try:
        agent = await get_agent_instance()
        return {
            "status": "healthy",
            "components": {
                "memory": "initialized" if agent.memory else "not_initialized",
                "intent_recognizer": "initialized" if agent.intent_recognizer else "not_initialized", 
                "conversation_manager": "initialized" if agent.conversation_manager else "not_initialized",
                "executor": "initialized" if hasattr(agent, 'executor') and agent.executor else "not_initialized"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent health check failed: {str(e)}")

@app.get("/agent/test/intent")
async def test_intent_recognition(message: str = "创建一个关于机器学习的10页PPT"):
    """Test intent recognition"""
    try:
        agent = await get_agent_instance()
        intent = await agent.intent_recognizer.identify(message)
        
        return {
            "message": message,
            "intent_type": intent.type.value,
            "confidence": intent.confidence,
            "parameters": intent.parameters
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent recognition failed: {str(e)}")

@app.post("/agent/chat/")
async def agent_chat(request: dict):
    """Basic chat with Agent"""
    try:
        message = request.get("message", "")
        session_id = request.get("session_id", "test-session")
        
        agent = await get_agent_instance()
        response = await agent.process_message(message, session_id)
        
        return {
            "response": response.text,
            "intent": response.intent,
            "action_required": response.action_required,
            "follow_up_question": response.follow_up_question,
            "extracted_params": response.extracted_params,
            "confidence": response.confidence
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/agent/chat/stream")
async def agent_chat_stream(request: dict):
    """Streaming chat with Agent (GPTs style)"""
    try:
        message = request.get("message", "")
        session_id = request.get("session_id", "test-session")
        
        agent = await get_agent_instance()
        
        # For testing, we'll simulate streaming without the full executor
        async def generate_stream():
            yield f"data: 🤖 收到您的消息: {message}\n\n"
            
            # Identify intent
            intent = await agent.intent_recognizer.identify(message)
            yield f"data: 🎯 识别意图: {intent.type.value}\n\n"
            yield f"data: 📊 置信度: {intent.confidence}\n\n"
            
            if intent.parameters:
                yield f"data: 🔧 提取参数: {intent.parameters}\n\n"
            
            if intent.type.value == "CREATE_PRESENTATION":
                yield f"data: ⚠️ 注意: 完整的PPT生成功能需要连接到完整的后端服务\n\n"
                yield f"data: ✅ Agent 核心功能验证成功！\n\n"
            else:
                response = await agent.process_message(message, session_id)
                yield f"data: 💬 {response.text}\n\n"
                if response.follow_up_question:
                    yield f"data: ❓ {response.follow_up_question}\n\n"
            
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming chat failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting PPT Agent Test Server...")
    print("📍 Available endpoints:")
    print("  - GET  /health")
    print("  - GET  /agent/test/health") 
    print("  - GET  /agent/test/intent")
    print("  - POST /agent/chat/")
    print("  - POST /agent/chat/stream")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )