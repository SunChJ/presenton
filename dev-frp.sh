#!/bin/bash

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🚀 启动开发环境 + FRP 内网穿透${NC}"

# 确保在项目根目录
cd "$(dirname "$0")"

# 检查 nginx 是否安装
if ! command -v nginx &> /dev/null; then
    echo -e "${RED}❌ nginx 未安装，请先安装: brew install nginx${NC}"
    exit 1
fi

# 检查 frpc 是否安装
if ! command -v frpc &> /dev/null; then
    echo -e "${RED}❌ FRP未安装，正在通过Brew安装...${NC}"
    brew install frp
fi

# 停止现有的 nginx 和 frpc
echo -e "${YELLOW}🔄 停止现有服务...${NC}"
sudo nginx -s stop 2>/dev/null || true
pkill -f "frpc.*frpc" 2>/dev/null || true
sleep 2

# 启动 nginx
echo -e "${YELLOW}🌐 启动 Nginx (端口 5000)...${NC}"
sudo nginx -c "$(pwd)/nginx-dev.conf"

# 启动 frpc (开发配置)
echo -e "${YELLOW}🌐 启动 FRP 内网穿透...${NC}"
frpc -c frp/frpc.dev.ini &
FRPC_PID=$!

echo -e "${GREEN}"
echo "🎯 开发环境已启动！"
echo ""
echo "📍 本地访问:"
echo "   http://localhost:5000"
echo ""
echo "🌐 外网访问:"
echo "   http://ppt.samsoncj.xyz:8080"
echo ""
echo "📊 服务状态:"
echo "   - Nginx: 运行在端口 5000"
echo "   - FRP: 映射 5000 → ppt.samsoncj.xyz:8080"
echo ""
echo "📝 接下来请在另一个终端运行:"
echo "   npm run dev-app"
echo ""
echo "🛑 停止服务: npm run stop 或 Ctrl+C"
echo -e "${NC}"

# 等待中断信号
trap 'echo -e "\n${YELLOW}🛑 停止服务...${NC}"; kill $FRPC_PID 2>/dev/null; sudo nginx -s stop 2>/dev/null; exit 0' INT

# 保持脚本运行
wait $FRPC_PID