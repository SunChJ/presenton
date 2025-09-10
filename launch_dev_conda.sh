#!/bin/bash

# Launch Development - Conda Environment with iTerm2
# 启动开发模式 - 使用iTerm2 2x2布局

PROJECT_ROOT="$(pwd)"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🚀 启动开发模式 - iTerm2多窗口...${NC}"
echo "================================"

# Terminal类型检测函数
detect_terminal() {
    if command -v osascript >/dev/null 2>&1; then
        if osascript -e 'tell application "iTerm2" to version' &> /dev/null; then
            echo "iterm2"
            return
        elif osascript -e 'tell application "Terminal" to version' &> /dev/null; then
            echo "terminal"
            return
        fi
    fi
    echo "none"
}

TERMINAL_TYPE=$(detect_terminal)

case $TERMINAL_TYPE in
    "iterm2")
        echo -e "${YELLOW}🍎 使用 iTerm2${NC}"
        ;;
    "terminal")
        echo -e "${YELLOW}🍎 使用 macOS Terminal${NC}"
        ;;
    *)
        echo -e "${RED}❌ 未检测到可用的终端应用${NC}"
        exit 1
        ;;
esac

# 检查端口占用并停止现有服务
check_and_kill_port() {
    local port=$1
    local service_name=$2
    if lsof -ti:$port > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  端口 $port 被占用，停止现有进程...${NC}"
        lsof -ti:$port | xargs kill -9
        sleep 2
    fi
    echo -e "${GREEN}✅ 端口 $port 已释放 ($service_name)${NC}"
}

# 停止现有服务
echo -e "${YELLOW}🛑 停止现有服务...${NC}"
check_and_kill_port 8000 "FastAPI"
check_and_kill_port 3001 "Next.js"
check_and_kill_port 5001 "Nginx Port"
check_and_kill_port 5678 "Debugpy"

# 彻底停止nginx进程
echo -e "${YELLOW}🛑 彻底停止nginx进程...${NC}"
if pgrep nginx > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  发现nginx进程，正在停止...${NC}"
    sudo pkill -f nginx || true
    sleep 2
    # 强制杀死残留进程
    sudo pkill -9 -f nginx || true
    sleep 1
fi
echo -e "${GREEN}✅ nginx进程已清理${NC}"

# 生成Nginx配置
echo -e "${YELLOW}📄 生成Nginx开发配置...${NC}"
sed "s|__USER__|$(whoami)|g; s|__GROUP__|$(id -gn)|g; s|__PROJECT_ROOT__|$PROJECT_ROOT|g" nginx-production.conf > /tmp/nginx-dev-$(whoami).conf

# 启动服务
echo -e "${YELLOW}🚀 启动开发服务...${NC}"

case $TERMINAL_TYPE in
    "iterm2")
        # iTerm2 - 2x2 Grid Layout
        osascript <<EOF
tell application "iTerm2"
    activate
    
    -- Top Left: Project Root
    set rootWindow to (create window with default profile)
    tell rootWindow
        set bounds to {50, 50, 700, 400}
    end tell
    set rootSession to current session of rootWindow
    tell rootSession
        write text "cd \"$PROJECT_ROOT\" && echo 'Starting FRP Client...' && ./start_frpc_conda.sh"
        set name to "🌐 FRP"
    end tell
    
    delay 1
    
    -- Top Right: FastAPI Backend
    set backendWindow to (create window with default profile)
    tell backendWindow
        set bounds to {700, 50, 1350, 400}
    end tell
    set backendSession to current session of backendWindow
    tell backendSession
        write text "cd \"$PROJECT_ROOT\" && echo 'Starting FastAPI Backend Development...' && source \"\$(conda info --base)/etc/profile.d/conda.sh\" && conda activate presenton && source .env.local && cd servers/fastapi && export APP_DATA_DIRECTORY=\"$PROJECT_ROOT/app_data\" && export TEMP_DIRECTORY=\"$PROJECT_ROOT/app_data/temp\" && export USER_CONFIG_PATH=\"$PROJECT_ROOT/app_data/userConfig.json\" && export DATABASE_URL=\"sqlite:///$PROJECT_ROOT/app_data/presenton-dev.db\" && export LLM=\"google\" && export IMAGE_PROVIDER=\"google\" && export GOOGLE_API_KEY=\"AIzaSyDxOJfpsvAdXjXlRU_Qjwsq3dRVPFKMCdw\" && export CAN_CHANGE_KEYS=\"true\" && export PYDEVD_DISABLE_FILE_VALIDATION=\"1\" && export ENABLE_DEBUGPY=\"true\" && python -X frozen_modules=off server.py --port 8000 --reload true"
        set name to "⚡ FastAPI-Dev"
    end tell
    
    delay 1
    
    -- Bottom Left: Next.js Frontend (Development Mode)
    set frontendWindow to (create window with default profile)
    tell frontendWindow
        set bounds to {50, 400, 700, 750}
    end tell
    set frontendSession to current session of frontendWindow
    tell frontendSession
        write text "cd \"$PROJECT_ROOT\" && echo 'Starting Next.js Frontend Development...' && source \"\$(conda info --base)/etc/profile.d/conda.sh\" && conda activate presenton && cd servers/nextjs && export APP_DATA_DIRECTORY=\"$PROJECT_ROOT/app_data\" && export TEMP_DIRECTORY=\"$PROJECT_ROOT/app_data/temp\" && export USER_CONFIG_PATH=\"$PROJECT_ROOT/app_data/userConfig.json\" && npm run dev -- -p 3001"
        set name to "🎨 Next.js-Dev"
    end tell
    
    delay 1
    
    -- Bottom Right: Nginx Proxy
    set nginxWindow to (create window with default profile)
    tell nginxWindow
        set bounds to {700, 400, 1350, 750}
    end tell
    set nginxSession to current session of nginxWindow
    tell nginxSession
        write text "cd \"$PROJECT_ROOT\" && echo 'Starting Nginx Proxy Development...' && sleep 8 && sudo nginx -c /tmp/nginx-dev-\$(whoami).conf && echo 'Nginx started successfully!' && echo 'Monitoring access via: curl http://localhost:5001' && while true; do echo '[Nginx Status Check]'; curl -s -o /dev/null -w 'HTTP Status: %{http_code}' http://localhost:5001; echo ''; sleep 30; done"
        set name to "🌐 Nginx-Dev"
    end tell
