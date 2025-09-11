from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class MarkdownToPPTRequest(BaseModel):
    """V2版本：基于Markdown大纲生成PPT的请求模型"""
    
    markdown_content: str = Field(
        description="Markdown格式的演示文稿大纲内容",
        min_length=10
    )
    template: str = Field(
        default="modern",
        description="指定使用的模板类型，默认为modern"
    )
    language: str = Field(
        default="Chinese", 
        description="生成内容的语言"
    )
    export_format: str = Field(
        default="pptx",
        description="导出格式：pptx或pdf"
    )


class ParsedSlideOutline(BaseModel):
    """解析后的单张幻灯片大纲"""
    
    title: str = Field(description="幻灯片标题")
    content_type: str = Field(description="内容类型：intro, bullets, comparison, image_content等")
    raw_content: str = Field(description="原始Markdown内容")
    suggested_layout: Optional[str] = Field(description="建议使用的布局ID")
    content_hints: Dict[str, Any] = Field(default_factory=dict, description="内容生成提示")


class ParsedMarkdownOutline(BaseModel):
    """解析后的完整Markdown大纲结构"""
    
    title: str = Field(description="演示文稿主标题")
    slides: List[ParsedSlideOutline] = Field(description="解析后的幻灯片列表")
    total_slides: int = Field(description="幻灯片总数")
    template: str = Field(description="使用的模板类型")
    
    
class MarkdownToPPTResponse(BaseModel):
    """V2版本：生成PPT的响应模型"""
    
    success: bool = Field(description="是否成功")
    presentation_id: Optional[UUID] = Field(default=None, description="生成的演示文稿ID")
    preview_url: Optional[str] = Field(default=None, description="预览链接地址")
    edit_url: Optional[str] = Field(default=None, description="编辑链接地址")
    download_url: Optional[str] = Field(default=None, description="下载链接地址")
    slides_count: Optional[int] = Field(default=None, description="生成的幻灯片数量")
    processing_time: Optional[float] = Field(default=None, description="处理耗时（秒）")
    message: Optional[str] = Field(default=None, description="处理结果消息")
    error_details: Optional[str] = Field(default=None, description="错误详情")


class TemplateMatchingResult(BaseModel):
    """模板匹配结果"""
    
    slide_index: int = Field(description="幻灯片索引")
    matched_layout_id: str = Field(description="匹配的布局ID")
    confidence: float = Field(description="匹配置信度 0-1")
    reasoning: str = Field(description="匹配原因说明")