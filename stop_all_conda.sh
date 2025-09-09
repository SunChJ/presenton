#!/bin/bash

# 停止所有Conda环境下的服务

set -e

echo "🛑 停止所有Presenton服务..."

# 停止Python进程
echo "停止FastAPI服务..."
pkill -f "python server.py" || true

# 停止Node.js进程  
echo "停止Next.js服务..."
pkill -f "npm run dev" || true
pkill -f "next dev" || true

# 停止FRP客户端
echo "停止FRP客户端..."
pkill -f "frpc" || true

echo "✅ 所有服务已停止"

# 显示剩余相关进程
echo "📊 检查剩余进程："
ps aux | grep -E "(python server.py|npm run dev|next dev|frpc)" | grep -v grep || echo "  无相关进程运行"