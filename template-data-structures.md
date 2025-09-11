# Template 系统数据结构流动详解

## 🔄 完整数据流动图

```
用户输入 ──────────────────── API请求 ──────────────── 模板解析 ──────────────── 内容生成 ──────────────── 最终渲染
   │                          │                        │                        │                        │
   ▼                          ▼                        ▼                        ▼                        ▼
┌──────────────┐        ┌──────────────┐        ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│GenerateRequest│       │LayoutModel   │       │ SlideSchema  │       │ SlideContent │       │RenderedSlide │
│   Request    │  ───▶ │PresentationLayout│ ───▶│  Definition  │  ───▶ │   Generated  │  ───▶ │   Component  │
└──────────────┘        └──────────────┘        └──────────────┘        └──────────────┘        └──────────────┘
```

## 📋 1. 用户请求阶段 - GeneratePresentationRequest

```
POST /api/v1/ppt/presentation/generate
{
    "prompt": "Introduction to Machine Learning",     // 🎯 用户输入的主题
    "n_slides": 8,                                   // 📊 幻灯片数量
    "language": "Chinese",                           // 🌐 语言设置
    "template": "general",                           // 🎨 选择的模板名称
    "export_as": "pptx"                             // 📦 导出格式
}

↓ 转换为内部数据结构

class GeneratePresentationRequest:
    prompt: str                    # 用户主题描述
    n_slides: int = 8             # 幻灯片数量 (5-15)
    language: str = "English"      # 展示语言
    template: str = "general"      # 模板名称
    export_as: str = "pptx"       # 导出格式 (pptx/pdf)
```

## 📋 2. 模板结构获取阶段 - PresentationLayoutModel

```
get_layout_by_name("general") 调用流程:

步骤1: HTTP 请求前端
GET http://localhost:3001/api/layout?group=general

步骤2: Puppeteer 访问 Schema 页面
访问: http://localhost:3001/schema?group=general

步骤3: 前端返回的原始数据
<div data-layouts='[
    {
        "id": "general-intro-slide",
        "name": "Intro Slide", 
        "description": "介绍幻灯片布局",
        "json_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Main title",
                    "minLength": 3,
                    "maxLength": 40
                },
                "description": {
                    "type": "string", 
                    "description": "Main description",
                    "minLength": 10,
                    "maxLength": 150
                },
                "presenterName": {
                    "type": "string",
                    "description": "Presenter name",
                    "minLength": 2,
                    "maxLength": 50
                },
                "image": {
                    "type": "object",
                    "properties": {
                        "__image_url__": {"type": "string"},
                        "__image_prompt__": {"type": "string"}
                    }
                }
            },
            "required": ["title", "description"]
        }
    },
    {
        "id": "general-content-bullets",
        "name": "Content with Bullets",
        "description": "带项目符号的内容幻灯片",
        "json_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "bullets": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Bullet points"
                },
                "subtitle": {"type": "string"}
            }
        }
    }
]'>

步骤4: 转换为结构化模型
class PresentationLayoutModel:
    name: str = "general"                    # 模板名称
    ordered: bool = False                    # 是否要求顺序
    slides: List[SlideLayoutModel] = [       # 幻灯片类型列表
        SlideLayoutModel(
            id="general-intro-slide",
            name="Intro Slide", 
            description="介绍幻灯片布局",
            json_schema={...}                # JSON Schema 定义
        ),
        SlideLayoutModel(
            id="general-content-bullets",
            name="Content with Bullets",
            description="带项目符号的内容",
            json_schema={...}
        )
        # ... 更多幻灯片类型
    ]
```

## 📋 3. 大纲生成阶段 - PresentationOutlineModel  

