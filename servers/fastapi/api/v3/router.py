"""
V3版本的主路由器
提供增强的演示文稿生成API
"""

from fastapi import APIRouter
from .ppt.router import V3_PPT_ROUTER

# V3版本的主路由器
V3_ROUTER = APIRouter(prefix="/api/v3", tags=["API V3"])

# 注册所有V3模块路由
V3_ROUTER.include_router(V3_PPT_ROUTER)
