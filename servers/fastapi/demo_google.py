#!/usr/bin/env python3
"""
Google Gemini演示脚本
展示如何在Presenton中使用Google Gemini
"""

import os
import sys
import asyncio
sys.path.insert(0, '.')

from services.llm_client import LLMClient
from models.llm_message import LLMUserMessage


async def demo_google_generation():
    """演示Google Gemini文本生成"""
    print("🎯 Google Gemini文本生成演示")
    print("-" * 40)

    # 设置环境变量
    os.environ['LLM'] = 'google'
    os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY', 'test_key')
    os.environ['GOOGLE_MODEL'] = 'gemini-1.5-flash'

    client = LLMClient()

    messages = [
        LLMUserMessage(content="请用中文详细介绍Google Gemini AI模型的特点和优势")
    ]

    print("📝 用户输入:", messages[0].content)
    print("\n🤖 AI回复:")

    if os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_API_KEY') != 'test_key':
        try:
            # 真实API调用
            response = await client.generate(
                model="gemini-1.5-flash",
                messages=messages,
                max_tokens=500
            )
            print(response)
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            print("💡 请检查API密钥是否正确")
    else:
        # 模拟回复
        print("Google Gemini是Google开发的最新一代AI模型，具有以下特点：")
        print("")
        print("🚀 核心特点：")
        print("• 多模态能力：支持文本、图片、视频等多种输入")
        print("• 强大的推理能力：可以进行复杂的逻辑推理")
        print("• 优秀的代码生成：支持多种编程语言")
        print("• 实时对话：支持流式响应")
        print("")
        print("💪 主要优势：")
        print("• Google官方支持，稳定可靠")
        print("• 每月15美元免费额度")
        print("• 低延迟，高响应速度")
        print("• 与Google生态系统深度集成")
        print("• 强大的多语言支持")
        print("")
        print("🔧 技术亮点：")
        print("• 基于Transformer架构优化")
        print("• 支持长上下文（可达数百万tokens）")
        print("• 内置安全性和可靠性保障")
        print("• 持续学习和模型更新")
        print("")
        print("(注: 这是一个模拟回复，请设置GOOGLE_API_KEY以获得真实响应)")


async def demo_google_models():
    """演示不同Google模型"""
    print("\n🎯 Google Gemini模型对比演示")
    print("-" * 40)

    models = [
        ("gemini-1.5-flash", "Gemini 1.5 Flash", "速度最快，成本最低"),
        ("gemini-1.5-pro", "Gemini 1.5 Pro", "高性能，功能最全"),
        ("gemini-pro", "Gemini Pro", "经典稳定版")
    ]

    messages = [
        LLMUserMessage(content="请用一句话概括人工智能的发展历程")
    ]

    for model, name, desc in models:
        print(f"\n🧠 {name}")
        print(f"   特点: {desc}")
        print(f"   模型ID: {model}")

        if os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_API_KEY') != 'test_key':
            try:
                client = LLMClient()
                response = await client.generate(
                    model=model,
                    messages=messages,
                    max_tokens=100
                )
                print(f"   💬 回复: {response}")
            except Exception as e:
                print(f"   ❌ 错误: {e}")
        else:
            if model == "gemini-1.5-flash":
                print("   💬 回复: 从图灵测试到深度学习，AI已从理论走向实用，深刻改变着人类社会")
            elif model == "gemini-1.5-pro":
                print("   💬 回复: 人工智能从20世纪50年代的理论萌芽，经历符号主义和连接主义的交替发展，到21世纪深度学习的突破，已成为推动科技进步的核心力量")
            else:  # gemini-pro
                print("   💬 回复: 人工智能的发展历程是从理论探索走向实用应用的华丽转身")


