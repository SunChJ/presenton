#!/bin/bash

# FRP客户端启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 确保在项目根目录
cd "$(dirname "$0")"

echo -e "${YELLOW}🌐 启动FRP客户端...${NC}"

# 检查是否通过Brew安装了frp
if ! command -v frpc &> /dev/null; then
    echo -e "${RED}❌ FRP未安装，正在通过Brew安装...${NC}"
    brew install frp
fi

# 检查配置文件是否存在
if [ ! -f "frp/frpc.manual.ini" ]; then
    echo -e "${RED}❌ 配置文件不存在：frp/frpc.manual.ini${NC}"
    exit 1
fi

# 检查是否已经在运行
if pgrep -f "frpc.*frpc.manual.ini" > /dev/null; then
    echo -e "${YELLOW}⚠️ FRP客户端已在运行${NC}"
    ps aux | grep "frpc.*frpc.manual.ini" | grep -v grep
    exit 1
fi

echo -e "${GREEN}"
echo "🚀 启动FRP客户端..."
echo "📍 本地端口: 8000 (FastAPI后端API)"
echo "🌐 外网域名: http://ppt.samsoncj.xyz:8080"
echo "📊 FRP管理面板: http://93.179.115.189:7500"
echo "   用户名: admin"
echo "   密码: cs123456"
echo "🛑 停止服务: 按 Ctrl+C"
echo -e "${NC}"

# 启动FRP客户端
frpc -c frp/frpc.manual.ini