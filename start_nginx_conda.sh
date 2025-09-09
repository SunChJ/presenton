#!/bin/bash

# Conda环境下的Nginx启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🌐 启动Nginx反向代理服务（Conda环境）...${NC}"

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

# 确保在项目根目录
cd "$(dirname "$0")"

# 检查nginx是否安装
if ! command -v nginx &> /dev/null; then
    echo -e "${RED}❌ nginx 未安装，请先安装:${NC}"
    echo "  macOS: brew install nginx"
    echo "  Linux: sudo apt install nginx"
    exit 1
fi

# 检查配置文件是否存在
if [ ! -f "nginx-dev.conf" ]; then
    echo -e "${RED}❌ Nginx配置文件不存在：nginx-dev.conf${NC}"
    exit 1
fi

# 停止现有的 nginx
echo -e "${YELLOW}🔄 停止现有的 nginx 进程...${NC}"
sudo nginx -s stop 2>/dev/null || true
sleep 2

# 导入端口检查工具
source "./check_and_kill_port.sh"

# 检查并清理端口 5001
if ! check_and_kill_port 5001 "Nginx"; then
    echo -e "${RED}❌ 无法释放端口 5001，请手动处理${NC}"
    exit 1
fi

# 获取当前目录绝对路径
CURRENT_DIR=$(pwd)

# 创建临时的 Nginx 配置文件，替换路径和用户占位符
echo -e "${YELLOW}📝 生成 Nginx 配置文件...${NC}"
TEMP_NGINX_CONF="/tmp/nginx-dev-$(whoami).conf"

# 获取当前用户和组
CURRENT_USER=$(whoami)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CURRENT_GROUP=$(id -gn)
else
    # Linux
    CURRENT_GROUP=$(id -gn)
fi

# 替换配置文件中的占位符
sed -e "s|__PROJECT_ROOT__|$CURRENT_DIR|g" \
    -e "s|__USER__|$CURRENT_USER|g" \
    -e "s|__GROUP__|$CURRENT_GROUP|g" \
    nginx-dev.conf > "$TEMP_NGINX_CONF"

# 修复权限问题：确保静态文件可读
chmod -R 755 servers/fastapi/static/ 2>/dev/null || true

echo -e "${GREEN}"
echo "🚀 启动Nginx反向代理..."
echo "🐍 Conda环境: presenton"
echo "📂 工作目录: $CURRENT_DIR"
echo "📄 配置文件: $TEMP_NGINX_CONF"
echo "📍 服务地址: http://localhost:5001"
echo "🔄 代理配置:"
echo "  • / → http://localhost:3001 (Next.js)"
echo "  • /api/v1/ → http://localhost:8000 (FastAPI)"
echo "  • /static → 静态文件服务"
echo "🛑 停止服务: 按 Ctrl+C 或运行 sudo nginx -s stop"
echo -e "${NC}"

# 启动 nginx (使用临时配置文件)
sudo nginx -c "$TEMP_NGINX_CONF"

# 验证 nginx 启动成功
sleep 1
if curl -s http://localhost:5001 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Nginx 已成功启动并运行在端口 5001${NC}"
else
    echo -e "${YELLOW}⚠️ Nginx 已启动但后端服务尚未就绪${NC}"
fi

echo ""
echo -e "${YELLOW}📝 接下来请在其他终端启动:${NC}"
echo "  • 后端服务: ./start_backend_conda.sh"
echo "  • 前端服务: ./start_frontend_conda.sh"
echo "  • FRP穿透: ./start_frp.sh"
echo ""

# 保持脚本运行，监听中断信号
trap 'echo -e "\n${YELLOW}🛑 停止Nginx服务...${NC}"; sudo nginx -s stop 2>/dev/null; echo -e "${GREEN}✅ Nginx已停止${NC}"; [ -f "$TEMP_NGINX_CONF" ] && rm -f "$TEMP_NGINX_CONF" && echo -e "${GREEN}✅ 临时配置文件已清理${NC}"; exit 0' INT

echo -e "${YELLOW}✨ Nginx正在运行中...（按 Ctrl+C 停止）${NC}"
while true; do
    sleep 5
    # 检查nginx是否还在运行
    if ! pgrep nginx > /dev/null; then
        echo -e "${RED}❌ Nginx进程意外停止${NC}"
        exit 1
    fi
done