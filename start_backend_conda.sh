#!/bin/bash

# Conda环境下的FastAPI后端启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}⚙️ 启动FastAPI后端服务（Conda环境）...${NC}"

# 引入端口清理工具
source ./check_and_kill_port.sh

# 清理8000端口
check_and_kill_port 8000 "FastAPI后端服务"

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

# 加载环境变量
echo -e "${YELLOW}📝 加载环境变量...${NC}"
set -a
source .env.local
set +a

# 配置用户配置文件路径
export USER_CONFIG_PATH="${PWD}/app_data/userConfig.json"
echo -e "${YELLOW}📄 用户配置文件路径: $USER_CONFIG_PATH${NC}"

# 确保在项目根目录
cd "$(dirname "$0")"

# 确保数据目录存在
echo -e "${YELLOW}📁 创建必要目录...${NC}"
mkdir -p app_data
mkdir -p /tmp/presenton

# 设置Python路径，让FastAPI能找到模块
export PYTHONPATH="${PWD}/servers/fastapi:$PYTHONPATH"

echo -e "${GREEN}"
echo "🚀 启动FastAPI服务器..."
echo "🐍 Python环境: $(python --version)"
echo "📂 工作目录: $(pwd)"
echo "📍 服务地址: http://localhost:8000"
echo "📋 API文档: http://localhost:8000/docs"
echo "🛑 停止服务: 按 Ctrl+C"
echo -e "${NC}"

# 从项目根目录启动，这样相对路径就正确了
python servers/fastapi/server.py --port 8000