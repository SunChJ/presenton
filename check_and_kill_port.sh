#!/bin/bash

# 端口检查和清理工具脚本

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

check_and_kill_port() {
    local port=$1
    local service_name=$2
    
    echo -e "${YELLOW}🔍 检查端口 $port ($service_name)...${NC}"
    
    # 检查端口是否被占用
    if lsof -i :$port > /dev/null 2>&1; then
        echo -e "${RED}⚠️ 端口 $port 被占用${NC}"
        
        # 显示占用进程
        echo "占用进程："
        lsof -i :$port
        
        # 获取进程PID
        local pids=$(lsof -ti :$port)
        
        if [ -n "$pids" ]; then
            echo -e "${YELLOW}🔄 尝试终止占用端口 $port 的进程...${NC}"
            for pid in $pids; do
                # 获取进程信息
                local process_info=$(ps -p $pid -o comm= 2>/dev/null || echo "unknown")
                echo -e "${YELLOW}  终止进程: PID $pid ($process_info)${NC}"
                
                # 尝试优雅终止
                kill $pid 2>/dev/null || true
                sleep 1
                
                # 如果还在运行，强制终止
                if kill -0 $pid 2>/dev/null; then
                    echo -e "${RED}  强制终止: PID $pid${NC}"
                    kill -9 $pid 2>/dev/null || true
                fi
            done
            
            # 等待端口释放
            sleep 2
            
            # 再次检查
            if lsof -i :$port > /dev/null 2>&1; then
                echo -e "${RED}❌ 端口 $port 仍被占用，请手动处理${NC}"
                return 1
            else
                echo -e "${GREEN}✅ 端口 $port 已释放${NC}"
                return 0
            fi
        fi
    else
        echo -e "${GREEN}✅ 端口 $port 可用${NC}"
        return 0
    fi
}

# 如果直接运行此脚本
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    if [ $# -eq 0 ]; then
        echo "用法: $0 <端口> [服务名称]"
        echo "示例: $0 5001 Nginx"
        exit 1
    fi
    
    check_and_kill_port $1 "${2:-未知服务}"
fi