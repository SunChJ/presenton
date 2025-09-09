#!/bin/bash

# 常见的frp token测试脚本

TOKENS=("12345678" "jwt_99527_scj" "frp123456" "test_token" "samsoncj" "presenton" "")

echo "🔍 测试常见的FRP token..."

for token in "${TOKENS[@]}"; do
    echo ""
    if [ -z "$token" ]; then
        echo "测试无token配置..."
        sed -i.bak 's/token = .*/# token = /' frp/frpc.manual.ini
    else
        echo "测试token: $token"
        sed -i.bak "s/.*token = .*/token = $token/" frp/frpc.manual.ini
    fi
    
    # 测试连接（5秒超时）
    timeout 5 frpc -c frp/frpc.manual.ini
    
    if [ $? -eq 0 ]; then
        echo "✅ 成功！正确的token是: $token"
        break
    else
        echo "❌ 失败"
    fi
    
    sleep 1
done

echo ""
echo "📝 如果都失败了，请检查VPS上的frps配置文件"