"""
V3版本的请求模型
定义V3 API的请求数据结构
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from uuid import UUID


class V3PresentationRequest(BaseModel):
    """V3版本：演示文稿生成请求"""
    
    user_input: str = Field(
        description="用户输入的演示文稿内容或主题",
        min_length=10
    )
    template: str = Field(
        default="modern",
        description="指定使用的模板类型"
    )
    language: str = Field(
        default="Chinese", 
        description="生成内容的语言"
    )
    n_slides: Optional[int] = Field(
        default=None,
        description="期望的幻灯片数量，如果不指定则自动确定"
    )
    enable_search: bool = Field(
        default=True,
        description="是否启用内容搜索和图片搜索"
    )
    export_format: Literal["html", "pdf", "pptx"] = Field(
        default="html",
        description="导出格式"
    )
    custom_instructions: Optional[str] = Field(
        default=None,
        description="自定义生成指令"
    )


class V3StepRequest(BaseModel):
    """V3版本：单步执行请求"""
    
    step: Literal["outline", "search", "content", "html", "preview", "export"] = Field(
        description="要执行的步骤"
    )
    presentation_id: UUID = Field(
        description="演示文稿ID"
    )
    step_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="步骤特定的数据"
    )


class V3StreamingRequest(BaseModel):
    """V3版本：流式生成请求"""
    
    user_input: str = Field(
        description="用户输入内容"
    )
    template: str = Field(
        default="modern",
        description="模板类型"
    )
    language: str = Field(
        default="Chinese",
        description="语言"
    )
    enable_search: bool = Field(
        default=True,
        description="是否启用搜索"
    )


class V3ContentSearchRequest(BaseModel):
    """V3版本：内容搜索请求"""
    
    query: str = Field(
        description="搜索查询"
    )
    search_type: Literal["web", "images", "both"] = Field(
        default="both",
        description="搜索类型"
    )
    max_results: int = Field(
        default=5,
        description="最大结果数量"
    )
    language: str = Field(
        default="Chinese",
        description="搜索语言"
    )
