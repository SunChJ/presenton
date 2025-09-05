#!/usr/bin/env python3
"""
Environment setup script for Presenton PPT Agent
Based on Dockerfile configuration
"""
import os
import sys
import shutil
from pathlib import Path


def setup_directories():
    """Setup required directories based on Dockerfile ENV settings"""
    print("📁 Setting up directories...")
    
    # Based on Dockerfile ENV settings
    app_data_dir = os.getenv("APP_DATA_DIRECTORY", "./app_data")
    temp_dir = os.getenv("TEMP_DIRECTORY", "/tmp/presenton")
    
    directories = [
        app_data_dir,
        temp_dir,
        f"{app_data_dir}/exports",
        f"{app_data_dir}/images", 
        f"{app_data_dir}/user_data",
        f"{app_data_dir}/fonts",
        f"{temp_dir}/uploads"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, mode=0o755, exist_ok=True)
            print(f"✅ Created/verified directory: {directory}")
        except PermissionError as e:
            print(f"⚠️ Permission issue with {directory}, trying alternative...")
            # Try alternative location for temp directory
            if directory.startswith("/tmp"):
                alt_dir = directory.replace("/tmp", "./tmp")
                os.makedirs(alt_dir, mode=0o755, exist_ok=True)
                os.environ["TEMP_DIRECTORY"] = alt_dir
                print(f"✅ Created alternative directory: {alt_dir}")
            else:
                print(f"❌ Failed to create {directory}: {e}")


def setup_environment_variables():
    """Setup environment variables based on Dockerfile"""
    print("🌍 Setting up environment variables...")
    
    env_vars = {
        "APP_DATA_DIRECTORY": "./app_data",
        "TEMP_DIRECTORY": "./tmp/presenton", 
        "PYTHONPATH": f"{os.getcwd()}/servers/fastapi",
        # Default LLM settings for testing
        "LLM": "openai",
        "CAN_CHANGE_KEYS": "true",
        "DISABLE_ANONYMOUS_TELEMETRY": "true"
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
            print(f"✅ Set {key}={value}")
        else:
            print(f"ℹ️ {key} already set to {os.environ[key]}")


def setup_python_path():
    """Setup Python path for imports"""
    print("🐍 Setting up Python path...")
    
    fastapi_path = os.path.join(os.getcwd(), "servers", "fastapi")
    if os.path.exists(fastapi_path):
        if fastapi_path not in sys.path:
            sys.path.insert(0, fastapi_path)
            print(f"✅ Added to Python path: {fastapi_path}")
        else:
            print(f"ℹ️ Already in Python path: {fastapi_path}")
    else:
        print(f"❌ FastAPI directory not found: {fastapi_path}")


def check_dependencies():
    """Check if required Python packages are installed"""
    print("📦 Checking Python dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "sqlmodel",
        "aiohttp",
        "asyncpg",
        "pydantic"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True


def create_minimal_config():
    """Create minimal configuration files if needed"""
    print("⚙️ Creating minimal configuration...")
    
    # Create a minimal database URL for SQLite
    db_path = os.path.join(os.environ.get("APP_DATA_DIRECTORY", "./app_data"), "presenton.db")
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    print(f"✅ Set DATABASE_URL to: sqlite:///{db_path}")
    
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)


def verify_agent_imports():
    """Verify that our Agent imports work correctly"""
    print("🤖 Verifying Agent imports...")
    
    try:
        # Add the FastAPI path to sys.path
        setup_python_path()
        
        # Change to fastapi directory for asset resolution
        original_cwd = os.getcwd()
        fastapi_dir = os.path.join(original_cwd, "servers", "fastapi")
        
        if os.path.exists(fastapi_dir):
            os.chdir(fastapi_dir)
            print(f"✅ Changed to FastAPI directory: {fastapi_dir}")
        
        try:
            # Test basic imports
            from services.agent.core.ppt_agent import PPTAgent
            from services.agent.intent.recognizer import IntentRecognizer
            from services.agent.memory.conversation_memory import ConversationMemory
            
            print("✅ Agent core imports successful")
            
            # Test agent instantiation (skip for now due to dependencies)
            # agent = PPTAgent()
            # print("✅ Agent instantiation successful")
            
            print("✅ Agent import verification successful (instantiation skipped)")
            return True
            
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Agent verification error: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Presenton Environment Setup")
    print("=" * 50)
    
    # Change to project root if we're not there
    if not os.path.exists("servers/fastapi"):
        if os.path.exists("../servers/fastapi"):
            os.chdir("..")
        else:
            print("❌ Cannot find servers/fastapi directory")
            sys.exit(1)
    
    try:
        # Setup steps
        setup_environment_variables()
        setup_directories()
        setup_python_path()
        create_minimal_config()
        
        # Verification steps
        if not check_dependencies():
            print("\n❌ Dependency check failed")
            sys.exit(1)
            
        if not verify_agent_imports():
            print("\n❌ Agent verification failed")
            sys.exit(1)
        
        print("\n" + "=" * 50)
        print("🎉 Environment setup completed successfully!")
        print("\nYou can now run:")
        print("  python test_agent.py")
        print("  or")
        print("  cd servers/fastapi && python server.py --port 8000")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()