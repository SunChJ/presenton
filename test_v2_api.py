#!/usr/bin/env python3
"""
V2 API测试脚本
用于验证Markdown转PPT功能是否正常工作
"""

import requests
import json

# API配置
BASE_URL = "http://localhost:8000"
V2_ENDPOINT = f"{BASE_URL}/api/v2/ppt/markdown-to-ppt/generate"

# 测试数据
test_markdown = """# AI技术发展趋势

## 人工智能概述
人工智能是当前最热门的技术领域之一，正在改变各行各业的工作方式。
从机器学习到深度学习，AI技术不断突破创新。

## 主要技术方向
- 机器学习：让机器从数据中学习模式
- 深度学习：模拟人脑神经网络的学习方式  
- 自然语言处理：让机器理解和生成人类语言
- 计算机视觉：让机器"看懂"图像和视频
- 强化学习：通过试错来优化决策

## 应用案例
成功案例包括：
智能客服系统提升了客户满意度
自动驾驶技术革新了交通出行
医疗AI辅助医生进行精准诊断

## 发展前景
未来AI将在更多领域发挥重要作用
预计到2030年，AI将创造更多就业机会

## 总结
AI技术的发展势不可挡，我们需要积极拥抱这一技术变革
关键是要在创新与安全之间找到平衡点

## 谢谢
感谢大家聆听，欢迎提问交流！
"""

def test_v2_api():
    """测试V2 API"""
    print("🚀 开始测试 V2 Markdown转PPT API...")
    print(f"📡 请求地址: {V2_ENDPOINT}")
    
    # 构建请求数据
    request_data = {
        "markdown_content": test_markdown,
        "template": "modern", 
        "language": "Chinese",
        "export_format": "pptx"
    }
    
    print("📝 请求数据:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    try:
        # 发送POST请求
        print("\n⏳ 发送API请求...")
        response = requests.post(
            V2_ENDPOINT,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # 60秒超时
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API请求成功!")
            print("📄 响应内容:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get("success"):
                print(f"\n🎉 PPT生成成功!")
                print(f"📁 演示文稿ID: {result.get('presentation_id')}")
                print(f"👀 预览链接: {BASE_URL}{result.get('preview_url')}")
                print(f"✏️ 编辑链接: {BASE_URL}{result.get('edit_url')}")
                print(f"⬇️ 下载链接: {BASE_URL}{result.get('download_url')}")
                print(f"📊 幻灯片数量: {result.get('slides_count')}")
                print(f"⏱️ 处理时间: {result.get('processing_time'):.2f}秒")
            else:
                print(f"❌ PPT生成失败: {result.get('message')}")
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
    print("🧪 Presenton V2 API 测试工具")
    print("=" * 60)
    
    # 先检查服务器状态
    if test_server_health():
        print("\n" + "=" * 60)
        # 服务器正常，开始API测试
        test_v2_api()
    else:
        print("\n💡 启动建议:")
        print("   cd servers/fastapi")
        print("   python server.py --port 8000")
    
    print("\n" + "=" * 60)
    print("🎯 测试完成!")