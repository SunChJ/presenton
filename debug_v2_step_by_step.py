#!/usr/bin/env python3
"""
逐步调试V2 API的每个步骤
"""

import asyncio
import sys
import uuid
sys.path.append('/Users/samsoncj/Downloads/presenton/servers/fastapi')

async def debug_v2_api():
    try:
        from models.v2.markdown_ppt_request import MarkdownToPPTRequest
        from services.v2.markdown_parser import MarkdownOutlineParser
        from models.presentation_outline_model import PresentationOutlineModel, SlideOutlineModel
        from models.sql.presentation import PresentationModel
        from models.sql.slide import SlideModel
        from services.database import get_async_session
        from utils.get_layout_by_name import get_layout_by_name
        
        print("=== V2 API 逐步调试 ===")
        
        # 步骤1: 创建请求
        request = MarkdownToPPTRequest(
            markdown_content="# iPhone测试\n## 第一页\n内容测试\n## 第二页\n- 要点1\n- 要点2",
            template="modern",
            language="Chinese",
            export_format="pptx"
        )
        print("✅ 步骤1: 请求创建成功")
        
        # 步骤2: 解析Markdown
        parser = MarkdownOutlineParser()
        parsed_outline = parser.parse_markdown_outline(request.markdown_content, request.template)
        print(f"✅ 步骤2: Markdown解析成功, 标题: {parsed_outline.title}")
        
        # 步骤3: 转换为标准格式
        slide_outlines = []
        for parsed_slide in parsed_outline.slides:
            slide_content = f"## {parsed_slide.title}\n{parsed_slide.raw_content}"
            slide_outline = SlideOutlineModel(content=slide_content)
            slide_outlines.append(slide_outline)
        
        standard_outline = PresentationOutlineModel(slides=slide_outlines)
        presentation_title = parsed_outline.title
        print("✅ 步骤3: 标准格式转换成功")
        
        # 步骤4: 数据库操作
        async for session in get_async_session():
            presentation_id = uuid.uuid4()
            
            presentation = PresentationModel(
                id=presentation_id,
                title=presentation_title,
                content=request.markdown_content,
                n_slides=len(standard_outline.slides),
                language=request.language
            )
            
            session.add(presentation)
            await session.commit()
            print("✅ 步骤4: 演示文稿记录创建成功")
            
            # 步骤5: 获取模板
            layout_model = await get_layout_by_name(request.template)
            print("✅ 步骤5: 模板加载成功")
            
            # 步骤6: 创建幻灯片
            for slide_number, slide_outline in enumerate(standard_outline.slides, 1):
                # 选择布局
                layout_index = (slide_number - 1) % len(layout_model.slides)
                selected_layout = layout_model.slides[layout_index]
                
                # 解析内容
                content_lines = slide_outline.content.split('\n')
                title = content_lines[0].replace('## ', '') if content_lines else f"Slide {slide_number}"
                body_content = '\n'.join(content_lines[1:]).strip() if len(content_lines) > 1 else ""
                
                basic_content = {
                    "title": title,
                    "content": body_content,
                    "body": body_content
                }
                
                # 添加bullets
                bullets = []
                for line in body_content.split('\n'):
                    line = line.strip()
                    if line.startswith(('- ', '* ', '+ ')):
                        bullets.append(line[2:].strip())
                
                if bullets:
                    basic_content["bullets"] = bullets
                
                slide = SlideModel(
                    presentation_id=presentation_id,
                    slide_number=slide_number,
                    layout_id=selected_layout.id,
                    content=basic_content
                )
                
                session.add(slide)
            
            await session.commit()
            print("✅ 步骤6: 幻灯片创建成功")
            print(f"🎉 全部成功! 演示文稿ID: {presentation_id}")
            
            break
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_v2_api())