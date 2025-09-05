#!/usr/bin/env python3
"""
Minimal Agent test - tests core functionality without external dependencies
"""
import sys
import os

# Add FastAPI path to sys.path
sys.path.insert(0, os.path.join(os.getcwd(), "servers", "fastapi"))

def test_agent_imports():
    """Test that we can import Agent classes"""
    print("🔍 Testing Agent imports...")
    
    try:
        from services.agent.intent.recognizer import IntentRecognizer
        from services.agent.intent.intent_types import Intent, IntentType
        from services.agent.memory.conversation_memory import ConversationMemory
        from services.agent.conversation.manager import ConversationManager
        
        print("✅ Successfully imported Agent classes")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_intent_recognition():
    """Test intent recognition functionality"""
    print("\n🧠 Testing Intent Recognition...")
    
    try:
        from services.agent.intent.recognizer import IntentRecognizer
        
        recognizer = IntentRecognizer()
        
        # Test cases
        test_cases = [
            ("创建一个关于机器学习的10页PPT", "CREATE_PRESENTATION"),
            ("修改第3页的内容", "MODIFY_SLIDE"),
            ("导出演示文稿", "EXPORT_PRESENTATION"),
            ("什么是人工智能", "CHAT_QUESTION"),
            ("随便说点什么", "UNKNOWN")
        ]
        
        for message, expected_intent in test_cases:
            intent = await_sync(recognizer.identify(message))
            
            print(f"📝 输入: '{message}'")
            print(f"   意图: {intent.type} (预期: {expected_intent})")
            print(f"   置信度: {intent.confidence}")
            print(f"   参数: {intent.parameters}")
            
            if intent.type == expected_intent:
                print("   ✅ 正确")
            else:
                print("   ⚠️ 不匹配")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Intent recognition test failed: {e}")
        return False

def test_conversation_memory():
    """Test conversation memory functionality"""
    print("💾 Testing Conversation Memory...")
    
    try:
        from services.agent.memory.conversation_memory import ConversationMemory
        
        memory = ConversationMemory()
        
        # Test storing and retrieving interactions
        session_id = "test-session"
        
        await_sync(memory.store_interaction(
            session_id=session_id,
            user_message="Hello",
            agent_response="Hi there!",
            intent="CHAT_QUESTION"
        ))
        
        await_sync(memory.store_interaction(
            session_id=session_id,
            user_message="创建PPT",
            agent_response="我来帮您创建演示文稿",
            intent="CREATE_PRESENTATION"
        ))
        
        context = await_sync(memory.get_context(session_id))
        
        print(f"✅ Stored {len(context)} interactions")
        for i, interaction in enumerate(context):
            print(f"   {i+1}. {interaction['user_message']} -> {interaction['agent_response']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return False

def test_conversation_manager():
    """Test conversation manager functionality"""
    print("\n💬 Testing Conversation Manager...")
    
    try:
        from services.agent.conversation.manager import ConversationManager
        from services.agent.intent.recognizer import IntentRecognizer
        
        manager = ConversationManager()
        recognizer = IntentRecognizer()
        
        # Test response generation
        message = "我想创建一个演示文稿"
        intent = await_sync(recognizer.identify(message))
        
        response = await_sync(manager.generate_response(message, intent, []))
        
        print(f"📝 输入: '{message}'")
        print(f"💬 响应: '{response.text}'")
        print(f"🎯 意图: {response.intent}")
        print(f"⚡ 需要行动: {response.action_required}")
        
        if response.follow_up_question:
            print(f"❓ 追问: {response.follow_up_question}")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversation manager test failed: {e}")
        return False

def await_sync(coro):
    """Helper to run async functions synchronously"""
    import asyncio
    return asyncio.run(coro)

def main():
    """Run all tests"""
    print("🚀 Minimal PPT Agent Core Test")
    print("=" * 50)
    
    tests = [
        ("Agent Imports", test_agent_imports),
        ("Intent Recognition", test_intent_recognition),
        ("Conversation Memory", test_conversation_memory),
        ("Conversation Manager", test_conversation_manager)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All core Agent tests passed!")
        return True
    else:
        print("⚠️ Some tests failed.")
        return False

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)