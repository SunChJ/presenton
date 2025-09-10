import uvicorn
import argparse
import debugpy

debugpy.listen(5678)
print("等待调试器连接...")
debugpy.wait_for_client()  # 可选，等待调试器连接后再继续

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
