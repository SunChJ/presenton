# Google Gemini集成指南

## 概述

Presenton现在支持Google Gemini AI模型，提供强大的人工智能功能，包括多模态支持、代码生成等。

## 配置步骤

### 1. 获取Google API密钥

1. **访问Google AI Studio**
   ```
   https://makersuite.google.com/app/apikey
   ```

2. **登录Google账户**
   - 使用你的Google账号登录
   - 如果没有Google账号，请先注册

3. **创建API密钥**
   - 点击 "Create API key"
   - 选择项目（或创建新项目）
   - API密钥会自动生成

4. **复制并保存密钥**
   - 密钥格式类似：`AIzaSyD...`
   - 妥善保存，**不要分享给他人**

### 2. 环境配置

#### 方法1: .env文件（推荐）
在 `servers/fastapi/.env` 文件中添加：

```bash
# Google Gemini配置
LLM=google
GOOGLE_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxx
GOOGLE_MODEL=gemini-1.5-flash
```

#### 方法2: 环境变量
```bash
export LLM=google
export GOOGLE_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxx
export GOOGLE_MODEL=gemini-1.5-flash
```

#### 方法3: 使用设置脚本
```bash
python quick_google_setup.py
```

### 3. 支持的模型

Google Gemini提供多个模型选择：

| 模型 | 特点 | 适用场景 |
|------|------|----------|
| `gemini-1.5-flash` | 速度最快，成本最低 | 日常对话，快速响应 |
| `gemini-1.5-pro` | 高性能，功能最全 | 复杂任务，专业应用 |
| `gemini-pro` | 经典稳定版 | 一般应用，稳定性要求高 |

## 功能特性

### ✅ 已支持的功能

1. **文本生成**
   - 支持流式和非流式生成
   - 智能上下文理解
   - 多语言支持

2. **多模态支持**
   - 文本输入
   - 图片理解
   - 混合输入

3. **代码生成**
   - 多语言代码生成
   - 代码解释和优化
   - 调试辅助

4. **结构化输出**
   - JSON模式输出
   - 自定义格式
   - 工具调用支持

### 🚀 独特优势

1. **多模态能力**
   - 可以处理文本、图片、视频
   - 强大的视觉理解能力

2. **代码专长**
   - 优秀的编程能力
   - 支持多种编程语言
   - 代码质量高

3. **免费额度**
   - 每月15美元免费额度
   - 足够日常使用

4. **Google生态**
   - 与Google Workspace集成
   - Google Drive、Gmail等支持

## 使用示例

### 基础文本生成

```python
from services.llm_client import LLMClient
from models.llm_message import LLMUserMessage

client = LLMClient()
messages = [
    LLMUserMessage(content="请解释什么是机器学习")
]

response = await client.generate(
    model="gemini-1.5-flash",
    messages=messages,
    max_tokens=500
)
```

### 流式生成

```python
async for chunk in client.stream(
    model="gemini-1.5-flash",
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
    model="gemini-1.5-flash",
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

### 免费额度
- **每月15美元** 免费额度
- 足够个人用户日常使用
- 超出后按量付费

### 价格表

| 模型 | 输入价格 | 输出价格 |
|------|----------|----------|
| Gemini 1.5 Flash | $0.075/1M tokens | $0.30/1M tokens |
| Gemini 1.5 Pro | $1.25/1M tokens | $5.00/1M tokens |
| Gemini Pro | $0.50/1M tokens | $1.50/1M tokens |

### 速率限制

- **每分钟请求数**: 60次
- **每日请求数**: 1500次（免费用户）
- **并发请求**: 限制较少

## 在Presenton中的使用

### V3版本集成

Google Gemini已完全集成到Presenton V3版本中：

```bash
# 配置Google
export LLM=google
export GOOGLE_MODEL=gemini-1.5-flash

# 启动V3演示
python start_v3_demo.py
```

### API端点

```bash
# 基础生成
POST /api/v3/ppt/presentation/generate

# 流式生成
POST /api/v3/ppt/streaming/generate

# 单步执行
POST /api/v3/ppt/presentation/step
```

## 最佳实践

### 1. 模型选择

- **日常使用**: `gemini-1.5-flash`（速度快，成本低）
- **复杂任务**: `gemini-1.5-pro`（性能更好）
- **稳定需求**: `gemini-pro`（经典稳定）

### 2. 提示优化

Google Gemini对清晰的提示响应更好：

```python
# 好的提示
messages = [
    LLMUserMessage(content="""
请详细解释机器学习的概念，包括：
1. 定义
2. 主要类型
3. 应用领域
4. 发展趋势

请用中文回答，保持专业性和易懂性。
""")
]
```

### 3. 错误处理

```python
try:
    response = await client.generate(model, messages)
except HTTPException as e:
    if "rate limit" in str(e.detail):
        await asyncio.sleep(60)  # 等待后重试
        response = await client.generate(model, messages)
```

## 故障排除

### 常见问题

#### 1. API密钥错误

**错误**: `Google API Key is not set`

**解决**: 确保正确设置了环境变量
```bash
export GOOGLE_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 2. 模型不存在

**错误**: `model not found`

**解决**: 使用正确的模型名称
```bash
# 正确
export GOOGLE_MODEL=gemini-1.5-flash

# 错误
export GOOGLE_MODEL=gemini-flash
```

#### 3. 配额不足

**错误**: `quota exceeded`

**解决**:
- 检查API控制台的配额使用情况
- 等待配额重置或升级账户
- 降低请求频率

#### 4. 网络问题

**错误**: `connection error`

**解决**:
- 检查网络连接
- Google服务可能在某些地区受限
- 考虑使用代理或VPN

### 测试配置

运行内置测试验证配置：

```bash
cd servers/fastapi
python test_google.py  # 如果存在的话
```

或者手动测试：

```python
from services.llm_client import LLMClient
client = LLMClient()
print(f"提供商: {client.llm_provider}")
print(f"模型: {client._client}")
```

## 总结

Google Gemini为Presenton提供了：

- ✅ **强大的多模态AI能力**
- ✅ **优秀的代码生成**
- ✅ **充足的免费额度**
- ✅ **Google官方支持**
- ✅ **稳定的性能**

通过简单的配置，你就可以在Presenton中享受Google Gemini带来的强大AI功能！

