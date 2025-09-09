#!/bin/bash

# Conda环境下的简化多终端启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Presenton 开发环境快速启动${NC}"

# 检查conda环境
if ! conda env list | grep -q "^presenton "; then
    echo -e "${RED}❌ 请先运行: ./setup_conda_env.sh${NC}"
    exit 1
fi

# 确保在项目根目录
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

# 检测终端应用 (优先使用 iTerm2)
detect_terminal() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - 优先检测 iTerm2
        if osascript -e 'tell application "iTerm2" to version' &> /dev/null; then
            echo "iterm2"
        elif osascript -e 'tell application "Terminal" to version' &> /dev/null; then
            echo "terminal"
        else
            echo "none"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v gnome-terminal &> /dev/null; then
            echo "gnome-terminal"
        elif command -v konsole &> /dev/null; then
            echo "konsole"
        elif command -v xterm &> /dev/null; then
            echo "xterm"
        else
            echo "none"
        fi
    else
        echo "none"
    fi
}

TERMINAL_TYPE=$(detect_terminal)

case $TERMINAL_TYPE in
    "iterm2")
        echo -e "${YELLOW}🍎 使用 iTerm2${NC}"
        ;;
    "terminal")
        echo -e "${YELLOW}🍎 使用 macOS Terminal${NC}"
        ;;
    "gnome-terminal")
        echo -e "${YELLOW}🐧 使用 GNOME Terminal${NC}"
        ;;
    "none")
        echo -e "${RED}❌ 未找到支持的终端应用，请使用 ./start_full_conda.sh${NC}"
        exit 1
        ;;
    *)
        echo -e "${YELLOW}🐧 使用 $TERMINAL_TYPE${NC}"
        ;;
esac

# 停止现有服务
echo -e "${YELLOW}🔄 停止现有服务...${NC}"
./stop_all_conda.sh > /dev/null 2>&1 || true

# 启动服务
echo -e "${YELLOW}🚀 启动服务...${NC}"

case $TERMINAL_TYPE in
    "iterm2")
        # iTerm2 - 2x2 Grid Layout
        osascript <<EOF
tell application "iTerm2"
    activate
    
    -- Top Left: Nginx Proxy
    set nginxWindow to (create window with default profile)
    tell nginxWindow
        set bounds to {50, 50, 700, 400}
    end tell
    set nginxSession to current session of nginxWindow
    tell nginxSession
        write text "cd \"$PROJECT_ROOT\" && echo 'Starting Nginx Proxy...' && ./start_nginx_conda.sh"
        set name to "🌐 Nginx"
    end tell
    
    delay 1
    
    -- Top Right: FastAPI Backend
    set backendWindow to (create window with default profile)
    tell backendWindow
        set bounds to {700, 50, 1350, 400}
    end tell
    set backendSession to current session of backendWindow
    tell backendSession
        write text "cd \"$PROJECT_ROOT\" && echo 'Starting FastAPI Backend...' && sleep 2 && ./start_backend_conda.sh"
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
        write text "cd \"$PROJECT_ROOT\" && echo 'Starting Next.js Frontend...' && sleep 4 && ./start_frontend_conda.sh"
        set name to "🎨 Next.js"
    end tell
    
    delay 1
    
    -- Bottom Right: FRP Tunnel
    set frpWindow to (create window with default profile)
    tell frpWindow
        set bounds to {700, 400, 1350, 750}
    end tell
    set frpSession to current session of frpWindow
    tell frpSession
        write text "cd \"$PROJECT_ROOT\" && echo 'Starting FRP Tunnel...' && sleep 6 && ./start_frpc_conda.sh"
        set name to "🌐 FRP"
    end tell
    
    -- Focus on nginx window
    select nginxSession
    
end tell
EOF
        ;;
    "terminal")
        # macOS Terminal - 备用方案
        osascript <<EOF
tell application "Terminal"
    activate
    
    -- Nginx 窗口
    set nginxTab to do script "cd \"$PROJECT_ROOT\" && echo '🌐 Nginx 反向代理' && ./start_nginx_conda.sh"
    set custom title of nginxTab to "🌐 Nginx Proxy"
    delay 3
    
    -- 后端窗口
    set backendTab to do script "cd \"$PROJECT_ROOT\" && echo '⚡ FastAPI 后端' && ./start_backend_conda.sh"  
    set custom title of backendTab to "⚡ FastAPI Backend"
    delay 2
    
    -- 前端窗口
    set frontendTab to do script "cd \"$PROJECT_ROOT\" && echo '🎨 Next.js 前端' && ./start_frontend_conda.sh"
    set custom title of frontendTab to "🎨 Next.js Frontend"
    delay 2
    
    -- FRP 内网穿透窗口
    set frpTab to do script "cd \"$PROJECT_ROOT\" && echo '🌐 FRP 内网穿透' && ./start_frpc_conda.sh"
    set custom title of frpTab to "🌐 FRP Tunnel"
    
end tell
EOF
        ;;
    "gnome-terminal")
        # Linux GNOME Terminal
        gnome-terminal \
            --tab --title="🌐 Nginx" -- bash -c "cd '$PROJECT_ROOT' && echo '🌐 Nginx 反向代理' && ./start_nginx_conda.sh; exec bash" \
            --tab --title="⚡ Backend" -- bash -c "cd '$PROJECT_ROOT' && sleep 3 && echo '⚡ FastAPI 后端' && ./start_backend_conda.sh; exec bash" \
            --tab --title="🎨 Frontend" -- bash -c "cd '$PROJECT_ROOT' && sleep 5 && echo '🎨 Next.js 前端' && ./start_frontend_conda.sh; exec bash" \
            --tab --title="🌐 FRP" -- bash -c "cd '$PROJECT_ROOT' && sleep 7 && echo '🌐 FRP 内网穿透' && ./start_frpc_conda.sh; exec bash"
        ;;
    *)
        echo -e "${RED}❌ 不支持的终端类型: $TERMINAL_TYPE${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 开发环境已启动！${NC}"
echo ""
echo -e "${BLUE}📱 2x2 窗口布局:${NC}"
echo "  • 🌐 左上: Nginx 代理服务"
echo "  • ⚡ 右上: FastAPI 后端服务" 
echo "  • 🎨 左下: Next.js 前端服务"
echo "  • 🌐 右下: FRP 内网穿透服务"
echo ""
echo -e "${BLUE}🌐 访问地址:${NC}"
echo "  • 本地完整应用: http://localhost:5001"
echo "  • 外网访问: http://ppt.samsoncj.xyz:8080"
echo "  • API文档: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}💡 提示:${NC}"
echo "  • 4个服务在2x2网格布局的独立窗口中运行"
echo "  • 关闭对应窗口可停止单个服务"
echo "  • 运行 ./stop_all_conda.sh 停止所有服务"
echo ""
echo -e "${GREEN}✨ 开发愉快！${NC}"