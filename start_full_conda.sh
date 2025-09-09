#!/bin/bash

# Conda环境下的完整开发环境启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 启动Presenton完整开发环境（Conda环境）...${NC}"

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

# 检查必要的工具
echo -e "${YELLOW}🔍 检查必要工具...${NC}"
missing_tools=()

if ! command -v nginx &> /dev/null; then
    missing_tools+=("nginx")
fi

if ! command -v python &> /dev/null; then
    missing_tools+=("python")
fi

if ! command -v node &> /dev/null; then
    missing_tools+=("node")
fi

if [ ${#missing_tools[@]} -ne 0 ]; then
    echo -e "${RED}❌ 缺少必要工具: ${missing_tools[*]}${NC}"
    echo "请运行 ./setup_conda_env.sh 重新配置环境"
    exit 1
fi

# 停止可能运行的服务
echo -e "${YELLOW}🔄 停止现有服务...${NC}"
sudo nginx -s stop 2>/dev/null || true
pkill -f "python.*server.py" 2>/dev/null || true
pkill -f "python.*mcp_server.py" 2>/dev/null || true
pkill -f "node.*next" 2>/dev/null || true
sleep 2

# 创建必要目录
echo -e "${YELLOW}📁 创建必要目录...${NC}"
mkdir -p app_data
mkdir -p logs
mkdir -p /tmp/presenton

# 配置环境变量
export USER_CONFIG_PATH="${PWD}/app_data/userConfig.json"
export PYTHONPATH="${PWD}/servers/fastapi:$PYTHONPATH"

echo -e "${GREEN}"
echo "🎯 启动服务组件..."
echo "🐍 Conda环境: presenton"
echo "📂 工作目录: $(pwd)"
echo "📄 配置文件: $USER_CONFIG_PATH"
echo -e "${NC}"

# 启动 Nginx
echo -e "${YELLOW}🌐 启动 Nginx 反向代理...${NC}"
sudo nginx -c "$(pwd)/nginx-dev.conf"
sleep 1

# 启动 FastAPI 后端
echo -e "${YELLOW}⚡ 启动 FastAPI 后端服务...${NC}"
cd servers/fastapi
python server.py --port 8000 --reload false > ../../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ../..
sleep 2

# 启动 MCP 服务
echo -e "${YELLOW}🔗 启动 MCP 服务...${NC}"
cd servers/fastapi
python mcp_server.py --port 8001 > ../../logs/mcp.log 2>&1 &
MCP_PID=$!
cd ../..
sleep 1

# 检查前端依赖
if [ ! -d "servers/nextjs/node_modules" ]; then
    echo -e "${YELLOW}📦 安装前端依赖...${NC}"
    cd servers/nextjs && npm install && cd ../..
fi

# 启动 Next.js 前端
echo -e "${YELLOW}🎨 启动 Next.js 前端服务...${NC}"
cd servers/nextjs
npm run dev -- -p 3001 > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..

# 等待服务启动
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 5

# 检查服务状态
check_service() {
    local service_name=$1
    local port=$2
    local pid=$3
    
    if curl -s http://localhost:$port > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name (端口 $port)${NC}"
        return 0
    else
        echo -e "${RED}❌ $service_name (端口 $port) - 启动失败${NC}"
        return 1
    fi
}

echo -e "${BLUE}📊 服务状态检查:${NC}"
check_service "Nginx代理" 5001
check_service "FastAPI后端" 8000
check_service "Next.js前端" 3001

echo ""
echo -e "${GREEN}🎉 开发环境启动完成！${NC}"
echo ""
echo -e "${BLUE}🌐 访问地址:${NC}"
echo "  • 完整应用: http://localhost:5001"
echo "  • 前端直连: http://localhost:3001"
echo "  • 后端API: http://localhost:8000"
echo "  • API文档: http://localhost:8000/docs"
echo ""
echo -e "${BLUE}📋 进程信息:${NC}"
echo "  • Nginx: 系统服务"
echo "  • Backend: PID $BACKEND_PID"
echo "  • MCP: PID $MCP_PID"
echo "  • Frontend: PID $FRONTEND_PID"
echo ""
echo -e "${BLUE}📁 日志文件:${NC}"
echo "  • 后端日志: logs/backend.log"
echo "  • MCP日志: logs/mcp.log"
echo "  • 前端日志: logs/frontend.log"
echo ""
echo -e "${YELLOW}🛑 停止所有服务: ./stop_all_conda.sh 或 按 Ctrl+C${NC}"

# 设置信号处理
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 正在停止所有服务...${NC}"
    
    # 停止 nginx
    sudo nginx -s stop 2>/dev/null && echo -e "${GREEN}✅ Nginx已停止${NC}" || echo -e "${RED}⚠️ Nginx停止失败${NC}"
    
    # 停止后端服务
    kill $BACKEND_PID 2>/dev/null && echo -e "${GREEN}✅ FastAPI后端已停止${NC}" || echo -e "${RED}⚠️ FastAPI停止失败${NC}"
    
    # 停止MCP服务
    kill $MCP_PID 2>/dev/null && echo -e "${GREEN}✅ MCP服务已停止${NC}" || echo -e "${RED}⚠️ MCP停止失败${NC}"
    
    # 停止前端服务
    kill $FRONTEND_PID 2>/dev/null && echo -e "${GREEN}✅ Next.js前端已停止${NC}" || echo -e "${RED}⚠️ Next.js停止失败${NC}"
    
    echo -e "${GREEN}🎯 所有服务已停止${NC}"
    exit 0
}

trap cleanup INT TERM

# 保持脚本运行
echo -e "${YELLOW}✨ 所有服务正在运行中...（按 Ctrl+C 停止）${NC}"
while true; do
    sleep 10
    
    # 检查关键进程是否还在运行
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ FastAPI后端进程意外停止${NC}"
        cleanup
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Next.js前端进程意外停止${NC}"
        cleanup
    fi
    
    if ! pgrep nginx > /dev/null; then
        echo -e "${RED}❌ Nginx进程意外停止${NC}"
        cleanup
    fi
done