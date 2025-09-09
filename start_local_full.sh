#!/bin/bash

# Presenton 完整本地启动脚本
# 模拟Docker环境的配置和处理

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 启动 Presenton 完整本地环境...${NC}"

# ===== 环境变量配置 =====
echo -e "${YELLOW}📝 配置环境变量...${NC}"
export APP_DATA_DIRECTORY="${PWD}/app_data"
export TEMP_DIRECTORY="/tmp/presenton"
export NODE_ENV="development"

# 从 .env.local 加载环境变量（如果存在）
if [ -f ".env.local" ]; then
    echo -e "${GREEN}✅ 加载 .env.local 文件${NC}"
    set -a
    source .env.local
    set +a
fi

# 创建必要的目录
echo -e "${YELLOW}📁 创建必要目录...${NC}"
mkdir -p "$APP_DATA_DIRECTORY"
mkdir -p "$TEMP_DIRECTORY"
mkdir -p "${PWD}/logs"

# ===== 检查依赖 =====
echo -e "${YELLOW}🔍 检查系统依赖...${NC}"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3未安装${NC}"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js未安装${NC}"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 系统依赖检查完成${NC}"

# ===== Python依赖安装 =====
echo -e "${YELLOW}🐍 检查Python依赖...${NC}"
cd servers/fastapi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}创建Python虚拟环境...${NC}"
    python3 -m venv venv
fi

# 激活虚拟环境
echo -e "${YELLOW}激活Python虚拟环境...${NC}"
source venv/bin/activate

# 安装Python依赖
if [ ! -f "venv/installed.flag" ] || [ "requirements.txt" -nt "venv/installed.flag" ]; then
    echo -e "${YELLOW}安装Python依赖...${NC}"
    pip install --upgrade pip
    pip install aiohttp aiomysql aiosqlite asyncpg
    pip install fastapi[standard] pathvalidate pdfplumber
    pip install chromadb sqlmodel anthropic google-genai openai fastmcp
    pip install python-pptx nltk redis pytest
    pip install docling --extra-index-url https://download.pytorch.org/whl/cpu
    touch venv/installed.flag
    echo -e "${GREEN}✅ Python依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ Python依赖已存在${NC}"
fi

cd ../..

# ===== Node.js依赖安装 =====
echo -e "${YELLOW}📦 检查Node.js依赖...${NC}"
cd servers/nextjs

if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules" ]; then
    echo -e "${YELLOW}安装Node.js依赖...${NC}"
    npm install
    echo -e "${GREEN}✅ Node.js依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ Node.js依赖已存在${NC}"
fi

cd ../..

# ===== 检查Nginx配置 =====
echo -e "${YELLOW}🌐 配置Nginx...${NC}"
if [ ! -f "nginx.local.conf" ]; then
    echo -e "${YELLOW}创建本地Nginx配置...${NC}"
    cat > nginx.local.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    upstream backend {
        server 127.0.0.1:8000;
    }
    
    upstream frontend {
        server 127.0.0.1:3000;
    }

    server {
        listen 80;
        
        # 静态资源
        location /_next/ {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # API请求转发到FastAPI
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # app_data静态文件
        location /app_data/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # 其他请求转发到Next.js
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF
fi

# ===== 启动服务 =====
echo -e "${BLUE}🎯 启动服务...${NC}"

# 启动FastAPI后端
echo -e "${YELLOW}⚙️ 启动FastAPI后端...${NC}"
cd servers/fastapi
source venv/bin/activate
python server.py --port 8000 --reload > ../../logs/fastapi.log 2>&1 &
FASTAPI_PID=$!
echo -e "${GREEN}✅ FastAPI已启动 (PID: $FASTAPI_PID)${NC}"
cd ../..

# 等待FastAPI启动
sleep 3

# 启动Next.js前端
echo -e "${YELLOW}🎨 启动Next.js前端...${NC}"
cd servers/nextjs
npm run dev -- -p 3000 > ../../logs/nextjs.log 2>&1 &
NEXTJS_PID=$!
echo -e "${GREEN}✅ Next.js已启动 (PID: $NEXTJS_PID)${NC}"
cd ../..

# 等待Next.js启动
sleep 5

# 启动Nginx（如果已安装）
if command -v nginx &> /dev/null; then
    echo -e "${YELLOW}🌐 启动本地Nginx...${NC}"
    # 检查端口80是否被占用
    if ! lsof -i :80 &> /dev/null; then
        sudo nginx -c "${PWD}/nginx.local.conf" -p "${PWD}" > logs/nginx.log 2>&1 &
        NGINX_PID=$!
        echo -e "${GREEN}✅ Nginx已启动 (PID: $NGINX_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️ 端口80被占用，跳过Nginx启动${NC}"
        NGINX_PID=""
    fi
else
    echo -e "${YELLOW}⚠️ Nginx未安装，跳过Nginx启动${NC}"
    NGINX_PID=""
fi

# 等待所有服务启动
sleep 3

echo -e "${GREEN}"
echo "🎉 Presenton 启动完成！"
echo ""
echo "📍 访问地址："
echo "  • Next.js开发服务器: http://localhost:3000"
echo "  • FastAPI后端服务: http://localhost:8000"
if [ -n "$NGINX_PID" ]; then
    echo "  • Nginx反向代理: http://localhost:80"
fi
echo ""
echo "📁 数据目录: $APP_DATA_DIRECTORY"
echo "📋 日志目录: ${PWD}/logs/"
echo ""
echo "🔧 服务状态："
echo "  • FastAPI PID: $FASTAPI_PID"
echo "  • Next.js PID: $NEXTJS_PID"
if [ -n "$NGINX_PID" ]; then
    echo "  • Nginx PID: $NGINX_PID"
fi
echo ""
echo "📝 查看日志："
echo "  • FastAPI: tail -f logs/fastapi.log"
echo "  • Next.js: tail -f logs/nextjs.log"
if [ -n "$NGINX_PID" ]; then
    echo "  • Nginx: tail -f logs/nginx.log"
fi
echo ""
echo "🛑 停止服务："
echo "  • 按 Ctrl+C 停止"
echo "  • 或运行: ./stop_local_full.sh"
echo -e "${NC}"

# 创建停止脚本
cat > stop_local_full.sh << 'EOF'
#!/bin/bash
echo "🛑 停止Presenton本地服务..."

# 停止可能运行的进程
echo "停止Python和Node.js进程..."
pkill -f "python server.py"
pkill -f "npm run dev"
pkill -f "next dev"

# 停止Nginx
if pgrep nginx > /dev/null; then
    echo "停止Nginx..."
    sudo nginx -s stop 2>/dev/null || true
fi

echo "✅ 所有服务已停止"
EOF

chmod +x stop_local_full.sh

# 等待用户中断
trap 'echo -e "\n${YELLOW}🛑 正在停止服务...${NC}"; ./stop_local_full.sh; exit 0' INT

# 保持脚本运行
wait