end tell
EOF
        ;;
    "terminal")
        # macOS Terminal fallback
        echo -e "${YELLOW}使用 Terminal 启动开发服务...${NC}"
        
        # 启动FastAPI
        osascript -e 'tell app "Terminal" to do script "cd '\"$PROJECT_ROOT\"' && source \"$(conda info --base)/etc/profile.d/conda.sh\" && conda activate presenton && source .env.local && cd servers/fastapi && export APP_DATA_DIRECTORY=\"'$PROJECT_ROOT'/app_data\" && export TEMP_DIRECTORY=\"'$PROJECT_ROOT'/app_data/temp\" && export USER_CONFIG_PATH=\"'$PROJECT_ROOT'/app_data/userConfig.json\" && export DATABASE_URL=\"sqlite:///'$PROJECT_ROOT'/app_data/presenton-dev.db\" && export LLM=\"google\" && export IMAGE_PROVIDER=\"google\" && export GOOGLE_API_KEY=\"AIzaSyDxOJfpsvAdXjXlRU_Qjwsq3dRVPFKMCdw\" && export CAN_CHANGE_KEYS=\"true\" && export PYDEVD_DISABLE_FILE_VALIDATION=\"1\" && export ENABLE_DEBUGPY=\"true\" && python -X frozen_modules=off server.py --port 8000 --reload true"'
        
        sleep 2
        
        # 启动Next.js开发服务器
        osascript -e 'tell app "Terminal" to do script "cd '\"$PROJECT_ROOT\"' && source \"$(conda info --base)/etc/profile.d/conda.sh\" && conda activate presenton && cd servers/nextjs && export APP_DATA_DIRECTORY=\"'$PROJECT_ROOT'/app_data\" && export TEMP_DIRECTORY=\"'$PROJECT_ROOT'/app_data/temp\" && export USER_CONFIG_PATH=\"'$PROJECT_ROOT'/app_data/userConfig.json\" && npm run dev -- -p 3001"'
        
        sleep 5
        
        # 启动Nginx
        sudo nginx -c /tmp/nginx-dev-$(whoami).conf
        ;;
esac

sleep 3

echo -e "${GREEN}✅ 开发环境启动完成！${NC}"
echo "================================"
echo -e "${GREEN}📱 iTerm2窗口布局 (2x2):${NC}"
echo "  • 🏠 左上: 项目根目录/FRP客户端"
echo "  • ⚡ 右上: FastAPI后端服务 (开发模式 + 热重载)"
echo "  • 🎨 左下: Next.js前端服务 (开发模式 + 热重载)"
echo "  • 🌐 右下: Nginx反向代理"
echo ""
echo -e "${GREEN}🌍 访问地址:${NC}"
echo "  • 本地: http://localhost:5001"
echo "  • 外网: https://ppt.samsoncj.xyz"
echo ""
echo -e "${GREEN}🔥 开发模式特性:${NC}"
echo "  • FastAPI: 代码修改自动重载 (--reload)"
echo "  • Next.js: 热重载 (npm run dev)"
echo "  • 数据库: presenton-dev.db (独立开发数据库)"
echo ""
echo -e "${GREEN}🛑 停止服务: 关闭iTerm2窗口或 Ctrl+C${NC}"