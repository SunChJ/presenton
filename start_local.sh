#!/bin/bash

# Presenton 本地开发启动脚本
# 使用Conda环境 + FRP容器的混合部署方案

set -e

echo "🚀 启动 Presenton 本地开发环境..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查conda是否安装
if ! command -v conda &> /dev/null; then
    echo -e "${RED}❌ Conda未安装，请先安装Miniconda或Anaconda${NC}"
    exit 1
fi

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker未安装，请先安装Docker${NC}"
    exit 1
fi

# 设置环境变量
export APP_DATA_DIRECTORY="${PWD}/app_data"
export TEMP_DIRECTORY="/tmp/presenton"

# 创建必要的目录
mkdir -p "$APP_DATA_DIRECTORY"
mkdir -p "$TEMP_DIRECTORY"

# 检查并创建conda环境
echo -e "${YELLOW}📦 检查Conda环境...${NC}"
if ! conda env list | grep -q "^presenton "; then
    echo -e "${YELLOW}创建新的Conda环境：presenton${NC}"
    conda env create -f environment.yml
else
    echo -e "${GREEN}✅ Conda环境已存在${NC}"
fi

# 激活conda环境
echo -e "${YELLOW}🔧 激活Conda环境...${NC}"
eval "$(conda shell.bash hook)"
conda activate presenton

# 检查Node.js依赖
echo -e "${YELLOW}📦 安装前端依赖...${NC}"
cd servers/nextjs
if [ ! -d "node_modules" ]; then
    npm install
else
    echo -e "${GREEN}✅ 前端依赖已安装${NC}"
fi
cd ../..

# 启动FRP容器
echo -e "${YELLOW}🌐 启动FRP容器...${NC}"
docker-compose -f docker-compose.frp-only.yml up -d

# 等待FRP启动
sleep 3

# 检查Nginx配置是否存在
if [ ! -f "nginx.local.conf" ]; then
    echo -e "${YELLOW}📝 创建本地Nginx配置...${NC}"
    cat > nginx.local.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server localhost:8000;
    }
    
    upstream frontend {
        server localhost:3000;
    }

    server {
        listen 80;
        
        # API请求转发到FastAPI
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # 静态文件和其他请求转发到Next.js
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF
fi

# 启动Nginx（如果需要）
if command -v nginx &> /dev/null; then
    echo -e "${YELLOW}🌐 启动本地Nginx...${NC}"
    sudo nginx -c "${PWD}/nginx.local.conf" -p "${PWD}" || echo -e "${YELLOW}⚠️ Nginx启动失败，将直接使用端口访问${NC}"
fi

# 启动后端服务
echo -e "${YELLOW}⚙️ 启动FastAPI后端...${NC}"
cd servers/fastapi
python server.py --port 8000 --reload &
FASTAPI_PID=$!
cd ../..

# 启动前端服务
echo -e "${YELLOW}🎨 启动Next.js前端...${NC}"
cd servers/nextjs
npm run dev -- -p 3000 &
NEXTJS_PID=$!
cd ../..

# 等待服务启动
sleep 5

echo -e "${GREEN}"
echo "🎉 Presenton 启动完成！"
echo ""
echo "📍 访问地址："
echo "  • 本地访问: http://localhost:3000 (开发)"
echo "  • 本地访问: http://localhost:8000 (API)"
if [ -n "${DOMAIN}" ]; then
    echo "  • 外网访问: https://${DOMAIN}"
fi
echo ""
echo "🔧 服务状态："
echo "  • FastAPI PID: $FASTAPI_PID"
echo "  • Next.js PID: $NEXTJS_PID"
echo "  • FRP容器: presenton-frp"
echo ""
echo "🛑 停止服务："
echo "  • 按 Ctrl+C 停止"
echo "  • 或运行: ./stop_local.sh"
echo -e "${NC}"

# 等待用户中断
trap 'echo -e "\n${YELLOW}🛑 正在停止服务...${NC}"; kill $FASTAPI_PID $NEXTJS_PID 2>/dev/null; docker-compose -f docker-compose.frp-only.yml down; exit 0' INT

wait