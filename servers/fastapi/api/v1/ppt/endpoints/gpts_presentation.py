"""
GPTs专用的演示文稿生成API
独立于本地Next.js工作流程
"""

import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel
from typing import Optional

from services.database import get_async_session
from models.sql.presentation import PresentationModel


# GPTs专用的请求模型
class GPTsPresentationRequest(BaseModel):
    prompt: str
    n_slides: int = 8
    language: str = "Chinese"
    template: str = "general"
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
    GPTs专用的演示文稿生成API - 使用原生generate API
    直接调用现有的完整生成流程，确保与原始API完全一致
    """
    try:
        from models.generate_presentation_request import GeneratePresentationRequest
        from api.v1.ppt.endpoints.presentation import generate_presentation_api
        print("Successfully imported GeneratePresentationRequest and generate_presentation_api")
    except ImportError as import_error:
        print(f"Import error: {import_error}")
        raise
    
    try:
        print(f"GPTs API: Converting GPTs request to GeneratePresentationRequest")
        print(f"Topic: {request.prompt[:100]}...")
        print(f"Settings: {request.n_slides} slides, {request.template} template, {request.language}")
        
        # 转换GPTs请求为标准的GeneratePresentationRequest
        # 注意：保留export_as但在生成流程中捕获导出错误
        generate_request = GeneratePresentationRequest(
            content=request.prompt,
            instructions=request.instructions,
            tone=request.tone,
            verbosity=None,  # GPTs不支持verbosity
            web_search=False,  # 默认关闭web搜索
            n_slides=request.n_slides,
            language=request.language,
            template=request.template,
            files=None,  # GPTs不支持文件上传
            export_as=request.export_as  # 保留原始值，在生成时处理导出错误
        )
        
        print(f"Calling original generate_presentation_api...")
        
        # 调用完整生成API，但捕获导出异常
        from api.v1.ppt.endpoints.presentation import generate_presentation_api
        
        try:
            # 调用完整生成流程
            result = await generate_presentation_api(generate_request, sql_session)
            print(f"完整生成成功！")
            
        except Exception as error:
            print(f"生成过程中出现错误: {error}")
            error_str = str(error).lower()
            
            # 检查是否是可恢复的错误类型
            recoverable_errors = [
                "export", "pptx", "temp_directory",  # 导出相关错误
                "overloaded", "quota", "rate limit", "503", "429",  # API限额错误
                "unavailable", "service unavailable"  # 服务不可用错误
            ]
            
            is_recoverable = any(keyword in error_str for keyword in recoverable_errors)
            
            if is_recoverable:
                print(f"检测到可恢复错误，尝试查找已创建的presentation...")
                
                # 查找可能已创建的presentation（即使部分失败）
                from sqlmodel import select
                recent_presentations = await sql_session.execute(
                    select(PresentationModel)
                    .where(PresentationModel.content == generate_request.content)
                    .order_by(PresentationModel.created_at.desc())
                    .limit(1)
                )
                recent_presentation = recent_presentations.scalar_one_or_none()
                
                if recent_presentation:
                    print(f"找到已生成的presentation: {recent_presentation.id}")
                    result = type('PresentationResult', (), {
                        'presentation_id': recent_presentation.id,
                        'edit_path': f"/presentation?id={recent_presentation.id}",
                        'path': f"/presentation?id={recent_presentation.id}"
                    })()
                    
                    # 返回部分成功的结果，并提示问题
                    base_url = "https://ppt.samsoncj.xyz"
                    presentation_id = str(result.presentation_id)
                    full_edit_url = f"{base_url}{result.edit_path}"
                    
                    return GPTsPresentationResponse(
                        presentation_id=presentation_id,
                        title="AI Generated Presentation (部分生成)",
                        outline="⚠️ 生成过程中遇到API限制，已保存部分内容",
                        edit_url=full_edit_url,
                        path=full_edit_url,
                        message=f"⚠️ 生成过程中遇到问题：{str(error)[:100]}...\n\n但已保存演示文稿基础信息和部分内容：\n\n📋 标题: AI Generated Presentation\n📊 幻灯片数: {request.n_slides}\n🎨 模板: {request.template}\n🌐 语言: {request.language}\n\n🔗 **查看已生成内容**: {full_edit_url}\n\n💡 您可以在编辑页面手动完善内容，或稍后重新生成。\n\n🔄 如果是API限额问题，请稍后再试。"
                    )
                else:
                    # 没有找到任何已创建的presentation，创建一个基本的
                    print("未找到已创建的presentation，创建基本记录...")
                    presentation_id = uuid.uuid4()
                    presentation = PresentationModel(
                        id=presentation_id,
                        title="AI Generated Presentation (生成失败)",
                        content=generate_request.content,
                        language=generate_request.language,
                        tone=generate_request.tone,
                        instructions=generate_request.instructions,
                        n_slides=generate_request.n_slides,
                        template=generate_request.template,
                        export_as=generate_request.export_as,
                    )
                    
                    sql_session.add(presentation)
                    await sql_session.commit()
                    
                    base_url = "https://ppt.samsoncj.xyz"
                    return GPTsPresentationResponse(
                        presentation_id=str(presentation_id),
                        title="AI Generated Presentation (生成失败)",
                        outline="❌ 生成过程失败，已保存基础信息",
                        edit_url=f"{base_url}/presentation?id={presentation_id}",
                        path=f"{base_url}/presentation?id={presentation_id}",
                        message=f"❌ 生成失败：{str(error)[:100]}...\n\n已创建空白演示文稿模板：\n📋 标题: AI Generated Presentation\n📊 幻灯片数: {request.n_slides}\n🎨 模板: {request.template}\n\n🔗 您可以在编辑页面手动创建内容\n💡 或稍后重新尝试生成"
                    )
            else:
                # 非可恢复错误，重新抛出
                print(f"不可恢复的错误，重新抛出: {error}")
                raise error
        
        print(f"Generation completed successfully")
        print(f"Result: {result}")
        
        # 转换响应格式给GPTs - result是PresentationPathAndEditPath对象
        base_url = "https://ppt.samsoncj.xyz"
        presentation_id = str(result.presentation_id)
        
        # 构造完整的URL
        full_edit_url = f"{base_url}{result.edit_path}"
        full_path_url = f"{base_url}{result.path}" if result.path != result.edit_path else full_edit_url
        
        print(f"Generated presentation URLs:")
        print(f"  Edit URL: {full_edit_url}")
        print(f"  Download Path: {full_path_url}")
        
        return GPTsPresentationResponse(
            presentation_id=presentation_id,
            title="AI Generated Presentation", 
            outline="✅ 演示文稿已完全生成",
            edit_url=full_edit_url,
            path=full_path_url,
            message=f"✅ 演示文稿已成功生成并完成！\n\n📊 幻灯片数量: {request.n_slides}\n🎨 模板风格: {request.template}\n🌐 语言: {request.language}\n\n🔗 **在线查看和编辑**: {full_edit_url}\n📥 **下载链接**: {full_path_url}\n\n🎉 您的演示文稿已完全生成，包含：\n• 📄 完整的幻灯片内容\n• 🖼️ 自动生成的图片\n• 🎨 专业的设计布局\n• ⚡ 可在线编辑和导出\n\n💡 点击链接即可查看您的演示文稿！"
        )

    except Exception as e:
        import traceback
        print(f"Error in GPTs presentation generation: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        print(f"Request data: {request}")
        print(f"Generate request data: {generate_request.model_dump() if 'generate_request' in locals() else 'Not created yet'}")
        
        # 即使生成失败，也要保存基本的演示文稿记录到数据库
        # 用户可以在前端重新生成
        try:
            presentation_id = uuid.uuid4()
            presentation_title = "AI Generated Presentation"
            
            # 创建基本的presentation记录，但不包含structure和outlines
            # 这样前端可以重新生成大纲和准备演示文稿
            presentation = PresentationModel(
                id=presentation_id,
                title=presentation_title,
                content=request.prompt,
                language=request.language,
                tone=request.tone,
                instructions=request.instructions,
                n_slides=request.n_slides,
                # 注意：不设置template, export_as，让前端处理
            )
            
            sql_session.add(presentation)
            await sql_session.commit()
            
            base_url = "https://ppt.samsoncj.xyz"
            
            return GPTsPresentationResponse(
                presentation_id=str(presentation_id),
                title=presentation_title or "AI Generated Presentation",
                outline="生成过程中遇到问题，已保存基础信息",
                edit_url=f"{base_url}/presentation?id={presentation_id}",
                path=f"{base_url}/presentation?id={presentation_id}",
                message=f"⚠️ 生成过程中遇到问题，但已保存演示文稿基础信息\n\n📋 标题: {presentation_title}\n📊 幻灯片数: {request.n_slides}\n🎨 模板: {request.template}\n🔗 请点击链接在前端重新生成"
            )
        except Exception as save_error:
            print(f"Failed to save presentation record: {str(save_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"演示文稿生成和保存都失败: {str(e)}"
            )


