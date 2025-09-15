#!/bin/bash

# OpenRouter快速设置脚本
# 用于快速配置OpenRouter环境变量

echo "🚀 OpenRouter快速设置脚本"
echo "=========================="

# 检查是否已经设置
if [ -n "$OPENROUTER_API_KEY" ]; then
    echo "✅ OPENROUTER_API_KEY 已经设置"
else
    echo "请输入你的OpenRouter API密钥:"
    echo "1. 访问 https://openrouter.ai/"
    echo "2. 登录并获取API密钥"
    echo "3. 粘贴密钥 (以 sk-or-v1- 开头):"
    read -s api_key

    if [ -n "$api_key" ]; then
        export OPENROUTER_API_KEY="$api_key"
        echo "✅ OPENROUTER_API_KEY 已设置"
    else
        echo "❌ API密钥不能为空"
        exit 1
    fi
fi

# 设置LLM提供商
export LLM="openrouter"
echo "✅ LLM提供商设置为: openrouter"

# 选择默认模型
echo ""
echo "选择默认模型:"
echo "1. anthropic/claude-3-haiku:beta (推荐，性价比高)"
echo "2. openai/gpt-4o-mini (快速且便宜)"
echo "3. google/gemini-flash-1.5 (Google最便宜)"
echo "4. anthropic/claude-3.5-sonnet:beta (高性能)"
echo "5. 自定义模型"

read -p "请选择 (1-5): " choice

case $choice in
    1)
        export OPENROUTER_MODEL="anthropic/claude-3-haiku:beta"
        echo "✅ 使用 Claude 3 Haiku"
        ;;
    2)
        export OPENROUTER_MODEL="openai/gpt-4o-mini"
        echo "✅ 使用 GPT-4o Mini"
        ;;
    3)
        export OPENROUTER_MODEL="google/gemini-flash-1.5"
        echo "✅ 使用 Gemini Flash"
        ;;
    4)
        export OPENROUTER_MODEL="anthropic/claude-3.5-sonnet:beta"
        echo "✅ 使用 Claude 3.5 Sonnet"
        ;;
    5)
        read -p "请输入模型名称: " custom_model
        if [ -n "$custom_model" ]; then
            export OPENROUTER_MODEL="$custom_model"
            echo "✅ 使用自定义模型: $custom_model"
        else
            export OPENROUTER_MODEL="anthropic/claude-3-haiku:beta"
            echo "⚠️  使用默认模型: anthropic/claude-3-haiku:beta"
        fi
        ;;
    *)
        export OPENROUTER_MODEL="anthropic/claude-3-haiku:beta"
        echo "⚠️  使用默认模型: anthropic/claude-3-haiku:beta"
        ;;
esac

echo ""
echo "🎉 配置完成！"
echo "=============="
echo "当前配置:"
echo "LLM: $LLM"
echo "API Key: ${OPENROUTER_API_KEY:0:20}..."
echo "Model: $OPENROUTER_MODEL"
echo ""
echo "💡 提示:"
echo "1. 运行以下命令使配置持久化:"
echo "   echo 'export LLM=\"$LLM\"' >> ~/.bashrc"
echo "   echo 'export OPENROUTER_API_KEY=\"$OPENROUTER_API_KEY\"' >> ~/.bashrc"
echo "   echo 'export OPENROUTER_MODEL=\"$OPENROUTER_MODEL\"' >> ~/.bashrc"
echo ""
echo "2. 或者添加到你的 .env 文件:"
echo "   LLM=$LLM"
echo "   OPENROUTER_API_KEY=$OPENROUTER_API_KEY"
echo "   OPENROUTER_MODEL=$OPENROUTER_MODEL"
echo ""
echo "3. 测试配置:"
echo "   cd servers/fastapi"
echo "   python test_openrouter.py"
echo ""
echo "4. 启动服务器:"
echo "   python server.py --port 8000"