```
LLM 调用: generate_ppt_outline()
输入参数:
- prompt: "Introduction to Machine Learning"
- n_slides: 8
- language: "Chinese" 
- available_layouts: PresentationLayoutModel

LLM 返回的 JSON 流:
{
    "title": "机器学习入门介绍",
    "slides": [
        {
            "title": "什么是机器学习",
            "body": "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习模式...",
            "slide_type": "general-intro-slide"     # 👈 关键: 指定使用的布局类型
        },
        {
            "title": "机器学习的主要类型", 
            "body": "监督学习、无监督学习、强化学习的概念和应用场景",
            "slide_type": "general-content-bullets"
        },
        {
            "title": "监督学习详解",
            "body": "分类和回归问题的定义、常见算法和实际应用案例",
            "slide_type": "general-content-bullets" 
        }
        // ... 更多幻灯片大纲
    ],
    "notes": [
        "重点讲解机器学习与传统编程的区别",
        "准备实际案例演示不同算法的效果"
    ]
}

↓ 解析为结构化数据

class PresentationOutlineModel:
    title: str = "机器学习入门介绍"
    slides: List[SlideOutlineModel] = [
        SlideOutlineModel(
            title="什么是机器学习",
            body="机器学习是人工智能的一个分支...",
            slide_type="general-intro-slide"    # 布局类型引用
        ),
        SlideOutlineModel(
            title="机器学习的主要类型", 
            body="监督学习、无监督学习...",
            slide_type="general-content-bullets"
        )
        # ...
    ]
    notes: List[str] = ["重点讲解...", "准备实际案例..."]
```

## 📋 4. 幻灯片内容生成阶段 - SlideModel

```
对每张幻灯片调用: get_slide_content_from_type_and_outline()

输入:
- slide_outline: SlideOutlineModel (大纲信息)
- slide_layout: SlideLayoutModel (布局Schema)  
- presentation_outline: PresentationOutlineModel (整体大纲)

处理过程:
1. 根据 slide_type 找到对应的 JSON Schema
2. LLM 根据 Schema 约束生成结构化内容
3. 验证生成的数据是否符合 Schema 要求

示例 - 生成 "general-intro-slide" 内容:

LLM 输入 Schema:
{
    "type": "object",
    "properties": {
        "title": {"type": "string", "minLength": 3, "maxLength": 40},
        "description": {"type": "string", "minLength": 10, "maxLength": 150}, 
        "presenterName": {"type": "string", "minLength": 2, "maxLength": 50},
        "presentationDate": {"type": "string"},
        "image": {
            "type": "object",
            "properties": {
                "__image_url__": {"type": "string"},
                "__image_prompt__": {"type": "string"}  
            }
        }
    }
}

LLM 生成结果:
{
    "title": "什么是机器学习",
    "description": "机器学习是人工智能的一个分支，它使用算法和统计模型让计算机系统能够从数据中学习和改进，而无需明确编程。",
    "presenterName": "AI 专家",
    "presentationDate": "2024年12月", 
    "image": {
        "__image_url__": "",                                    # 稍后由图片服务填充
        "__image_prompt__": "modern computer analyzing data with AI algorithms visualization"
    }
}

↓ 存储为数据库记录

class SlideModel:
    id: UUID = uuid.uuid4()
    presentation_id: UUID                        # 所属演示文稿ID
    slide_number: int = 1                       # 幻灯片序号
    layout_id: str = "general-intro-slide"      # 布局类型ID
    content: Dict = {                           # 结构化内容数据
        "title": "什么是机器学习",
        "description": "机器学习是人工智能...",
        "presenterName": "AI 专家", 
        "presentationDate": "2024年12月",
        "image": {
            "__image_url__": "https://generated-image-url.jpg",
            "__image_prompt__": "modern computer..."
        }
    }
    created_at: datetime
    updated_at: datetime
```

## 📋 5. 图片资源处理阶段 - ImageModel

```
图片生成流程:

输入: image.__image_prompt__ = "modern computer analyzing data with AI algorithms"

调用: ImageGenerationService.generate_image()

根据配置的图片提供商处理:
- DALL-E 3: OpenAI API 调用
- Gemini Flash: Google API 调用  
- Pexels: 搜索相关图片
- Pixabay: 搜索免费图片

返回结果:
{
    "image_url": "https://images.example.com/generated/uuid.jpg",
    "local_path": "/app_data/images/presentation_id/slide_1_image.jpg", 
    "prompt_used": "modern computer analyzing data with AI algorithms",
    "provider": "dall-e-3",
    "generated_at": "2024-12-11T10:30:00Z"
}

更新幻灯片数据:
slide.content["image"]["__image_url__"] = image_result["image_url"]
```

## 📋 6. 前端渲染阶段 - React Component Props

