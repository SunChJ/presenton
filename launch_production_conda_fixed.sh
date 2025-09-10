#!/bin/bash

# Launch Production - Fixed iTerm2 version
# 启动生产模式 - 修复版iTerm2脚本

PROJECT_ROOT="$(pwd)"

echo "🚀 启动生产模式 - iTerm2多窗口..."
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

# 启动iTerm2窗口（参考开发脚本，避免中文符号）
echo "🚀 启动iTerm2 2x2窗口布局..."

osascript <<EOF
tell application "iTerm2"
    -- Top Left: Project Root
    set rootWindow to (create window with default profile)
    tell rootWindow
        set bounds to {50, 50, 700, 400}
    end tell
    set rootSession to current session of rootWindow
    tell rootSession
        write text "cd \"$PROJECT_ROOT\""
        write text "echo 'Production Mode - Project Root'"
        write text "echo 'FastAPI: http://localhost:8000'"
        write text "echo 'Next.js: http://localhost:3001'" 
        write text "echo 'Nginx: http://localhost:5001'"
        write text "echo 'FRP: https://ppt.samsoncj.xyz'"
        set name to "Root"
    end tell
    
    delay 1
    
    -- Top Right: FastAPI Backend
    set backendWindow to (create window with default profile)
    tell backendWindow
        set bounds to {700, 50, 1350, 400}
    end tell
    set backendSession to current session of backendWindow
    tell backendSession
        write text "cd \"$PROJECT_ROOT\""
        write text "source \"\$(conda info --base)/etc/profile.d/conda.sh\""
        write text "conda activate presenton"
        write text "cd servers/fastapi"
        write text "echo 'Starting FastAPI Backend Production...'"
        write text "python server.py"
        set name to "FastAPI"
    end tell
    
    delay 1
    
    -- Bottom Left: Next.js Frontend
    set frontendWindow to (create window with default profile)  
    tell frontendWindow
        set bounds to {50, 400, 700, 750}
    end tell
    set frontendSession to current session of frontendWindow
    tell frontendSession
        write text "cd \"$PROJECT_ROOT\""
        write text "source \"\$(conda info --base)/etc/profile.d/conda.sh\""
        write text "conda activate presenton"
        write text "cd servers/nextjs"
        write text "export USER_CONFIG_PATH=\"$PROJECT_ROOT/app_data/userConfig.json\""
        write text "echo 'Starting Next.js Frontend Production...'"
        write text "echo \"USER_CONFIG_PATH set to: $PROJECT_ROOT/app_data/userConfig.json\""
        write text "npm start"
        set name to "Next.js"
    end tell
    
    delay 1
    
    -- Bottom Right: Nginx Proxy
    set nginxWindow to (create window with default profile)
    tell nginxWindow
        set bounds to {700, 400, 1350, 750}
    end tell
    set nginxSession to current session of nginxWindow
    tell nginxSession
        write text "cd \"$PROJECT_ROOT\""
        write text "echo 'Starting Nginx Proxy Production...'"
        write text "sleep 8"
        write text "sudo nginx -c /tmp/nginx-prod-\$(whoami).conf"
        write text "echo 'Nginx started, monitoring logs...'"
        write text "tail -f /var/log/nginx/error.log"
        set name to "Nginx"
    end tell
end tell
EOF

echo "✅ 生产环境启动完成！"
echo "================================"
echo "📱 iTerm2窗口布局 (2x2):"
echo "  左上: 项目根目录"
echo "  右上: FastAPI后端"
echo "  左下: Next.js前端"
echo "  右下: Nginx反向代理"
echo ""
echo "🌍 访问地址:"
echo "  本地: http://localhost:5001"
echo "  外网: https://ppt.samsoncj.xyz"
echo ""
echo "🛑 停止服务: ./stop_production_conda.sh"