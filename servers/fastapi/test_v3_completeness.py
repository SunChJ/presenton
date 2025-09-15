#!/usr/bin/env python3
"""
V3项目完整性验证测试集
验证V3 Presentation Generator的6步流程实现情况
"""

import sys
import os
import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.insert(0, '.')

class V3CompletenessValidator:
    """V3完整性验证器"""

    def __init__(self):
        self.test_results = {
            "test_time": datetime.now().isoformat(),
            "steps": {},
            "overall_score": 0,
            "recommendations": []
        }
        self.test_input = "我想制作一个关于人工智能技术发展趋势的演示文稿，包括AI技术概述、当前主要技术方向、应用案例和未来发展趋势"

    def print_header(self, title: str):
        """打印测试标题"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")

    def print_step(self, step_name: str, status: str, details: str = ""):
        """打印步骤结果"""
        status_emoji = {
            "PASS": "✅",
            "PARTIAL": "⚠️",
            "FAIL": "❌",
            "MISSING": "🚫"
        }
        print(f"{status_emoji.get(status, '❓')} {step_name}: {status}")
        if details:
            print(f"   {details}")

    async def validate_step1_outline_generation(self) -> Dict[str, Any]:
        """验证步骤1: 生成大纲 (Markdown解析)"""
        self.print_header("步骤1: 生成大纲验证")

        step_results = {
            "step_name": "outline_generation",
            "score": 0,
            "max_score": 100,
            "components": {}
        }

        # 1.1 测试增强Markdown解析器导入
        try:
            from api.v3.utils.markdown_enhancer import EnhancedMarkdownParser
            parser = EnhancedMarkdownParser()
            step_results["components"]["markdown_parser"] = {"status": "PASS", "score": 20}
            self.print_step("Markdown解析器导入", "PASS")
        except Exception as e:
            step_results["components"]["markdown_parser"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("Markdown解析器导入", "FAIL", f"错误: {e}")
            return step_results

        # 1.2 测试文本输入解析
        try:
            result = parser.parse_user_input(self.test_input, "modern")
            required_fields = ["title", "slides", "total_slides", "template"]

            if all(field in result for field in required_fields):
                step_results["components"]["text_parsing"] = {"status": "PASS", "score": 25}
                self.print_step("文本输入解析", "PASS", f"生成 {result['total_slides']} 张幻灯片")
            else:
                missing = [f for f in required_fields if f not in result]
                step_results["components"]["text_parsing"] = {"status": "PARTIAL", "score": 15}
                self.print_step("文本输入解析", "PARTIAL", f"缺少字段: {missing}")
        except Exception as e:
            step_results["components"]["text_parsing"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("文本输入解析", "FAIL", f"错误: {e}")

        # 1.3 测试内容类型识别
        try:
            if result.get("slides"):
                slide = result["slides"][0]
                if "type" in slide and "suggested_layout" in slide:
                    step_results["components"]["content_type_detection"] = {"status": "PASS", "score": 25}
                    self.print_step("内容类型识别", "PASS", f"识别类型: {slide.get('type')}")
                else:
                    step_results["components"]["content_type_detection"] = {"status": "PARTIAL", "score": 10}
                    self.print_step("内容类型识别", "PARTIAL", "类型识别不完整")
            else:
                step_results["components"]["content_type_detection"] = {"status": "FAIL", "score": 0}
                self.print_step("内容类型识别", "FAIL", "无幻灯片数据")
        except Exception as e:
            step_results["components"]["content_type_detection"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("内容类型识别", "FAIL", f"错误: {e}")

        # 1.4 测试增强内容提示
        try:
            if result.get("slides") and "content_hints" in result["slides"][0]:
                step_results["components"]["content_hints"] = {"status": "PASS", "score": 30}
                hints = result["slides"][0]["content_hints"]
                self.print_step("内容提示生成", "PASS", f"提示数量: {len(hints)}")
            else:
                step_results["components"]["content_hints"] = {"status": "PARTIAL", "score": 15}
                self.print_step("内容提示生成", "PARTIAL", "内容提示不完整")
        except Exception as e:
            step_results["components"]["content_hints"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("内容提示生成", "FAIL", f"错误: {e}")

        # 计算总分
        step_results["score"] = sum(comp["score"] for comp in step_results["components"].values())
        return step_results

    async def validate_step2_content_search(self) -> Dict[str, Any]:
        """验证步骤2: 搜索内容和图片"""
        self.print_header("步骤2: 内容搜索验证")

        step_results = {
            "step_name": "content_search",
            "score": 0,
            "max_score": 100,
            "components": {}
        }

        # 2.1 测试内容搜索服务导入
        try:
            from api.v3.services.content_search import ContentSearchService
            search_service = ContentSearchService()
            step_results["components"]["search_service"] = {"status": "PASS", "score": 20}
            self.print_step("内容搜索服务", "PASS")
        except Exception as e:
            step_results["components"]["search_service"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("内容搜索服务", "FAIL", f"错误: {e}")
            return step_results

        # 2.2 测试关键词提取
        try:
            test_slide = {"title": "人工智能概述", "content": "人工智能技术发展趋势分析"}
            keywords = search_service._extract_keywords(test_slide)

            if keywords and len(keywords) > 0:
                step_results["components"]["keyword_extraction"] = {"status": "PASS", "score": 25}
                self.print_step("关键词提取", "PASS", f"提取关键词: {keywords}")
            else:
                step_results["components"]["keyword_extraction"] = {"status": "FAIL", "score": 0}
                self.print_step("关键词提取", "FAIL", "无法提取关键词")
        except Exception as e:
            step_results["components"]["keyword_extraction"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("关键词提取", "FAIL", f"错误: {e}")

        # 2.3 测试网络内容搜索
        try:
            web_results = await search_service._search_web_content(["人工智能"], "Chinese")

            if web_results and len(web_results) > 0:
                step_results["components"]["web_search"] = {"status": "PASS", "score": 30}
                self.print_step("网络内容搜索", "PASS", f"搜索结果数: {len(web_results)}")
            else:
                step_results["components"]["web_search"] = {"status": "PARTIAL", "score": 10}
                self.print_step("网络内容搜索", "PARTIAL", "搜索结果为空")
        except Exception as e:
            step_results["components"]["web_search"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("网络内容搜索", "FAIL", f"错误: {e}")

        # 2.4 测试图片搜索
        try:
            image_results = await search_service._search_images(["人工智能"], "Chinese")

            if image_results and len(image_results) > 0:
                step_results["components"]["image_search"] = {"status": "PASS", "score": 25}
                self.print_step("图片搜索", "PASS", f"图片数量: {len(image_results)}")
            else:
                step_results["components"]["image_search"] = {"status": "PARTIAL", "score": 10}
                self.print_step("图片搜索", "PARTIAL", "图片搜索结果为空")
        except Exception as e:
            step_results["components"]["image_search"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("图片搜索", "FAIL", f"错误: {e}")

        step_results["score"] = sum(comp["score"] for comp in step_results["components"].values())
        return step_results

    async def validate_step3_content_generation(self) -> Dict[str, Any]:
        """验证步骤3: 生成PPT内容"""
        self.print_header("步骤3: PPT内容生成验证")

        step_results = {
            "step_name": "content_generation",
            "score": 0,
            "max_score": 100,
            "components": {}
        }

        # 3.1 测试内容生成器导入
        try:
            from api.v3.utils.content_generator import EnhancedContentGenerator
            generator = EnhancedContentGenerator()
            step_results["components"]["content_generator"] = {"status": "PASS", "score": 30}
            self.print_step("内容生成器", "PASS")
        except Exception as e:
            step_results["components"]["content_generator"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("内容生成器", "FAIL", f"错误: {e}")
            return step_results

        # 3.2 测试PPT内容生成
        try:
            test_data = {
                "title": "AI技术发展",
                "slides": [
                    {"title": "概述", "content": "人工智能概述", "type": "intro"},
                    {"title": "技术方向", "content": "主要技术方向", "type": "bullets"}
                ]
            }

            result = await generator.generate_ppt_content(test_data, "modern", "Chinese")

            if result and "slides" in result:
                enhanced_count = sum(1 for slide in result["slides"] if slide.get("enhanced"))
                if enhanced_count > 0:
                    step_results["components"]["content_enhancement"] = {"status": "PASS", "score": 40}
                    self.print_step("内容增强", "PASS", f"增强 {enhanced_count} 张幻灯片")
                else:
                    step_results["components"]["content_enhancement"] = {"status": "PARTIAL", "score": 20}
                    self.print_step("内容增强", "PARTIAL", "增强标记缺失")
            else:
                step_results["components"]["content_enhancement"] = {"status": "FAIL", "score": 0}
                self.print_step("内容增强", "FAIL", "内容生成失败")
        except Exception as e:
            step_results["components"]["content_enhancement"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("内容增强", "FAIL", f"错误: {e}")

        # 3.3 测试模板和语言支持
        try:
            if result and result.get("template") == "modern" and result.get("language") == "Chinese":
                step_results["components"]["template_language"] = {"status": "PASS", "score": 30}
                self.print_step("模板和语言支持", "PASS")
            else:
                step_results["components"]["template_language"] = {"status": "PARTIAL", "score": 15}
                self.print_step("模板和语言支持", "PARTIAL", "配置不完整")
        except Exception as e:
            step_results["components"]["template_language"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("模板和语言支持", "FAIL", f"错误: {e}")

        step_results["score"] = sum(comp["score"] for comp in step_results["components"].values())
        return step_results

    async def validate_step4_html_generation(self) -> Dict[str, Any]:
        """验证步骤4: 专业HTML生成 (角色扮演)"""
        self.print_header("步骤4: 专业HTML生成验证")

        step_results = {
            "step_name": "html_generation",
            "score": 0,
            "max_score": 100,
            "components": {}
        }

        # 4.1 测试HTML设计专家导入
        try:
            from api.v3.services.html_design_expert import HTMLDesignExpert
            expert = HTMLDesignExpert()
            step_results["components"]["html_expert"] = {"status": "PASS", "score": 20}
            self.print_step("HTML设计专家", "PASS")
        except Exception as e:
            step_results["components"]["html_expert"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("HTML设计专家", "FAIL", f"错误: {e}")
            return step_results

        # 4.2 测试专家角色设定
        try:
            persona = expert.expert_persona
            if persona and len(persona.strip()) > 100:
                step_results["components"]["expert_persona"] = {"status": "PASS", "score": 15}
                self.print_step("专家角色设定", "PASS", f"角色描述长度: {len(persona)}")
            else:
                step_results["components"]["expert_persona"] = {"status": "PARTIAL", "score": 5}
                self.print_step("专家角色设定", "PARTIAL", "角色设定不够详细")
        except Exception as e:
            step_results["components"]["expert_persona"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("专家角色设定", "FAIL", f"错误: {e}")

        # 4.3 测试布局模板加载
        try:
            templates = expert.layout_templates
            style_themes = expert.style_themes

            if templates and style_themes:
                template_count = len(templates)
                theme_count = len(style_themes)
                step_results["components"]["templates_themes"] = {"status": "PASS", "score": 25}
                self.print_step("模板和主题", "PASS", f"模板: {template_count}, 主题: {theme_count}")
            else:
                step_results["components"]["templates_themes"] = {"status": "PARTIAL", "score": 10}
                self.print_step("模板和主题", "PARTIAL", "模板或主题缺失")
        except Exception as e:
            step_results["components"]["templates_themes"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("模板和主题", "FAIL", f"错误: {e}")

        # 4.4 测试HTML生成
        try:
            test_content = {
                "title": "AI技术发展",
                "slides": [
                    {"title": "概述", "content": "人工智能概述", "type": "intro"},
                    {"title": "要点", "content": "主要技术要点", "type": "bullets"}
                ]
            }

            html_result = await expert.generate_presentation_html(test_content, "modern", "Chinese")

            required_fields = ["html_content", "css_styles", "layout_type", "components"]
            if all(field in html_result for field in required_fields):
                step_results["components"]["html_generation"] = {"status": "PASS", "score": 40}
                self.print_step("HTML内容生成", "PASS", f"生成组件数: {len(html_result['components'])}")
            else:
                missing = [f for f in required_fields if f not in html_result]
                step_results["components"]["html_generation"] = {"status": "PARTIAL", "score": 20}
                self.print_step("HTML内容生成", "PARTIAL", f"缺少字段: {missing}")
        except Exception as e:
            step_results["components"]["html_generation"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("HTML内容生成", "FAIL", f"错误: {e}")

        step_results["score"] = sum(comp["score"] for comp in step_results["components"].values())
        return step_results

    async def validate_step5_streaming_preview(self) -> Dict[str, Any]:
        """验证步骤5: 流式生成展示"""
        self.print_header("步骤5: 流式生成展示验证")

        step_results = {
            "step_name": "streaming_preview",
            "score": 0,
            "max_score": 100,
            "components": {}
        }

        # 5.1 测试流式端点导入
        try:
            from api.v3.ppt.endpoints.streaming_generator import V3_STREAMING_ROUTER
            step_results["components"]["streaming_router"] = {"status": "PASS", "score": 25}
            self.print_step("流式路由器", "PASS")
        except Exception as e:
            step_results["components"]["streaming_router"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("流式路由器", "FAIL", f"错误: {e}")

        # 5.2 测试增强Agent流式处理
        try:
            from api.v3.services.enhanced_agent import V3EnhancedAgent
            from api.v3.models.v3_requests import V3PresentationRequest

            agent = V3EnhancedAgent()
            request = V3PresentationRequest(
                user_input=self.test_input,
                template="modern",
                language="Chinese",
                enable_search=True,
                export_format="html"
            )

            # 测试流式生成器是否可以创建
            stream_gen = agent.process_presentation_request(request)
            if stream_gen:
                step_results["components"]["streaming_agent"] = {"status": "PASS", "score": 35}
                self.print_step("流式Agent", "PASS", "流式生成器创建成功")
            else:
                step_results["components"]["streaming_agent"] = {"status": "FAIL", "score": 0}
                self.print_step("流式Agent", "FAIL", "无法创建流式生成器")
        except Exception as e:
            step_results["components"]["streaming_agent"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("流式Agent", "FAIL", f"错误: {e}")

        # 5.3 测试步骤处理器
        try:
            step_handlers = agent.step_handlers
            expected_steps = ["outline", "search", "content", "html", "preview", "export"]

            if all(step in step_handlers for step in expected_steps):
                step_results["components"]["step_handlers"] = {"status": "PASS", "score": 25}
                self.print_step("步骤处理器", "PASS", f"支持步骤: {list(step_handlers.keys())}")
            else:
                missing_steps = [s for s in expected_steps if s not in step_handlers]
                step_results["components"]["step_handlers"] = {"status": "PARTIAL", "score": 15}
                self.print_step("步骤处理器", "PARTIAL", f"缺少步骤: {missing_steps}")
        except Exception as e:
            step_results["components"]["step_handlers"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("步骤处理器", "FAIL", f"错误: {e}")

        # 5.4 测试V3响应模型
        try:
            from api.v3.models.v3_responses import V3StreamingResponse

            # 创建测试响应
            test_response = V3StreamingResponse(
                step="test",
                status="processing",
                message="测试消息",
                progress=50.0
            )

            if test_response.step == "test" and test_response.progress == 50.0:
                step_results["components"]["response_model"] = {"status": "PASS", "score": 15}
                self.print_step("响应模型", "PASS", "V3响应模型正常")
            else:
                step_results["components"]["response_model"] = {"status": "FAIL", "score": 0}
                self.print_step("响应模型", "FAIL", "响应模型验证失败")
        except Exception as e:
            step_results["components"]["response_model"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("响应模型", "FAIL", f"错误: {e}")

        step_results["score"] = sum(comp["score"] for comp in step_results["components"].values())
        return step_results

    async def validate_step6_export_services(self) -> Dict[str, Any]:
        """验证步骤6: 导出PDF/PPTX"""
        self.print_header("步骤6: 导出服务验证")

        step_results = {
            "step_name": "export_services",
            "score": 0,
            "max_score": 100,
            "components": {}
        }

        # 6.1 测试导出工具导入
        try:
            from api.v3.utils.export_utils import HTMLToPDFConverter, HTMLToPPTXConverter
            pdf_converter = HTMLToPDFConverter()
            pptx_converter = HTMLToPPTXConverter()
            step_results["components"]["export_converters"] = {"status": "PASS", "score": 30}
            self.print_step("导出转换器", "PASS", "PDF和PPTX转换器")
        except Exception as e:
            step_results["components"]["export_converters"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("导出转换器", "FAIL", f"错误: {e}")
            return step_results

        # 6.2 测试PDF转换功能
        try:
            import uuid
            test_html_data = {
                "html_content": "<html><body><h1>Test</h1></body></html>",
                "css_styles": "body { font-family: Arial; }"
            }

            pdf_result = await pdf_converter.convert(test_html_data, uuid.uuid4())

            if pdf_result and pdf_result.endswith('.pdf'):
                step_results["components"]["pdf_conversion"] = {"status": "PASS", "score": 35}
                self.print_step("PDF转换", "PASS", f"输出路径: {pdf_result}")
            else:
                step_results["components"]["pdf_conversion"] = {"status": "PARTIAL", "score": 15}
                self.print_step("PDF转换", "PARTIAL", "PDF路径格式可能有问题")
        except Exception as e:
            step_results["components"]["pdf_conversion"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("PDF转换", "FAIL", f"错误: {e}")

        # 6.3 测试PPTX转换功能
        try:
            pptx_result = await pptx_converter.convert(test_html_data, uuid.uuid4())

            if pptx_result and pptx_result.endswith('.pptx'):
                step_results["components"]["pptx_conversion"] = {"status": "PASS", "score": 35}
                self.print_step("PPTX转换", "PASS", f"输出路径: {pptx_result}")
            else:
                step_results["components"]["pptx_conversion"] = {"status": "PARTIAL", "score": 15}
                self.print_step("PPTX转换", "PARTIAL", "PPTX路径格式可能有问题")
        except Exception as e:
            step_results["components"]["pptx_conversion"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("PPTX转换", "FAIL", f"错误: {e}")

        step_results["score"] = sum(comp["score"] for comp in step_results["components"].values())
        return step_results

    async def validate_dsl_system(self) -> Dict[str, Any]:
        """验证DSL系统"""
        self.print_header("DSL系统验证")

        step_results = {
            "step_name": "dsl_system",
            "score": 0,
            "max_score": 100,
            "components": {}
        }

        # DSL.1 测试DSL模型导入
        try:
            from api.v3.models.dsl_models import (
                PresentationDSL, SlideDSL, ComponentModel,
                LayoutModel, StyleModel, DSLGenerationRequest
            )
            step_results["components"]["dsl_models"] = {"status": "PASS", "score": 25}
            self.print_step("DSL模型", "PASS", "所有DSL模型导入成功")
        except Exception as e:
            step_results["components"]["dsl_models"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("DSL模型", "FAIL", f"错误: {e}")
            return step_results

        # DSL.2 测试DSL生成器
        try:
            from api.v3.services.dsl_generator import DSLGenerator
            dsl_generator = DSLGenerator()

            # 测试生成器的各种处理器
            layout_generators = dsl_generator.layout_generators
            component_generators = dsl_generator.component_generators

            if layout_generators and component_generators:
                step_results["components"]["dsl_generator"] = {"status": "PASS", "score": 30}
                self.print_step("DSL生成器", "PASS",
                              f"布局生成器: {len(layout_generators)}, 组件生成器: {len(component_generators)}")
            else:
                step_results["components"]["dsl_generator"] = {"status": "PARTIAL", "score": 15}
                self.print_step("DSL生成器", "PARTIAL", "生成器不完整")
        except Exception as e:
            step_results["components"]["dsl_generator"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("DSL生成器", "FAIL", f"错误: {e}")

        # DSL.3 测试DSL生成请求
        try:
            test_content = {
                "title": "测试演示文稿",
                "slides": [
                    {"title": "概述", "content": "内容概述", "type": "intro"},
                    {"title": "要点", "content": "关键要点", "type": "bullets"}
                ]
            }

            dsl_request = DSLGenerationRequest(
                content=test_content,
                template="modern",
                language="Chinese"
            )

            dsl_response = await dsl_generator.generate_presentation_dsl(dsl_request)

            if dsl_response.success and dsl_response.dsl:
                step_results["components"]["dsl_generation"] = {"status": "PASS", "score": 45}
                self.print_step("DSL生成", "PASS",
                              f"生成DSL包含 {len(dsl_response.dsl.slides)} 张幻灯片")
            else:
                step_results["components"]["dsl_generation"] = {"status": "PARTIAL", "score": 20}
                self.print_step("DSL生成", "PARTIAL", f"生成结果: {dsl_response.message}")
        except Exception as e:
            step_results["components"]["dsl_generation"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("DSL生成", "FAIL", f"错误: {e}")

        step_results["score"] = sum(comp["score"] for comp in step_results["components"].values())
        return step_results

    async def validate_integration_completeness(self) -> Dict[str, Any]:
        """验证集成完整性"""
        self.print_header("集成完整性验证")

        step_results = {
            "step_name": "integration",
            "score": 0,
            "max_score": 100,
            "components": {}
        }

        # INT.1 测试V3路由器集成
        try:
            from api.v3.router import V3_ROUTER
            from api.main import app

            # 检查V3路由是否已集成到主应用
            v3_routes = [route for route in app.routes if hasattr(route, 'path') and '/v3/' in route.path]

            if len(v3_routes) > 0:
                step_results["components"]["router_integration"] = {"status": "PASS", "score": 30}
                self.print_step("路由器集成", "PASS", f"V3路由数量: {len(v3_routes)}")
            else:
                step_results["components"]["router_integration"] = {"status": "FAIL", "score": 0}
                self.print_step("路由器集成", "FAIL", "V3路由未集成")
        except Exception as e:
            step_results["components"]["router_integration"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("路由器集成", "FAIL", f"错误: {e}")

        # INT.2 测试端到端流程
        try:
            from api.v3.services.enhanced_agent import V3EnhancedAgent
            from api.v3.models.v3_requests import V3PresentationRequest

            agent = V3EnhancedAgent()
            request = V3PresentationRequest(
                user_input="测试演示文稿生成的完整功能验证",  # 增加字符串长度
                template="modern",
                language="Chinese",
                enable_search=False,  # 禁用搜索以简化测试
                export_format="html"
            )

            # 尝试执行一个完整的流程（但不等待完成）
            stream = agent.process_presentation_request(request)
            first_response = await stream.__anext__()

            if first_response and first_response.step == "outline":
                step_results["components"]["end_to_end"] = {"status": "PASS", "score": 40}
                self.print_step("端到端流程", "PASS", f"首个步骤: {first_response.step}")
            else:
                step_results["components"]["end_to_end"] = {"status": "PARTIAL", "score": 20}
                self.print_step("端到端流程", "PARTIAL", "流程启动异常")
        except Exception as e:
            step_results["components"]["end_to_end"] = {"status": "FAIL", "score": 0, "error": str(e)}
            self.print_step("端到端流程", "FAIL", f"错误: {e}")

        # INT.3 测试数据库依赖
        try:
            from services.database import get_async_session
            session_gen = get_async_session()
            if session_gen:
                step_results["components"]["database"] = {"status": "PASS", "score": 30}
                self.print_step("数据库集成", "PASS", "数据库会话创建成功")
            else:
                step_results["components"]["database"] = {"status": "FAIL", "score": 0}
                self.print_step("数据库集成", "FAIL", "无法创建数据库会话")
        except Exception as e:
            step_results["components"]["database"] = {"status": "PARTIAL", "score": 15, "error": str(e)}
            self.print_step("数据库集成", "PARTIAL", f"数据库可能未配置: {e}")

        step_results["score"] = sum(comp["score"] for comp in step_results["components"].values())
        return step_results

    def generate_completeness_report(self):
        """生成完整性报告"""
        self.print_header("V3项目完整性评估报告")

        total_score = 0
        total_max_score = 0
        step_scores = []

        for step_name, step_data in self.test_results["steps"].items():
            score = step_data["score"]
            max_score = step_data["max_score"]
            percentage = (score / max_score * 100) if max_score > 0 else 0

            step_scores.append({
                "name": step_name,
                "score": score,
                "max_score": max_score,
                "percentage": percentage
            })

            total_score += score
            total_max_score += max_score

        overall_percentage = (total_score / total_max_score * 100) if total_max_score > 0 else 0

        print(f"\n📊 总体完成度: {overall_percentage:.1f}% ({total_score}/{total_max_score})")
        print("\n📋 各步骤完成度:")

        for step in step_scores:
            status_icon = "🟢" if step["percentage"] >= 80 else "🟡" if step["percentage"] >= 60 else "🔴"
            print(f"{status_icon} {step['name']}: {step['percentage']:.1f}% ({step['score']}/{step['max_score']})")

        # 生成建议
        self.generate_recommendations(step_scores, overall_percentage)

        # 保存详细报告
        self.save_detailed_report()

    def generate_recommendations(self, step_scores: List[Dict], overall_percentage: float):
        """生成改进建议"""
        print(f"\n💡 改进建议:")

        recommendations = []

        if overall_percentage < 70:
            recommendations.append("⚠️  项目完整度较低，建议优先完善核心功能")

        for step in step_scores:
            if step["percentage"] < 50:
                recommendations.append(f"🔧 {step['name']} 需要重点关注和完善")
            elif step["percentage"] < 80:
                recommendations.append(f"⚡ {step['name']} 基本功能完整，需要优化细节")

        # 具体的技术建议
        low_score_steps = [s for s in step_scores if s["percentage"] < 60]

        if any("content_generation" in s["name"] for s in low_score_steps):
            recommendations.append("📝 内容生成逻辑需要集成实际的LLM调用")

        if any("export" in s["name"] for s in low_score_steps):
            recommendations.append("📤 导出服务需要实现实际的PDF和PPTX转换逻辑")

        if any("search" in s["name"] for s in low_score_steps):
            recommendations.append("🔍 搜索服务需要集成真实的搜索API")

        if any("html" in s["name"] for s in low_score_steps):
            recommendations.append("🎨 HTML生成需要完善DSL到HTML的编译逻辑")

        for rec in recommendations:
            print(f"  {rec}")

    def save_detailed_report(self):
        """保存详细报告"""
        report_file = f"v3_completeness_report_{int(time.time())}.json"

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)

            print(f"\n💾 详细报告已保存至: {report_file}")
        except Exception as e:
            print(f"\n❌ 保存报告失败: {e}")

    async def run_all_validations(self):
        """运行所有验证测试"""
        print("🚀 开始V3项目完整性验证...")
        print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🧪 测试输入: {self.test_input}")

        # 执行所有验证步骤
        validations = [
            ("steps", "step1", self.validate_step1_outline_generation()),
            ("steps", "step2", self.validate_step2_content_search()),
            ("steps", "step3", self.validate_step3_content_generation()),
            ("steps", "step4", self.validate_step4_html_generation()),
            ("steps", "step5", self.validate_step5_streaming_preview()),
            ("steps", "step6", self.validate_step6_export_services()),
            ("steps", "dsl_system", self.validate_dsl_system()),
            ("steps", "integration", self.validate_integration_completeness())
        ]

        for category, step_name, validation_coro in validations:
            try:
                result = await validation_coro
                if category not in self.test_results:
                    self.test_results[category] = {}
                self.test_results[category][step_name] = result
            except Exception as e:
                print(f"❌ 验证 {step_name} 时发生错误: {e}")
                if category not in self.test_results:
                    self.test_results[category] = {}
                self.test_results[category][step_name] = {
                    "step_name": step_name,
                    "score": 0,
                    "max_score": 100,
                    "components": {},
                    "error": str(e)
                }

        # 生成报告
        self.generate_completeness_report()


async def main():
    """主函数"""
    validator = V3CompletenessValidator()
    await validator.run_all_validations()


if __name__ == "__main__":
    asyncio.run(main())