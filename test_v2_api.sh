#!/bin/bash

# V2 API测试脚本
# 用于验证markdown_to_ppt是否按期望执行

set -e

echo "🚀 开始测试V2 Markdown转PPT API"
echo "=================================================="

# 检查必要的工具
if ! command -v jq &> /dev/null; then
    echo "❌ 错误: 需要安装jq工具"
    echo "安装命令: brew install jq"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    echo "❌ 错误: 需要安装curl工具"
    exit 1
fi

# 检查测试文件
TEST_MD_FILE="/Users/samsoncj/Downloads/presenton/test_md_2_ppt.md"
if [[ ! -f "$TEST_MD_FILE" ]]; then
    echo "❌ 错误: 测试文件不存在: $TEST_MD_FILE"
    exit 1
fi

echo "✅ 环境检查完成"
echo ""

# 显示测试文件内容
echo "📄 测试Markdown内容:"
echo "----------------------------------------"
head -20 "$TEST_MD_FILE"
echo "..."
echo "总行数: $(wc -l < "$TEST_MD_FILE")"
echo ""

# 构建请求JSON
echo "🔧 构建API请求..."
REQUEST_JSON=$(jq -n --rawfile content "$TEST_MD_FILE" '{
  "markdown_content": $content,
  "template": "modern",
  "language": "Chinese",
  "export_format": "pptx"
}')

echo "✅ 请求JSON构建完成"
echo ""

# 发送API请求
echo "📡 发送API请求到: https://ppt.samsoncj.xyz/api/v2/ppt/markdown-to-ppt/generate"
echo "请求参数:"
echo "- template: modern"
echo "- language: Chinese" 
echo "- export_format: pptx"
echo ""

echo "⏰ 开始请求... (这可能需要几分钟)"
echo "----------------------------------------"

RESPONSE=$(curl -X POST "https://ppt.samsoncj.xyz/api/v2/ppt/markdown-to-ppt/generate" \
    -H "Content-Type: application/json" \
    -d "$REQUEST_JSON" \
    -w "\n\nHTTP状态码: %{http_code}\n响应时间: %{time_total}s\n" \
    2>/dev/null)

echo "$RESPONSE"
echo "----------------------------------------"

# 解析响应
echo ""
echo "📊 解析API响应..."

# 提取JSON部分（去掉HTTP状态信息）
RESPONSE_JSON=$(echo "$RESPONSE" | sed '/HTTP状态码:/,$d')

if echo "$RESPONSE_JSON" | jq . > /dev/null 2>&1; then
    echo "✅ 响应JSON格式正确"
    
    # 检查成功状态
    SUCCESS=$(echo "$RESPONSE_JSON" | jq -r '.success // false')
    
    if [[ "$SUCCESS" == "true" ]]; then
        echo "🎉 API调用成功!"
        echo ""
        
        # 显示关键信息
        PRESENTATION_ID=$(echo "$RESPONSE_JSON" | jq -r '.presentation_id // "null"')
        SLIDES_COUNT=$(echo "$RESPONSE_JSON" | jq -r '.slides_count // "null"')
        PROCESSING_TIME=$(echo "$RESPONSE_JSON" | jq -r '.processing_time // "null"')
        PREVIEW_URL=$(echo "$RESPONSE_JSON" | jq -r '.preview_url // "null"')
        DOWNLOAD_URL=$(echo "$RESPONSE_JSON" | jq -r '.download_url // "null"')
        MESSAGE=$(echo "$RESPONSE_JSON" | jq -r '.message // "无消息"')
        
        echo "📋 生成结果:"
        echo "- 演示文稿ID: $PRESENTATION_ID"
        echo "- 幻灯片数量: $SLIDES_COUNT"
        echo "- 处理时间: ${PROCESSING_TIME}秒"
        echo "- 消息: $MESSAGE"
        echo ""
        
        echo "🔗 访问链接:"
        echo "- 预览链接: https://ppt.samsoncj.xyz$PREVIEW_URL"
        echo "- 下载链接: https://ppt.samsoncj.xyz$DOWNLOAD_URL"
        echo ""
        
        echo "✨ 测试成功完成!"
        
    else
        echo "❌ API调用失败"
        echo ""
        
        ERROR_MESSAGE=$(echo "$RESPONSE_JSON" | jq -r '.message // "未知错误"')
        ERROR_DETAILS=$(echo "$RESPONSE_JSON" | jq -r '.error_details // "无详细信息"')
        PROCESSING_TIME=$(echo "$RESPONSE_JSON" | jq -r '.processing_time // "null"')
        
        echo "💥 错误信息:"
        echo "- 错误消息: $ERROR_MESSAGE"
        echo "- 错误详情: $ERROR_DETAILS"
        echo "- 处理时间: ${PROCESSING_TIME}秒"
        echo ""
        
        echo "🔍 可能的问题:"
        if [[ "$ERROR_DETAILS" == *"NOT NULL constraint failed"* ]]; then
            echo "- 数据库字段约束失败，可能是SlideModel字段映射问题"
        elif [[ "$ERROR_DETAILS" == *"layout"* ]]; then
            echo "- 布局相关错误，检查模板获取是否成功"
        elif [[ "$ERROR_DETAILS" == *"timeout"* ]]; then
            echo "- 请求超时，可能是网络或服务器性能问题"
        else
            echo "- 其他未知错误，查看服务器日志获取更多信息"
        fi
        
        exit 1
    fi
    
else
    echo "❌ 响应不是有效的JSON格式"
    echo "原始响应:"
    echo "$RESPONSE_JSON"
    exit 1
fi

echo ""
echo "=================================================="
echo "🏁 V2 API测试完成"