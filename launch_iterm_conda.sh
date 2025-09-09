#!/bin/bash

# 专为 iTerm2 优化的开发环境启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}🚀 Presenton iTerm2 专享启动${NC}"

# 检查 iTerm2 是否可用
if ! osascript -e 'tell application "iTerm2" to version' &> /dev/null; then
    echo -e "${RED}❌ iTerm2 未安装或无法访问${NC}"
    echo -e "${YELLOW}💡 请安装 iTerm2 或使用: ./launch_dev_conda.sh${NC}"
    exit 1
fi

# 检查conda环境
if ! conda env list | grep -q "^presenton "; then
    echo -e "${RED}❌ 请先运行: ./setup_conda_env.sh${NC}"
    exit 1
fi

# 确保在项目根目录
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

echo -e "${PURPLE}✨ 使用 iTerm2 启动多服务开发环境${NC}"

# 停止现有服务
echo -e "${YELLOW}🔄 停止现有服务...${NC}"
./stop_all_conda.sh > /dev/null 2>&1 || true

# 启动服务 - iTerm2 专用优化配置
echo -e "${YELLOW}🚀 在 iTerm2 中启动服务...${NC}"

osascript <<EOF
tell application "iTerm2"
    activate
    
    -- First window: Nginx Proxy
    set nginxWindow to (create window with default profile)
    set nginxSession to current session of nginxWindow
    tell nginxSession
        write text "cd \"$PROJECT_ROOT\""
        write text "clear"
        write text "echo 'Starting Nginx Proxy...' && ./start_nginx_conda.sh"
        set name to "🌐 Nginx Proxy"
    end tell
    set name of nginxWindow to "🌐 Nginx Proxy"
    
    delay 3
    
    -- Second window: FastAPI Backend
    set backendWindow to (create window with default profile)
    set backendSession to current session of backendWindow
    tell backendSession
        write text "cd \"$PROJECT_ROOT\""
        write text "clear"
        write text "echo 'Starting FastAPI Backend...' && sleep 2 && ./start_backend_conda.sh"
        set name to "⚡ FastAPI Backend"
    end tell
    set name of backendWindow to "⚡ FastAPI Backend"
    
    delay 2
    
    -- Third window: Next.js Frontend
    set frontendWindow to (create window with default profile)
    set frontendSession to current session of frontendWindow
    tell frontendSession
        write text "cd \"$PROJECT_ROOT\""
        write text "clear"
        write text "echo 'Starting Next.js Frontend...' && sleep 4 && ./start_frontend_conda.sh"
        set name to "🎨 Next.js Frontend"
    end tell
    set name of frontendWindow to "🎨 Next.js Frontend"
    
    delay 2
    
    -- Fourth window: FRP Tunnel
    set frpWindow to (create window with default profile)
    set frpSession to current session of frpWindow
    tell frpSession
        write text "cd \"$PROJECT_ROOT\""
        write text "clear"
        write text "echo 'Starting FRP Tunnel...' && sleep 6 && ./start_frpc_conda.sh"
        set name to "🌐 FRP Tunnel"
    end tell
    set name of frpWindow to "🌐 FRP Tunnel"
    
    -- Focus on first window
    select nginxSession
    
end tell
EOF

echo ""
echo -e "${GREEN}🎉 iTerm2 开发环境已启动！${NC}"
echo ""
echo -e "${BLUE}📱 iTerm2 窗口:${NC}"
echo "  • 🌐 Nginx Proxy - 反向代理 (端口 5001)"
echo "  • ⚡ FastAPI Backend - 后端 API (端口 8000)"
echo "  • 🎨 Next.js Frontend - 前端界面 (端口 3001)"
echo "  • 🌐 FRP Tunnel - 内网穿透服务"
echo ""
echo -e "${BLUE}🌐 访问地址:${NC}"
echo "  • 本地完整应用: http://localhost:5001"
echo "  • 外网访问: http://ppt.samsoncj.xyz:8080"
echo "  • API 文档: http://localhost:8000/docs"
echo ""
echo -e "${PURPLE}✨ iTerm2 特色功能:${NC}"
echo "  • 漂亮的标签页图标和名称"
echo "  • 统一窗口管理"
echo "  • 颜色编码的服务标识"
echo "  • 优化的启动时序"
echo ""
echo -e "${YELLOW}💡 使用提示:${NC}"
echo "  • 每个服务在独立的 iTerm2 窗口中运行"
echo "  • 使用 Cmd+` 快速切换窗口"
echo "  • 关闭对应窗口停止单个服务"
echo "  • 运行 ./stop_all_conda.sh 停止所有服务"
echo ""
echo -e "${GREEN}✨ 开发愉快！${NC}"