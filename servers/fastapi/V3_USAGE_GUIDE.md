# Presenton V3 使用指南

## 概述

V3版本是基于V2版本的重大改进，实现了你想要的交互逻辑：用户输入 → Agent步骤化执行 → 专业HTML生成 → 流式展示 → 导出功能。

## 核心特性

### 1. 步骤化Agent执行器
V3版本的核心是6步骤的流式执行器：

1. **生成大纲** - 基于用户输入智能生成演示文稿大纲
2. **搜索内容和图片** - 增强内容搜索和图片推荐
3. **生成PPT内容** - 基于V2逻辑生成结构化内容
4. **专业HTML生成** - 角色扮演生成高质量HTML+Tailwind
5. **流式生成展示** - 实时流式预览和进度反馈
6. **导出功能** - 支持HTML/PDF/PPTX多格式导出

### 2. API端点

#### 基础生成API
```http
POST /api/v3/ppt/presentation/generate
Content-Type: application/json

{
  "user_input": "我想制作一个关于人工智能技术发展趋势的演示文稿，包括AI技术概述、当前主要技术方向、应用案例和未来发展趋势",
  "template": "modern",
  "language": "Chinese",
  "n_slides": 5,
  "enable_search": true,
  "export_format": "html",
  "custom_instructions": "请生成专业、美观的演示文稿"
}
```

#### 流式生成API
```http
POST /api/v3/ppt/streaming/generate
Content-Type: application/json

{
  "user_input": "人工智能在教育领域的应用",
  "template": "modern",
  "enable_search": true
}
```

#### 单步执行API
```http
POST /api/v3/ppt/presentation/step
Content-Type: application/json

{
  "step": "outline",
  "user_input": "人工智能技术发展趋势",
  "language": "Chinese"
}
```

### 3. 流式响应格式

V3版本支持Server-Sent Events (SSE)流式响应：

```javascript
// 前端示例
const eventSource = new EventSource('/api/v3/ppt/streaming/generate');

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log(`步骤 ${data.step}: ${data.message}`);
  console.log(`进度: ${data.progress}%`);
};
```

### 4. 响应数据结构

#### V3PresentationResponse
```typescript
interface V3PresentationResponse {
  presentation_id: string;
  title: string;
  slides: SlideData[];
  html_content: string;
  export_urls: {
    html: string;
    pdf: string;
    pptx: string;
  };
  processing_time: number;
  created_at: string;
}
```

#### V3StreamingResponse
```typescript
interface V3StreamingResponse {
  step: string;
  success: boolean;
  data?: any;
  message: string;
  progress: number;
  next_step?: string;
}
```

## 测试和验证

### 运行测试脚本
```bash
cd servers/fastapi
python test_v3_simple.py
```

### 启动服务器
```bash
cd servers/fastapi
python server.py --port 8000
```

### 使用测试脚本
```bash
cd servers/fastapi
python test_v3_api.py
```

## 架构优势

### 1. 模块化设计
- **清晰的分层架构**：API层 → 服务层 → 工具层
- **独立的服务组件**：每个功能模块独立开发和测试
- **灵活的依赖注入**：支持服务间的松耦合

### 2. 流式处理
- **实时反馈**：用户可以看到每个步骤的执行进度
- **错误恢复**：单个步骤失败不影响整个流程
- **资源优化**：按需加载，避免一次性处理大量数据

### 3. 专业角色扮演
- **HTML设计专家**：模拟专业设计师生成高质量HTML
- **智能布局生成**：基于内容类型自动选择最佳布局
- **样式优化**：生成符合Tailwind CSS最佳实践的代码

### 4. 增强的DSL系统
- **声明式配置**：通过DSL描述演示文稿结构
- **动态生成**：运行时生成HTML和样式
- **主题支持**：支持多种主题和自定义样式

## 与V2版本的差异

| 特性 | V2版本 | V3版本 |
|------|--------|--------|
| 执行方式 | 单次生成 | 步骤化流式执行 |
| 用户交互 | 等待结果 | 实时进度反馈 |
| 内容搜索 | 基础支持 | 增强搜索服务 |
| HTML生成 | 模板渲染 | 专业角色扮演 |
| 导出格式 | HTML/PDF | HTML/PDF/PPTX |
| 错误处理 | 简单错误 | 步骤级错误恢复 |

## 部署和使用

### 环境要求
- Python 3.11+
- FastAPI
- SQLAlchemy
- ChromaDB
- 支持的LLM服务（OpenAI, Gemini, Anthropic等）

### 配置说明
确保在环境变量或配置文件中设置：
```bash
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
# 其他LLM服务配置...
```

### 前端集成
V3版本完全兼容现有的前端架构，可以通过以下方式集成：
1. 更新API调用URL为V3端点
2. 添加流式响应处理逻辑
3. 实现实时进度显示

## 总结

V3版本在保持V2版本优势的同时，提供了更强的交互性和实时反馈能力。通过步骤化的执行流程和专业的HTML生成，V3版本能够提供更好的用户体验和更高质量的演示文稿输出。
