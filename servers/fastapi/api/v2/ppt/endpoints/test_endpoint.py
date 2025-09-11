from fastapi import APIRouter
from models.v2.markdown_ppt_request import MarkdownToPPTRequest, MarkdownToPPTResponse

TEST_ROUTER = APIRouter(prefix="/test", tags=["V2 Test"])

@TEST_ROUTER.post("/simple", response_model=MarkdownToPPTResponse)
async def test_simple_endpoint(request: MarkdownToPPTRequest) -> MarkdownToPPTResponse:
    """简单测试端点"""
    
    try:
        # 只做基础解析测试
        from services.v2.markdown_parser import MarkdownOutlineParser
        
        parser = MarkdownOutlineParser()
        parsed = parser.parse_markdown_outline(request.markdown_content, request.template)
        
        return MarkdownToPPTResponse(
            success=True,
            slides_count=parsed.total_slides,
            processing_time=0.1,
            message=f"测试成功：解析了{parsed.total_slides}张幻灯片"
        )
        
    except Exception as e:
        return MarkdownToPPTResponse(
            success=False,
            processing_time=0.1,
            message="测试失败",
            error_details=str(e)
        )