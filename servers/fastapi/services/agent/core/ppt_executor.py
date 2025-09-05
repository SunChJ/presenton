import uuid
from typing import Dict, Any, Optional, AsyncGenerator
from fastapi import HTTPException

from models.generate_presentation_request import GeneratePresentationRequest
from api.v1.ppt.endpoints.presentation import generate_presentation_api
from services.database import get_async_session
from ..intent.intent_types import Intent, IntentType


class PPTExecutor:
    """Execute PPT-related operations based on agent intent"""
    
    def __init__(self):
        pass
    
    async def execute_action(
        self, 
        intent: Intent, 
        message: str,
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """Execute action based on intent and yield progress updates"""
        
        if intent.type == IntentType.CREATE_PRESENTATION:
            async for update in self._create_presentation(intent, message, session_id):
                yield update
        elif intent.type == IntentType.MODIFY_SLIDE:
            async for update in self._modify_slide(intent, message, session_id):
                yield update
        elif intent.type == IntentType.EXPORT_PRESENTATION:
            async for update in self._export_presentation(intent, message, session_id):
                yield update
        else:
            yield f"抱歉，我目前还不支持 {intent.type} 操作。"
    
    async def _create_presentation(
        self, 
        intent: Intent, 
        message: str,
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """Create presentation based on intent parameters"""
        params = intent.parameters
        
        # Extract or use default parameters
        topic = params.get("topic", "")
        n_slides = params.get("n_slides", 8)
        language = "Chinese"  # Default language
        template = "general"  # Default template
        
        # If no topic specified, try to extract from the entire message
        if not topic:
            # Simple extraction - everything after common phrases
            topic = message.replace("创建", "").replace("生成", "").replace("PPT", "").replace("演示", "").strip()
            if not topic:
                yield "❌ 无法确定演示主题，请明确指定要创建的内容。"
                return
        
        yield f"🎯 开始创建关于 '{topic}' 的 {n_slides} 页演示文稿..."
        
        try:
            # Prepare request
            request = GeneratePresentationRequest(
                content=topic,
                n_slides=n_slides,
                language=language,
                template=template,
                export_as="pptx"
            )
            
            yield f"📝 正在生成演示大纲..."
            
            # Get database session
            async with get_async_session() as session:
                # Call the existing presentation generation API
                result = await generate_presentation_api(request, session)
                
                yield f"✅ 演示文稿创建成功！"
                yield f"📂 文件路径: {result.path}"
                yield f"🔗 编辑链接: {result.edit_path}"
                yield f"🎉 您可以点击编辑链接来查看和修改演示文稿。"
                
        except HTTPException as e:
            yield f"❌ 创建演示文稿时出错: {e.detail}"
        except Exception as e:
            yield f"❌ 创建演示文稿时发生未知错误: {str(e)}"
    
    async def _modify_slide(
        self, 
        intent: Intent, 
        message: str,
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """Modify slide based on intent parameters"""
        yield "🔧 修改幻灯片功能正在开发中..."
        yield "💡 提示：您可以通过编辑链接直接修改演示文稿。"
    
    async def _export_presentation(
        self, 
        intent: Intent, 
        message: str,
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """Export presentation based on intent parameters"""
        yield "📤 导出演示文稿功能正在开发中..."
        yield "💡 提示：演示文稿在创建时已自动导出为 PPTX 格式。"