#!/bin/bash

# Conda 统一环境管理脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🐍 使用Conda统一配置Presenton开发环境...${NC}"

# 检查conda是否安装
if ! command -v conda &> /dev/null; then
    echo -e "${RED}❌ Conda未安装，请先安装Miniconda或Anaconda${NC}"
    echo "下载地址: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# 清理旧的虚拟环境
echo -e "${YELLOW}🧹 清理旧的开发环境...${NC}"

# 删除Python虚拟环境
if [ -d "servers/fastapi/venv" ]; then
    echo "删除旧的Python虚拟环境..."
    rm -rf servers/fastapi/venv
fi

# 检查并创建conda环境
echo -e "${YELLOW}📦 配置Conda环境...${NC}"
if conda env list | grep -q "^presenton "; then
    echo -e "${YELLOW}删除已存在的presenton环境...${NC}"
    conda env remove -n presenton -y
fi

echo -e "${YELLOW}创建新的Conda环境...${NC}"
conda env create -f environment-full.yml

# 激活环境
echo -e "${YELLOW}🔧 激活Conda环境...${NC}"
eval "$(conda shell.bash hook)"
conda activate presenton

# 验证环境
echo -e "${YELLOW}✅ 验证环境配置...${NC}"
echo "Python版本: $(python --version)"
echo "Node.js版本: $(node --version)"
echo "npm版本: $(npm --version)"

# 安装Node.js依赖
echo -e "${YELLOW}📦 安装前端依赖...${NC}"
cd servers/nextjs

if [ -d "node_modules" ]; then
    echo "删除旧的node_modules..."
    rm -rf node_modules package-lock.json
fi

npm install
cd ../..

# 创建必要的目录
echo -e "${YELLOW}📁 创建必要目录...${NC}"
mkdir -p app_data
mkdir -p logs
mkdir -p /tmp/presenton

# 创建环境变量文件
echo -e "${YELLOW}📝 配置环境变量...${NC}"
if [ ! -f ".env.local" ]; then
    cat > .env.local << 'EOF'
# Presenton Conda环境配置
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

echo -e "${GREEN}"
echo "🎉 Conda环境配置完成！"
echo ""
echo "🐍 **环境信息：**"
echo "  • 环境名称: presenton" 
echo "  • Python: $(python --version)"
echo "  • Node.js: $(node --version)"
echo ""
echo "🚀 **启动服务：**"
echo "  • 激活环境: conda activate presenton"
echo "  • 后端服务: ./start_backend_conda.sh"
echo "  • 前端服务: ./start_frontend_conda.sh" 
echo "  • FRP客户端: ./start_frp.sh"
echo ""
echo "🔧 **环境管理：**"
echo "  • 查看环境: conda env list"
echo "  • 删除环境: conda env remove -n presenton"
echo "  • 更新环境: conda env update -f environment-full.yml"
echo -e "${NC}"