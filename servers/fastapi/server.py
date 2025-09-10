import uvicorn
import argparse
import debugpy
import os

# Only enable debugpy if explicitly requested
if os.getenv("ENABLE_DEBUGPY") == "true":
    try:
        debugpy.listen(5678)
        print("等待调试器连接...")
        debugpy.wait_for_client()  # 可选，等待调试器连接后再继续
    except RuntimeError as e:
        if "Address already in use" in str(e):
            print("调试器端口已被占用，尝试连接到现有调试器...")
            # 如果端口被占用，说明VSCode已经在监听，我们可以继续运行
            pass
        else:
            raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the FastAPI server")
    parser.add_argument(
        "--port", type=int, required=True, help="Port number to run the server on"
    )
    parser.add_argument(
        "--reload", type=str, default="false", help="Reload the server on code changes"
    )
    args = parser.parse_args()
    reload = args.reload == "true"
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=args.port,
        log_level="info",
        reload=reload,
    )
