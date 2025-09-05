#!/usr/bin/env python3
"""
Quick test script for PPT Agent functionality
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test agent health"""
    print("🔍 Testing Agent Health...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/ppt/agent/test/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Status: {data['status']}")
            print(f"📊 Components: {data['components']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_intent_recognition():
    """Test intent recognition"""
    print("\n🧠 Testing Intent Recognition...")
    test_message = "创建一个关于机器学习的10页PPT"
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/ppt/agent/test/intent",
            params={"message": test_message}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Message: {data['message']}")
            print(f"🎯 Intent: {data['intent_type']}")
            print(f"📊 Confidence: {data['confidence']}")
            print(f"🔧 Parameters: {data['parameters']}")
            return True
        else:
            print(f"❌ Intent recognition failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Intent recognition error: {e}")
        return False

def test_basic_chat():
    """Test basic chat functionality"""
    print("\n💬 Testing Basic Chat...")
    
    payload = {
        "message": "你好，我想创建一个演示文稿",
        "session_id": "test-session-001"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/ppt/agent/chat/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response']}")
            print(f"🎯 Intent: {data['intent']}")
            print(f"⚡ Action Required: {data['action_required']}")
            return True
        else:
            print(f"❌ Basic chat failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Basic chat error: {e}")
        return False

def test_streaming_chat():
    """Test streaming chat (GPTs style)"""
    print("\n🌊 Testing Streaming Chat...")
    
    payload = {
        "message": "帮我创建一个关于人工智能的5页演示文稿",
        "session_id": "test-session-002"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/ppt/agent/chat/stream",
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True
        )
        
        if response.status_code == 200:
            print("✅ Streaming response received:")
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    if line.startswith("data: "):
                        content = line[6:]  # Remove "data: " prefix
                        if content == "[DONE]":
                            print("🏁 Stream completed!")
                            break
                        else:
                            print(f"📝 {content}")
            return True
        else:
            print(f"❌ Streaming chat failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Streaming chat error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting PPT Agent Verification Tests\n")
    
    tests = [
        ("Health Check", test_health),
        ("Intent Recognition", test_intent_recognition), 
        ("Basic Chat", test_basic_chat),
        ("Streaming Chat", test_streaming_chat)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        except KeyboardInterrupt:
            print("\n⏸️ Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Agent is working correctly.")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()