async def demo_google_code_generation():
    """演示Google代码生成能力"""
    print("\n🎯 Google Gemini代码生成演示")
    print("-" * 40)

    code_prompt = """
请用Python写一个简单的计算器函数，支持加减乘除运算。
要求：
1. 函数名为calculator
2. 参数为两个数字和一个运算符
3. 返回计算结果
4. 处理除零错误
"""

    messages = [
        LLMUserMessage(content=code_prompt)
    ]

    print("📝 代码生成任务:", code_prompt.strip())
    print("\n🤖 生成的代码:")

    if os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_API_KEY') != 'test_key':
        try:
            client = LLMClient()
            response = await client.generate(
                model="gemini-1.5-flash",
                messages=messages,
                max_tokens=300
            )
            print(response)
        except Exception as e:
            print(f"❌ 代码生成失败: {e}")
    else:
        # 模拟代码生成
        print("```python")
        print("def calculator(num1, num2, operator):")
        print("    \"\"\"")
        print("    简单计算器函数")
        print("    ")
        print("    Args:")
        print("        num1: 第一个数字")
        print("        num2: 第二个数字")
        print("        operator: 运算符 (+, -, *, /)")
        print("    ")
        print("    Returns:")
        print("        计算结果")
        print("    \"\"\"")
        print("    try:")
        print("        if operator == '+':")
        print("            return num1 + num2")
        print("        elif operator == '-':")
        print("            return num1 - num2")
        print("        elif operator == '*':")
        print("            return num1 * num2")
        print("        elif operator == '/':")
        print("            if num2 == 0:")
        print("                raise ValueError(\"除数不能为零\")")
        print("            return num1 / num2")
        print("        else:")
        print("            raise ValueError(f\"不支持的运算符: {operator}\")")
        print("    except Exception as e:")
        print("        return f\"计算错误: {e}\"")
        print("")
        print("# 使用示例")
        print("print(calculator(10, 5, '+'))  # 15")
        print("print(calculator(10, 5, '-'))  # 5")
        print("print(calculator(10, 5, '*'))  # 50")
        print("print(calculator(10, 0, '/'))  # 计算错误: 除数不能为零")
        print("```")
        print("")
        print("(注: 这是一个模拟代码示例，请设置GOOGLE_API_KEY以获得真实的AI生成代码)")


def show_usage_guide():
    """显示使用指南"""
    print("\n📚 Google Gemini使用指南")
    print("-" * 40)
    print("1. 获取API密钥:")
    print("   访问: https://makersuite.google.com/app/apikey")
    print("   登录Google账户并创建API密钥")
    print("")
    print("2. 配置环境变量:")
    print("   export LLM=google")
    print("   export GOOGLE_API_KEY=your_api_key_here")
    print("   export GOOGLE_MODEL=gemini-1.5-flash")
    print("")
    print("3. 或使用快速设置脚本:")
    print("   python quick_google_setup.py")
    print("")
    print("4. 测试配置:")
    print("   python test_google.py")
    print("")
    print("5. 启动Presenton:")
    print("   python start_v3_demo.py")
    print("")
    print("💡 价格信息:")
    print("• 每月免费额度: 15美元")
    print("• Gemini 1.5 Flash: $0.075/1M 输入, $0.30/1M 输出")
    print("• Gemini 1.5 Pro: $1.25/1M 输入, $5.00/1M 输出")


async def main():
    """主演示函数"""
    print("🚀 Presenton + Google Gemini 演示")
    print("=" * 60)
    print("   🤖 体验Google最先进的AI模型")
    print("   🎯 多模态能力，代码生成专家")
    print("   ⚡ 每月15美元免费额度")
    print("=" * 60)

    # 检查配置
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == 'test_key':
        print("⚠️  未检测到有效的GOOGLE_API_KEY")
        print("   演示将使用模拟数据")
        print("   如需真实体验，请运行:")
        print("   python quick_google_setup.py")
        print("")

    # 运行演示
    await demo_google_generation()
    await demo_google_models()
    await demo_google_code_generation()
    show_usage_guide()

    print("\n🎉 演示完成！")
    print("\n🔗 相关链接:")
    print("• Google AI Studio: https://makersuite.google.com/")
    print("• Gemini模型文档: https://ai.google.dev/docs")
    print("• 价格详情: https://ai.google.dev/pricing")
    print("")
    print("💪 Google Gemini的优势:")
    print("• 多模态AI，理解文本、图片、视频")
    print("• 优秀的编程和代码生成能力")
    print("• Google官方支持，稳定可靠")
    print("• 大量免费额度，降低使用成本")


if __name__ == "__main__":
    asyncio.run(main())

