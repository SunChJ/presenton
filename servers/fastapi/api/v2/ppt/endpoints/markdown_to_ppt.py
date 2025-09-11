import time
import uuid
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models.v2.markdown_ppt_request import (
    MarkdownToPPTRequest, 
    MarkdownToPPTResponse,
    ParsedMarkdownOutline,
    ParsedSlideOutline
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
        # 🚀 V2 API - UPDATED VERSION 2.0 🚀
        print("🚀 V2 API - UPDATED VERSION 2.0 - Starting markdown to PPT generation...")
        
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
        
        # 4. 使用原项目的成熟机制：布局选择 + 内容生成
        print("Step 4: Using original project mechanisms...")
        optimized_slides = await _generate_v2_using_original_pipeline(
            parsed_outline,
            request,
            layout_model
        )
        
        # 5. 使用V2专用的生成流程
        print("Step 5: Generating presentation using V2 pipeline...")
        presentation_response = await _generate_presentation_v2(
            optimized_slides,
            presentation_title,
            request,
            layout_model,
            session
        )
        print(f"📤 生成完成，准备返回响应: {presentation_response}")
        
        processing_time = time.time() - start_time
        
        return MarkdownToPPTResponse(
            success=True,
            presentation_id=presentation_response.get("presentation_id"),
            preview_url=presentation_response.get("preview_url"),
            edit_url=f"http://localhost:5001/presentation?id={presentation_response.get('presentation_id')}",
            download_url=None,  # 移除导出，后续可手动导出
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


async def _generate_v2_using_original_pipeline(
    parsed_outline: ParsedMarkdownOutline,
    request: MarkdownToPPTRequest,
    layout_model
) -> List[Dict[str, Any]]:
    """V2版本：直接使用原项目的成熟管道 - 布局选择 + 内容生成"""
    
    from models.presentation_outline_model import PresentationOutlineModel, SlideOutlineModel
    from utils.llm_calls.generate_presentation_structure import generate_presentation_structure
    
    print(f"🎯 Step 4.1: 使用原项目布局选择机制")
    
    # 1. 转换为标准PresentationOutlineModel格式
    slide_outlines = []
    for slide in parsed_outline.slides:
        slide_content = f"## {slide.title}\n{_extract_slide_body(slide)}"
        slide_outline = SlideOutlineModel(content=slide_content)
        slide_outlines.append(slide_outline)
    
    standard_outline = PresentationOutlineModel(slides=slide_outlines)
    
    # 2. 使用原项目的布局选择
    presentation_structure = await generate_presentation_structure(
        standard_outline, 
        layout_model,
        instructions=f"Language: {request.language}. Generate presentation in {request.language}."
    )
    
    selected_layouts = presentation_structure.slides
    print(f"✅ 布局选择完成：{[layout_model.slides[idx].id for idx in selected_layouts]}")
    
    print(f"🎯 Step 4.2: 批量处理所有幻灯片内容 (1次LLM调用)")
    
    # 3. 批量处理所有幻灯片内容
    optimized_slides = await _batch_process_slides_content(
        parsed_outline.slides,
        selected_layouts,
        layout_model,
        request.language
    )
    
    print(f"✅ 批量内容处理完成 - 处理了{len(optimized_slides)}张幻灯片")
    
    # 添加调试信息
    for slide in optimized_slides:
        print(f"📋 幻灯片 {slide['slide_index'] + 1}: {slide['layout_id']}")
    
    return optimized_slides


async def _batch_process_slides_content(
    parsed_slides,
    selected_layouts,
    layout_model,
    language: str
) -> List[Dict[str, Any]]:
    """批量处理所有幻灯片内容 - 1次LLM调用"""
    
    from services.llm_client import LLMClient
    from utils.llm_provider import get_model
    from models.llm_message import LLMUserMessage
    
    # 强调语言一致性的提示
    language_instruction = ""
    if language == "zh-CN" or language == "Chinese":
        language_instruction = "**重要：所有输出内容必须使用中文，包括标题、正文、描述等所有文本字段。**"
    elif language == "en" or language == "English":
        language_instruction = "**Important: All output content must be in English, including titles, body text, descriptions and all text fields.**"
    
    # 构建批量处理prompt
    batch_prompt = f"""
你是专业的PPT内容设计师。现在需要批量处理多张幻灯片，将MD内容适配到对应的布局Schema。

{language_instruction}

## 需要处理的幻灯片（共{len(parsed_slides)}张）：
"""
    
    # 为每张幻灯片准备信息
    for i, (slide, layout_idx) in enumerate(zip(parsed_slides, selected_layouts)):
        selected_layout = layout_model.slides[layout_idx]
        extracted_images = _extract_images_from_markdown(slide.raw_content)
        
        batch_prompt += f"""

### 幻灯片 {i+1}:
- 标题: {slide.title}
- 布局: {selected_layout.id} ({selected_layout.name})
- MD内容: {slide.raw_content}
- 图片: {extracted_images}
- 布局Schema: {selected_layout.json_schema}
"""
    
    batch_prompt += f"""

## 处理要求：
1. **内容保真**: 直接使用MD内容，不要重新创作
2. **严格适配**: 按照每张幻灯片的布局Schema生成内容
3. **图片暂时忽略**: 图片字段可以临时填入placeholder，后续会被MD图片覆盖
4. **字段完整**: 确保所有required字段都有合适的内容

## 输出格式：
返回JSON数组，包含{len(parsed_slides)}个幻灯片对象：
```json
[
  {{
    "slide_index": 0,
    "layout_id": "对应的layout_id",
    "content": {{ 按照对应Schema生成的完整JSON对象 }}
  }},
  ...
]
```

直接返回JSON数组：
"""
    
    try:
        client = LLMClient()
        model = get_model()
        
        # 构建数组Schema
        array_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "slide_index": {"type": "integer"},
                    "layout_id": {"type": "string"},
                    "content": {"type": "object"}
                },
                "required": ["slide_index", "layout_id", "content"]
            }
        }
        
        print("📡 批量LLM调用处理所有幻灯片内容...")
        response = await client.generate_structured(
            model=model,
            messages=[LLMUserMessage(content=batch_prompt)],
            response_format=array_schema,
            strict=True
        )
        
        # 处理响应
        if hasattr(response, 'content'):
            slides_content = response.content
        else:
            slides_content = response
            
        if isinstance(slides_content, str):
            import json
            slides_content = json.loads(slides_content)
        
        print("✅ 批量内容生成完成，开始应用MD图片...")
        
        # 为每张幻灯片应用MD中的图片
        for i, slide_data in enumerate(slides_content):
            original_slide = parsed_slides[i]
            selected_layout = layout_model.slides[selected_layouts[i]]
            extracted_images = _extract_images_from_markdown(original_slide.raw_content)
            
            # 应用MD图片
            slide_data["content"] = _override_images_with_md_content(
                slide_data["content"], 
                selected_layout, 
                extracted_images
            )
        
        return slides_content
        
    except Exception as e:
        print(f"❌ 批量内容处理失败: {e}")
        raise e


