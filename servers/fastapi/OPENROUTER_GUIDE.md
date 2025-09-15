# OpenRouter集成指南

## 概述

Presenton现在支持通过[OpenRouter](https://openrouter.ai/)使用多种LLM模型。OpenRouter提供统一的API接口，支持来自不同提供商的模型，包括Anthropic Claude、OpenAI GPT系列、Google Gemini等。

## 配置步骤

### 1. 获取OpenRouter API密钥

1. 访问 [OpenRouter网站](https://openrouter.ai/)
2. 注册账户（支持GitHub登录）
3. 在Dashboard中获取API密钥
4. 为账户充值（支持信用卡、加密货币等）

### 2. 环境配置

在你的环境变量或`.env`文件中设置：

```bash
# 设置LLM提供商为OpenRouter
export LLM=openrouter

# 设置OpenRouter API密钥
export OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx

# 设置默认模型（可选，默认为anthropic/claude-3-haiku:beta）
export OPENROUTER_MODEL=anthropic/claude-3-haiku:beta
```

### 3. 支持的模型

OpenRouter支持多种模型，以下是一些常用选项：

#### Anthropic Claude系列
```bash
# 推荐：性价比高的轻量级模型
export OPENROUTER_MODEL=anthropic/claude-3-haiku:beta

# 高性能模型
export OPENROUTER_MODEL=anthropic/claude-3-sonnet:beta

# 最新模型
export OPENROUTER_MODEL=anthropic/claude-3.5-sonnet:beta
```

#### OpenAI GPT系列
```bash
# 轻量级模型，成本低
export OPENROUTER_MODEL=openai/gpt-4o-mini

# 高性能模型
export OPENROUTER_MODEL=openai/gpt-4o

# 最新旗舰模型
export OPENROUTER_MODEL=openai/gpt-4o-2024-08-06
```

#### Google Gemini
```bash
# Google Gemini 1.5 Pro
export OPENROUTER_MODEL=google/gemini-pro-1.5

# Google Gemini Flash（更快更便宜）
export OPENROUTER_MODEL=google/gemini-flash-1.5
```

#### Meta Llama
```bash
# Meta Llama 3.1 8B（免费）
export OPENROUTER_MODEL=meta/llama-3.1-8b-instruct

# Meta Llama 3.1 70B
export OPENROUTER_MODEL=meta/llama-3.1-70b-instruct
```

#### 其他模型
```bash
# Mistral Large
export OPENROUTER_MODEL=mistralai/mistral-large

# Cohere Command R+
export OPENROUTER_MODEL=cohere/command-r-plus
```

## 功能特性

### ✅ 已支持的功能

1. **基础文本生成**
   - 支持所有OpenRouter模型
   - 兼容OpenAI API格式

2. **流式生成**
   - 实时流式响应
   - 支持V3版本的步骤化生成

3. **结构化输出**
   - 支持JSON模式输出
   - 兼容工具调用功能

4. **多模型支持**
   - 动态切换不同模型
   - 统一的API接口

### 🔧 高级配置

#### 模型参数调整

```bash
# 设置温度参数（0.0-2.0）
export TEMPERATURE=0.7

# 设置最大token数
export MAX_TOKENS=2000

# 启用思考模式（部分模型支持）
export DISABLE_THINKING=false
```

#### 负载均衡

OpenRouter支持自动负载均衡，你可以在同一个模型名称后添加不同的后缀来使用不同的提供商：

```bash
# 使用Anthropic官方API
export OPENROUTER_MODEL=anthropic/claude-3-haiku:beta

# 使用AWS上的Claude
export OPENROUTER_MODEL=anthropic/claude-3-haiku:beta:aws

# 使用Together AI上的Claude
export OPENROUTER_MODEL=anthropic/claude-3-haiku:beta:together
```

## 使用示例

### 基础使用

```python
from services.llm_client import LLMClient
from models.llm_message import LLMUserMessage

# 初始化客户端
client = LLMClient()

# 创建消息
messages = [
    LLMUserMessage(content="请解释什么是机器学习")
]

# 生成响应
response = await client.generate(
    model="anthropic/claude-3-haiku:beta",
    messages=messages,
    max_tokens=500
)

print(response)
```

### 流式生成

```python
# 流式生成
async for chunk in client.stream(
    model="anthropic/claude-3-haiku:beta",
    messages=messages,
    max_tokens=500
):
    print(chunk, end="", flush=True)
```

### 结构化输出

```python
from pydantic import BaseModel

class Answer(BaseModel):
    explanation: str
    examples: list[str]

response = await client.generate_structured(
    model="anthropic/claude-3-haiku:beta",
    messages=messages,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "answer",
            "schema": Answer.model_json_schema()
        }
    }
)
```

## 价格和限制

### 价格对比

| 模型 | 输入价格 | 输出价格 | 备注 |
|------|----------|----------|------|
| Claude 3 Haiku | $0.25/1M | $1.25/1M | 性价比最高 |
| GPT-4o Mini | $0.15/1M | $0.60/1M | OpenAI最便宜 |
| Gemini Flash | $0.075/1M | $0.30/1M | Google最便宜 |
| Claude 3.5 Sonnet | $3/1M | $15/1M | 高性能模型 |

### 速率限制

OpenRouter有速率限制，具体取决于你的账户等级：

- **免费账户**: 每分钟20个请求
- **付费账户**: 根据充值金额提升限制
- **企业账户**: 更高的并发限制

## 故障排除

### 常见问题

#### 1. API密钥错误

**错误**: `OpenRouter API Key is not set`

**解决**: 确保设置了正确的环境变量
```bash
export OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
```

#### 2. 模型不存在

**错误**: `model not found`

**解决**: 使用正确的模型名称
```bash
# 正确
export OPENROUTER_MODEL=anthropic/claude-3-haiku:beta

# 错误
export OPENROUTER_MODEL=claude-3-haiku
```

#### 3. 账户余额不足

**错误**: `insufficient balance`

**解决**: 在OpenRouter账户中充值

#### 4. 速率限制

**错误**: `rate limit exceeded`

**解决**:
- 降低请求频率
- 升级账户等级
- 实现重试逻辑

### 测试脚本

运行内置的测试脚本验证配置：

```bash
cd servers/fastapi
python test_openrouter.py
```

## 最佳实践

### 1. 模型选择

- **日常使用**: `anthropic/claude-3-haiku:beta`（平衡性能和成本）
- **复杂任务**: `anthropic/claude-3.5-sonnet:beta`（高性能）
- **快速响应**: `openai/gpt-4o-mini` 或 `google/gemini-flash-1.5`（速度优先）

### 2. 成本优化

- 使用合适大小的模型
- 设置合理的max_tokens
- 监控API使用量

### 3. 错误处理

```python
try:
    response = await client.generate(model, messages)
except HTTPException as e:
    if "rate limit" in str(e.detail):
        # 等待后重试
        await asyncio.sleep(60)
        response = await client.generate(model, messages)
    else:
        raise
```

## 总结

通过OpenRouter集成，Presenton现在支持：

- ✅ **20+ 主流LLM模型**
- ✅ **统一的API接口**
- ✅ **灵活的模型切换**
- ✅ **成本优化选项**
- ✅ **完整的流式支持**

这为用户提供了更多的选择，可以根据具体需求选择最适合的模型和价格方案。
