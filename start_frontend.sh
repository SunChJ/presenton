#!/bin/bash

# Next.js前端启动脚本

set -e

# 颜色定义  
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🎨 启动Next.js前端服务...${NC}"

# 检查环境配置
if [ ! -f ".env.local" ]; then
    echo "❌ 环境未配置，请先运行: ./setup_env.sh"
    exit 1
fi

# 加载环境变量
set -a
source .env.local 
set +a

# 进入前端目录
cd servers/nextjs

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "❌ Node.js依赖不存在，正在安装..."
    npm install
fi

# 检查Next.js是否安装
if [ ! -f "node_modules/.bin/next" ]; then
    echo "❌ Next.js未正确安装，重新安装依赖..."
    rm -rf node_modules package-lock.json
    npm install
fi

echo -e "${GREEN}"
echo "🚀 启动Next.js开发服务器..."
echo "📂 当前目录: $(pwd)"
echo "📍 服务地址: http://localhost:3001"
echo "🔄 热重载: 已启用"
echo "🛑 停止服务: 按 Ctrl+C"
echo -e "${NC}"

# 启动开发服务器 - 使用完整路径
./node_modules/.bin/next dev -p 3001