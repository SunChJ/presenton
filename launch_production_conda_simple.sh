#!/bin/bash

# Launch Production - Simplified Multi-Terminal
# 启动生产模式 - 简化多终端版本

PROJECT_ROOT="$(pwd)"

echo "🚀 启动生产模式服务..."
echo "================================"

# 检查端口占用并停止现有服务
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

# 启动Terminal窗口
echo "🖥️  启动Terminal窗口..."

# FastAPI后端
osascript -e "
tell application \"Terminal\"
    do script \"cd '$PROJECT_ROOT' && source \\\"\$(conda info --base)/etc/profile.d/conda.sh\\\" && conda activate presenton && cd servers/fastapi && echo '🔧 FastAPI后端 (生产模式)' && python server.py\"
end tell
"

sleep 3

# Next.js前端
osascript -e "
tell application \"Terminal\"
    do script \"cd '$PROJECT_ROOT' && source \\\"\$(conda info --base)/etc/profile.d/conda.sh\\\" && conda activate presenton && cd servers/nextjs && export USER_CONFIG_PATH='$PROJECT_ROOT/app_data/userConfig.json' && echo '📦 Next.js前端 (生产模式)' && echo 'USER_CONFIG_PATH: $PROJECT_ROOT/app_data/userConfig.json' && npm start\"
end tell
"

sleep 5

# Nginx反向代理
osascript -e "
tell application \"Terminal\"
    do script \"cd '$PROJECT_ROOT' && echo '🌐 Nginx反向代理 (生产模式)' && sudo nginx -c /tmp/nginx-prod-\$(whoami).conf && echo '✅ Nginx已启动，监控日志...' && tail -f /var/log/nginx/error.log\"
end tell
"

sleep 3

echo "✅ 生产环境启动完成！"
echo "================================"
echo "📱 Terminal窗口:"
echo "  窗口1: FastAPI后端服务"
echo "  窗口2: Next.js前端服务"
echo "  窗口3: Nginx反向代理"
echo ""
echo "🌍 访问地址:"
echo "  本地: http://localhost:5001"
echo "  外网: https://ppt.samsoncj.xyz"
echo ""
echo "🛑 停止服务: ./stop_production_conda.sh"