```
前端获取幻灯片数据:
GET /api/v1/ppt/presentation/{presentation_id}/slides

返回数据结构:
{
    "slides": [
        {
            "id": "slide-uuid-1",
            "slide_number": 1,
            "layout_id": "general-intro-slide",
            "content": {
                "title": "什么是机器学习",
                "description": "机器学习是人工智能的一个分支...",
                "presenterName": "AI 专家",
                "presentationDate": "2024年12月",
                "image": {
                    "__image_url__": "https://images.example.com/generated/uuid.jpg",
                    "__image_prompt__": "modern computer analyzing data"
                }
            }
        }
        // ... 更多幻灯片
    ]
}

React 组件渲染:
1. LayoutContext 根据 layout_id 加载对应组件
2. 将 slide.content 作为 props 传递给组件

// IntroSlideLayout 组件接收的 props:
interface IntroSlideLayoutProps {
    data?: {
        title?: string;                    // "什么是机器学习"
        description?: string;              // "机器学习是人工智能的一个分支..."
        presenterName?: string;            // "AI 专家"
        presentationDate?: string;         // "2024年12月"
        image?: {
            __image_url__?: string;        // "https://images.example.com/..."
            __image_prompt__?: string;     // "modern computer analyzing data"
        }
    }
}

// 最终渲染的 JSX:
<div className="w-full h-full bg-white">
    <div className="flex h-full">
        <div className="flex-1">
            <img src="https://images.example.com/generated/uuid.jpg" 
                 alt="modern computer analyzing data" />
        </div>
        <div className="flex-1">
            <h1>{data.title}</h1>          {/* 什么是机器学习 */}
            <p>{data.description}</p>       {/* 机器学习是人工智能... */}
            <div className="presenter-info">
                <span>{data.presenterName}</span>    {/* AI 专家 */}
                <span>{data.presentationDate}</span> {/* 2024年12月 */}
            </div>
        </div>
    </div>
</div>
```

## 📋 7. 导出阶段 - PPTX/PDF 数据

```
导出处理流程:

1. 获取完整演示文稿数据:
class PresentationWithSlides:
    presentation: PresentationModel = {
        "id": "presentation-uuid",
        "title": "机器学习入门介绍", 
        "template": "general",
        "export_format": "pptx"
    }
    slides: List[SlideModel] = [
        SlideModel(...),  # 所有幻灯片数据
        SlideModel(...),
        # ...
    ]

2. PPTX 生成过程:
PptxPresentationCreator.create_presentation()

输入处理:
- 遍历每个 SlideModel
- 根据 layout_id 确定幻灯片布局
- 将 slide.content 数据填充到模板中

生成的 PPTX 结构:
presentation.pptx
├── slide1.xml          # 包含 "什么是机器学习" 的内容和布局
├── slide2.xml          # 包含 "机器学习的主要类型" 的内容
├── media/
│   ├── image1.jpg      # 第1张幻灯片的图片
│   └── image2.jpg      # 第2张幻灯片的图片  
└── theme/
    └── theme1.xml      # general 模板的主题样式

3. 最终返回结果:
{
    "presentation_id": "presentation-uuid",
    "path": "/static/exports/presentation-uuid/机器学习入门介绍.pptx",
    "edit_path": "/presentation?id=presentation-uuid"
}
```

## 🔍 数据结构关键对应关系

```
模板组件                    JSON Schema                    生成内容                    最终渲染
─────────                  ─────────                     ─────────                  ─────────  
layoutId:                 "properties": {               LLM生成:                   React Props:
"general-intro-slide"      "title": {                    "title": "什么是机器学习"    data.title
                            "type": "string"              
                           }                             
                                                        
layoutName:                "description": {              "description":             data.description  
"Intro Slide"              "type": "string"              "机器学习是..."             
                           
React组件:                 "presenterName": {            "presenterName":           data.presenterName
IntroSlideLayout           "type": "string"              "AI 专家"                   
                           
Zod Schema:                "image": {                    "image": {                 data.image
introSlideSchema           "type": "object"              "__image_url__": "...",    
                           }                             "__image_prompt__": "..."   
                                                        }                          
```

## 🌐 完整 API 接口列表

### 📋 模板相关 API

#### 1. 获取所有模板组
```
GET /api/templates
返回: GroupedLayoutsResponse[]

[
    {
        "groupName": "general",
        "files": ["IntroSlideLayout.tsx", "TeamSlideLayout.tsx", ...],
        "settings": {
            "description": "General purpose layouts",
            "ordered": false,
            "default": true
        }
    },
    {
        "groupName": "modern", 
        "files": ["z10TeamSlideLayout.tsx", ...],
        "settings": {
            "description": "Modern design templates",
            "ordered": false,
            "default": false
        }
    }
]
```

