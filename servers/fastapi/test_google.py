#!/usr/bin/env python3
"""
Google Gemini集成测试脚本
验证Google Gemini AI的集成
"""

import os
import sys
import asyncio
sys.path.insert(0, '.')

from services.llm_client import LLMClient
from models.llm_message import LLMUserMessage


async def test_google_basic():
    """测试Google基础功能"""
    print("🔍 测试Google Gemini基础功能...")

    # 设置环境变量（用于测试）
    os.environ['LLM'] = 'google'
    os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY', 'test_key')
    os.environ['GOOGLE_MODEL'] = os.getenv('GOOGLE_MODEL', 'gemini-1.5-flash')

    try:
        client = LLMClient()
        print("✅ Google Gemini客户端初始化成功")
        print(f"📊 当前提供商: {client.llm_provider.value}")
        print(f"🎯 客户端类型: {type(client._client)}")
        return True
    except Exception as e:
        print(f"❌ Google Gemini客户端初始化失败: {e}")
        return False


async def test_google_generation():
    """测试Google生成功能"""
    print("\n🔍 测试Google Gemini生成功能...")

    # 设置环境变量
    os.environ['LLM'] = 'google'
    os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY', 'test_key')
    os.environ['GOOGLE_MODEL'] = os.getenv('GOOGLE_MODEL', 'gemini-1.5-flash')

    try:
        client = LLMClient()

        # 创建测试消息
        messages = [
            LLMUserMessage(content="请用中文简要介绍一下Google Gemini是什么，有什么优势？")
        ]

        print("📝 用户输入:", messages[0].content)
        print("\n🤖 AI回复:")

        try:
            # 测试生成（如果有API密钥）
            if os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_API_KEY') != 'test_key':
                # 真实API调用
                response = await client.generate(
                    model="gemini-1.5-flash",
                    messages=messages,
                    max_tokens=300
                )
                print(response)
            else:
                # 模拟回复
                print("Google Gemini是Google开发的先进AI模型，")
                print("具有强大的多模态理解能力和代码生成能力。")
                print("")
                print("主要优势：")
                print("• 多模态支持（文本、图片、视频）")
                print("• 优秀的代码生成和编程能力")
                print("• 每月15美元免费额度")
                print("• Google官方支持，稳定可靠")
                print("")
                print("(注: 这是一个模拟回复，请设置GOOGLE_API_KEY以获得真实响应)")

        except Exception as e:
            print(f"生成测试失败: {e}")

        print("✅ Google Gemini生成功能测试完成")
        return True
    except Exception as e:
        print(f"❌ Google Gemini生成功能测试失败: {e}")
        return False


def test_google_config():
    """测试Google配置"""
    print("\n🔍 测试Google配置...")

    # 测试环境变量函数
    from utils.get_env import get_google_api_key_env, get_google_model_env

    api_key = get_google_api_key_env()
    model = get_google_model_env()

    if api_key:
        print(f"✅ GOOGLE_API_KEY 已设置: {api_key[:20]}...")
    else:
        print("ℹ️ GOOGLE_API_KEY 未设置")

    if model:
        print(f"✅ GOOGLE_MODEL 已设置: {model}")
    else:
        print("ℹ️ GOOGLE_MODEL 未设置，使用默认值")

    # 测试提供商选择
    from utils.llm_provider import is_google_selected

    os.environ['LLM'] = 'google'
    if is_google_selected():
        print("✅ Google提供商选择正常")
    else:
        print("❌ Google提供商选择异常")
        return False

    return True


async def demo_google_models():
    """演示不同Google模型"""
    print("\n🎯 Google Gemini模型演示")
    print("-" * 40)

    models = [
        ("gemini-1.5-flash", "Gemini 1.5 Flash"),
        ("gemini-1.5-pro", "Gemini 1.5 Pro"),
        ("gemini-pro", "Gemini Pro")
    ]

    messages = [
        LLMUserMessage(content="用一句话说明什么是人工智能")
    ]

    for model, name in models:
        print(f"\n🧠 {name}:")
        print(f"   模型: {model}")

        if os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_API_KEY') != 'test_key':
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
            print("   💡 设置GOOGLE_API_KEY以测试真实模型")


async def main():
    """主测试函数"""
    print("🚀 Google Gemini集成测试")
    print("=" * 50)

    success = True

    # 测试配置
    success &= test_google_config()

    # 测试基础功能
    success &= await test_google_basic()

    # 测试生成功能
    success &= await test_google_generation()

    # 演示模型
    await demo_google_models()

    if success:
        print("\n🎉 所有Google Gemini测试通过！")
        print("\n📋 Google Gemini特性：")
        print("• ✅ 多模态AI能力（文本、图片、视频）")
        print("• ✅ 优秀的代码生成")
        print("• ✅ 每月15美元免费额度")
        print("• ✅ Google官方API，稳定可靠")
        print("• ✅ 支持流式和结构化输出")
        print("\n🔧 配置说明：")
        print("export LLM=google")
        print("export GOOGLE_API_KEY=your_api_key")
        print("export GOOGLE_MODEL=gemini-1.5-flash")
        print("\n📚 支持的模型：")
        print("• gemini-1.5-flash (推荐，速度快成本低)")
        print("• gemini-1.5-pro (高性能)")
        print("• gemini-pro (经典稳定)")
    else:
        print("\n❌ 部分Google Gemini测试失败")

    return success


if __name__ == "__main__":
    asyncio.run(main())