async def _build_slide_from_md_content(
    parsed_slide,
    selected_layout,
    language: str
) -> Dict[str, Any]:
    """借鉴原项目LLM处理内容，但直接使用MD中的图片"""
    
    from models.presentation_outline_model import SlideOutlineModel
    from utils.llm_calls.generate_slide_content import get_slide_content_from_type_and_outline
    
    # 1. 先提取MD中的图片
    extracted_images = _extract_images_from_markdown(parsed_slide.raw_content)
    
    # 2. 转换为标准格式供LLM处理
    slide_content_md = f"## {parsed_slide.title}\n{_extract_slide_body(parsed_slide)}"
    slide_outline = SlideOutlineModel(content=slide_content_md)
    
    # 3. 使用原项目的LLM内容处理（用于适配布局schema）
    slide_content = await get_slide_content_from_type_and_outline(
        slide_outline,
        selected_layout,
        language=language,
        instructions=f"Use the provided markdown content directly. Language: {language}. Keep content authentic to the original markdown."
    )
    
    # 4. 强制使用MD中的图片，覆盖LLM生成的图片字段
    slide_content = _override_images_with_md_content(slide_content, selected_layout, extracted_images)
    
    return slide_content


def _override_images_with_md_content(
    slide_content: Dict[str, Any], 
    selected_layout, 
    extracted_images: List[Dict[str, str]]
) -> Dict[str, Any]:
    """强制使用MD中的图片，覆盖LLM生成的图片字段"""
    
    if not extracted_images or not selected_layout.json_schema:
        return slide_content
    
    schema_props = selected_layout.json_schema.get("properties", {})
    
    # 查找所有图片字段
    image_fields = []
    for field_name, field_info in schema_props.items():
        if (field_info.get("type") == "object" and 
            isinstance(field_info.get("properties"), dict) and
            "__image_url__" in field_info.get("properties", {})):
            image_fields.append(field_name)
    
    # 强制覆盖图片字段，优先使用MD中的图片
    for i, field_name in enumerate(image_fields):
        if i < len(extracted_images):
            image_info = extracted_images[i]
            
            # 直接使用MD中的原始图片URL
            slide_content[field_name] = {
                "__image_url__": image_info["original_url"],
                "__image_prompt__": image_info["prompt"]
            }
            print(f"🖼️ 使用MD图片覆盖字段 {field_name}: {image_info['alt']}")
        else:
            # 如果MD图片不够，保持LLM生成的图片提示（但不强制覆盖）
            if field_name in slide_content and isinstance(slide_content[field_name], dict):
                print(f"📷 保持LLM生成的图片字段 {field_name}")
    
    return slide_content