#### 2. 获取特定模板的布局结构 (前端内部API)
```
GET /api/layout?group={template_name}
示例: GET /api/layout?group=general

返回: PresentationLayoutModel
{
    "name": "general",
    "ordered": false,
    "slides": [
        {
            "id": "general-intro-slide",
            "name": "Intro Slide",
            "description": "A clean slide layout with title...",
            "json_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "minLength": 3, "maxLength": 40},
                    "description": {"type": "string", "minLength": 10, "maxLength": 150},
                    // ...
                }
            }
        }
        // ... 更多幻灯片类型
    ]
}
```

#### 3. Schema 提取页面 (Puppeteer 访问)
```
GET /schema?group={template_name}
示例: GET /schema?group=general

返回 HTML 页面，包含以下属性:
<div data-layouts='[...]' data-group-settings='{...}'>
```

### 📋 演示文稿生成相关 API

#### 4. 生成完整演示文稿
```
POST /api/v1/ppt/presentation/generate
Content-Type: application/json

请求体:
{
    "prompt": "Introduction to Machine Learning",
    "n_slides": 8,
    "language": "Chinese", 
    "template": "general",
    "export_as": "pptx"
}

返回: PresentationPathAndEditPath
{
    "presentation_id": "uuid-string",
    "path": "/static/exports/presentation-uuid/机器学习入门介绍.pptx",
    "edit_path": "/presentation?id=presentation-uuid"
}
```

#### 5. 获取演示文稿详情
```
GET /api/v1/ppt/presentations/{presentation_id}

返回: PresentationModel
{
    "id": "presentation-uuid",
    "title": "机器学习入门介绍",
    "template": "general",
    "language": "Chinese",
    "export_format": "pptx", 
    "status": "completed",
    "created_at": "2024-12-11T10:00:00Z",
    "updated_at": "2024-12-11T10:05:00Z"
}
```

#### 6. 获取演示文稿的所有幻灯片
```
GET /api/v1/ppt/presentations/{presentation_id}/slides

返回: List[SlideModel]
[
    {
        "id": "slide-uuid-1",
        "presentation_id": "presentation-uuid",
        "slide_number": 1,
        "layout_id": "general-intro-slide", 
        "content": {
            "title": "什么是机器学习",
            "description": "机器学习是人工智能的一个分支...",
            "presenterName": "AI 专家",
            "presentationDate": "2024年12月",
            "image": {
                "__image_url__": "https://images.example.com/generated/uuid.jpg",
                "__image_prompt__": "modern computer analyzing data"
            }
        },
        "created_at": "2024-12-11T10:01:00Z",
        "updated_at": "2024-12-11T10:03:00Z"
    }
    // ... 更多幻灯片
]
```

### 📋 幻灯片操作相关 API

#### 7. 获取单个幻灯片详情
```
GET /api/v1/ppt/slides/{slide_id}

返回: SlideModel
{
    "id": "slide-uuid-1", 
    "presentation_id": "presentation-uuid",
    "slide_number": 1,
    "layout_id": "general-intro-slide",
    "content": { /* 结构化内容数据 */ },
    "created_at": "2024-12-11T10:01:00Z",
    "updated_at": "2024-12-11T10:03:00Z"
}
```

#### 8. 更新幻灯片内容
```
PUT /api/v1/ppt/slides/{slide_id}
Content-Type: application/json

请求体:
{
    "content": {
        "title": "更新后的标题",
        "description": "更新后的描述内容...",
        // ... 其他字段
    }
}

返回: SlideModel (更新后的数据)
```

#### 9. 重新生成幻灯片内容
```
POST /api/v1/ppt/slides/{slide_id}/regenerate
Content-Type: application/json

请求体:
{
    "instruction": "请让内容更加简洁明了"  // 可选的重新生成指示
}

返回: SlideModel (重新生成后的数据)
```

### 📋 图片生成相关 API

