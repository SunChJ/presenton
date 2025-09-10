import aiohttp
from fastapi import HTTPException
from models.presentation_layout import PresentationLayoutModel
from typing import List

async def get_layout_by_name(layout_name: str) -> PresentationLayoutModel:
    url = f"http://localhost:3001/api/layout?group={layout_name}"
    
    try:
        print(f"Attempting to fetch layout from frontend API: {url}")
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    layout_json = await response.json()
                    print(f"Successfully fetched layout '{layout_name}' from frontend API")
                    return PresentationLayoutModel(**layout_json)
                else:
                    response_text = await response.text()
                    print(f"Frontend API failed with status {response.status}")
                    print(f"Response body: {response_text[:500]}")
                    print(f"Using enhanced fallback layout for '{layout_name}'")
    except aiohttp.ClientError as e:
        print(f"Frontend API connection error: {e}")
        print(f"This usually means Next.js server is not running on port 3001")
        print(f"Using enhanced fallback layout for '{layout_name}'")
    except Exception as e:
        print(f"Unexpected error accessing frontend API: {e}")
        print(f"Using enhanced fallback layout for '{layout_name}'")
    
    # Fallback: 使用增强的静态layout定义
    return get_fallback_layout(layout_name)


def get_fallback_layout(layout_name: str) -> PresentationLayoutModel:
    """当前端API失败时使用的fallback layout定义"""
    
    # 完整的专业slide布局定义
    comprehensive_slides = [
        {
            "id": "title",
            "name": "Title Slide",
            "description": "Main title slide with title and subtitle",
            "json_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Main presentation title"},
                    "subtitle": {"type": "string", "description": "Subtitle or tagline"},
                    "author": {"type": "string", "description": "Author or company name"}
                },
                "required": ["title"]
            }
        },
        {
            "id": "outline",
            "name": "Outline Slide",
            "description": "Presentation agenda or outline",
            "json_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Outline title"},
                    "items": {"type": "array", "items": {"type": "string"}, "description": "Outline items"}
                },
                "required": ["title", "items"]
            }
        },
        {
            "id": "content_bullets",
            "name": "Content with Bullets",
            "description": "Main content slide with bullet points",
            "json_schema": {
                "type": "object", 
                "properties": {
                    "title": {"type": "string", "description": "Slide title"},
                    "bullets": {"type": "array", "items": {"type": "string"}, "description": "Bullet point content"},
                    "subtitle": {"type": "string", "description": "Optional subtitle"}
                },
                "required": ["title", "bullets"]
            }
        },
        {
            "id": "content_text",
            "name": "Content with Text",
            "description": "Content slide with paragraph text",
            "json_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Slide title"},
                    "content": {"type": "string", "description": "Main content text"},
                    "subtitle": {"type": "string", "description": "Optional subtitle"}
                },
                "required": ["title", "content"]
            }
        },
        {
            "id": "comparison",
            "name": "Comparison Slide",
            "description": "Two-column comparison layout",
            "json_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Comparison title"},
                    "left_title": {"type": "string", "description": "Left column title"},
                    "left_content": {"type": "array", "items": {"type": "string"}, "description": "Left column points"},
                    "right_title": {"type": "string", "description": "Right column title"},
                    "right_content": {"type": "array", "items": {"type": "string"}, "description": "Right column points"}
                },
                "required": ["title", "left_title", "left_content", "right_title", "right_content"]
            }
        },
        {
            "id": "image_content",
            "name": "Image with Content",
            "description": "Slide with image and accompanying text",
            "json_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Slide title"},
                    "content": {"type": "string", "description": "Text content"},
                    "image_description": {"type": "string", "description": "Description for image generation"}
                },
                "required": ["title", "content"]
            }
        },
        {
            "id": "quote",
            "name": "Quote Slide",
            "description": "Quote or testimonial slide",
            "json_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Slide title"},
                    "quote": {"type": "string", "description": "Quote text"},
                    "author": {"type": "string", "description": "Quote author"},
                    "context": {"type": "string", "description": "Additional context"}
                },
                "required": ["title", "quote"]
            }
        },
        {
            "id": "conclusion",
            "name": "Conclusion Slide",
            "description": "Summary and conclusion slide",
            "json_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Conclusion title"},
                    "summary": {"type": "string", "description": "Key takeaways summary"},
                    "call_to_action": {"type": "string", "description": "Next steps or call to action"}
                },
                "required": ["title", "summary"]
            }
        },
        {
            "id": "thank_you",
            "name": "Thank You Slide",
            "description": "Final thank you slide with contact info",
            "json_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Thank you message"},
                    "contact_info": {"type": "string", "description": "Contact information"},
                    "additional_message": {"type": "string", "description": "Additional closing message"}
                },
                "required": ["title"]
            }
        }
    ]
    
    # 验证layout_name是否在允许的列表中
    allowed_layouts = ["general", "classic", "classic-dark", "modern", "professional"]
    if layout_name not in allowed_layouts:
        layout_name = "general"  # 默认使用general
        
    print(f"Using enhanced fallback layout for '{layout_name}' with {len(comprehensive_slides)} slide types")
    
    return PresentationLayoutModel(
        name=layout_name,
        ordered=False,
        slides=comprehensive_slides
    )
