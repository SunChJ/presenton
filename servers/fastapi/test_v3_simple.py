#!/usr/bin/env python3
"""
V3版本简单测试脚本
验证V3模块的基本功能
"""

import sys
import os
sys.path.insert(0, '.')

def test_v3_imports():
    """测试V3模块导入"""
    print("🔍 测试V3模块导入...")

    try:
        from api.v3.router import V3_ROUTER
        print("✅ V3路由器导入成功")
    except Exception as e:
        print(f"❌ V3路由器导入失败: {e}")
        return False

    try:
        from api.v3.services.enhanced_agent import V3EnhancedAgent
        print("✅ V3增强Agent导入成功")
    except Exception as e:
        print(f"❌ V3增强Agent导入失败: {e}")
        return False

    try:
        from api.v3.services.content_search import ContentSearchService
        print("✅ 内容搜索服务导入成功")
    except Exception as e:
        print(f"❌ 内容搜索服务导入失败: {e}")
        return False

    try:
        from api.v3.services.html_design_expert import HTMLDesignExpert
        print("✅ HTML设计专家导入成功")
    except Exception as e:
        print(f"❌ HTML设计专家导入失败: {e}")
        return False

    try:
        from api.v3.services.dsl_generator import DSLGenerator
        print("✅ DSL生成器导入成功")
    except Exception as e:
        print(f"❌ DSL生成器导入失败: {e}")
        return False

    try:
        from api.v3.models.v3_requests import V3PresentationRequest
        from api.v3.models.v3_responses import V3PresentationResponse
        print("✅ V3模型导入成功")
    except Exception as e:
        print(f"❌ V3模型导入失败: {e}")
        return False

    return True

def test_v3_endpoints():
    """测试V3端点"""
    print("\n🔍 测试V3端点...")

    try:
        from api.v3.ppt.endpoints.presentation_generator import V3_PRESENTATION_ROUTER
        from api.v3.ppt.endpoints.streaming_generator import V3_STREAMING_ROUTER
        print("✅ V3端点导入成功")
    except Exception as e:
        print(f"❌ V3端点导入失败: {e}")
        return False

    return True

def test_main_app():
    """测试主应用程序"""
    print("\n🔍 测试主应用程序...")

    try:
        from api.main import app
        print("✅ 主应用程序导入成功")
        print(f"📊 应用路由数量: {len(app.routes)}")
    except Exception as e:
        print(f"❌ 主应用程序导入失败: {e}")
        return False

    return True

if __name__ == "__main__":
    print("🚀 开始V3版本测试...\n")

    success = True
    success &= test_v3_imports()
    success &= test_v3_endpoints()
    success &= test_main_app()

    if success:
        print("\n🎉 所有V3测试通过！")
        print("\n📋 V3版本特性：")
        print("• 步骤化Agent执行器 (6个核心步骤)")
        print("• 增强的Markdown解析器")
        print("• 内容搜索服务")
        print("• 专业HTML设计专家")
        print("• 灵活的DSL系统")
        print("• 流式生成展示")
        print("• 增强的导出功能")
        print("• 完整的API端点")
    else:
        print("\n❌ 部分测试失败，请检查错误信息")
