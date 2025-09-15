"""
V3版本的DSL模型
定义演示文稿DSL的数据结构
"""

from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum


class LayoutType(str, Enum):
    """布局类型枚举"""
    GRID = "grid"
    FLEX = "flex"
    ABSOLUTE = "absolute"
    CUSTOM = "custom"


class ComponentType(str, Enum):
    """组件类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    LIST = "list"
    CHART = "chart"
    QUOTE = "quote"
    CARD = "card"
    BUTTON = "button"
    DIVIDER = "divider"


class PositionModel(BaseModel):
    """位置模型"""
    x: float = Field(description="X坐标")
    y: float = Field(description="Y坐标")
    width: float = Field(description="宽度")
    height: float = Field(description="高度")
    z_index: Optional[int] = Field(default=0, description="层级")


class ColorModel(BaseModel):
    """颜色模型"""
    primary: str = Field(description="主色调")
    secondary: str = Field(description="辅助色")
    accent: str = Field(description="强调色")
    background: str = Field(description="背景色")
    text: str = Field(description="文字色")


class TypographyModel(BaseModel):
    """字体模型"""
    font_family: str = Field(description="字体族")
    font_size: float = Field(description="字体大小")
    font_weight: str = Field(description="字体粗细")
    line_height: float = Field(description="行高")
    letter_spacing: float = Field(description="字符间距")


class ComponentModel(BaseModel):
    """组件模型"""
    id: str = Field(description="组件ID")
    type: ComponentType = Field(description="组件类型")
    content: Dict[str, Any] = Field(description="组件内容")
    position: PositionModel = Field(description="位置信息")
    style: Dict[str, Any] = Field(default_factory=dict, description="样式信息")
    children: Optional[List["ComponentModel"]] = Field(default=None, description="子组件")


class LayoutModel(BaseModel):
    """布局模型"""
    type: LayoutType = Field(description="布局类型")
    structure: Dict[str, Any] = Field(description="布局结构")
    grid_config: Optional[Dict[str, Any]] = Field(default=None, description="网格配置")
    flex_config: Optional[Dict[str, Any]] = Field(default=None, description="弹性布局配置")


class StyleModel(BaseModel):
    """样式模型"""
    theme: str = Field(description="主题名称")
    colors: ColorModel = Field(description="颜色配置")
    typography: TypographyModel = Field(description="字体配置")
    spacing: Dict[str, float] = Field(description="间距配置")
    borders: Dict[str, Any] = Field(description="边框配置")
    shadows: Dict[str, Any] = Field(description="阴影配置")


class SlideDSL(BaseModel):
    """幻灯片DSL模型"""
    id: str = Field(description="幻灯片ID")
    title: str = Field(description="幻灯片标题")
    layout: LayoutModel = Field(description="布局配置")
    components: List[ComponentModel] = Field(description="组件列表")
    style: StyleModel = Field(description="样式配置")
    background: Optional[Dict[str, Any]] = Field(default=None, description="背景配置")


class PresentationDSL(BaseModel):
    """演示文稿DSL模型"""
    id: str = Field(description="演示文稿ID")
    title: str = Field(description="演示文稿标题")
    description: Optional[str] = Field(default=None, description="描述")
    slides: List[SlideDSL] = Field(description="幻灯片列表")
    global_style: StyleModel = Field(description="全局样式")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class DSLGenerationRequest(BaseModel):
    """DSL生成请求"""
    content: Dict[str, Any] = Field(description="内容数据")
    layout_preference: Optional[str] = Field(default=None, description="布局偏好")
    style_preference: Optional[str] = Field(default=None, description="样式偏好")
    template: str = Field(default="modern", description="模板类型")
    language: str = Field(default="Chinese", description="语言")


class DSLGenerationResponse(BaseModel):
    """DSL生成响应"""
    success: bool = Field(description="是否成功")
    dsl: Optional[PresentationDSL] = Field(default=None, description="生成的DSL")
    processing_time: float = Field(description="处理时间（秒）")
    message: str = Field(description="生成消息")
    error_details: Optional[str] = Field(default=None, description="错误详情")
