#!/bin/bash

# Conda环境下的FRP客户端启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🌐 启动FRP内网穿透服务（Conda环境）...${NC}"

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
echo -e "${YELLOW}📝 加载环境变量...${NC}"
set -a
source .env.local
set +a

# 检查frpc是否安装
if ! command -v frpc &> /dev/null; then
    echo -e "${RED}❌ FRP未安装，正在通过Brew安装...${NC}"
    brew install frp
fi

# 检查配置文件是否存在
if [ ! -f "frp/frpc.dev.ini" ]; then
    echo -e "${RED}❌ 配置文件不存在：frp/frpc.dev.ini${NC}"
    exit 1
fi

# 检查是否已经在运行
if pgrep -f "frpc.*frpc.dev.ini" > /dev/null; then
    echo -e "${YELLOW}⚠️ FRP客户端已在运行${NC}"
    ps aux | grep "frpc.*frpc.dev.ini" | grep -v grep
    echo -e "${YELLOW}如需重启，请先运行: pkill -f 'frpc.*frpc.dev.ini'${NC}"
    exit 1
fi

echo -e "${GREEN}"
echo "🚀 启动FRP内网穿透客户端..."
echo "🐍 Conda环境: presenton"
echo "📍 本地端口: 5001 (Nginx完整服务)"
echo "🌐 外网域名: http://ppt.samsoncj.xyz:8080"
echo "📊 FRP管理面板: http://93.179.115.189:7500"
echo "   用户名: admin"
echo "   密码: cs123456"
echo "🛑 停止服务: 按 Ctrl+C"
echo -e "${NC}"

# 启动FRP客户端
frpc -c frp/frpc.dev.ini