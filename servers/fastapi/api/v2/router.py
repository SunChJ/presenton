from fastapi import APIRouter
from .ppt.router import V2_PPT_ROUTER

# V2版本的主路由器
V2_ROUTER = APIRouter(prefix="/api/v2", tags=["API V2"])

# 注册所有V2模块路由
V2_ROUTER.include_router(V2_PPT_ROUTER)