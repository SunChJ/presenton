#!/bin/bash

# Build Production - Conda Environment
# 构建生产模式应用

set -e

echo "🏗️  构建生产模式应用..."
echo "================================"

# 激活conda环境
echo "🐍 激活Conda环境..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate presenton

# 构建后端（FastAPI）
echo "🔧 检查后端依赖..."
cd servers/fastapi
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "ℹ️  未找到requirements.txt，跳过后端依赖安装"
fi
cd ../..

# 构建前端（Next.js）
echo "📦 构建Next.js前端..."
cd servers/nextjs
npm install
npm run build
cd ../..

echo "✅ 生产构建完成！"
echo ""
echo "📝 下一步运行: ./start_production_conda.sh"