#!/usr/bin/env python3
"""
V3 API测试脚本
用于验证V3版本的演示文稿生成功能
"""

import requests
import json
import time

# API配置
BASE_URL = "http://localhost:8000"
V3_ENDPOINT = f"{BASE_URL}/api/v3/ppt/presentation/generate"
V3_STREAMING_ENDPOINT = f"{BASE_URL}/api/v3/ppt/streaming/generate"

# 测试数据
test_user_input = """
我想制作一个关于人工智能技术发展趋势的演示文稿，包括以下内容：
1. AI技术概述和发展历程
2. 当前主要技术方向（机器学习、深度学习、自然语言处理等）
3. 应用案例和成功故事
4. 未来发展趋势和挑战
5. 总结和建议
"""

def test_v3_api():
    """测试V3 API"""
    print("🚀 开始测试 V3 演示文稿生成 API...")
    print(f"📡 请求地址: {V3_ENDPOINT}")
    
    # 构建请求数据
    request_data = {
        "user_input": test_user_input,
        "template": "modern",
        "language": "Chinese",
        "n_slides": 5,
        "enable_search": True,
        "export_format": "html",
        "custom_instructions": "请生成专业、美观的演示文稿"
    }
    
    print("📝 请求数据:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    try:
        # 发送POST请求
        print("\n⏳ 发送API请求...")
        response = requests.post(
            V3_ENDPOINT,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2分钟超时
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API请求成功!")
            print("📄 响应内容:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("success"):
                print(f"\n🎉 演示文稿生成成功!")
                print(f"📁 演示文稿ID: {result.get('presentation_id')}")
                print(f"📝 标题: {result.get('title')}")
                print(f"📊 幻灯片数量: {result.get('slides_count')}")
                print(f"👀 预览链接: {BASE_URL}{result.get('preview_url')}")
                print(f"✏️ 编辑链接: {BASE_URL}{result.get('edit_url')}")
                print(f"⬇️ 下载链接: {BASE_URL}{result.get('download_url')}")
                print(f"⏱️ 处理时间: {result.get('processing_time'):.2f}秒")
                print(f"📋 完成步骤: {', '.join(result.get('steps_completed', []))}")
            else:
                print(f"❌ 演示文稿生成失败: {result.get('message')}")
                print(f"🔍 错误详情: {result.get('error_details')}")
        
        else:
            print(f"❌ API请求失败!")
            print(f"📄 错误响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 无法连接到服务器")
        print("💡 请确认FastAPI服务器是否在运行 (python server.py --port 8000)")
        
    except requests.exceptions.Timeout:
        print("⏰ 请求超时: API响应时间过长")
        
    except Exception as e:
        print(f"💥 未知错误: {str(e)}")


def test_v3_streaming():
    """测试V3流式API"""
    print("\n🌊 开始测试 V3 流式生成 API...")
    print(f"📡 请求地址: {V3_STREAMING_ENDPOINT}")
    
    # 构建请求数据
    request_data = {
        "user_input": test_user_input,
        "template": "modern",
        "language": "Chinese",
        "enable_search": True
    }
    
    try:
        print("⏳ 发送流式API请求...")
        response = requests.post(
            V3_STREAMING_ENDPOINT,
            json=request_data,
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=120
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 流式API请求成功!")
            print("📄 流式响应内容:")
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # 移除 'data: ' 前缀
                        if data_str == '[DONE]':
                            print("🏁 流式生成完成!")
                            break
                        try:
                            data = json.loads(data_str)
                            print(f"📋 步骤: {data.get('step')} | 状态: {data.get('status')} | 进度: {data.get('progress')}% | 消息: {data.get('message')}")
                        except json.JSONDecodeError:
                            print(f"📄 原始数据: {data_str}")
        else:
            print(f"❌ 流式API请求失败!")
            print(f"📄 错误响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 无法连接到服务器")
        
    except requests.exceptions.Timeout:
        print("⏰ 请求超时: 流式API响应时间过长")
        
    except Exception as e:
        print(f"💥 未知错误: {str(e)}")


def test_server_health():
    """测试服务器健康状态"""
    print("🏥 检查服务器状态...")
    
    try:
        # 检查根路径
        health_response = requests.get(f"{BASE_URL}/docs", timeout=10)
        if health_response.status_code == 200:
            print("✅ 服务器运行正常")
            return True
        else:
            print(f"⚠️ 服务器响应异常: {health_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        return False
    except Exception as e:
        print(f"❌ 服务器检查失败: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Presenton V3 API 测试工具")
    print("=" * 60)
    
    # 先检查服务器状态
    if test_server_health():
        print("\n" + "=" * 60)
        # 服务器正常，开始API测试
        test_v3_api()
        
        print("\n" + "=" * 60)
        # 测试流式API
        test_v3_streaming()
    else:
        print("\n💡 启动建议:")
        print("   cd servers/fastapi")
        print("   python server.py --port 8000")
    
    print("\n" + "=" * 60)
    print("🎯 V3 API测试完成!")
