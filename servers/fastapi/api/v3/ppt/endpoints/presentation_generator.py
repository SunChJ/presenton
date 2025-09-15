"""
V3演示文稿生成端点
提供增强的演示文稿生成API
"""

import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.v3_requests import V3PresentationRequest, V3StepRequest
from ...models.v3_responses import V3PresentationResponse, V3StepResponse
from ...services.enhanced_agent import V3EnhancedAgent
from services.database import get_async_session

V3_PRESENTATION_ROUTER = APIRouter(prefix="/presentation", tags=["V3 Presentation"])


@V3_PRESENTATION_ROUTER.post("/generate", response_model=V3PresentationResponse)
async def generate_presentation(
    request: V3PresentationRequest,
    session: AsyncSession = Depends(get_async_session)
) -> V3PresentationResponse:
    """V3版本：生成演示文稿
    
    主要流程：
    1. 生成大纲 (基于用户输入)
    2. 搜索内容和图片 (可选)
    3. 生成PPT内容
    4. 专业HTML生成
    5. 流式预览
    6. 导出功能
    
    Args:
        request: V3演示文稿生成请求
        session: 数据库会话
        
    Returns:
        V3PresentationResponse: 生成结果响应
    """
    
    start_time = time.time()
    
    try:
        # 初始化增强Agent
        agent = V3EnhancedAgent()
        
        # 执行完整的演示文稿生成流程
        steps_completed = []
        final_result = None
        
        async for step_response in agent.process_presentation_request(request):
            steps_completed.append(step_response.step)
            
            # 保存最终结果
            if step_response.status == "completed":
                final_result = step_response.data
        
        processing_time = time.time() - start_time
        
        # 构建响应
        if final_result:
            return V3PresentationResponse(
                success=True,
                presentation_id=final_result.get("presentation_id"),
                title=final_result.get("title", "Generated Presentation"),
                slides_count=final_result.get("slides_count"),
                preview_url=final_result.get("preview_url"),
                edit_url=final_result.get("edit_url"),
                download_url=final_result.get("download_url"),
                processing_time=processing_time,
                message=f"成功生成包含{final_result.get('slides_count', 0)}张幻灯片的演示文稿",
                steps_completed=steps_completed
            )
        else:
            return V3PresentationResponse(
                success=False,
                processing_time=processing_time,
                message="演示文稿生成失败",
                steps_completed=steps_completed
            )
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        return V3PresentationResponse(
            success=False,
            processing_time=processing_time,
            message="生成演示文稿时发生错误",
            error_details=str(e)
        )


@V3_PRESENTATION_ROUTER.post("/step", response_model=V3StepResponse)
async def execute_single_step(
    request: V3StepRequest,
    session: AsyncSession = Depends(get_async_session)
) -> V3StepResponse:
    """V3版本：执行单个步骤
    
    支持的步骤：
    - outline: 生成大纲
    - search: 搜索内容
    - content: 生成PPT内容
    - html: 生成HTML
    - preview: 生成预览
    - export: 导出演示文稿
    
    Args:
        request: 单步执行请求
        session: 数据库会话
        
    Returns:
        V3StepResponse: 步骤执行结果
    """
    
    try:
        # 初始化增强Agent
        agent = V3EnhancedAgent()
        
        # 执行指定步骤
        result = await agent.execute_single_step(
            step=request.step,
            presentation_id=request.presentation_id,
            step_data=request.step_data
        )
        
        return result
        
    except Exception as e:
        return V3StepResponse(
            step=request.step,
            success=False,
            data=None,
            message=f"步骤执行失败: {str(e)}",
            processing_time=0.0
        )


@V3_PRESENTATION_ROUTER.get("/status/{presentation_id}")
async def get_presentation_status(
    presentation_id: str,
    session: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """获取演示文稿状态"""
    
    # 这里可以实现演示文稿状态查询逻辑
    # 目前返回基本状态信息
    
    return {
        "presentation_id": presentation_id,
        "status": "completed",
        "message": "演示文稿状态查询功能待实现"
    }


@V3_PRESENTATION_ROUTER.delete("/{presentation_id}")
async def delete_presentation(
    presentation_id: str,
    session: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """删除演示文稿"""
    
    # 这里可以实现演示文稿删除逻辑
    # 目前返回基本删除信息
    
    return {
        "presentation_id": presentation_id,
        "status": "deleted",
        "message": "演示文稿删除功能待实现"
    }
