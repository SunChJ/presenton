import time
import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models.v2.markdown_ppt_request import (
    MarkdownToPPTRequest, 
    MarkdownToPPTResponse,
    ParsedMarkdownOutline
)
from models.presentation_outline_model import (
    PresentationOutlineModel, 
    SlideOutlineModel
)
from services.v2.markdown_parser import MarkdownOutlineParser
from services.database import get_async_session

# 导入现有的生成流程组件
from utils.llm_calls.generate_slide_content import get_slide_content_from_type_and_outline
from models.sql.presentation import PresentationModel
from models.sql.slide import SlideModel
from utils.export_utils import export_presentation
from utils.get_layout_by_name import get_layout_by_name
from utils.process_slides import process_slide_add_placeholder_assets


MARKDOWN_TO_PPT_ROUTER = APIRouter(prefix="/markdown-to-ppt", tags=["Markdown to PPT V2"])


@MARKDOWN_TO_PPT_ROUTER.post("/generate", response_model=MarkdownToPPTResponse)
async def generate_ppt_from_markdown(
    request: MarkdownToPPTRequest,
    session: AsyncSession = Depends(get_async_session)
) -> MarkdownToPPTResponse:
    """V2版本：基于Markdown大纲生成PPT
    
    主要流程：
    1. 解析Markdown大纲结构
    2. 智能匹配模板布局组件
    3. 转换为标准格式接入现有生成流程
    4. 返回生成结果和链接
    
    Args:
        request: Markdown转PPT请求
        session: 数据库会话
        
    Returns:
        MarkdownToPPTResponse: 生成结果响应
    """
    
    start_time = time.time()
    
    try:
        # 1. 获取模板布局信息（先获取，用于智能匹配）
        print("Step 1: Getting template layout...")
        layout_model = await get_layout_by_name(request.template)
        print(f"Retrieved layout '{request.template}' with {len(layout_model.slides)} available slides")
        
        # 2. 解析Markdown大纲（带布局智能匹配）
        print("Step 2: Parsing markdown outline with layout matching...")
        parser = MarkdownOutlineParser()
        parsed_outline = parser.parse_markdown_outline(
            request.markdown_content, 
            request.template,
            layout_model
        )
        
        print(f"Parsed {parsed_outline.total_slides} slides from markdown")
        
        # 3. 转换为标准的PresentationOutlineModel格式
        print("Step 3: Converting to standard outline format...")
        standard_outline = await _convert_to_standard_format(
            parsed_outline, 
            request,
            layout_model
        )
        
        # 提取title信息（从解析的markdown获取）
        presentation_title = parsed_outline.title
        
        # 4. 使用V2专用的生成流程
        print("Step 4: Generating presentation using V2 pipeline...")
        presentation_response = await _generate_presentation_v2(
            parsed_outline,
            presentation_title,
            request,
            layout_model,
            session
        )
        
        processing_time = time.time() - start_time
        
        return MarkdownToPPTResponse(
            success=True,
            presentation_id=presentation_response.get("presentation_id"),
            preview_url=f"/presentation?id={presentation_response.get('presentation_id')}",
            edit_url=f"/presentation?id={presentation_response.get('presentation_id')}",
            download_url=presentation_response.get("path"),
            slides_count=parsed_outline.total_slides,
            processing_time=processing_time,
            message=f"成功生成包含{parsed_outline.total_slides}张幻灯片的演示文稿"
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"Error generating PPT from markdown: {str(e)}")
        
        return MarkdownToPPTResponse(
            success=False,
            presentation_id=None,
            preview_url=None,
            edit_url=None,
            download_url=None,
            slides_count=None,
            processing_time=processing_time,
            message="生成PPT时发生错误",
            error_details=str(e)
        )


async def _convert_to_standard_format(
    parsed_outline: ParsedMarkdownOutline,
    request: MarkdownToPPTRequest,
    layout_model
) -> PresentationOutlineModel:
    """将V2格式转换为现有系统的标准格式"""
    
    # 创建标准的幻灯片大纲列表
    slide_outlines = []
    
    for parsed_slide in parsed_outline.slides:
        # 构建幻灯片大纲 - 现在包含layout信息
        slide_content = f"## {parsed_slide.title}\n{_extract_slide_body(parsed_slide)}"
        slide_outline = SlideOutlineModel(
            content=slide_content,
            slide_type=parsed_slide.suggested_layout  # 👈 关键：添加layout类型信息
        )
        slide_outlines.append(slide_outline)
    
    # 创建标准的演示文稿大纲
    return PresentationOutlineModel(
        slides=slide_outlines
    )


def _extract_slide_body(parsed_slide) -> str:
    """从解析的幻灯片中提取主体内容"""
    
    # 移除标题行，保留内容部分
    lines = parsed_slide.raw_content.split('\n')
    body_lines = []
    
    for line in lines:
        line = line.strip()
        
        # 跳过标题行
        if line.startswith(('## ', '### ')):
            continue
        
        if line:  # 非空行
            body_lines.append(line)
    
    return '\n'.join(body_lines) if body_lines else parsed_slide.title


