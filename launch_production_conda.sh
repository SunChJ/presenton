#!/bin/bash

# Launch Production - Conda Environment with iTerm2
# 启动生产模式 - 使用iTerm2 2x2布局

PROJECT_ROOT="$(pwd)"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🚀 启动生产模式 - iTerm2多窗口...${NC}"
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
echo -e "${YELLOW}📄 生成Nginx生产配置...${NC}"
sed "s|__USER__|$(whoami)|g; s|__GROUP__|$(id -gn)|g; s|__PROJECT_ROOT__|$PROJECT_ROOT|g" nginx-production.conf > /tmp/nginx-prod-$(whoami).conf

# 启动服务
echo -e "${YELLOW}🚀 启动服务...${NC}"

case $TERMINAL_TYPE in
    "iterm2")
        # iTerm2 - 2x2 Grid Layout (完全模仿开发脚本)
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
        write text "cd \"$PROJECT_ROOT\" && echo 'Starting FastAPI Backend Production...' && source \"\$(conda info --base)/etc/profile.d/conda.sh\" && conda activate presenton && source .env.local && cd servers/fastapi && export APP_DATA_DIRECTORY=\"$PROJECT_ROOT/app_data\" && export TEMP_DIRECTORY=\"$PROJECT_ROOT/app_data/temp\" && export USER_CONFIG_PATH=\"$PROJECT_ROOT/app_data/userConfig.json\" && export DATABASE_URL=\"sqlite:///$PROJECT_ROOT/app_data/presenton-prod.db\" && export LLM=\"google\" && export IMAGE_PROVIDER=\"google\" && export GOOGLE_API_KEY=\"AIzaSyDxOJfpsvAdXjXlRU_Qjwsq3dRVPFKMCdw\" && export CAN_CHANGE_KEYS=\"true\" && python server.py --port 8000"
        set name to "⚡ FastAPI"
    end tell
    
    delay 1
    
    -- Bottom Left: Next.js Frontend
    set frontendWindow to (create window with default profile)
    tell frontendWindow
        set bounds to {50, 400, 700, 750}
    end tell
    set frontendSession to current session of frontendWindow
    tell frontendSession
        write text "cd \"$PROJECT_ROOT\" && echo 'Starting Next.js Frontend Production...' && source \"\$(conda info --base)/etc/profile.d/conda.sh\" && conda activate presenton && cd servers/nextjs && export USER_CONFIG_PATH=\"$PROJECT_ROOT/app_data/userConfig.json\" && npm start -- -p 3001"
        set name to "🎨 Next.js"
    end tell
    
    delay 1
    
    -- Bottom Right: Nginx Proxy
    set nginxWindow to (create window with default profile)
    tell nginxWindow
        set bounds to {700, 400, 1350, 750}
    end tell
    set nginxSession to current session of nginxWindow
    tell nginxSession
        write text "cd \"$PROJECT_ROOT\" && echo 'Starting Nginx Proxy Production...' && sleep 8 && sudo nginx -c /tmp/nginx-prod-\$(whoami).conf && echo 'Nginx started successfully!' && echo 'Monitoring access via: curl http://localhost:5001' && while true; do echo '[Nginx Status Check]'; curl -s -o /dev/null -w 'HTTP Status: %{http_code}' http://localhost:5001; echo ''; sleep 30; done"
        set name to "🌐 Nginx"
    end tell
end tell
EOF
        ;;
    "terminal")
        # macOS Terminal fallback
        echo -e "${YELLOW}使用 Terminal 启动服务...${NC}"
        ./launch_production_conda_simple.sh
        ;;
esac

sleep 3

echo -e "${GREEN}✅ 生产环境启动完成！${NC}"
echo "================================"
echo -e "${GREEN}📱 iTerm2窗口布局 (2x2):${NC}"
echo "  • 🏠 左上: 项目根目录"
echo "  • ⚡ 右上: FastAPI后端服务"
echo "  • 🎨 左下: Next.js前端服务"
echo "  • 🌐 右下: Nginx反向代理"
echo ""
echo -e "${GREEN}🌍 访问地址:${NC}"
echo "  • 本地: http://localhost:5001"
echo "  • 外网: https://ppt.samsoncj.xyz"
echo ""
echo -e "${GREEN}🛑 停止服务: ./stop_production_conda.sh${NC}"