#!/usr/bin/env python3
"""
简化的V2测试 - 只测试基础组件
"""

import asyncio
import sys
import uuid
sys.path.append('/Users/samsoncj/Downloads/presenton/servers/fastapi')

from services.v2.markdown_parser import MarkdownOutlineParser
from models.presentation_outline_model import PresentationOutlineModel, SlideOutlineModel
from models.sql.presentation import PresentationModel
from models.sql.slide import SlideModel
from services.database import get_async_session
from utils.get_layout_by_name import get_layout_by_name

async def simple_test():
    """简化测试流程"""
    print("=== V2 简化测试 ===")
    
    try:
        # 1. Markdown解析
        print("Step 1: Markdown解析...")
        parser = MarkdownOutlineParser()
        parsed = parser.parse_markdown_outline(
            "# 测试演示\n## 第一页\n这是测试内容\n## 第二页\n- 要点1\n- 要点2",
            "modern"
        )
        print(f"✅ 解析成功: {parsed.total_slides} slides")
        
        # 2. 转换为标准格式
        print("Step 2: 转换标准格式...")
        slide_outlines = []
        for slide in parsed.slides:
            content = f"## {slide.title}\n{slide.raw_content}"
            outline = SlideOutlineModel(content=content)
            slide_outlines.append(outline)
        
        standard_outline = PresentationOutlineModel(
            title=parsed.title,
            slides=slide_outlines,
            notes=["V2 测试生成"]
        )
        print(f"✅ 标准格式转换成功: {len(standard_outline.slides)} slides")
        
        # 3. 数据库操作
        print("Step 3: 数据库操作...")
        async for session in get_async_session():
            # 创建演示文稿
            pres_id = uuid.uuid4()
            presentation = PresentationModel(
                id=pres_id,
                title=parsed.title,
                content="# 测试演示\n## 第一页\n这是测试内容\n## 第二页\n- 要点1\n- 要点2",
                n_slides=len(standard_outline.slides),
                language="Chinese"
            )
            
            session.add(presentation)
            await session.commit()
            print(f"✅ 演示文稿创建成功: {pres_id}")
            
            # 获取模板
            layout = await get_layout_by_name("modern")
            print(f"✅ 模板加载成功: {len(layout.slides)} layouts")
            
            # 创建幻灯片
            slides_created = 0
            for i, slide_outline in enumerate(standard_outline.slides, 1):
                # 选择布局
                layout_idx = (i - 1) % len(layout.slides)
                selected_layout = layout.slides[layout_idx]
                
                # 解析内容
                lines = slide_outline.content.split('\n')
                title = lines[0].replace('## ', '') if lines else f"Slide {i}"
                body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""
                
                content_data = {
                    "title": title,
                    "content": body,
                    "body": body
                }
                
                # 添加项目符号
                bullets = []
                for line in body.split('\n'):
                    line = line.strip()
                    if line.startswith(('- ', '* ', '+ ')):
                        bullets.append(line[2:].strip())
                
                if bullets:
                    content_data["bullets"] = bullets
                
                slide = SlideModel(
                    presentation_id=pres_id,
                    slide_number=i,
                    layout_id=selected_layout.id,
                    content=content_data
                )
                
                session.add(slide)
                slides_created += 1
            
            await session.commit()
            print(f"✅ 幻灯片创建成功: {slides_created} slides")
            
            print(f"\n🎉 测试完成!")
            print(f"演示文稿ID: {pres_id}")
            print(f"幻灯片数量: {slides_created}")
            
            break
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_test())