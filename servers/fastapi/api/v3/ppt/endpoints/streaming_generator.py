"""
V3流式生成端点
提供实时流式生成和预览功能
"""

import asyncio
import time
from typing import AsyncGenerator, Dict, Any
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.v3_requests import V3StreamingRequest
from ...models.v3_responses import V3StreamingResponse
from ...services.enhanced_agent import V3EnhancedAgent
from ....services.database import get_async_session

V3_STREAMING_ROUTER = APIRouter(prefix="/streaming", tags=["V3 Streaming"])


@V3_STREAMING_ROUTER.post("/generate")
async def stream_presentation_generation(
    request: V3StreamingRequest,
    session: AsyncSession = Depends(get_async_session)
) -> StreamingResponse:
    """V3版本：流式生成演示文稿
    
    提供实时流式生成，支持SSE (Server-Sent Events)
    
    Args:
        request: 流式生成请求
        session: 数据库会话
        
    Returns:
        StreamingResponse: 流式响应
    """
    
    async def generate_stream() -> AsyncGenerator[str, None]:
        """生成流式响应"""
        
        try:
            # 初始化增强Agent
            agent = V3EnhancedAgent()
            
            # 构建V3演示文稿请求
            from ...models.v3_requests import V3PresentationRequest
            
            presentation_request = V3PresentationRequest(
                user_input=request.user_input,
                template=request.template,
                language=request.language,
                enable_search=request.enable_search,
                export_format="html"  # 流式生成默认使用HTML
            )
            
            # 流式执行生成流程
            async for step_response in agent.process_presentation_request(presentation_request):
                # 格式化SSE响应
                sse_data = {
                    "step": step_response.step,
                    "status": step_response.status,
                    "data": step_response.data,
                    "message": step_response.message,
                    "progress": step_response.progress,
                    "timestamp": step_response.timestamp.isoformat()
                }
                
                # 发送SSE事件
                yield f"data: {sse_data}\n\n"
                
                # 添加小延迟以模拟实时处理
                await asyncio.sleep(0.1)
            
            # 发送完成事件
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            # 发送错误事件
            error_data = {
                "step": "error",
                "status": "error",
                "data": None,
                "message": f"流式生成失败: {str(e)}",
                "progress": 0.0,
                "timestamp": time.time()
            }
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@V3_STREAMING_ROUTER.get("/preview/{presentation_id}")
async def stream_preview(
    presentation_id: str,
    session: AsyncSession = Depends(get_async_session)
) -> StreamingResponse:
    """流式预览演示文稿"""
    
    async def generate_preview() -> AsyncGenerator[str, None]:
        """生成预览流"""
        
        try:
            # 这里可以实现预览生成逻辑
            # 目前返回模拟数据
            
            preview_data = {
                "presentation_id": presentation_id,
                "status": "preview_ready",
                "message": "预览已就绪",
                "preview_url": f"/v3/preview/{presentation_id}",
                "timestamp": time.time()
            }
            
            yield f"data: {preview_data}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_data = {
                "presentation_id": presentation_id,
                "status": "error",
                "message": f"预览生成失败: {str(e)}",
                "timestamp": time.time()
            }
            yield f"data: {error_data}\n\n"
    
    return StreamingResponse(
        generate_preview(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@V3_STREAMING_ROUTER.get("/progress/{presentation_id}")
async def get_generation_progress(
    presentation_id: str,
    session: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """获取生成进度"""
    
    # 这里可以实现进度查询逻辑
    # 目前返回模拟进度数据
    
    return {
        "presentation_id": presentation_id,
        "current_step": "html_generation",
        "progress": 75.0,
        "status": "processing",
        "message": "正在生成HTML内容...",
        "estimated_time_remaining": 30  # 秒
    }
