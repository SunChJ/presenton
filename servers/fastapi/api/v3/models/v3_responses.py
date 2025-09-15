"""
V3版本的响应模型
定义V3 API的响应数据结构
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class V3StepResponse(BaseModel):
    """V3版本：单步执行响应"""
    
    step: str = Field(description="执行的步骤")
    success: bool = Field(description="是否成功")
    data: Optional[Dict[str, Any]] = Field(default=None, description="步骤数据")
    message: str = Field(description="步骤消息")
    processing_time: float = Field(description="处理时间（秒）")
    next_step: Optional[str] = Field(default=None, description="下一步骤")


class V3PresentationResponse(BaseModel):
    """V3版本：演示文稿生成响应"""
    
    success: bool = Field(description="是否成功")
    presentation_id: Optional[UUID] = Field(default=None, description="演示文稿ID")
    title: Optional[str] = Field(default=None, description="演示文稿标题")
    slides_count: Optional[int] = Field(default=None, description="幻灯片数量")
    preview_url: Optional[str] = Field(default=None, description="预览链接")
    edit_url: Optional[str] = Field(default=None, description="编辑链接")
    download_url: Optional[str] = Field(default=None, description="下载链接")
    processing_time: float = Field(description="总处理时间（秒）")
    message: str = Field(description="生成结果消息")
    error_details: Optional[str] = Field(default=None, description="错误详情")
    steps_completed: List[str] = Field(default_factory=list, description="已完成的步骤")


class V3StreamingResponse(BaseModel):
    """V3版本：流式生成响应"""
    
    step: str = Field(description="当前步骤")
    status: Literal["started", "processing", "completed", "error"] = Field(description="步骤状态")
    data: Optional[Dict[str, Any]] = Field(default=None, description="步骤数据")
    message: str = Field(description="步骤消息")
    progress: float = Field(description="进度百分比 (0-100)")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class V3ContentSearchResponse(BaseModel):
    """V3版本：内容搜索响应"""
    
    success: bool = Field(description="是否成功")
    query: str = Field(description="搜索查询")
    results: List[Dict[str, Any]] = Field(description="搜索结果")
    total_results: int = Field(description="总结果数量")
    processing_time: float = Field(description="搜索时间（秒）")
    message: str = Field(description="搜索结果消息")


class V3OutlineResponse(BaseModel):
    """V3版本：大纲生成响应"""
    
    success: bool = Field(description="是否成功")
    title: str = Field(description="演示文稿标题")
    slides: List[Dict[str, Any]] = Field(description="幻灯片大纲")
    total_slides: int = Field(description="幻灯片总数")
    content_type: str = Field(description="内容类型")
    processing_time: float = Field(description="处理时间（秒）")
    message: str = Field(description="生成消息")


class V3HTMLResponse(BaseModel):
    """V3版本：HTML生成响应"""
    
    success: bool = Field(description="是否成功")
    html_content: str = Field(description="生成的HTML内容")
    css_styles: str = Field(description="CSS样式")
    layout_type: str = Field(description="布局类型")
    components: List[Dict[str, Any]] = Field(description="组件列表")
    processing_time: float = Field(description="处理时间（秒）")
    message: str = Field(description="生成消息")


class V3ExportResponse(BaseModel):
    """V3版本：导出响应"""
    
    success: bool = Field(description="是否成功")
    file_url: str = Field(description="文件下载链接")
    file_size: Optional[int] = Field(default=None, description="文件大小（字节）")
    export_format: str = Field(description="导出格式")
    processing_time: float = Field(description="处理时间（秒）")
    message: str = Field(description="导出消息")