async def _generate_presentation_v2(
    optimized_slides: List[Dict[str, Any]],
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
        n_slides=len(optimized_slides),
        language=request.language
    )
    
    session.add(presentation)
    await session.commit()
    
    # 2. 为每张幻灯片生成内容  
    slides_data = []
    
    # 批量创建所有幻灯片
    print(f"🚀 开始批量创建 {len(optimized_slides)} 张幻灯片...")
    
    for slide_number, slide_data in enumerate(optimized_slides, 1):
        # 获取对应的布局
        selected_layout = _get_layout_by_id(layout_model, slide_data["layout_id"])
        if not selected_layout:
            selected_layout = layout_model.slides[0]
        
        slide_content = slide_data["content"]
        
        # 创建幻灯片记录
        slide_model_data = {
            "presentation": presentation_id,
            "layout_group": request.template,
            "layout": selected_layout.id, 
            "index": slide_number - 1,
            "speaker_note": "",
            "content": slide_content
        }
        
        slide = SlideModel(**slide_model_data)
        
        # 处理图片和图标资源
        process_slide_add_placeholder_assets(slide)
        
        session.add(slide)
        slides_data.append(slide)
        
        print(f"✅ 准备幻灯片 {slide_number}: {selected_layout.id}")
    
    # 一次性批量提交所有幻灯片
    print("💾 批量保存到数据库...")
    await session.commit()
    print(f"✅ 数据库保存完成，共创建 {len(slides_data)} 张幻灯片")
    
    # 直接返回完整预览链接，不执行导出
    result = {
        "presentation_id": presentation_id,
        "preview_url": f"http://localhost:5001/presentation?id={presentation_id}",
        "slides_count": len(slides_data)
    }
    print(f"🔗 返回结果: {result}")
    return result


def _get_layout_by_id(layout_model, layout_id: str):
    """根据ID获取布局"""
    if not layout_model or not layout_model.slides:
        return None
    
    for layout in layout_model.slides:
        if layout.id == layout_id:
            return layout
    
    return None


async def _build_v2_slide_content_with_llm(
    parsed_slide: ParsedSlideOutline,
    selected_layout,
    language: str
) -> Dict[str, Any]:
    """V2专用：使用LLM优化Markdown内容并适配布局Schema"""
    
    from services.llm_client import LLMClient
    from utils.llm_provider import get_model
    from utils.schema_utils import remove_fields_from_schema
    from models.llm_message import LLMUserMessage
    
    # 提取Markdown中的图片
    extracted_images = _extract_images_from_markdown(parsed_slide.raw_content)
    
    # 获取布局的JSON Schema
    if not selected_layout or not selected_layout.json_schema:
        # 回退到简单构建
        return await _build_v2_slide_content_simple(parsed_slide, selected_layout, language)
    
    # 强调语言一致性的提示
    language_instruction = ""
    if language == "zh-CN" or language == "Chinese":
        language_instruction = "**重要：所有输出内容必须使用中文，包括标题、正文、描述等所有文本字段。**"
    elif language == "en" or language == "English":
        language_instruction = "**Important: All output content must be in English, including titles, body text, descriptions and all text fields.**"
    
    # 准备LLM提示 - 专门针对PPT页面优化和模板适配
    llm_prompt = f"""
你是一个专业的PPT内容设计师。现在需要将一页Markdown格式的PPT内容优化并适配到指定的幻灯片布局中。

{language_instruction}

## 📄 这一页PPT的原始内容：
{parsed_slide.raw_content}

## 🎯 页面标题：
{parsed_slide.title}

## 🖼️ 页面中的图片：
{extracted_images}

## 📋 目标布局Schema (必须严格匹配)：
{selected_layout.json_schema}

## 🎨 优化要求：
1. **模板适配**：严格按照布局Schema的字段要求组织内容
2. **内容提炼**：将原始内容提炼成适合PPT展示的简洁要点
3. **图片利用**：如果原内容有图片，优先使用；如果布局需要但没有图片，生成合适的图片描述
4. **字段填充**：确保Schema中的required字段都有合适的内容
5. **演讲备注**：生成这一页的演讲要点

## 💡 模板适配策略：
- 仔细分析Schema结构，识别布局类型（列表、对比、图表等）
- 根据布局类型重新组织原始内容
- 确保所有required字段都有恰当的值
- 保持内容的逻辑性和专业性

## 📝 输出格式：
严格按照上述Schema返回JSON对象，确保包含所有required字段。

---
直接返回JSON，无需解释：
"""

    try:
        # 调用LLM生成优化内容
        client = LLMClient()
        model = get_model()
        
        # 移除图片相关字段，稍后单独处理
        response_schema = remove_fields_from_schema(
            selected_layout.json_schema, 
            ["__image_url__", "__icon_url__"]
        )
        
        response = await client.generate_structured(
            model=model,
            messages=[LLMUserMessage(content=llm_prompt)],
            response_format=response_schema,
            strict=True
        )
        
        # 处理LLM响应
        if hasattr(response, 'content'):
            llm_content = response.content
        else:
            llm_content = response
            
        # 解析JSON响应
        import json
        if isinstance(llm_content, str):
            slide_content = json.loads(llm_content)
        else:
            slide_content = llm_content
            
        # 添加图片处理
        slide_content = _add_images_to_content(slide_content, selected_layout, extracted_images)
        
        # 不添加演讲者备注，MD内容即为PPT内容
        
        print(f"✅ LLM优化完成 - 生成了{len(slide_content)}个字段")
        return slide_content
        
    except Exception as e:
        print(f"⚠️ LLM优化失败，回退到简单模式: {e}")
        # 回退到简单构建
        return await _build_v2_slide_content_simple(parsed_slide, selected_layout, language)


