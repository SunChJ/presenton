"""
V3 HTML设计专家服务
专业角色扮演，负责生成高质量的HTML+Tailwind内容
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from ..models.v3_responses import V3HTMLResponse
from ..models.dsl_models import PresentationDSL, SlideDSL, ComponentModel, LayoutModel, StyleModel, TypographyModel


class HTMLDesignExpert:
    """HTML设计专家 - 专业角色扮演"""
    
    def __init__(self):
        self.expert_persona = self._create_expert_persona()
        self.layout_templates = self._load_layout_templates()
        self.style_themes = self._load_style_themes()
    
    def _create_expert_persona(self) -> str:
        """创建专家角色设定"""
        return """
        你是一位资深的HTML/CSS设计师和前端开发专家，拥有10年以上的经验。
        你专门负责将演示文稿内容转换为专业、美观、响应式的HTML+Tailwind CSS代码。
        
        你的专长包括：
        1. 现代Web设计趋势和最佳实践
        2. Tailwind CSS高级技巧和组件设计
        3. 响应式布局和移动端适配
        4. 用户体验(UX)和视觉设计
        5. 无障碍访问(Accessibility)设计
        6. 性能优化和代码质量
        
        你的设计原则：
        - 简洁明了，突出重点
        - 视觉层次清晰，易于阅读
        - 色彩搭配和谐，符合品牌调性
        - 布局合理，充分利用空间
        - 交互友好，用户体验佳
        - 代码整洁，易于维护
        """
    
    def _load_layout_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载布局模板"""
        return {
            "modern": {
                "type": "grid",
                "grid_template_columns": "repeat(12, 1fr)",
                "gap": "1.5rem",
                "padding": "2rem"
            },
            "classic": {
                "type": "flex",
                "flex_direction": "column",
                "gap": "1rem",
                "padding": "1.5rem"
            },
            "minimal": {
                "type": "grid",
                "grid_template_columns": "1fr",
                "gap": "2rem",
                "padding": "3rem"
            }
        }
    
    def _load_style_themes(self) -> Dict[str, Dict[str, Any]]:
        """加载样式主题"""
        return {
            "modern": {
                "colors": {
                    "primary": "#3B82F6",
                    "secondary": "#64748B",
                    "accent": "#F59E0B",
                    "background": "#FFFFFF",
                    "text": "#1F2937"
                },
                "typography": {
                    "font_family": "Inter, sans-serif",
                    "heading_size": "2.5rem",
                    "body_size": "1rem",
                    "line_height": "1.6"
                }
            },
            "classic": {
                "colors": {
                    "primary": "#1F2937",
                    "secondary": "#6B7280",
                    "accent": "#DC2626",
                    "background": "#F9FAFB",
                    "text": "#111827"
                },
                "typography": {
                    "font_family": "Georgia, serif",
                    "heading_size": "2.25rem",
                    "body_size": "1.125rem",
                    "line_height": "1.7"
                }
            }
        }
    
    async def generate_presentation_html(
        self, 
        content_data: Dict[str, Any], 
        template: str = "modern",
        language: str = "Chinese"
    ) -> Dict[str, Any]:
        """生成演示文稿HTML"""
        
        start_time = time.time()
        
        try:
            # 1. 分析内容结构
            content_analysis = await self._analyze_content_structure(content_data)
            
            # 2. 生成DSL结构
            dsl = await self._generate_presentation_dsl(content_analysis, template)
            
            # 3. 编译为HTML+CSS
            html_result = await self._compile_dsl_to_html(dsl, template)
            
            processing_time = time.time() - start_time
            
            return {
                "html_content": html_result["html"],
                "css_styles": html_result["css"],
                "layout_type": template,
                "components": html_result["components"],
                "processing_time": processing_time,
                "dsl": dsl
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            raise Exception(f"HTML生成失败: {str(e)}")
    
    async def _analyze_content_structure(
        self, 
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析内容结构"""
        
        slides = content_data.get("slides", [])
        analysis = {
            "total_slides": len(slides),
            "slide_types": [],
            "content_complexity": "medium",
            "has_images": False,
            "has_lists": False,
            "has_charts": False
        }
        
        for slide in slides:
            slide_type = self._classify_slide_type(slide)
            analysis["slide_types"].append(slide_type)
            
            # 检查内容特征
            if slide.get("images") or slide.get("enhanced_content", {}).get("images"):
                analysis["has_images"] = True
            
            if "bullets" in slide.get("content", "").lower() or "列表" in slide.get("content", ""):
                analysis["has_lists"] = True
            
            if "chart" in slide.get("content", "").lower() or "图表" in slide.get("content", ""):
                analysis["has_charts"] = True
        
        return analysis
    
    def _classify_slide_type(self, slide: Dict[str, Any]) -> str:
        """分类幻灯片类型"""
        
        title = slide.get("title", "").lower()
        content = slide.get("content", "").lower()
        
        # 基于标题和内容进行分类
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
    
    async def _generate_presentation_dsl(
        self, 
        content_analysis: Dict[str, Any], 
        template: str
    ) -> PresentationDSL:
        """生成演示文稿DSL"""
        
        # 这里可以集成LLM来生成更智能的DSL
        # 目前使用规则基础的方法
        
        slides = []
        for i, slide_type in enumerate(content_analysis["slide_types"]):
            slide_dsl = await self._generate_slide_dsl(slide_type, i, template)
            slides.append(slide_dsl)
        
        # 生成全局样式
        global_style = self._generate_global_style(template)
        
        return PresentationDSL(
            id=f"presentation_{int(time.time())}",
            title="Generated Presentation",
            slides=slides,
            global_style=global_style
        )
    
    async def _generate_slide_dsl(
        self, 
        slide_type: str, 
        index: int, 
        template: str
    ) -> SlideDSL:
        """生成单个幻灯片DSL"""
        
        # 根据幻灯片类型生成不同的布局和组件
        if slide_type == "intro":
            layout = self._create_intro_layout()
            components = self._create_intro_components()
        elif slide_type == "list":
            layout = self._create_list_layout()
            components = self._create_list_components()
        elif slide_type == "comparison":
            layout = self._create_comparison_layout()
            components = self._create_comparison_components()
        else:
            layout = self._create_default_layout()
            components = self._create_default_components()
        
        # 生成样式
        style = self._generate_slide_style(template)
        
        return SlideDSL(
            id=f"slide_{index}",
            title=f"Slide {index + 1}",
            layout=layout,
            components=components,
            style=style
        )
    
    def _create_intro_layout(self) -> LayoutModel:
        """创建介绍页布局"""
        return LayoutModel(
            type="grid",
            structure={
                "grid_template_areas": '"title" "content" "image"',
                "grid_template_rows": "auto 1fr auto",
                "gap": "2rem"
            }
        )
    
    def _create_list_layout(self) -> LayoutModel:
        """创建列表页布局"""
        return LayoutModel(
            type="grid",
            structure={
                "grid_template_areas": '"title" "list"',
                "grid_template_rows": "auto 1fr",
                "gap": "1.5rem"
            }
        )
    
    def _create_comparison_layout(self) -> LayoutModel:
        """创建对比页布局"""
        return LayoutModel(
            type="grid",
            structure={
                "grid_template_areas": '"title" "left" "right"',
                "grid_template_columns": "1fr 1fr",
                "grid_template_rows": "auto 1fr",
                "gap": "1.5rem"
            }
        )
    
    def _create_default_layout(self) -> LayoutModel:
        """创建默认布局"""
        return LayoutModel(
            type="flex",
            structure={
                "flex_direction": "column",
                "gap": "1rem"
            }
        )
    
    def _create_intro_components(self) -> List[ComponentModel]:
        """创建介绍页组件"""
        return [
            ComponentModel(
                id="title",
                type="text",
                content={"text": "演示文稿标题", "level": "h1"},
                position={"x": 0, "y": 0, "width": 100, "height": 20},
                style={"font_size": "2.5rem", "font_weight": "bold"}
            ),
            ComponentModel(
                id="content",
                type="text",
                content={"text": "演示文稿内容描述", "level": "p"},
                position={"x": 0, "y": 25, "width": 100, "height": 50},
                style={"font_size": "1.2rem", "line_height": "1.6"}
            )
        ]
    
    def _create_list_components(self) -> List[ComponentModel]:
        """创建列表页组件"""
        return [
            ComponentModel(
                id="title",
                type="text",
                content={"text": "要点列表", "level": "h2"},
                position={"x": 0, "y": 0, "width": 100, "height": 15},
                style={"font_size": "2rem", "font_weight": "bold"}
            ),
            ComponentModel(
                id="list",
                type="list",
                content={"items": ["要点1", "要点2", "要点3"]},
                position={"x": 0, "y": 20, "width": 100, "height": 60},
                style={"font_size": "1.1rem"}
            )
        ]
    
    def _create_comparison_components(self) -> List[ComponentModel]:
        """创建对比页组件"""
        return [
            ComponentModel(
                id="title",
                type="text",
                content={"text": "对比分析", "level": "h2"},
                position={"x": 0, "y": 0, "width": 100, "height": 15},
                style={"font_size": "2rem", "font_weight": "bold"}
            ),
            ComponentModel(
                id="left",
                type="card",
                content={"title": "选项A", "content": "描述内容A"},
                position={"x": 0, "y": 20, "width": 48, "height": 60},
                style={"background": "#F3F4F6", "padding": "1rem"}
            ),
            ComponentModel(
                id="right",
                type="card",
                content={"title": "选项B", "content": "描述内容B"},
                position={"x": 52, "y": 20, "width": 48, "height": 60},
                style={"background": "#F3F4F6", "padding": "1rem"}
            )
        ]
    
    def _create_default_components(self) -> List[ComponentModel]:
        """创建默认组件"""
        return [
            ComponentModel(
                id="content",
                type="text",
                content={"text": "默认内容", "level": "p"},
                position={"x": 0, "y": 0, "width": 100, "height": 100},
                style={"font_size": "1.2rem"}
            )
        ]
    
    def _generate_slide_style(self, template: str) -> StyleModel:
        """生成幻灯片样式"""
        theme = self.style_themes.get(template, self.style_themes["modern"])
        
        return StyleModel(
            theme=template,
            colors=theme["colors"],
            typography=TypographyModel(
                font_family=theme["typography"]["font_family"],
                font_size=16.0,
                font_weight="normal",
                line_height=theme["typography"]["line_height"],
                letter_spacing=0.0
            ),
            spacing={"small": 8.0, "medium": 16.0, "large": 32.0},
            borders={"radius": 8.0, "width": 1.0},
            shadows={"small": "0 1px 3px rgba(0,0,0,0.1)"}
        )
    
    def _generate_global_style(self, template: str) -> StyleModel:
        """生成全局样式"""
        return self._generate_slide_style(template)
    
    async def _compile_dsl_to_html(
        self, 
        dsl: PresentationDSL, 
        template: str
    ) -> Dict[str, Any]:
        """将DSL编译为HTML+CSS"""
        
        html_parts = []
        css_parts = []
        components = []
        
        # 生成每个幻灯片的HTML
        for slide in dsl.slides:
            slide_html, slide_css, slide_components = await self._compile_slide_to_html(slide)
            html_parts.append(slide_html)
            css_parts.append(slide_css)
            components.extend(slide_components)
        
        # 合并HTML
        full_html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{dsl.title}</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                {''.join(css_parts)}
            </style>
        </head>
        <body class="bg-gray-50">
            <div class="presentation-container">
                {''.join(html_parts)}
            </div>
        </body>
        </html>
        """
        
        return {
            "html": full_html,
            "css": ''.join(css_parts),
            "components": components
        }
    
    async def _compile_slide_to_html(
        self, 
        slide: SlideDSL
    ) -> tuple[str, str, List[Dict[str, Any]]]:
        """将单个幻灯片编译为HTML"""
        
        # 这里实现具体的DSL到HTML的编译逻辑
        # 目前返回简化的HTML结构
        
        html = f"""
        <div class="slide" id="{slide.id}">
            <h2 class="slide-title">{slide.title}</h2>
            <div class="slide-content">
                <!-- 组件内容将在这里渲染 -->
            </div>
        </div>
        """
        
        css = f"""
        .slide {{
            padding: 2rem;
            margin-bottom: 2rem;
            background: white;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .slide-title {{
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #1F2937;
        }}
        """
        
        components = [
            {
                "id": slide.id,
                "type": "slide",
                "html": html,
                "css": css
            }
        ]
        
        return html, css, components