#### 10. 生成图片
```
POST /api/v1/ppt/images/generate  
Content-Type: application/json

请求体:
{
    "prompt": "modern computer analyzing data with AI algorithms",
    "provider": "dall-e-3",  // dall-e-3, gemini_flash, pexels, pixabay
    "size": "1024x1024"      // 可选，默认 1024x1024
}

返回:
{
    "image_url": "https://images.example.com/generated/uuid.jpg",
    "local_path": "/app_data/images/uuid.jpg",
    "prompt_used": "modern computer analyzing data with AI algorithms",
    "provider": "dall-e-3",
    "generated_at": "2024-12-11T10:30:00Z"
}
```

#### 11. 获取图片列表
```
GET /api/v1/ppt/images?presentation_id={presentation_id}

返回: List[ImageModel]
[
    {
        "id": "image-uuid",
        "presentation_id": "presentation-uuid", 
        "slide_id": "slide-uuid",
        "image_url": "https://images.example.com/generated/uuid.jpg",
        "local_path": "/app_data/images/uuid.jpg",
        "prompt": "modern computer analyzing data",
        "provider": "dall-e-3",
        "created_at": "2024-12-11T10:30:00Z"
    }
]
```

### 📋 布局和模板管理 API

#### 12. 获取布局详情  
```
GET /api/v1/ppt/layouts/{layout_name}
示例: GET /api/v1/ppt/layouts/general

返回: PresentationLayoutModel (同 /api/layout 返回格式)
```

#### 13. 获取所有可用布局列表
```
GET /api/v1/ppt/layouts

返回: List[LayoutSummary]
[
    {
        "name": "general", 
        "description": "General purpose layouts",
        "slide_count": 9,
        "is_default": true
    },
    {
        "name": "modern",
        "description": "Modern design templates", 
        "slide_count": 7,
        "is_default": false
    }
]
```

### 📋 自定义模板相关 API

#### 14. 上传 PPTX 创建自定义模板
```
POST /api/v1/ppt/template-management/upload
Content-Type: multipart/form-data

Form Data:
- file: [PPTX 文件]
- template_name: "我的自定义模板"
- description: "基于公司品牌的演示模板"

返回:
{
    "presentation_id": "custom-template-uuid",
    "template_name": "我的自定义模板",
    "status": "processing",
    "created_at": "2024-12-11T11:00:00Z"
}
```

#### 15. 获取自定义模板摘要
```
GET /api/v1/ppt/template-management/summary

返回:
{
    "presentations": [
        {
            "presentation_id": "custom-template-uuid",
            "template": {
                "name": "我的自定义模板",
                "description": "基于公司品牌的演示模板"
            },
            "last_updated_at": "2024-12-11T11:05:00Z",
            "slide_count": 6,
            "status": "ready"
        }
    ]
}
```

### 📋 导出相关 API

#### 16. 导出演示文稿
```
POST /api/v1/ppt/presentations/{presentation_id}/export
Content-Type: application/json

请求体:
{
    "format": "pptx",  // pptx 或 pdf
    "quality": "high"  // low, medium, high
}

返回:
{
    "export_id": "export-uuid",
    "download_url": "/static/exports/presentation-uuid/presentation.pptx", 
    "status": "completed",
    "file_size": 2048576,  // 字节
    "created_at": "2024-12-11T10:10:00Z"
}
```

#### 17. 获取导出状态
```
GET /api/v1/ppt/exports/{export_id}/status

返回:
{
    "export_id": "export-uuid",
    "status": "completed",  // pending, processing, completed, failed
    "progress": 100,        // 0-100
    "download_url": "/static/exports/presentation-uuid/presentation.pptx",
    "error_message": null
}
```

## 🔄 API 调用时序图

```
用户请求 ──────────────────── 后端处理 ──────────────────── 数据存储 ──────────────────── 前端渲染
   │                          │                          │                          │
   ├─ POST /generate ────────▶ ├─ GET /api/layout ──────▶ ├─ INSERT Presentation ──▶ ├─ GET /slides
   │                          ├─ LLM Content Gen ──────▶ ├─ INSERT Slides ──────▶ ├─ Load Components  
   │                          ├─ POST /images/gen ─────▶ ├─ INSERT Images ──────▶ ├─ Render JSX
   │                          └─ POST /export ─────────▶ └─ UPDATE Status ──────▶ └─ Display Result
```

这样你就能清楚地看到数据是如何在整个系统中流动和转换的！每个阶段的数据结构都有明确的用途和转换规则，配合完整的API接口，整个系统的交互逻辑就非常清晰了。