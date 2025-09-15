#!/usr/bin/env python3
"""
V3版本演示启动脚本
快速启动V3版本的演示服务
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def check_environment():
    """检查环境配置 - 仅Google Gemini"""
    print("🔍 检查环境配置...")

    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 11):
        print(f"❌ 需要Python 3.11+，当前版本: {python_version.major}.{python_version.minor}")
        return False

    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")

    # 检查Google配置
    print("\n🔍 检查Google Gemini配置...")

    # 检查LLM提供商
    llm_provider = os.getenv('LLM', '').lower()
    if llm_provider != 'google':
        print(f"⚠️  当前LLM提供商: {llm_provider}")
        print("   建议设置为: google")
        print("   自动设置为Google...")
        os.environ['LLM'] = 'google'

    # 检查Google API密钥
    google_key = os.getenv('GOOGLE_API_KEY')
    if not google_key:
        print("❌ 缺少Google API密钥")
        print("请设置环境变量:")
        print("   export GOOGLE_API_KEY=your-google-api-key")
        print("或在.env文件中添加:")
        print("   GOOGLE_API_KEY=your-google-api-key")
        print("")
        print("获取Google API密钥:")
        print("1. 访问: https://makersuite.google.com/app/apikey")
        print("2. 创建新的API密钥")
        print("3. 复制密钥并设置到环境变量")
        return False

    print("✅ Google API密钥已配置")

    # 检查Google模型
    google_model = os.getenv('GOOGLE_MODEL', 'gemini-1.5-flash')
    print(f"✅ 使用模型: {google_model}")

    return True

def test_v3_imports():
    """测试V3模块导入"""
    print("\n🔍 测试V3模块导入...")

    try:
        sys.path.insert(0, '.')
        from api.v3.router import V3_ROUTER
        from api.v3.services.enhanced_agent import V3EnhancedAgent
        from api.v3.services.content_search import ContentSearchService
        from api.v3.services.html_design_expert import HTMLDesignExpert
        from api.v3.services.dsl_generator import DSLGenerator
        print("✅ 所有V3模块导入成功")
        return True
    except Exception as e:
        print(f"❌ V3模块导入失败: {e}")
        return False

def start_server(port=8000):
    """启动服务器"""
    print(f"\n🚀 启动V3演示服务器 (端口: {port})...")

    try:
        # 设置环境变量
        env = os.environ.copy()
        env['PYTHONPATH'] = '.'

        # 启动服务器
        cmd = [sys.executable, 'server.py', '--port', str(port)]
        print(f"执行命令: {' '.join(cmd)}")

        process = subprocess.Popen(
            cmd,
            cwd=os.getcwd(),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

        # 等待服务器启动
        time.sleep(3)

        if process.poll() is None:
            print(f"\n🎉 服务器启动成功！")
            print(f"🌐 访问地址: http://localhost:{port}")
            print(f"📚 API文档: http://localhost:{port}/docs")
            print(f"🔄 V3 API文档: http://localhost:{port}/docs#/V3")
            print(f"\n🤖 当前配置:")
            print(f"   LLM提供商: Google Gemini")
            print(f"   模型: {os.getenv('GOOGLE_MODEL', 'gemini-1.5-flash')}")
            print(f"   API密钥: {os.getenv('GOOGLE_API_KEY', '已配置')[:20]}...")
            print(f"\n📋 可用的V3 API端点:")
            print("• POST /api/v3/ppt/presentation/generate - 基础生成")
            print("• POST /api/v3/ppt/streaming/generate - 流式生成")
            print("• POST /api/v3/ppt/presentation/step - 单步执行")
            print(f"\n💡 测试命令:")
            print(f"   curl -X POST http://localhost:{port}/api/v3/ppt/presentation/generate \\")
            print("        -H \"Content-Type: application/json\" \\")
            print("        -d '{\"user_input\": \"人工智能发展趋势\", \"template\": \"modern\"}'")
            print("\n按 Ctrl+C 停止服务器")
            return process
        else:
            print("❌ 服务器启动失败")
            return None

    except Exception as e:
        print(f"❌ 启动服务器时出错: {e}")
        return None

def main():
    """主函数 - Google Gemini专用版本"""
    print("🎯 Presenton V3 + Google Gemini 演示启动器")
    print("=" * 60)
    print("   🚀 专门为Google Gemini优化的启动脚本")
    print("   🤖 强大的多模态AI模型")
    print("   ⚡ Google官方API，稳定可靠")
    print("=" * 60)

    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请修复配置后重试")
        return

    # 测试V3导入
    if not test_v3_imports():
        print("\n❌ V3模块测试失败，请检查代码")
        return

    # 启动服务器
    port = int(os.getenv('PORT', 8000))
    process = start_server(port)

    if process:
        try:
            # 等待用户中断
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 正在停止服务器...")
            process.terminate()
            process.wait()
            print("✅ 服务器已停止")
    else:
        print("\n❌ 无法启动服务器")

if __name__ == "__main__":
    main()
