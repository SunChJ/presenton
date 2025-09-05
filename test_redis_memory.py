#!/usr/bin/env python3
"""
Test script for Redis conversation memory system
"""
import sys
import os
import asyncio

# Add FastAPI path to sys.path
sys.path.insert(0, os.path.join(os.getcwd(), "servers", "fastapi"))

# Set environment variables
os.environ["APP_DATA_DIRECTORY"] = "./app_data"
os.environ["TEMP_DIRECTORY"] = "./tmp/presenton"
os.environ["DATABASE_URL"] = "sqlite:///./app_data/presenton.db"

async def test_redis_memory():
    """Test Redis memory functionality"""
    print("🔄 Testing Redis Memory System")
    print("=" * 50)
    
    try:
        from services.agent.memory.memory_manager import get_memory_manager
        
        # Test with different Redis configurations
        test_cases = [
            ("Local Redis", "redis://localhost:6379", True),
            ("Invalid Redis", "redis://invalid-host:6379", True),
            ("No Redis (In-Memory)", None, False)
        ]
        
        for test_name, redis_url, use_redis in test_cases:
            print(f"\n📋 Testing: {test_name}")
            print("-" * 30)
            
            try:
                # Create manager for this test
                if redis_url:
                    os.environ["REDIS_URL"] = redis_url
                else:
                    os.environ.pop("REDIS_URL", None)
                
                manager = await get_memory_manager(
                    redis_url=redis_url,
                    use_redis=use_redis,
                    session_ttl=300  # 5 minutes for testing
                )
                
                memory = await manager.get_memory_instance()
                
                # Test basic functionality
                test_session = f"test_session_{test_name.lower().replace(' ', '_')}"
                
                print(f"📝 Storing interaction in session: {test_session}")
                await memory.store_interaction(
                    session_id=test_session,
                    user_message="Test message",
                    agent_response="Test response",
                    intent="TEST_INTENT",
                    parameters={"test": "value"}
                )
                
                print("📖 Retrieving context...")
                context = await memory.get_context(test_session, last_n=1)
                
                if context:
                    print(f"✅ Context retrieved: {len(context)} interactions")
                    print(f"   Last message: {context[-1]['user_message']}")
                    print(f"   Response: {context[-1]['agent_response']}")
                    print(f"   Intent: {context[-1]['intent']}")
                else:
                    print("❌ No context retrieved")
                
                # Get stats
                if hasattr(memory, 'get_session_stats'):
                    stats = await memory.get_session_stats()
                    print(f"📊 Memory Stats:")
                    print(f"   Storage Type: {stats.get('storage_type', 'unknown')}")
                    print(f"   Redis Connected: {stats.get('redis_connected', False)}")
                    if stats.get('redis_version'):
                        print(f"   Redis Version: {stats['redis_version']}")
                
                # Test session listing
                if hasattr(memory, 'get_active_sessions'):
                    sessions = await memory.get_active_sessions()
                    print(f"🗂️ Active Sessions: {len(sessions)}")
                
                # Cleanup
                print("🧹 Cleaning up test session...")
                await memory.clear_session(test_session)
                
                # Cleanup manager
                await manager.cleanup()
                
                print(f"✅ {test_name} test completed successfully")
                
            except Exception as e:
                print(f"❌ {test_name} test failed: {e}")
                import traceback
                print(f"   Error details: {traceback.format_exc()}")
        
        print(f"\n{'='*50}")
        print("🎉 Redis memory testing completed!")
        
    except Exception as e:
        print(f"❌ Redis memory testing failed: {e}")
        import traceback
        print(f"Error details: {traceback.format_exc()}")


async def test_agent_with_redis():
    """Test Agent with Redis memory"""
    print("\n🤖 Testing Agent with Redis Memory")
    print("=" * 50)
    
    try:
        from services.agent.core.ppt_agent import PPTAgent
        
        # Create agent
        agent = PPTAgent()
        await agent.initialize()
        
        print(f"✅ Agent initialized")
        print(f"   Memory type: {type(agent.memory).__name__}")
        
        # Test conversation
        test_session = "agent_redis_test"
        
        print(f"\n💬 Testing conversation in session: {test_session}")
        
        messages = [
            "你好",
            "创建一个关于AI的演示文稿", 
            "修改第2页",
            "导出为PDF"
        ]
        
        for i, message in enumerate(messages, 1):
            print(f"\n{i}. 用户: {message}")
            
            response = await agent.process_message(message, test_session)
            print(f"   Agent: {response.text[:100]}{'...' if len(response.text) > 100 else ''}")
            print(f"   Intent: {response.intent}")
            print(f"   Action Required: {response.action_required}")
        
        # Check conversation history
        print(f"\n📚 Checking conversation history...")
        context = await agent.memory.get_context(test_session)
        print(f"   Total interactions: {len(context)}")
        
        for i, interaction in enumerate(context):
            print(f"   {i+1}. {interaction['user_message']} -> {interaction['agent_response'][:50]}...")
        
        # Cleanup
        await agent.memory.clear_session(test_session)
        print(f"\n🧹 Test session cleaned up")
        
        print(f"✅ Agent + Redis memory test completed successfully")
        
    except Exception as e:
        print(f"❌ Agent + Redis memory test failed: {e}")
        import traceback
        print(f"Error details: {traceback.format_exc()}")


async def main():
    """Run all Redis memory tests"""
    print("🚀 Redis Conversation Memory Test Suite")
    print("=" * 60)
    
    await test_redis_memory()
    await test_agent_with_redis()
    
    print(f"\n{'='*60}")
    print("✨ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())