async def _generate_presentation_v2(
    parsed_outline: ParsedMarkdownOutline,
    presentation_title: str,
    request: MarkdownToPPTRequest,
    layout_model,
    session: AsyncSession
) -> Dict[str, Any]:
    """V2专用的演示文稿生成流程"""
    
    # 生成演示文稿ID
    presentation_id = uuid.uuid4()
    
    # 1. 创建演示文稿记录
    presentation = PresentationModel(
        id=presentation_id,
        title=presentation_title,
        content=request.markdown_content,
        n_slides=len(parsed_outline.slides),
        language=request.language
    )
    
    session.add(presentation)
    await session.commit()
    
    # 2. 为每张幻灯片生成内容
    slides_data = []
    
    for slide_number, parsed_slide in enumerate(parsed_outline.slides, 1):
        
        # 获取智能匹配的布局
        selected_layout = _get_layout_by_id(layout_model, parsed_slide.suggested_layout)
        if not selected_layout:
            # 回退到第一个可用布局
            selected_layout = layout_model.slides[0]
        
        print(f"Creating V2 slide {slide_number} with layout: {selected_layout.id}")
        
        # V2专用：直接从Markdown内容构建幻灯片内容
        slide_content = await _build_v2_slide_content(
            parsed_slide, 
            selected_layout,
            request.language
        )
        
        # 创建幻灯片记录
        slide = SlideModel(
            presentation=presentation_id,
            layout_group=request.template,
            layout=selected_layout.id,
            index=slide_number - 1,
            speaker_note=slide_content.get("__speaker_note__", ""),
            content=slide_content
        )
        
        # 在数据库操作前检查字段
        print(f"Before database operations - slide {slide_number}:")
        print(f"  presentation: {slide.presentation} ({type(slide.presentation)})")
        print(f"  layout_group: {slide.layout_group} ({type(slide.layout_group)})")
        print(f"  layout: {slide.layout} ({type(slide.layout)})")
        print(f"  index: {slide.index} ({type(slide.index)})")
        
        # V2专用：简化的资源处理（不生成图片，使用占位符）
        process_slide_add_placeholder_assets(slide)
        
        # 在process_slide_add_placeholder_assets后再次检查
        print(f"After process_slide_add_placeholder_assets - slide {slide_number}:")
        print(f"  presentation: {slide.presentation} ({type(slide.presentation)})")
        print(f"  layout_group: {slide.layout_group} ({type(slide.layout_group)})")
        print(f"  layout: {slide.layout} ({type(slide.layout)})")
        print(f"  index: {slide.index} ({type(slide.index)})")
        
        session.add(slide)
        slides_data.append(slide)
    
    await session.commit()
    
    # 3. 导出为文件
    try:
        export_result = await export_presentation(
            presentation_id=presentation_id,
            export_format=request.export_format,
            session=session
        )
        export_path = export_result.get("path", "")
    except Exception as e:
        print(f"V2 Export failed: {e}")
        export_path = ""
    
    return {
        "presentation_id": presentation_id,
        "path": export_path,
        "slides_count": len(slides_data)
    }


def _get_layout_by_id(layout_model, layout_id: str):
    """根据ID获取布局"""
    if not layout_model or not layout_model.slides:
        return None
    
    for layout in layout_model.slides:
        if layout.id == layout_id:
            return layout
    
    return None


async def _build_v2_slide_content(
    parsed_slide: ParsedSlideOutline,
    selected_layout,
    language: str
) -> Dict[str, Any]:
    """V2专用：根据Markdown内容和布局构建幻灯片内容"""
    
    # 基础内容
    slide_content = {
        "title": parsed_slide.title,
        "content": _extract_slide_body(parsed_slide),
    }
    
    # 根据content_hints添加结构化数据
    hints = parsed_slide.content_hints or {}
    
    # 添加列表项
    if hints.get("bullet_points"):
        slide_content["bullets"] = hints["bullet_points"][:6]
    
    # 添加对比数据
    if hints.get("comparison_items"):
        slide_content.update(hints["comparison_items"])
    
    # 根据布局schema添加必需字段
    if selected_layout and selected_layout.json_schema:
        schema_props = selected_layout.json_schema.get("properties", {})
        required_fields = selected_layout.json_schema.get("required", [])
        
        # 为必需字段提供默认值
        for field in required_fields:
            if field not in slide_content:
                field_info = schema_props.get(field, {})
                slide_content[field] = _get_default_value_for_field(field, field_info)
    
    # 添加演讲者备注
    slide_content["__speaker_note__"] = f"关于{parsed_slide.title}的详细说明"
    
    return slide_content


def _get_default_value_for_field(field_name: str, field_info: Dict) -> Any:
    """为布局必需字段提供默认值"""
    
    field_type = field_info.get("type", "string")
    
    # 通用默认值映射
    common_defaults = {
        "companyName": "示例公司",
        "date": "2024年12月",
        "description": "相关描述内容",
        "contactNumber": "+86 123 4567 8900",
        "contactAddress": "北京市朝阳区示例地址",
        "contactWebsite": "https://example.com",
        "website": "https://example.com",
        "email": "contact@example.com",
        "phone": "+86 123 4567 8900",
        "address": "北京市朝阳区示例地址"
    }
    
    if field_name in common_defaults:
        return common_defaults[field_name]
    
    # 根据类型返回默认值
    if field_type == "string":
        return f"示例{field_name}"
    elif field_type == "number":
        return 0
    elif field_type == "boolean":
        return False
    elif field_type == "array":
        return []
    elif field_type == "object":
        return {}
    
    return ""