#!/bin/bash

# Conda环境下的Next.js前端启动脚本

set -e

# 颜色定义  
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🎨 启动Next.js前端服务（Conda环境）...${NC}"

# 检查conda环境
if ! conda env list | grep -q "^presenton "; then
    echo -e "${RED}❌ presenton conda环境不存在，请先运行: ./setup_conda_env.sh${NC}"
    exit 1
fi

# 激活conda环境
echo -e "${YELLOW}🐍 激活Conda环境...${NC}"
eval "$(conda shell.bash hook)"
conda activate presenton

# 检查环境配置
if [ ! -f ".env.local" ]; then
    echo -e "${RED}❌ 环境未配置，请先运行: ./setup_conda_env.sh${NC}"
    exit 1
fi

# 确保在项目根目录
cd "$(dirname "$0")"

# 加载环境变量
set -a
source .env.local 
set +a

# 检查并安装前端依赖
if [ ! -d "servers/nextjs/node_modules" ]; then
    echo -e "${YELLOW}📦 安装Node.js依赖...${NC}"
    cd servers/nextjs && npm install && cd ../..
    echo -e "${GREEN}✅ Node.js依赖安装完成${NC}"
fi

echo -e "${GREEN}"
echo "🚀 启动Next.js开发服务器..."
echo "🟢 Node.js环境: $(node --version)"
echo "📂 工作目录: $(pwd)"
echo "📍 服务地址: http://localhost:3001"
echo "🔄 热重载: 已启用"
echo "🛑 停止服务: 按 Ctrl+C"
echo -e "${NC}"

# 从项目根目录启动Next.js
echo "📂 切换到前端目录: servers/nextjs"
cd servers/nextjs && npm run dev -- -p 3001