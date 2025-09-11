#!/usr/bin/env python3
"""
V2 API调试脚本
逐步测试每个组件，找出500错误的具体原因
"""

import asyncio
import sys
import os

# 添加FastAPI路径
sys.path.append('/Users/samsoncj/Downloads/presenton/servers/fastapi')

from models.v2.markdown_ppt_request import MarkdownToPPTRequest
from services.v2.markdown_parser import MarkdownOutlineParser
from services.v2.template_matcher import TemplateModuleMatcher
from services.database import get_async_session
from models.presentation_outline_model import PresentationOutlineModel, SlideOutlineModel
from models.sql.presentation import PresentationModel
from models.sql.slide import SlideModel
from utils.get_layout_by_name import get_layout_by_name
import uuid

# 测试数据
test_request = {
    "markdown_content": "# 测试演示\n## 第一页\n这是测试内容\n## 第二页\n- 要点1\n- 要点2",
    "template": "modern",
    "language": "Chinese", 
    "export_format": "pptx"
}

async def test_step_by_step():
    """逐步测试V2 API的每个步骤"""
    
    print("=== V2 API 分步调试 ===")
    
    try:
        # 步骤 1: 解析请求
        print("Step 1: 解析请求...")
        request = MarkdownToPPTRequest(**test_request)
        print(f"✅ Request parsed: {request.template} template")
        
        # 步骤 2: Markdown解析
        print("Step 2: Markdown解析...")
        parser = MarkdownOutlineParser()
        parsed_outline = parser.parse_markdown_outline(
            request.markdown_content, 
            request.template
        )
        print(f"✅ Parsed {parsed_outline.total_slides} slides")
        
        # 步骤 3: 模板匹配
        print("Step 3: 模板匹配...")
        matcher = TemplateModuleMatcher()
        matching_results = await matcher.match_template_modules(
            parsed_outline.slides, 
            request.template
        )
        print(f"✅ Matched {len(matching_results)} layouts")
        
        # 步骤 4: 转换为标准格式
        print("Step 4: 转换为标准格式...")
        slide_outlines = []
        
        for i, (parsed_slide, match_result) in enumerate(zip(parsed_outline.slides, matching_results)):
            # 构建幻灯片大纲 - 使用现有系统的content格式
            slide_content = f"## {parsed_slide.title}\n{extract_slide_body(parsed_slide)}"
            slide_outline = SlideOutlineModel(
                content=slide_content
            )
            
            # 将布局信息存储在临时属性中
            slide_outline.layout_id = match_result.matched_layout_id
            slide_outlines.append(slide_outline)
        
        standard_outline = PresentationOutlineModel(
            title=parsed_outline.title,
            slides=slide_outlines,
            notes=[f"基于Markdown大纲自动生成，使用{request.template}模板"]
        )
        print(f"✅ Standard format created with {len(standard_outline.slides)} slides")
        
        # 步骤 5: 数据库操作测试
        print("Step 5: 数据库操作测试...")
        
        async for session in get_async_session():
            # 生成演示文稿ID
            presentation_id = uuid.uuid4()
            
            # 创建演示文稿记录
            presentation = PresentationModel(
                id=presentation_id,
                title=standard_outline.title,
                content=request.markdown_content,
                n_slides=len(standard_outline.slides),
                language=request.language
            )
            
            session.add(presentation)
            await session.commit()
            print(f"✅ Presentation created: {presentation_id}")
            
            # 步骤 6: 获取模板布局
            print("Step 6: 获取模板布局...")
            layout_model = await get_layout_by_name(request.template)
            print(f"✅ Layout loaded: {len(layout_model.slides)} available layouts")
            
            # 步骤 7: 创建幻灯片记录
            print("Step 7: 创建幻灯片记录...")
            slides_created = 0
            
            for slide_number, slide_outline in enumerate(standard_outline.slides, 1):
                # 从临时存储的布局ID获取布局信息
                layout_id = getattr(slide_outline, 'layout_id', 'modern-solution-slide')
                
                # 找到对应的布局定义
                slide_layout = None
                for layout in layout_model.slides:
                    if layout.id == layout_id:
                        slide_layout = layout
                        break
                
                if not slide_layout:
                    print(f"⚠️ Layout {layout_id} not found, using fallback")
                    slide_layout = layout_model.slides[0]
                
                # 从content中提取标题和内容
                content_lines = slide_outline.content.split('\n')
                title = content_lines[0].replace('## ', '') if content_lines else f"Slide {slide_number}"
                body_content = '\n'.join(content_lines[1:]).strip() if len(content_lines) > 1 else ""
                
                # 创建基本的幻灯片内容
                basic_content = {
                    "title": title,
                    "content": body_content,
                    "body": body_content
                }
                
                # 根据内容类型调整数据结构
                if "bullets" in layout_id.lower():
                    bullets = []
                    for line in body_content.split('\n'):
                        line = line.strip()
                        if line.startswith(('- ', '* ', '+ ')):
                            bullets.append(line[2:].strip())
                        elif line and not line.startswith('#'):
                            bullets.append(line)
                    
                    if bullets:
                        basic_content["bullets"] = bullets[:6]
                
                # 创建幻灯片记录
                slide = SlideModel(
                    presentation_id=presentation_id,
                    slide_number=slide_number,
                    layout_id=layout_id,
                    content=basic_content
                )
                
                session.add(slide)
                slides_created += 1
            
            await session.commit()
            print(f"✅ Created {slides_created} slide records")
            
            print(f"\n🎉 所有步骤成功完成!")
            print(f"📁 演示文稿ID: {presentation_id}")
            print(f"📊 幻灯片数量: {slides_created}")
            
            break  # 只使用第一个session
            
    except Exception as e:
        print(f"❌ 错误发生在: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

def extract_slide_body(parsed_slide) -> str:
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

if __name__ == "__main__":
    asyncio.run(test_step_by_step())