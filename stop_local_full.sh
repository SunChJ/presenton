#!/bin/bash
echo "🛑 停止Presenton本地服务..."

# 停止可能运行的进程
echo "停止Python和Node.js进程..."
pkill -f "python server.py"
pkill -f "npm run dev"
pkill -f "next dev"

# 停止Nginx
if pgrep nginx > /dev/null; then
    echo "停止Nginx..."
    sudo nginx -s stop 2>/dev/null || true
fi

echo "✅ 所有服务已停止"
