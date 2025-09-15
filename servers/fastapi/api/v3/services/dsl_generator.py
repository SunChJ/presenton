"""
V3 DSL生成器服务
负责生成和解析演示文稿DSL
"""

import time
from typing import Dict, Any, Optional, List
from ..models.dsl_models import (
    PresentationDSL, SlideDSL, ComponentModel, LayoutModel, StyleModel,
    DSLGenerationRequest, DSLGenerationResponse
)


class DSLGenerator:
    """DSL生成器"""
    
    def __init__(self):
        self.layout_generators = {
            "modern": self._generate_modern_layout,
            "classic": self._generate_classic_layout,
            "minimal": self._generate_minimal_layout
        }
        self.component_generators = {
            "text": self._generate_text_component,
            "image": self._generate_image_component,
            "list": self._generate_list_component,
            "chart": self._generate_chart_component,
            "card": self._generate_card_component
        }
    
    async def generate_presentation_dsl(
        self, 
        request: DSLGenerationRequest
    ) -> DSLGenerationResponse:
        """生成演示文稿DSL"""
        
        start_time = time.time()
        
        try:
            # 分析内容结构
            content_analysis = self._analyze_content(request.content)
            
            # 生成幻灯片DSL
            slides = []
            for i, slide_content in enumerate(content_analysis.get("slides", [])):
                slide_dsl = await self._generate_slide_dsl(
                    slide_content, i, request.template
                )
                slides.append(slide_dsl)
            
            # 生成全局样式
            global_style = self._generate_global_style(request.template)
            
            # 创建演示文稿DSL
            presentation_dsl = PresentationDSL(
                id=f"presentation_{int(time.time())}",
                title=content_analysis.get("title", "Generated Presentation"),
                description=content_analysis.get("description"),
                slides=slides,
                global_style=global_style,
                metadata={
                    "template": request.template,
                    "language": request.language,
                    "generated_at": time.time()
                }
            )
            
            processing_time = time.time() - start_time
            
            return DSLGenerationResponse(
                success=True,
                dsl=presentation_dsl,
                processing_time=processing_time,
                message="DSL生成成功"
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            return DSLGenerationResponse(
                success=False,
                dsl=None,
                processing_time=processing_time,
                message="DSL生成失败",
                error_details=str(e)
            )
    
    def _analyze_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """分析内容结构"""
        
        # 提取基本信息
        title = content.get("title", "Untitled Presentation")
        description = content.get("description", "")
        
        # 分析幻灯片
        slides = content.get("slides", [])
        slide_analysis = []
        
        for slide in slides:
            slide_info = {
                "title": slide.get("title", ""),
                "content": slide.get("content", ""),
                "type": self._classify_slide_type(slide),
                "components": self._extract_components(slide)
            }
            slide_analysis.append(slide_info)
        
        return {
            "title": title,
            "description": description,
            "slides": slide_analysis,
            "total_slides": len(slides)
        }
    
    def _classify_slide_type(self, slide: Dict[str, Any]) -> str:
        """分类幻灯片类型"""
        
        title = slide.get("title", "").lower()
        content = slide.get("content", "").lower()
        
        # 基于关键词分类
        if any(keyword in title for keyword in ["介绍", "概述", "introduction", "overview"]):
            return "intro"
        elif any(keyword in content for keyword in ["列表", "要点", "bullets", "points"]):
            return "list"
        elif any(keyword in content for keyword in ["对比", "比较", "comparison", "vs"]):
            return "comparison"
        elif any(keyword in content for keyword in ["图表", "数据", "chart", "data"]):
            return "chart"
        elif any(keyword in content for keyword in ["引用", "quote", "testimonial"]):
            return "quote"
        else:
            return "content"
    
    def _extract_components(self, slide: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取幻灯片组件"""
        
        components = []
        
        # 提取文本组件
        if slide.get("title"):
            components.append({
                "type": "text",
                "content": slide["title"],
                "level": "h2"
            })
        
        if slide.get("content"):
            components.append({
                "type": "text",
                "content": slide["content"],
                "level": "p"
            })
        
        # 提取列表组件
        if "bullets" in slide:
            components.append({
                "type": "list",
                "content": slide["bullets"]
            })
        
        # 提取图片组件
        if "images" in slide:
            for image in slide["images"]:
                components.append({
                    "type": "image",
                    "content": image
                })
        
        return components
    
    async def _generate_slide_dsl(
        self, 
        slide_content: Dict[str, Any], 
        index: int, 
        template: str
    ) -> SlideDSL:
        """生成单个幻灯片DSL"""
        
        # 生成布局
        layout = self._generate_layout(slide_content["type"], template)
        
        # 生成组件
        components = []
        for comp_data in slide_content["components"]:
            component = await self._generate_component(comp_data, index)
            components.append(component)
        
        # 生成样式
        style = self._generate_slide_style(template)
        
        return SlideDSL(
            id=f"slide_{index}",
            title=slide_content["title"],
            layout=layout,
            components=components,
            style=style
        )
    
    def _generate_layout(self, slide_type: str, template: str) -> LayoutModel:
        """生成布局"""
        
        generator = self.layout_generators.get(template, self._generate_modern_layout)
        return generator(slide_type)
    
    def _generate_modern_layout(self, slide_type: str) -> LayoutModel:
        """生成现代风格布局"""
        
        if slide_type == "intro":
            return LayoutModel(
                type="grid",
                structure={
                    "grid_template_areas": '"title" "content" "image"',
                    "grid_template_rows": "auto 1fr auto",
                    "gap": "2rem"
                }
            )
        elif slide_type == "list":
            return LayoutModel(
                type="grid",
                structure={
                    "grid_template_areas": '"title" "list"',
                    "grid_template_rows": "auto 1fr",
                    "gap": "1.5rem"
                }
            )
        else:
            return LayoutModel(
                type="flex",
                structure={
                    "flex_direction": "column",
                    "gap": "1rem"
                }
            )
    
    def _generate_classic_layout(self, slide_type: str) -> LayoutModel:
        """生成经典风格布局"""
        
        return LayoutModel(
            type="flex",
            structure={
                "flex_direction": "column",
                "gap": "1.5rem",
                "padding": "2rem"
            }
        )
    
    def _generate_minimal_layout(self, slide_type: str) -> LayoutModel:
        """生成极简风格布局"""
        
        return LayoutModel(
            type="grid",
            structure={
                "grid_template_areas": '"content"',
                "grid_template_rows": "1fr",
                "gap": "2rem",
                "padding": "3rem"
            }
        )
    
    async def _generate_component(
        self, 
        comp_data: Dict[str, Any], 
        slide_index: int
    ) -> ComponentModel:
        """生成组件"""
        
        comp_type = comp_data["type"]
        generator = self.component_generators.get(comp_type, self._generate_text_component)
        
        return generator(comp_data, slide_index)
    
    def _generate_text_component(
        self, 
        comp_data: Dict[str, Any], 
        slide_index: int
    ) -> ComponentModel:
        """生成文本组件"""
        
        return ComponentModel(
            id=f"text_{slide_index}_{int(time.time())}",
            type="text",
            content={
                "text": comp_data["content"],
                "level": comp_data.get("level", "p")
            },
            position={
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 20
            },
            style={
                "font_size": "1.2rem" if comp_data.get("level") == "p" else "2rem",
                "font_weight": "bold" if comp_data.get("level") == "h2" else "normal"
            }
        )
    
    def _generate_image_component(
        self, 
        comp_data: Dict[str, Any], 
        slide_index: int
    ) -> ComponentModel:
        """生成图片组件"""
        
        return ComponentModel(
            id=f"image_{slide_index}_{int(time.time())}",
            type="image",
            content={
                "src": comp_data["content"].get("url", ""),
                "alt": comp_data["content"].get("alt", "")
            },
            position={
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 40
            },
            style={
                "object_fit": "cover",
                "border_radius": "0.5rem"
            }
        )
    
    def _generate_list_component(
        self, 
        comp_data: Dict[str, Any], 
        slide_index: int
    ) -> ComponentModel:
        """生成列表组件"""
        
        return ComponentModel(
            id=f"list_{slide_index}_{int(time.time())}",
            type="list",
            content={
                "items": comp_data["content"]
            },
            position={
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 60
            },
            style={
                "list_style": "disc",
                "padding_left": "1.5rem"
            }
        )
    
    def _generate_chart_component(
        self, 
        comp_data: Dict[str, Any], 
        slide_index: int
    ) -> ComponentModel:
        """生成图表组件"""
        
        return ComponentModel(
            id=f"chart_{slide_index}_{int(time.time())}",
            type="chart",
            content={
                "data": comp_data["content"],
                "type": "bar"
            },
            position={
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 50
            },
            style={
                "background": "#f8f9fa",
                "border": "1px solid #dee2e6"
            }
        )
    
    def _generate_card_component(
        self, 
        comp_data: Dict[str, Any], 
        slide_index: int
    ) -> ComponentModel:
        """生成卡片组件"""
        
        return ComponentModel(
            id=f"card_{slide_index}_{int(time.time())}",
            type="card",
            content={
                "title": comp_data["content"].get("title", ""),
                "description": comp_data["content"].get("description", "")
            },
            position={
                "x": 0,
                "y": 0,
                "width": 100,
                "height": 30
            },
            style={
                "background": "#ffffff",
                "border": "1px solid #e5e7eb",
                "border_radius": "0.5rem",
                "padding": "1rem",
                "box_shadow": "0 1px 3px rgba(0, 0, 0, 0.1)"
            }
        )
    
    def _generate_slide_style(self, template: str) -> StyleModel:
        """生成幻灯片样式"""
        
        # 根据模板生成样式
        if template == "modern":
            return StyleModel(
                theme="modern",
                colors={
                    "primary": "#3B82F6",
                    "secondary": "#64748B",
                    "accent": "#F59E0B",
                    "background": "#FFFFFF",
                    "text": "#1F2937"
                },
                typography={
                    "font_family": "Inter, sans-serif",
                    "font_size": 16,
                    "font_weight": "normal",
                    "line_height": 1.6,
                    "letter_spacing": 0
                },
                spacing={
                    "small": 8,
                    "medium": 16,
                    "large": 32
                },
                borders={
                    "radius": 8,
                    "width": 1
                },
                shadows={
                    "small": "0 1px 3px rgba(0,0,0,0.1)"
                }
            )
        else:
            # 默认样式
            return StyleModel(
                theme="default",
                colors={
                    "primary": "#000000",
                    "secondary": "#666666",
                    "accent": "#007bff",
                    "background": "#FFFFFF",
                    "text": "#000000"
                },
                typography={
                    "font_family": "Arial, sans-serif",
                    "font_size": 14,
                    "font_weight": "normal",
                    "line_height": 1.5,
                    "letter_spacing": 0
                },
                spacing={
                    "small": 4,
                    "medium": 8,
                    "large": 16
                },
                borders={
                    "radius": 4,
                    "width": 1
                },
                shadows={
                    "small": "none"
                }
            )
    
    def _generate_global_style(self, template: str) -> StyleModel:
        """生成全局样式"""
        return self._generate_slide_style(template)