async def _build_v2_slide_content_simple(
    parsed_slide: ParsedSlideOutline,
    selected_layout,
    language: str
) -> Dict[str, Any]:
    """简单版本的内容构建（LLM失败时的回退方案）"""
    
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
    
    # 不添加演讲者备注
    
    return slide_content


def _extract_images_from_markdown(content: str) -> List[Dict[str, str]]:
    """从Markdown内容中提取图片链接和描述"""
    import re
    
    # 匹配Markdown图片语法: ![alt](url)
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    images = []
    
    for match in re.finditer(image_pattern, content):
        alt_text = match.group(1) or "相关图片"
        image_url = match.group(2)
        
        # 生成图片描述和提示
        if alt_text and alt_text.strip():
            prompt = f"展示{alt_text}的高质量专业图片"
            description = alt_text
        else:
            # 从URL或上下文推断图片内容
            prompt = "与当前主题相关的专业配图"
            description = "主题相关图片"
        
        images.append({
            "alt": description,
            "url": image_url,
            "prompt": prompt,
            "original_url": image_url  # 保留原始URL
        })
    
    # 添加调试信息
    if images:
        print(f"🖼️ 提取到 {len(images)} 张图片:")
        for i, img in enumerate(images):
            print(f"   {i+1}. {img['alt']} - {img['url'][:80]}...")
    
    return images


def _add_images_to_content(
    slide_content: Dict[str, Any], 
    selected_layout, 
    extracted_images: List[Dict[str, str]]
) -> Dict[str, Any]:
    """将提取的图片添加到幻灯片内容中"""
    
    if not extracted_images or not selected_layout.json_schema:
        return slide_content
    
    schema_props = selected_layout.json_schema.get("properties", {})
    
    # 查找需要图片的字段
    image_fields = []
    for field_name, field_info in schema_props.items():
        if (field_info.get("type") == "object" and 
            isinstance(field_info.get("properties"), dict) and
            "__image_url__" in field_info.get("properties", {})):
            image_fields.append(field_name)
    
    # 为图片字段分配提取的图片
    for i, field_name in enumerate(image_fields):
        if i < len(extracted_images):
            image_info = extracted_images[i]
            
            # 优先使用原始图片URL
            slide_content[field_name] = {
                "__image_url__": image_info["original_url"],
                "__image_prompt__": image_info["prompt"]
            }
            print(f"✅ 为字段 {field_name} 分配图片: {image_info['alt']}")
        else:
            # 如果图片不够，生成适合的图片描述
            slide_title = slide_content.get('title', '内容')
            slide_content[field_name] = {
                "__image_url__": "/static/images/placeholder.jpg",
                "__image_prompt__": f"专业的{slide_title}相关配图，高清，商务风格"
            }
            print(f"🎨 为字段 {field_name} 生成图片描述: {slide_title}相关配图")
    
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