# 云端部署方案

## Railway 一键部署（推荐）

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/presenton-ai-presentations?referralCode=ubp0kk)

1. 点击上面的按钮
2. 连接您的 GitHub 账户
3. Fork 本项目
4. 设置环境变量：
   ```
   LLM=openai
   OPENAI_API_KEY=your_openai_key
   CAN_CHANGE_KEYS=false
   ```
5. 部署完成后获得公网URL

## Docker 部署

### 基础部署：
```bash
docker run -d \
  --name presenton-agent \
  -p 80:80 \
  -e LLM="openai" \
  -e OPENAI_API_KEY="your_key_here" \
  -e CAN_CHANGE_KEYS="false" \
  -e REDIS_URL="redis://your-redis-url" \
  -v "./app_data:/app_data" \
  ghcr.io/presenton/presenton:latest
```

### 带Redis的部署：
```bash
# 启动Redis
docker run -d --name redis -p 6379:6379 redis:alpine

# 启动Presenton
docker run -d \
  --name presenton-agent \
  --link redis:redis \
  -p 80:80 \
  -e LLM="openai" \
  -e OPENAI_API_KEY="your_key_here" \
  -e REDIS_URL="redis://redis:6379" \
  -v "./app_data:/app_data" \
  ghcr.io/presenton/presenton:latest
```

## 环境变量配置

GPT Actions 推荐配置：
```bash
# LLM 配置
LLM=openai
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4

# 安全配置
CAN_CHANGE_KEYS=false

# Redis 配置（可选，提高性能）
REDIS_URL=redis://your-redis-host:6379

# CORS 配置（允许GPT访问）
CORS_ORIGINS=https://chat.openai.com,https://chatgpt.com

# 其他配置
DISABLE_ANONYMOUS_TELEMETRY=true
```

## API 访问测试

部署完成后，测试以下端点：

```bash
# 健康检查
curl https://your-domain.com/api/v1/ppt/agent/test/health

# 测试聊天
curl -X POST https://your-domain.com/api/v1/ppt/agent/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "message": "创建一个关于AI的演示文稿",
    "session_id": "test_123"
  }'
```

## 安全考虑

1. **API密钥保护**：设置 `CAN_CHANGE_KEYS=false`
2. **CORS配置**：限制访问来源
3. **速率限制**：考虑添加API速率限制
4. **日志监控**：监控API调用和错误

## GPT Actions 最终配置

部署完成后，在GPT Actions中：

1. 更新 Server URL 为您的域名
2. 测试所有API端点
3. 验证流式响应工作正常
4. 测试完整的演示文稿创建流程