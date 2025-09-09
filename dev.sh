#!/bin/bash

set -e

echo "🚀 启动 Presenton 开发环境..."

# 检查 nginx 是否安装
if ! command -v nginx &> /dev/null; then
    echo "❌ nginx 未安装，请先安装:"
    echo "   macOS: brew install nginx"
    echo "   Linux: sudo apt install nginx"
    exit 1
fi

# 获取当前目录
CURRENT_DIR=$(pwd)

# 检查是否在正确的目录
if [ ! -f "nginx-dev.conf" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

echo "📁 当前目录: $CURRENT_DIR"

# 停止可能已经运行的 nginx
echo "🔄 停止现有的 nginx 进程..."
sudo nginx -s stop 2>/dev/null || true

# 等待一下确保端口释放
sleep 2

# 检查端口是否被占用
if lsof -i :5000 > /dev/null 2>&1; then
    echo "⚠️  端口 5000 被占用，请释放后重试"
    exit 1
fi

# 启动 nginx (开发配置)
echo "🌐 启动 nginx (端口 5000)..."
sudo nginx -c "$CURRENT_DIR/nginx-dev.conf"

# 验证 nginx 启动成功
if ! curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo "✅ Nginx 已启动"
else
    echo "⚠️  Nginx 启动成功但服务尚未完全就绪"
fi

echo ""
echo "🎯 接下来启动应用服务器..."
echo "📝 请在另一个终端运行: node start.js --dev"
echo ""
echo "🌟 完成后访问: http://localhost:5000"
echo ""
echo "🛑 停止 nginx: sudo nginx -s stop"