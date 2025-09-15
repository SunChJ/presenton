#!/usr/bin/env python3
"""
OpenRouter演示脚本
展示如何在Presenton中使用OpenRouter
"""

import os
import sys
import asyncio
sys.path.insert(0, '.')

from services.llm_client import LLMClient
from models.llm_message import LLMUserMessage


async def demo_openrouter_generation():
    """演示OpenRouter文本生成"""
    print("🎯 OpenRouter文本生成演示")
    print("-" * 40)

    # 设置环境变量
    os.environ['LLM'] = 'openrouter'
    os.environ['OPENROUTER_API_KEY'] = os.getenv('OPENROUTER_API_KEY', 'test_key')
    os.environ['OPENROUTER_MODEL'] = 'anthropic/claude-3-haiku:beta'

    client = LLMClient()

    messages = [
        LLMUserMessage(content="请用中文简要介绍一下OpenRouter是什么，有什么优势？")
    ]

    print("📝 用户输入:", messages[0].content)
    print("\n🤖 AI回复:")

    try:
        if os.getenv('OPENROUTER_API_KEY') and os.getenv('OPENROUTER_API_KEY') != 'test_key':
            # 真实API调用
            response = await client.generate(
                model="anthropic/claude-3-haiku:beta",
                messages=messages,
                max_tokens=300
            )
            print(response)
        else:
            # 模拟回复
            print("OpenRouter是一个统一的AI模型API平台，支持来自不同提供商的20多种主流模型，")
            print("包括Anthropic Claude、OpenAI GPT系列、Google Gemini等。")
            print("")
            print("主要优势：")
            print("• 统一API接口，无需管理多个API密钥")
            print("• 支持负载均衡，自动选择最佳提供商")
            print("• 灵活的定价，按需选择模型")
            print("• 高可用性，单个提供商故障自动切换")
            print("")
            print("(注: 这是一个模拟回复，请设置OPENROUTER_API_KEY以获得真实响应)")

    except Exception as e:
        print(f"❌ 生成失败: {e}")


async def demo_openrouter_models():
    """演示不同模型的使用"""
    print("\n🎯 OpenRouter多模型演示")
    print("-" * 40)

    models = [
        ("anthropic/claude-3-haiku:beta", "Claude 3 Haiku (推荐)"),
        ("openai/gpt-4o-mini", "GPT-4o Mini"),
        ("google/gemini-flash-1.5", "Gemini Flash"),
        ("meta/llama-3.1-8b-instruct", "Llama 3.1 8B")
    ]

    messages = [
        LLMUserMessage(content="用一句话说明什么是机器学习")
    ]

    for model, name in models:
        print(f"\n🧠 {name}:")
        print(f"   模型: {model}")

        if os.getenv('OPENROUTER_API_KEY') and os.getenv('OPENROUTER_API_KEY') != 'test_key':
            try:
                client = LLMClient()
                response = await client.generate(
                    model=model,
                    messages=messages,
                    max_tokens=100
                )
                print(f"   回复: {response}")
            except Exception as e:
                print(f"   ❌ 错误: {e}")
        else:
            print("   💡 设置OPENROUTER_API_KEY以测试真实模型")


async def demo_openrouter_streaming():
    """演示流式生成"""
    print("\n🎯 OpenRouter流式生成演示")
    print("-" * 40)

    if not (os.getenv('OPENROUTER_API_KEY') and os.getenv('OPENROUTER_API_KEY') != 'test_key'):
        print("💡 设置OPENROUTER_API_KEY以测试流式生成")
        return

    client = LLMClient()
    messages = [
        LLMUserMessage(content="请写一段关于人工智能发展趋势的简短分析")
    ]

    print("📝 用户输入:", messages[0].content)
    print("\n🤖 AI流式回复:")
    print("-" * 20)

    try:
        async for chunk in client.stream(
            model="anthropic/claude-3-haiku:beta",
            messages=messages,
            max_tokens=200
        ):
            print(chunk, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"❌ 流式生成失败: {e}")


def show_pricing_info():
    """显示价格信息"""
    print("\n💰 OpenRouter模型价格参考 (USD/1M tokens)")
    print("-" * 50)

    pricing = [
        ("Claude 3 Haiku", "$0.25", "$1.25", "性价比最高"),
        ("GPT-4o Mini", "$0.15", "$0.60", "OpenAI最便宜"),
        ("Gemini Flash 1.5", "$0.075", "$0.30", "Google最便宜"),
        ("Claude 3.5 Sonnet", "$3.00", "$15.00", "高性能模型"),
        ("Llama 3.1 8B", "$0.00", "$0.00", "免费模型")
    ]

    print("<25"    print("-" * 50)
    for name, input_price, output_price, note in pricing:
        print("<25")

    print("\n💡 提示:")
    print("• 价格可能随时间变化，请以OpenRouter官网为准")
    print("• 免费额度通常有速率限制")
    print("• 企业用户可获得更好的价格")


async def main():
    """主演示函数"""
    print("🚀 Presenton + OpenRouter 演示")
    print("=" * 60)

    # 检查配置
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key or api_key == 'test_key':
        print("⚠️  未检测到有效的OPENROUTER_API_KEY")
        print("   演示将使用模拟数据")
        print("   如需真实测试，请运行:")
        print("   ./setup_openrouter.sh")
        print("")
    else:
        print("✅ OpenRouter API密钥已配置")
        print("   即将进行真实API调用测试")
        print("")

    # 运行演示
    await demo_openrouter_generation()
    await demo_openrouter_models()
    await demo_openrouter_streaming()
    show_pricing_info()

    print("\n🎉 演示完成！")
    print("\n📚 更多信息:")
    print("• OpenRouter官网: https://openrouter.ai/")
    print("• 完整配置指南: cat OPENROUTER_GUIDE.md")
    print("• 测试脚本: python test_openrouter.py")


if __name__ == "__main__":
    asyncio.run(main())
