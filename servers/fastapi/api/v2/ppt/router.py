from fastapi import APIRouter
from .endpoints.markdown_to_ppt import MARKDOWN_TO_PPT_ROUTER
from .endpoints.test_endpoint import TEST_ROUTER

# V2版本的PPT API路由器
V2_PPT_ROUTER = APIRouter(prefix="/ppt", tags=["PPT V2"])

# 注册所有V2端点
V2_PPT_ROUTER.include_router(MARKDOWN_TO_PPT_ROUTER)
V2_PPT_ROUTER.include_router(TEST_ROUTER)