#!/bin/bash

# Stop Production - Conda Environment
# 停止生产模式服务

echo "🛑 停止生产模式服务..."
echo "================================"

# 停止服务函数
stop_service() {
    local port=$1
    local service_name=$2
    if lsof -ti:$port > /dev/null 2>&1; then
        echo "🔴 停止 $service_name (端口 $port)..."
        lsof -ti:$port | xargs kill -9
        sleep 1
        echo "✅ $service_name 已停止"
    else
        echo "ℹ️  $service_name 未运行"
    fi
}

# 停止Nginx
echo "🌐 停止Nginx..."
sudo nginx -s quit > /dev/null 2>&1 || echo "ℹ️  Nginx未运行或已停止"

# 停止各服务
stop_service 8000 "FastAPI"
stop_service 3001 "Next.js"
stop_service 5001 "Nginx"

# 清理日志文件
echo "🧹 清理日志文件..."
rm -f /tmp/fastapi-prod.log
rm -f /tmp/nextjs-prod.log
rm -f /tmp/nginx-prod-$(whoami).conf

echo "✅ 所有生产服务已停止"