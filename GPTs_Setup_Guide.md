# Presenton GPTs 部署指南

## 🎯 概述

将Presenton部署为GPTs Action，让ChatGPT能够通过自然语言创建和管理PowerPoint演示文稿。

## 🚀 部署步骤

### 1. 启动本地服务

```bash
# 环境配置（仅首次需要）
./setup_env.sh

# 启动FastAPI后端（终端1）
./start_backend.sh

# 启动FRP客户端（终端2） 
./start_frp.sh
```

### 2. 验证服务状态

**本地测试：**
```bash
# 测试API健康状态
curl http://localhost:8000/api/v1/health

# 测试Agent接口
curl -X POST http://localhost:8000/api/v1/ppt/agent/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "session_id": "test_123"}'
```

**外网测试：**
```bash
# 测试外网API访问
curl http://ppt.samsoncj.xyz:8080/api/v1/health
```

### 3. 配置GPTs

1. **登录ChatGPT** - 访问 https://chatgpt.com
2. **创建新GPT** - 点击创建 → 配置新GPT
3. **基本信息设置**：
   - **名称**: `PPT制作助手`
   - **描述**: `专业的PowerPoint演示文稿创建助手，支持中英文内容生成`

4. **Instructions（指令）**：
   复制 `gpt_instructions.md` 的内容到Instructions框

5. **Actions配置**：
   - 点击 "Create new action"
   - 导入Schema：复制 `gpt_actions_schema.json` 的内容
   - **Authentication**: 选择 "None"（无需认证）

### 4. 测试GPTs功能

**测试用例：**

1. **创建演示文稿**：
   ```
   "帮我创建一个关于人工智能发展历程的8页演示文稿"
   ```

2. **查询状态**：
   ```
   "查看一下系统状态"
   ```

3. **复杂需求**：
   ```
   "创建一个面向企业客户的区块链技术介绍PPT，需要10页，专业风格"
   ```

## 📊 API接口说明

### 主要接口：

1. **Agent Chat（推荐）**
   - 端点：`POST /api/v1/ppt/agent/chat/`
   - 用途：智能对话，自动识别意图
   - 支持：创建、修改、查询等所有功能

2. **流式Chat**
   - 端点：`POST /api/v1/ppt/agent/chat/stream`
   - 用途：实时反馈，适合长时间操作

3. **直接生成**
   - 端点：`POST /api/v1/ppt/presentation/generate`  
   - 用途：直接生成演示文稿

### 访问地址：
- **本地开发**: http://localhost:8000
- **外网访问**: http://ppt.samsoncj.xyz:8080
- **API文档**: http://ppt.samsoncj.xyz:8080/docs

## 🔧 故障排除

### 常见问题：

1. **API无法访问**
   ```bash
   # 检查服务状态
   ps aux | grep "python server.py"
   
   # 检查端口
   lsof -i :8000
   
   # 重启后端
   ./start_backend.sh
   ```

2. **FRP连接失败**  
   ```bash
   # 检查FRP状态
   ps aux | grep frpc
   
   # 重启FRP
   ./start_frp.sh
   ```

3. **GPTs调用超时**
   - 检查VPS网络状态
   - 确认域名解析正确
   - 验证API响应时间

### 日志查看：
```bash
# FastAPI日志
tail -f logs/fastapi.log

# FRP日志  
tail -f frp/frpc.log
```

## 🌟 使用示例

### GPTs对话示例：

**用户**: "我需要一个关于可持续发展的演示文稿"

**GPTs回复**: "我来帮您创建关于可持续发展的演示文稿！为了制作最适合的内容，请告诉我：
- 您希望多少页？（建议8-12页）
- 目标受众是谁？（学生/企业/政府）
- 有特定的重点方向吗？（环保/经济/社会）"

**用户**: "10页，面向企业管理层，重点讲ESG"

**GPTs**: "✅ 完美！正在为您创建《企业ESG与可持续发展》演示文稿..."

## 📁 文件结构

```
presenton/
├── gpt_actions_schema.json    # GPTs Action配置
├── gpt_instructions.md        # GPTs指令文档  
├── start_backend.sh          # 后端启动脚本
├── start_frp.sh             # FRP启动脚本
├── setup_env.sh             # 环境配置脚本
└── frp/frpc.manual.ini      # FRP客户端配置
```

## 🎉 完成！

现在你的Presenton已经配置为GPTs Action，可以通过ChatGPT自然语言创建专业的PowerPoint演示文稿了！

**访问地址**：
- GPTs管理：https://chatgpt.com/gpts/mine
- API服务：http://ppt.samsoncj.xyz:8080
- 文档：http://ppt.samsoncj.xyz:8080/docs