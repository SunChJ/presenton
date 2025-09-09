#!/bin/bash

# Conda环境下的多终端启动脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 启动Presenton多终端开发环境（Conda环境）...${NC}"

# 检查conda环境
if ! conda env list | grep -q "^presenton "; then
    echo -e "${RED}❌ presenton conda环境不存在，请先运行: ./setup_conda_env.sh${NC}"
    exit 1
fi

# 检查环境配置
if [ ! -f ".env.local" ]; then
    echo -e "${RED}❌ 环境未配置，请先运行: ./setup_conda_env.sh${NC}"
    exit 1
fi

# 确保在项目根目录
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

echo -e "${YELLOW}📝 项目目录: $PROJECT_ROOT${NC}"

# 检测终端类型和操作系统 (优先使用 iTerm2)
detect_terminal() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - 优先检测 iTerm2
        if osascript -e 'tell application "iTerm2" to version' &> /dev/null; then
            echo "iterm2"
        elif command -v osascript &> /dev/null; then
            echo "macos_terminal"
        else
            echo "unknown"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v gnome-terminal &> /dev/null; then
            echo "gnome-terminal"
        elif command -v konsole &> /dev/null; then
            echo "konsole"
        elif command -v xterm &> /dev/null; then
            echo "xterm"
        else
            echo "unknown"
        fi
    else
        echo "unknown"
    fi
}

TERMINAL_TYPE=$(detect_terminal)
echo -e "${YELLOW}🖥️ 检测到终端类型: $TERMINAL_TYPE${NC}"

# 停止现有服务
echo -e "${YELLOW}🔄 停止现有服务...${NC}"
./stop_all_conda.sh > /dev/null 2>&1 || true
sleep 2

# 启动 Nginx (在当前终端)
echo -e "${YELLOW}🌐 在当前终端启动 Nginx...${NC}"
./start_nginx_conda.sh &
NGINX_PID=$!
sleep 3

# 根据不同操作系统和终端启动新窗口
start_new_terminal() {
    local title="$1"
    local command="$2"
    
    case $TERMINAL_TYPE in
        "iterm2")
            # iTerm2 - 优先选择
            osascript <<EOF
tell application "iTerm2"
    activate
    set newTab to (create tab with default profile in (current window))
    tell current session of newTab
        write text "cd \"$PROJECT_ROOT\" && echo -e \"${BLUE}📋 $title${NC}\" && $command"
        set name to "$title"
    end tell
end tell
EOF
            ;;
        "macos_terminal")
            # macOS Terminal - 备用
            osascript <<EOF
tell application "Terminal"
    activate
    set newTab to do script "cd \"$PROJECT_ROOT\" && echo -e \"${BLUE}📋 $title${NC}\" && $command"
    set custom title of newTab to "$title"
end tell
EOF
            ;;
        "gnome-terminal")
            # GNOME Terminal (Ubuntu等)
            gnome-terminal --tab --title="$title" -- bash -c "cd '$PROJECT_ROOT' && echo -e '${BLUE}📋 $title${NC}' && $command; exec bash"
            ;;
        "konsole")
            # KDE Konsole
            konsole --new-tab -e bash -c "cd '$PROJECT_ROOT' && echo -e '${BLUE}📋 $title${NC}' && $command; exec bash" &
            ;;
        "xterm")
            # XTerm
            xterm -T "$title" -e "cd '$PROJECT_ROOT' && echo -e '${BLUE}📋 $title${NC}' && $command; exec bash" &
            ;;
        *)
            echo -e "${RED}❌ 无法检测终端类型，请手动在新终端中运行:${NC}"
            echo -e "${YELLOW}  终端1 - $title: $command${NC}"
            return 1
            ;;
    esac
}

# 等待Nginx启动完成
echo -e "${YELLOW}⏳ 等待Nginx启动完成...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:5001 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Nginx已启动${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Nginx启动超时${NC}"
        exit 1
    fi
    sleep 1
done

echo -e "${YELLOW}🚀 启动新终端窗口...${NC}"

# 启动后端服务（新终端窗口1）
echo -e "${YELLOW}⚡ 启动后端服务终端...${NC}"
start_new_terminal "FastAPI Backend" "./start_backend_conda.sh"

sleep 2

# 启动前端服务（新终端窗口2） 
echo -e "${YELLOW}🎨 启动前端服务终端...${NC}"
start_new_terminal "Next.js Frontend" "./start_frontend_conda.sh"

sleep 2

# 可选：启动FRP服务（新终端窗口3）
read -p "是否启动FRP内网穿透服务？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🌐 启动FRP服务终端...${NC}"
    start_new_terminal "FRP Tunnel" "./start_frp.sh"
fi

echo ""
echo -e "${GREEN}🎉 多终端开发环境启动完成！${NC}"
echo ""
echo -e "${BLUE}📋 终端窗口说明:${NC}"
echo "  • 当前终端: Nginx反向代理 (PID: $NGINX_PID)"
echo "  • 新终端1: FastAPI后端服务"
echo "  • 新终端2: Next.js前端服务"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  • 新终端3: FRP内网穿透"
fi
echo ""
echo -e "${BLUE}🌐 访问地址:${NC}"
echo "  • 完整应用: http://localhost:5001"
echo "  • 前端直连: http://localhost:3001"  
echo "  • 后端API: http://localhost:8000"
echo "  • API文档: http://localhost:8000/docs"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  • 外网访问: http://ppt.samsoncj.xyz:8080"
fi
echo ""
echo -e "${YELLOW}💡 使用说明:${NC}"
echo "  • 每个服务在独立终端窗口中运行"
echo "  • 关闭对应终端窗口可停止单个服务" 
echo "  • 在当前终端按Ctrl+C停止Nginx"
echo "  • 或运行 ./stop_all_conda.sh 停止所有服务"
echo ""

# 设置信号处理
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 正在停止Nginx服务...${NC}"
    sudo nginx -s stop 2>/dev/null && echo -e "${GREEN}✅ Nginx已停止${NC}" || echo -e "${RED}⚠️ Nginx停止失败${NC}"
    echo -e "${YELLOW}💡 请手动关闭其他终端窗口以停止对应服务${NC}"
    exit 0
}

trap cleanup INT TERM

echo -e "${YELLOW}✨ Nginx正在当前终端运行中...（按 Ctrl+C 停止）${NC}"
echo -e "${YELLOW}📱 其他服务在独立终端窗口中运行${NC}"

# 保持脚本运行
while true; do
    sleep 5
    # 检查nginx是否还在运行
    if ! pgrep nginx > /dev/null; then
        echo -e "${RED}❌ Nginx进程意外停止${NC}"
        exit 1
    fi
done