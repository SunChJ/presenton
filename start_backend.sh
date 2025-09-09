#!/bin/bash

# FastAPI后端启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}⚙️ 启动FastAPI后端服务...${NC}"

# 检查环境配置
if [ ! -f ".env.local" ]; then
    echo "❌ 环境未配置，请先运行: ./setup_env.sh"
    exit 1
fi

# 加载环境变量
set -a
source .env.local
set +a

# 进入后端目录
cd servers/fastapi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ Python虚拟环境不存在，请先运行: ./setup_env.sh"
    exit 1
fi

# 激活虚拟环境
echo -e "${YELLOW}激活Python虚拟环境...${NC}"
source venv/bin/activate

echo -e "${GREEN}"
echo "🚀 启动FastAPI服务器..."
echo "📍 服务地址: http://localhost:8000"
echo "📋 API文档: http://localhost:8000/docs"
echo "🛑 停止服务: 按 Ctrl+C"
echo -e "${NC}"

# 启动服务器
python server.py --port 8000