#!/bin/bash

echo "🌐 启动FRP客户端（手动模式）..."

# 检查frpc是否存在
if [ ! -f "frp/frpc" ]; then
    echo "❌ frpc客户端不存在，正在下载..."
    cd frp
    
    # 检测系统架构
    ARCH=$(uname -m)
    if [ "$ARCH" = "arm64" ]; then
        URL="https://github.com/fatedier/frp/releases/download/v0.58.1/frp_0.58.1_darwin_arm64.tar.gz"
    else
        URL="https://github.com/fatedier/frp/releases/download/v0.58.1/frp_0.58.1_darwin_amd64.tar.gz"
    fi
    
    curl -L $URL -o frp.tar.gz
    tar -xzf frp.tar.gz
    mv frp_0.58.1_darwin_*/* ./
    chmod +x frpc
    rm -rf frp_0.58.1_darwin_* frp.tar.gz
    cd ..
fi

# 检查是否已经在运行
if pgrep -f "frpc" > /dev/null; then
    echo "⚠️ FRP客户端已在运行"
    ps aux | grep frpc | grep -v grep
    exit 1
fi

# 启动FRP客户端
echo "🚀 启动FRP客户端..."
cd frp
nohup ./frpc -c frpc.manual.ini > frpc.log 2>&1 &
echo "✅ FRP客户端已启动，日志文件：frp/frpc.log"
echo "📝 查看日志：tail -f frp/frpc.log"
echo "🛑 停止FRP：killall frpc"