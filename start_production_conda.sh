#!/bin/bash

# Start Production - Conda Environment  
# 启动生产模式服务

set -e

PROJECT_ROOT="$(pwd)"

echo "🚀 启动生产模式服务..."
echo "================================"

# 检查端口占用
check_and_kill_port() {
    local port=$1
    local service_name=$2
    if lsof -ti:$port > /dev/null 2>&1; then
        echo "⚠️  端口 $port 被占用，停止现有进程..."
        lsof -ti:$port | xargs kill -9
        sleep 2
    fi
    echo "✅ 端口 $port 已释放 ($service_name)"
}

# 停止现有服务
echo "🛑 停止现有服务..."
check_and_kill_port 8000 "FastAPI"
check_and_kill_port 3001 "Next.js" 
check_and_kill_port 5001 "Nginx"

# 生成Nginx配置
echo "📄 生成Nginx生产配置..."
sed "s|__USER__|$(whoami)|g; s|__GROUP__|$(id -gn)|g; s|__PROJECT_ROOT__|$PROJECT_ROOT|g" nginx-production.conf > /tmp/nginx-prod-$(whoami).conf

# 激活conda环境
echo "🐍 激活Conda环境..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate presenton

# 启动服务 (多终端窗口)
echo "🔧 启动FastAPI后端 (生产模式)..."
osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_ROOT' && source \"\$(conda info --base)/etc/profile.d/conda.sh\" && conda activate presenton && cd servers/fastapi && echo '🔧 FastAPI后端 (生产模式)' && python server.py"
end tell
EOF

sleep 3

echo "📦 启动Next.js前端 (生产模式)..."
osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_ROOT' && source \"\$(conda info --base)/etc/profile.d/conda.sh\" && conda activate presenton && cd servers/nextjs && echo '📦 Next.js前端 (生产模式)' && npm start"
end tell
EOF

sleep 5

echo "🌐 启动Nginx反向代理..."
osascript <<EOF
tell application "Terminal"
    do script "cd '$PROJECT_ROOT' && echo '🌐 Nginx反向代理 (生产模式)' && sudo nginx -c /tmp/nginx-prod-\$(whoami).conf && echo '✅ Nginx已启动' && echo '📊 监控Nginx日志:' && tail -f /var/log/nginx/error.log"
end tell
EOF

sleep 3

echo "✅ 生产服务启动完成！"
echo "================================"
echo "🌍 访问地址:"
echo "  本地: http://localhost:5001"
echo "  外网: https://ppt.samsoncj.xyz"
echo ""
echo "📊 服务状态:"
echo "  FastAPI: http://localhost:8000"
echo "  Next.js: http://localhost:3001"
echo "  Nginx:   http://localhost:5001"
echo ""
echo "📱 终端窗口:"
echo "  窗口1: FastAPI后端服务"
echo "  窗口2: Next.js前端服务"
echo "  窗口3: Nginx反向代理"
echo ""
echo "🛑 停止服务: ./stop_production_conda.sh"