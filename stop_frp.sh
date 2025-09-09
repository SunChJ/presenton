#!/bin/bash

echo "🛑 停止FRP客户端..."

# 停止frpc进程
if pgrep -f "frpc" > /dev/null; then
    killall frpc
    echo "✅ FRP客户端已停止"
else
    echo "ℹ️ FRP客户端未在运行"
fi

# 显示进程状态
echo "📊 当前FRP进程："
ps aux | grep frpc | grep -v grep || echo "  无FRP进程运行"