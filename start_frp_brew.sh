#!/bin/bash

echo "🌐 启动FRP客户端（Brew版本）..."

# 检查是否通过Brew安装了frp
if ! command -v frpc &> /dev/null; then
    echo "❌ FRP未通过Brew安装，正在安装..."
    brew install frp
fi

# 检查配置文件是否存在
if [ ! -f "frp/frpc.manual.ini" ]; then
    echo "❌ 配置文件不存在：frp/frpc.manual.ini"
    exit 1
fi

# 检查是否已经在运行
if pgrep -f "frpc.*frpc.manual.ini" > /dev/null; then
    echo "⚠️ FRP客户端已在运行"
    ps aux | grep "frpc.*frpc.manual.ini" | grep -v grep
    exit 1
fi

# 创建日志目录
mkdir -p frp

# 加载环境变量
if [ -f "frp/.env" ]; then
    echo "📝 加载环境变量..."
    source frp/.env
else
    echo "⚠️ 未找到frp/.env文件"
fi

# 启动FRP客户端
echo "🚀 启动FRP客户端..."
nohup frpc -c frp/frpc.manual.ini > frp/frpc.log 2>&1 &

sleep 2

# 检查是否启动成功
if pgrep -f "frpc.*frpc.manual.ini" > /dev/null; then
    echo "✅ FRP客户端启动成功"
    echo ""
    echo "📍 访问地址："
    echo "  • 外网域名: https://ppt.samsoncj.xyz"
    echo "  • 本地测试: http://localhost:80"
    echo ""
    echo "📝 查看日志: tail -f frp/frpc.log"
    echo "🛑 停止FRP: killall frpc"
else
    echo "❌ FRP客户端启动失败，请检查日志："
    tail frp/frpc.log
fi