#!/bin/bash

# 停止Presenton本地服务脚本

echo "🛑 停止Presenton本地服务..."

# 停止FRP容器
echo "停止FRP容器..."
docker-compose -f docker-compose.frp-only.yml down

# 停止可能运行的进程
echo "停止Python和Node.js进程..."
pkill -f "python server.py"
pkill -f "next dev"
pkill -f "npm run dev"

# 停止Nginx（如果存在）
if pgrep nginx > /dev/null; then
    echo "停止Nginx..."
    sudo nginx -s stop 2>/dev/null || true
fi

echo "✅ 所有服务已停止"