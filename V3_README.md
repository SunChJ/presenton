# Presenton V3 - 增强演示文稿生成系统

## 概述

V3版本是基于V2版本的重大改进，实现了你想要的交互逻辑：用户输入 → Agent步骤化执行 → 专业HTML生成 → 流式展示 → 导出功能。

## 核心特性

### 1. 步骤化Agent执行器
- **步骤1**: 生成大纲 (基于用户输入)
- **步骤2**: 搜索内容和图片 (可选)
- **步骤3**: 生成PPT内容
- **步骤4**: 专业HTML生成 (角色扮演)
- **步骤5**: 流式生成展示
- **步骤6**: 导出PDF/PPTX

### 2. 增强的Markdown解析
- 基于V2版本改进
- 支持纯文本和Markdown输入
- 智能内容类型识别
- 增强的内容分析

### 3. 专业HTML设计专家
- 角色扮演系统
- 智能布局生成
- Tailwind CSS优化
- 响应式设计

### 4. 灵活的DSL系统
- 动态布局生成
- 样式配置管理
- 组件化设计
- 主题支持

### 5. 流式生成展示
- 实时进度反馈
- SSE流式响应
- 步骤状态更新
- 预览功能

## 架构设计

```
V3 Presentation Generator
├── Enhanced PPT Agent (步骤化执行器)
│   ├── Step 1: 生成大纲
│   ├── Step 2: 搜索内容和图片
│   ├── Step 3: 生成PPT内容
│   ├── Step 4: 专业HTML生成
│   ├── Step 5: 流式生成展示
│   └── Step 6: 导出PDF/PPTX
├── Content Services
│   ├── Enhanced Markdown Parser
│   ├── Content Search Service
│   └── Image Search Service
├── HTML Design Expert
│   ├── Layout Generator
│   ├── Style Generator
│   └── Component Generator
├── DSL System
│   ├── Presentation DSL Schema
│   ├── Layout DSL Parser
│   └── Style DSL Compiler
└── Export Services
    ├── HTML to PDF Converter
    └── HTML to PPTX Converter
```

## API端点

### 主要端点

- `POST /api/v3/ppt/presentation/generate` - 生成演示文稿
- `POST /api/v3/ppt/streaming/generate` - 流式生成演示文稿
- `POST /api/v3/ppt/presentation/step` - 执行单个步骤
- `GET /api/v3/ppt/presentation/status/{id}` - 获取状态
- `DELETE /api/v3/ppt/presentation/{id}` - 删除演示文稿

### 请求示例

```json
{
  "user_input": "我想制作一个关于AI技术发展趋势的演示文稿",
  "template": "modern",
  "language": "Chinese",
  "n_slides": 5,
  "enable_search": true,
  "export_format": "html",
  "custom_instructions": "请生成专业、美观的演示文稿"
}
```

### 响应示例

```json
{
  "success": true,
  "presentation_id": "uuid",
  "title": "AI技术发展趋势",
  "slides_count": 5,
  "preview_url": "/v3/preview/uuid",
  "edit_url": "/v3/edit/uuid",
  "download_url": "/v3/download/uuid",
  "processing_time": 15.5,
  "message": "成功生成包含5张幻灯片的演示文稿",
  "steps_completed": ["outline", "search", "content", "html", "preview"]
}
```

## 使用方法

### 1. 启动服务器

```bash
cd servers/fastapi
python server.py --port 8000
```

### 2. 测试API

```bash
python test_v3_api.py
```

### 3. 使用流式API

```javascript
const eventSource = new EventSource('/api/v3/ppt/streaming/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    user_input: "你的演示文稿内容",
    template: "modern",
    language: "Chinese",
    enable_search: true
  })
});

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log(`步骤: ${data.step}, 状态: ${data.status}, 进度: ${data.progress}%`);
};
```

## 开发状态

### 已完成
- ✅ V3整体架构设计
- ✅ 目录结构和基础文件
- ✅ 核心模型定义
- ✅ 增强Agent框架
- ✅ 内容搜索服务
- ✅ HTML设计专家
- ✅ DSL系统
- ✅ API端点
- ✅ 流式生成
- ✅ 基础测试

### 待完善
- 🔄 实际LLM集成
- 🔄 真实搜索API集成
- 🔄 HTML编译实现
- 🔄 导出功能实现
- 🔄 前端界面
- 🔄 错误处理优化

## 技术栈

- **后端**: FastAPI + SQLModel + Redis
- **AI服务**: OpenAI/Anthropic/Google + 自定义角色扮演
- **前端**: Next.js + React + Tailwind CSS
- **导出**: Puppeteer (PDF) + python-pptx (PPTX)
- **流式处理**: Server-Sent Events (SSE)

## 与V2的对比

| 特性 | V2 | V3 |
|------|----|----|
| 输入方式 | Markdown | 文本 + Markdown |
| 处理方式 | 批量处理 | 步骤化流式处理 |
| 模板系统 | 固定React模板 | 动态DSL生成 |
| HTML生成 | 模板渲染 | 专业角色扮演 |
| 搜索功能 | 基础 | 增强搜索服务 |
| 导出功能 | 基础 | 多格式导出 |
| 用户体验 | 静态 | 实时流式反馈 |

## 下一步计划

1. **完善核心功能**: 实现真实的LLM集成和搜索服务
2. **优化HTML生成**: 完善专业角色扮演系统
3. **增强DSL系统**: 实现更灵活的布局生成
4. **开发前端界面**: 创建V3专用的用户界面
5. **性能优化**: 优化流式处理和响应速度
6. **测试完善**: 添加更多测试用例和错误处理

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

Apache 2.0
