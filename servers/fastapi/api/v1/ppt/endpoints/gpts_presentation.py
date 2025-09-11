"""
GPTs专用的演示文稿生成API
独立于本地Next.js工作流程
"""

import uuid
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from pydantic import BaseModel
from typing import Optional

from services.database import get_async_session
from models.sql.presentation import PresentationModel


# GPTs专用的请求模型
class GPTsPresentationRequest(BaseModel):
    prompt: str
    n_slides: int = 8
    language: str = "Chinese"
    template: str = "classic"
    export_as: str = "pptx"
    tone: Optional[str] = None
    instructions: Optional[str] = None


# GPTs专用的响应模型
class GPTsPresentationResponse(BaseModel):
    presentation_id: str
    title: str
    outline: str
    edit_url: str
    path: str
    message: str


router = APIRouter()


@router.post("/gpts/generate", response_model=GPTsPresentationResponse)  
async def generate_presentation_for_gpts(
    request: GPTsPresentationRequest,
    sql_session: AsyncSession = Depends(get_async_session),
):
    """
    GPTs专用的演示文稿生成API - 立即返回编辑链接，后台异步生成
    """
    try:
        from models.generate_presentation_request import GeneratePresentationRequest
        from api.v1.ppt.endpoints.presentation import generate_presentation_api
        
        print(f"GPTs API: Converting GPTs request to GeneratePresentationRequest")
        print(f"Topic: {request.prompt[:100]}...")
        print(f"Settings: {request.n_slides} slides, {request.template} template, {request.language}")
        
        # 转换GPTs请求为标准的GeneratePresentationRequest
        generate_request = GeneratePresentationRequest(
            content=request.prompt,
            instructions=request.instructions,
            tone=request.tone,
            verbosity=None,
            web_search=False,
            n_slides=request.n_slides,
            language=request.language,
            template=request.template,
            files=None,
            export_as=request.export_as
        )
        
        # 直接调用生成API并异步启动后台任务
        print(f"Starting presentation generation...")
        
        # 创建一个后台任务来处理生成
        async def background_generation():
            try:
                print(f"Background generation starting...")
                result = await generate_presentation_api(generate_request, sql_session)
                print(f"Background generation completed successfully: {result.presentation_id}")
                return result
            except Exception as bg_error:
                print(f"Background generation failed: {bg_error}")
                return None
        
        # 启动后台任务（不等待完成）
        task = asyncio.create_task(background_generation())
        
        # 等待很短的时间让presentation记录被创建
        await asyncio.sleep(0.1)
        
        # 尝试获取最近创建的presentation
        recent_presentations = await sql_session.execute(
            select(PresentationModel)
            .where(PresentationModel.content == generate_request.content)
            .order_by(PresentationModel.created_at.desc())
            .limit(1)
        )
        recent_presentation = recent_presentations.scalar_one_or_none()
        
        if recent_presentation:
            presentation_id = recent_presentation.id
            print(f"Found created presentation: {presentation_id}")
        else:
            # 如果还没有创建，创建一个临时的
            presentation_id = uuid.uuid4()
            temp_presentation = PresentationModel(
                id=presentation_id,
                title=f"AI Generated: {request.prompt[:50]}...",
                content=generate_request.content,
                language=generate_request.language,
                tone=generate_request.tone,
                instructions=generate_request.instructions,
                n_slides=generate_request.n_slides,
                template=generate_request.template,
                export_as=generate_request.export_as,
            )
            sql_session.add(temp_presentation)
            await sql_session.commit()
            print(f"Created temporary presentation: {presentation_id}")
        
        # 立即返回编辑链接
        base_url = "https://ppt.samsoncj.xyz"
        edit_path = f"/presentation?id={presentation_id}&stream=true"
        full_edit_url = f"{base_url}{edit_path}"
        
        print(f"Returning immediate response for presentation {presentation_id}")
        
        return GPTsPresentationResponse(
            presentation_id=str(presentation_id),
            title=f"AI Generated: {request.prompt[:50]}...",
            outline=f"🚀 正在生成 {request.n_slides} 页演示文稿...",
            edit_url=full_edit_url,
            path=full_edit_url,
            message=f"✨ 演示文稿生成已启动！\n\n📊 页数: {request.n_slides}\n🎨 模板: {request.template}\n🌐 语言: {request.language}\n\n🔗 **实时查看生成过程**: {full_edit_url}\n\n⏳ 正在后台生成内容，您可以:\n• 📱 点击链接实时查看生成进度\n• 🖼️ 观看AI自动添加图片和内容\n• ✏️ 生成完成后直接在线编辑\n• 📥 完成后可导出为PPTX/PDF\n\n💡 通常需要2-5分钟完成，请保持链接打开！"
        )
    
    except Exception as error:
        print(f"GPTs generation failed: {error}")
        
        # 生成失败，创建基础的presentation记录供用户手动编辑
        try:
            presentation_id = uuid.uuid4()
            fallback_presentation = PresentationModel(
                id=presentation_id,
                title="AI Generated Presentation (需要手动完成)",
                content=request.prompt,
                language=request.language,
                tone=request.tone,
                instructions=request.instructions,
                n_slides=request.n_slides,
                template=request.template,
                export_as=request.export_as,
            )
            
            sql_session.add(fallback_presentation)
            await sql_session.commit()
            
            base_url = "https://ppt.samsoncj.xyz"
            edit_url = f"{base_url}/presentation?id={presentation_id}&stream=true"
            
            return GPTsPresentationResponse(
                presentation_id=str(presentation_id),
                title="AI Generated Presentation (需要手动完成)",
                outline="⚠️ 自动生成遇到问题，已创建基础框架",
                edit_url=edit_url,
                path=edit_url,
                message=f"⚠️ 自动生成过程遇到问题，但已为您创建了演示文稿框架！\n\n📊 页数: {request.n_slides}\n🎨 模板: {request.template}\n🌐 语言: {request.language}\n\n🔗 **立即编辑**: {edit_url}\n\n💡 您可以：\n• 📝 在编辑页面手动添加内容\n• 🔄 点击重新生成按钮再次尝试\n• 📱 使用在线工具完善演示文稿\n\n⚠️ 错误详情: {str(error)[:200]}..."
            )
        except Exception as save_error:
            print(f"Failed to save fallback presentation: {save_error}")
            raise HTTPException(
                status_code=500,
                detail=f"生成演示文稿失败，同时无法保存基础信息: {str(save_error)}"
            )