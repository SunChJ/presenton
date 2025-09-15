"""
V3版本的PPT API路由器
提供增强的演示文稿生成功能
"""

from fastapi import APIRouter
from .endpoints.presentation_generator import V3_PRESENTATION_ROUTER
from .endpoints.streaming_generator import V3_STREAMING_ROUTER

# V3版本的PPT API路由器
V3_PPT_ROUTER = APIRouter(prefix="/ppt", tags=["PPT V3"])

# 注册所有V3端点
V3_PPT_ROUTER.include_router(V3_PRESENTATION_ROUTER)
V3_PPT_ROUTER.include_router(V3_STREAMING_ROUTER)
