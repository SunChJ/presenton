"""
V3增强Agent服务
基于V2版本改进的步骤化执行器
"""

import asyncio
import time
from typing import AsyncGenerator, Dict, Any, Optional
from uuid import UUID, uuid4

from ..models.v3_requests import V3PresentationRequest, V3StreamingRequest
from ..models.v3_responses import V3StepResponse, V3StreamingResponse
from ..models.dsl_models import PresentationDSL
from .content_search import ContentSearchService
from .html_design_expert import HTMLDesignExpert
from .dsl_generator import DSLGenerator


class V3EnhancedAgent:
    """V3增强Agent - 步骤化执行器"""
    
    def __init__(self):
        self.content_search_service = ContentSearchService()
        self.html_design_expert = HTMLDesignExpert()
        self.dsl_generator = DSLGenerator()
        self.step_handlers = {
            "outline": self._step1_generate_outline,
            "search": self._step2_search_content,
            "content": self._step3_generate_content,
            "html": self._step4_generate_html,
            "preview": self._step5_stream_preview,
            "export": self._step6_export_presentation
        }
    
    async def process_presentation_request(
        self, 
        request: V3PresentationRequest
    ) -> AsyncGenerator[V3StreamingResponse, None]:
        """处理演示文稿生成请求 - 流式执行"""
        
        presentation_id = uuid4()
        start_time = time.time()
        
        try:
            # 步骤1: 生成大纲
            yield V3StreamingResponse(
                step="outline",
                status="started",
                message="开始生成演示文稿大纲...",
                progress=0.0
            )
            
            outline_data = await self._step1_generate_outline(request.user_input, request)
            yield V3StreamingResponse(
                step="outline",
                status="completed",
                data=outline_data,
                message="大纲生成完成",
                progress=16.7
            )
            
            # 步骤2: 搜索内容和图片
            if request.enable_search:
                yield V3StreamingResponse(
                    step="search",
                    status="started",
                    message="开始搜索相关内容和图片...",
                    progress=16.7
                )
                
                search_data = await self._step2_search_content(outline_data, request)
                yield V3StreamingResponse(
                    step="search",
                    status="completed",
                    data=search_data,
                    message="内容搜索完成",
                    progress=33.3
                )
            else:
                search_data = outline_data
            
            # 步骤3: 生成PPT内容
            yield V3StreamingResponse(
                step="content",
                status="started",
                message="开始生成PPT内容...",
                progress=33.3
            )
            
            content_data = await self._step3_generate_content(search_data, request)
            yield V3StreamingResponse(
                step="content",
                status="completed",
                data=content_data,
                message="PPT内容生成完成",
                progress=50.0
            )
            
            # 步骤4: 专业HTML生成
            yield V3StreamingResponse(
                step="html",
                status="started",
                message="开始生成专业HTML内容...",
                progress=50.0
            )
            
            html_data = await self._step4_generate_html(content_data, request)
            yield V3StreamingResponse(
                step="html",
                status="completed",
                data=html_data,
                message="HTML内容生成完成",
                progress=66.7
            )
            
            # 步骤5: 流式预览
            yield V3StreamingResponse(
                step="preview",
                status="started",
                message="开始生成预览...",
                progress=66.7
            )
            
            preview_data = await self._step5_stream_preview(html_data, request)
            yield V3StreamingResponse(
                step="preview",
                status="completed",
                data=preview_data,
                message="预览生成完成",
                progress=83.3
            )
            
            # 步骤6: 导出功能
            if request.export_format != "html":
                yield V3StreamingResponse(
                    step="export",
                    status="started",
                    message=f"开始导出为{request.export_format.upper()}格式...",
                    progress=83.3
                )
                
                export_data = await self._step6_export_presentation(
                    html_data, request, presentation_id
                )
                yield V3StreamingResponse(
                    step="export",
                    status="completed",
                    data=export_data,
                    message="导出完成",
                    progress=100.0
                )
            else:
                yield V3StreamingResponse(
                    step="export",
                    status="completed",
                    data={"preview_url": preview_data.get("preview_url")},
                    message="HTML预览已就绪",
                    progress=100.0
                )
                
        except Exception as e:
            yield V3StreamingResponse(
                step="error",
                status="error",
                message=f"处理过程中发生错误: {str(e)}",
                progress=0.0
            )
    
    async def _step1_generate_outline(
        self, 
        user_input: str, 
        request: V3PresentationRequest
    ) -> Dict[str, Any]:
        """步骤1: 生成演示文稿大纲"""
        
        # 基于V2的Markdown解析器进行增强
        from ..utils.markdown_enhancer import EnhancedMarkdownParser
        
        parser = EnhancedMarkdownParser()
        outline = parser.parse_user_input(user_input, request.template)
        
        return {
            "title": outline.title,
            "slides": outline.slides,
            "total_slides": outline.total_slides,
            "content_type": "enhanced_markdown"
        }
    
    async def _step2_search_content(
        self, 
        outline_data: Dict[str, Any], 
        request: V3PresentationRequest
    ) -> Dict[str, Any]:
        """步骤2: 搜索内容和图片"""
        
        # 使用内容搜索服务增强大纲
        enhanced_content = await self.content_search_service.enhance_outline(
            outline_data, request.language
        )
        
        return enhanced_content
    
    async def _step3_generate_content(
        self, 
        search_data: Dict[str, Any], 
        request: V3PresentationRequest
    ) -> Dict[str, Any]:
        """步骤3: 生成PPT内容"""
        
        # 基于V2的内容生成逻辑进行增强
        from ..utils.content_generator import EnhancedContentGenerator
        
        generator = EnhancedContentGenerator()
        ppt_content = await generator.generate_ppt_content(
            search_data, request.template, request.language
        )
        
        return ppt_content
    
    async def _step4_generate_html(
        self, 
        content_data: Dict[str, Any], 
        request: V3PresentationRequest
    ) -> Dict[str, Any]:
        """步骤4: 专业HTML生成"""
        
        # 使用HTML设计专家生成专业HTML
        html_result = await self.html_design_expert.generate_presentation_html(
            content_data, request.template, request.language
        )
        
        return html_result
    
    async def _step5_stream_preview(
        self, 
        html_data: Dict[str, Any], 
        request: V3PresentationRequest
    ) -> Dict[str, Any]:
        """步骤5: 流式预览生成"""
        
        # 生成预览链接和实时预览数据
        preview_url = f"/v3/preview/{uuid4()}"
        
        return {
            "preview_url": preview_url,
            "html_content": html_data.get("html_content"),
            "css_styles": html_data.get("css_styles"),
            "layout_type": html_data.get("layout_type")
        }
    
    async def _step6_export_presentation(
        self, 
        html_data: Dict[str, Any], 
        request: V3PresentationRequest,
        presentation_id: UUID
    ) -> Dict[str, Any]:
        """步骤6: 导出演示文稿"""
        
        # 根据导出格式进行相应处理
        if request.export_format == "pdf":
            from ..utils.export_utils import HTMLToPDFConverter
            converter = HTMLToPDFConverter()
            file_url = await converter.convert(html_data, presentation_id)
        elif request.export_format == "pptx":
            from ..utils.export_utils import HTMLToPPTXConverter
            converter = HTMLToPPTXConverter()
            file_url = await converter.convert(html_data, presentation_id)
        else:
            file_url = html_data.get("preview_url")
        
        return {
            "file_url": file_url,
            "export_format": request.export_format,
            "presentation_id": presentation_id
        }
    
    async def execute_single_step(
        self, 
        step: str, 
        presentation_id: UUID, 
        step_data: Optional[Dict[str, Any]] = None
    ) -> V3StepResponse:
        """执行单个步骤"""
        
        start_time = time.time()
        
        try:
            if step not in self.step_handlers:
                raise ValueError(f"未知的步骤: {step}")
            
            handler = self.step_handlers[step]
            result = await handler(step_data or {})
            
            processing_time = time.time() - start_time
            
            return V3StepResponse(
                step=step,
                success=True,
                data=result,
                message=f"步骤 {step} 执行成功",
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            return V3StepResponse(
                step=step,
                success=False,
                data=None,
                message=f"步骤 {step} 执行失败: {str(e)}",
                processing_time=processing_time
            )
