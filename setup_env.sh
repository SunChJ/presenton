#!/bin/bash

# 环境配置和依赖安装脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🛠️ 配置Presenton开发环境...${NC}"

# ===== 环境变量配置 =====
echo -e "${YELLOW}📝 配置环境变量...${NC}"
export APP_DATA_DIRECTORY="${PWD}/app_data"
export TEMP_DIRECTORY="/tmp/presenton"

# 创建必要的目录
mkdir -p "$APP_DATA_DIRECTORY"
mkdir -p "$TEMP_DIRECTORY" 
mkdir -p "${PWD}/logs"

# 创建环境变量文件
if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}创建.env.local文件...${NC}"
    cat > .env.local << 'EOF'
# Presenton 本地开发环境变量
APP_DATA_DIRECTORY=./app_data
TEMP_DIRECTORY=/tmp/presenton
NODE_ENV=development

# LLM配置
LLM=google
GOOGLE_API_KEY=AIzaSyA6vag6ryPJlPZuo6G3B2AcUwZ7Bm7_DYQ

# 数据库配置
DATABASE_URL=sqlite:///./app_data/presenton.db

# 其他配置
CAN_CHANGE_KEYS=true
DISABLE_ANONYMOUS_TRACKING=true
EOF
fi

# ===== 检查系统依赖 =====
echo -e "${YELLOW}🔍 检查系统依赖...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3未安装${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 系统依赖检查完成${NC}"

# ===== Python环境配置 =====
echo -e "${YELLOW}🐍 配置Python环境...${NC}"
cd servers/fastapi

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}创建Python虚拟环境...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

if [ ! -f "venv/installed.flag" ] || [ "requirements.txt" -nt "venv/installed.flag" 2>/dev/null ]; then
    echo -e "${YELLOW}安装Python依赖...${NC}"
    pip install --upgrade pip
    pip install aiohttp aiomysql aiosqlite asyncpg greenlet
    pip install fastapi[standard] pathvalidate pdfplumber  
    pip install chromadb sqlmodel anthropic google-genai openai fastmcp
    pip install python-pptx nltk redis pytest uvicorn[standard]
    pip install docling --extra-index-url https://download.pytorch.org/whl/cpu
    touch venv/installed.flag
    echo -e "${GREEN}✅ Python依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ Python依赖已存在${NC}"
fi

cd ../..

# ===== Node.js环境配置 =====
echo -e "${YELLOW}📦 配置Node.js环境...${NC}"
cd servers/nextjs

if [ ! -d "node_modules" ] || [ "package.json" -nt "node_modules/.install_flag" 2>/dev/null ]; then
    echo -e "${YELLOW}安装Node.js依赖...${NC}"
    npm install
    touch node_modules/.install_flag
    echo -e "${GREEN}✅ Node.js依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ Node.js依赖已存在${NC}"
fi

cd ../..

echo -e "${GREEN}"
echo "🎉 环境配置完成！"
echo ""
echo "📂 创建的目录和文件："
echo "  • 数据目录: $APP_DATA_DIRECTORY"
echo "  • 临时目录: $TEMP_DIRECTORY"  
echo "  • 日志目录: ${PWD}/logs/"
echo "  • 环境配置: .env.local"
echo ""
echo "🚀 接下来可以启动服务："
echo "  • 后端: ./start_backend.sh"
echo "  • 前端: ./start_frontend.sh" 
echo "  • FRP: ./start_frp_brew.sh"
echo -e "${NC}"