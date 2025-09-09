#!/bin/bash

echo "🛑 停止开发环境..."

# 停止 nginx
echo "🌐 停止 nginx..."
sudo nginx -s stop 2>/dev/null && echo "✅ Nginx 已停止" || echo "⚠️  Nginx 可能未运行"

# 停止可能运行的 Node.js 进程
echo "🔄 查找并停止相关进程..."
pkill -f "node start.js" 2>/dev/null && echo "✅ Node.js 服务已停止" || echo "⚠️  未找到运行中的 Node.js 服务"

# 停止可能运行的 Python 服务
pkill -f "python.*server.py" 2>/dev/null && echo "✅ FastAPI 服务已停止" || echo "⚠️  未找到运行中的 FastAPI 服务"
pkill -f "python.*mcp_server.py" 2>/dev/null && echo "✅ MCP 服务已停止" || echo "⚠️  未找到运行中的 MCP 服务"

echo "🎯 开发环境已停止"