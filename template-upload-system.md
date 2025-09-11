# Presenton 自定义模板上传系统详解

## 🎯 系统概述

Presenton 的自定义模板上传功能允许用户上传现有的 PPTX 或 PDF 文件，自动解析其布局和样式，并生成可复用的 React 模板组件。整个过程涉及文件解析、视觉识别、HTML转换、React组件生成等多个环节。

## 🔄 完整工作流程

```
用户上传文件 ──────── 文件解析 ──────── 幻灯片处理 ──────── 模板生成 ──────── 保存使用
     │                │               │               │               │
     ▼                ▼               ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  PPTX/PDF    │ │  解压提取    │ │  AI视觉识别   │ │  React组件   │ │  数据库保存  │
│  文件上传    │ │  幻灯片数据  │ │  HTML生成    │ │  代码生成    │ │  模板可用    │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

## 📁 核心文件结构

### 前端文件
```
servers/nextjs/app/(presentation-generator)/custom-template/
├── page.tsx                           # 主页面组件
├── components/
│   ├── FileUploadSection.tsx         # 文件上传区域
│   ├── SaveLayoutModal.tsx           # 保存模板对话框
│   ├── FontManager.tsx               # 字体管理器
│   ├── EachSlide/                    # 幻灯片编辑组件
│   └── APIKeyWarning.tsx             # API密钥警告
├── hooks/
│   ├── useFileUpload.ts              # 文件上传逻辑
│   ├── useSlideProcessing.ts         # 幻灯片处理逻辑
│   ├── useLayoutSaving.ts            # 模板保存逻辑
│   ├── useFontManagement.ts          # 字体管理逻辑
│   └── useAPIKeyCheck.ts             # API密钥检查
└── types/                            # TypeScript类型定义
```

### 后端文件
```
servers/fastapi/api/v1/ppt/endpoints/
├── slide_to_html.py                  # 核心转换API
├── pptx_slides.py                    # PPTX解析API
└── pdf_slides.py                     # PDF解析API

models/sql/
├── template.py                       # 模板元数据模型
└── presentation_layout_code.py       # 布局代码模型
```

## 🎯 详细处理流程

### 1. 文件上传阶段

#### 前端上传组件 (FileUploadSection.tsx)
```typescript
// 支持的文件类型
accept=".pdf,.pptx"

// 文件大小限制
Maximum file size: 100MB

// 上传验证
const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.size <= 100 * 1024 * 1024) { // 100MB限制
        setSelectedFile(file);
    }
}
```

#### 文件类型处理
```typescript
// 支持的文件格式
POWERPOINT_TYPES = [".ppt", ".pptx", ".potx", ".ppsx"]
PDF_TYPES = [".pdf"]

// 根据文件类型选择不同的处理端点
if (fileExtension === ".pdf") {
    endpoint = "/api/v1/ppt/pdf-slides/";
} else if (POWERPOINT_TYPES.includes(fileExtension)) {
    endpoint = "/api/v1/ppt/pptx-slides/";
}
```

### 2. 文件解析阶段

#### PPTX 文件处理 (pptx_slides.py)

```python
# 1. 文件解压和内容提取
async def process_pptx_file(uploaded_file: UploadFile) -> PptxSlidesResponse:
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # 保存上传的文件
        pptx_path = os.path.join(temp_dir, "presentation.pptx")
        with open(pptx_path, "wb") as f:
            f.write(await uploaded_file.read())
        
        # 解压PPTX文件 (实际上是ZIP格式)
        with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # 提取幻灯片数据
        slides_data = []
        slide_files = find_slide_xml_files(temp_dir)
        
        for slide_file in slide_files:
            slide_data = extract_slide_data(slide_file, temp_dir)
            slides_data.append(slide_data)
```

#### 幻灯片数据提取
```python
# 2. XML内容解析
def extract_slide_data(slide_xml_path: str, temp_dir: str) -> SlideData:
    # 读取幻灯片XML内容
    with open(slide_xml_path, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    # 解析XML获取文本和样式信息
    tree = ET.parse(slide_xml_path)
    root = tree.getroot()
    
    # 提取字体信息
    fonts = extract_fonts_from_xml(root)
    normalized_fonts = [normalize_font_family_name(font) for font in fonts]
    
    return SlideData(
        slide_number=slide_number,
        xml_content=xml_content,
        normalized_fonts=normalized_fonts,
        screenshot_url=screenshot_path
    )
```

#### 字体处理和标准化
```python
# 3. 字体名称标准化
def normalize_font_family_name(raw_name: str) -> str:
    # 处理字体名称中的样式后缀 (Bold, Italic, Light等)
    # 例: "MontserratBold" -> "Montserrat"
    
    # 替换分隔符
    name = raw_name.replace("_", " ").replace("-", " ")
    
    # 处理驼峰命名
    name = insert_spaces_in_camel_case(name)
    
    # 移除样式标记
    style_tokens = ["bold", "italic", "light", "medium", "black"]
    for style in style_tokens:
        if name.lower().endswith(" " + style):
            name = name[:-(len(style) + 1)]
    
    return name.strip()
```

### 3. 视觉识别阶段

#### 截图生成
```python
# 4. 幻灯片截图生成
async def generate_slide_screenshots(pptx_path: str, output_dir: str):
    # 使用 LibreOffice 或 puppeteer 生成幻灯片截图
    subprocess.run([
        "libreoffice", "--headless", "--convert-to", "png",
        "--outdir", output_dir, pptx_path
    ])
    
    # 返回截图文件路径列表
    return [os.path.join(output_dir, f"slide_{i}.png") for i in range(slide_count)]
```

#### AI 视觉识别转换 (slide_to_html.py)

```python
# 5. 使用 GPT-5 将截图和XML转换为HTML
async def generate_html_from_slide(
    base64_image: str, 
    xml_content: str, 
    fonts: List[str]
) -> str:
    
    client = OpenAI(api_key=api_key)
    
    # 构建输入数据
    data_url = f"data:image/png;base64,{base64_image}"
    fonts_text = f"FONTS: {', '.join(fonts)}" if fonts else ""
    
    input_payload = [
        {"role": "system", "content": GENERATE_HTML_SYSTEM_PROMPT},
        {
            "role": "user", 
            "content": [
                {"type": "input_image", "image_url": data_url},
                {"type": "input_text", "text": f"OXML: \n\n{xml_content}\n{fonts_text}"},
            ],
        },
    ]
    
    # 调用 GPT-5 Responses API
    response = client.responses.create(
        model="gpt-5",
        input=input_payload,
        reasoning={"effort": "high"},
        text={"verbosity": "low"},
    )
    
    return response.output_text
```

#### HTML到React转换
```python
# 6. HTML转换为TSX React组件
async def generate_react_component_from_html(
    html_content: str, 
    image_base64: str = None
) -> str:
    
    input_payload = [
        {"role": "system", "content": HTML_TO_REACT_SYSTEM_PROMPT},
        {"role": "user", "content": [
            {"type": "input_text", "text": f"HTML INPUT:\n{html_content}"}
        ]},
    ]
    
    if image_base64:
        # 添加图片作为视觉参考
        input_payload[1]["content"].insert(0, {
            "type": "input_image", 
            "image_url": f"data:image/png;base64,{image_base64}"
        })
    
    response = client.responses.create(
        model="gpt-5",
        input=input_payload,
        reasoning={"effort": "minimal"},
        text={"verbosity": "low"},
    )
    
    # 清理生成的代码
    react_content = response.output_text
    react_content = react_content.replace("```tsx", "").replace("```", "")
    
    # 过滤import/export语句
    filtered_lines = []
    for line in react_content.split('\n'):
        if not line.strip().startswith(('import ', 'export ')):
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)
```

### 4. 前端处理逻辑

#### 幻灯片处理Hook (useSlideProcessing.ts)

```typescript
// 7. 前端处理流程控制
const processSlideToHtml = async (slide: SlideData, index: number) => {
    // 更新状态为处理中
    setSlides(prev => prev.map((s, i) => 
        i === index ? { ...s, processing: true, error: undefined } : s
    ));

    try {
        // 调用后端HTML转换API
        const response = await fetch("/api/v1/ppt/slide-to-html/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                image: slide.screenshot_url,
                xml: slide.xml_content,
                fonts: slide.normalized_fonts ?? [],
            }),
        });

        const htmlData = await response.json();

        // 更新成功状态
        setSlides(prev => prev.map((s, i) => 
            i === index ? {
                ...s,
                processing: false,
                processed: true,
                html: htmlData.html,
            } : s
        ));

        // 自动处理下一张幻灯片 (带1秒延迟)
        const nextIndex = index + 1;
        if (nextIndex < slides.length && !slides[nextIndex].processed) {
            setTimeout(() => {
                processSlideToHtml(slides[nextIndex], nextIndex);
            }, 1000);
        }

    } catch (error) {
        // 错误处理
        setSlides(prev => prev.map((s, i) => 
            i === index ? {
                ...s,
                processing: false,
                processed: false,
                error: error.message,
            } : s
        ));
    }
};
```

#### 模板保存Hook (useLayoutSaving.ts)

```typescript
// 8. 模板保存逻辑
const saveLayout = async (layoutName: string, description: string): Promise<string> => {
    const presentationId = uuidv4();
    const reactComponents = [];

    // 收集字体URL
    const FontUrls = [
        ...UploadedFonts.map(font => font.fontUrl),
        ...fontsData?.internally_supported_fonts?.map(f => f.google_fonts_url) || []
    ];

    // 将每张幻灯片转换为React组件
    for (let i = 0; i < slides.length; i++) {
        const slide = slides[i];
        
        // 调用HTML到React转换API
        const response = await fetch("/api/v1/ppt/html-to-react/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                html: slide.html,
                image: slide.screenshot_url,
            }),
        });

        const data = await response.json();

        reactComponents.push({
            presentation: presentationId,
            layout_id: `${slide.slide_number}`,
            layout_name: `Slide${slide.slide_number}`,
            layout_code: data.react_component,
            fonts: FontUrls,
        });
    }

    // 保存模板元数据
    await fetch("/api/v1/ppt/template-management/templates", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            id: presentationId,
            name: layoutName,
            description: description,
        }),
    });

    // 批量保存React组件
    await fetch("/api/v1/ppt/template-management/save-templates", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ layouts: reactComponents }),
    });

    return presentationId;
};
```

### 5. 数据库存储

#### 模板元数据存储 (TemplateModel)
```python
# 9. 模板基本信息
class TemplateModel(SQLModel, table=True):
    __tablename__ = "templates"
    
    id: uuid.UUID = Field(primary_key=True)        # 模板UUID
    name: str = Field(description="模板名称")         # 用户指定的名称
    description: Optional[str] = Field(default=None) # 模板描述
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
```

#### 布局代码存储 (PresentationLayoutCodeModel)
```python
# 10. React组件代码存储
class PresentationLayoutCodeModel(SQLModel, table=True):
    __tablename__ = "presentation_layout_codes"
    
    id: uuid.UUID = Field(primary_key=True)
    presentation: uuid.UUID = Field(foreign_key="templates.id")  # 模板ID
    layout_id: str = Field(description="布局标识符")               # 如: "1", "2", "3"
    layout_name: str = Field(description="布局名称")              # 如: "Slide1", "Slide2"
    layout_code: str = Field(description="TSX组件代码")           # React组件代码
    fonts: Optional[List[str]] = Field(default=None)            # 字体URL列表
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)
```

## 🔧 关键API接口

### 文件解析接口

#### 1. PPTX文件解析
```http
POST /api/v1/ppt/pptx-slides/
Content-Type: multipart/form-data

Form Data:
- file: [PPTX文件]

返回: PptxSlidesResponse
{
    "success": true,
    "slides": [
        {
            "slide_number": 1,
            "screenshot_url": "/app_data/images/uuid/slide_1.png",
            "xml_content": "<p:sld xmlns:p=...>",
            "normalized_fonts": ["Montserrat", "Open Sans"]
        }
    ],
    "total_slides": 5,
    "fonts": {
        "internally_supported_fonts": [
            {
                "name": "Open Sans",
                "google_fonts_url": "https://fonts.googleapis.com/css2?family=Open+Sans"
            }
        ],
        "not_supported_fonts": ["Custom Corporate Font"]
    }
}
```

#### 2. PDF文件解析
```http
POST /api/v1/ppt/pdf-slides/
Content-Type: multipart/form-data

Form Data:
- file: [PDF文件]

返回: 类似PPTX的响应格式，但XML内容为PDF文本提取结果
```

### 转换处理接口

#### 3. 幻灯片转HTML
```http
POST /api/v1/ppt/slide-to-html/
Content-Type: application/json

{
    "image": "/app_data/images/uuid/slide_1.png",
    "xml": "<p:sld xmlns:p=...>",
    "fonts": ["Montserrat", "Open Sans"]
}

返回: SlideToHtmlResponse
{
    "success": true,
    "html": "<div class=\"slide-container\">...</div>"
}
```

#### 4. HTML转React组件
```http
POST /api/v1/ppt/html-to-react/
Content-Type: application/json

{
    "html": "<div class=\"slide-container\">...</div>",
    "image": "/app_data/images/uuid/slide_1.png"  // 可选的视觉参考
}

返回: HtmlToReactResponse
{
    "success": true,
    "react_component": "const SlideComponent = ({ data }) => { return (<div>...</div>); }",
    "message": "React component generated successfully"
}
```

### 模板管理接口

#### 5. 创建模板元数据
```http
POST /api/v1/ppt/template-management/templates
Content-Type: application/json

{
    "id": "uuid-string",
    "name": "我的公司模板",
    "description": "基于公司品牌指南的演示模板"
}

返回: TemplateCreateResponse
{
    "success": true,
    "template": {
        "id": "uuid-string",
        "name": "我的公司模板",
        "description": "基于公司品牌指南的演示模板",
        "created_at": "2024-12-11T10:00:00Z"
    }
}
```

#### 6. 批量保存模板组件
```http
POST /api/v1/ppt/template-management/save-templates
Content-Type: application/json

{
    "layouts": [
        {
            "presentation": "template-uuid",
            "layout_id": "1",
            "layout_name": "Slide1",
            "layout_code": "const Slide1 = ({ data }) => { return (<div>...</div>); }",
            "fonts": ["https://fonts.googleapis.com/css2?family=Open+Sans"]
        }
        // ... 更多幻灯片组件
    ]
}

返回: SaveLayoutsResponse
{
    "success": true,
    "saved_count": 5,
    "message": "Successfully saved 5 layout(s)"
}
```

#### 7. 获取自定义模板摘要
```http
GET /api/v1/ppt/template-management/summary

返回: GetPresentationSummaryResponse
{
    "success": true,
    "presentations": [
        {
            "presentation_id": "template-uuid",
            "layout_count": 5,
            "last_updated_at": "2024-12-11T10:05:00Z",
            "template": {
                "id": "template-uuid",
                "name": "我的公司模板",
                "description": "基于公司品牌指南的演示模板",
                "created_at": "2024-12-11T10:00:00Z"
            }
        }
    ],
    "total_presentations": 1,
    "total_layouts": 5
}
```

## 📊 数据流转详解

### 上传到可用的完整链路

```
用户上传PPTX ────────────────── 文件解析 ────────────────── AI处理 ────────────────── 模板保存
      │                         │                        │                        │
      ▼                         ▼                        ▼                        ▼
┌─────────────┐         ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│ FormData:   │────────▶│ 解压PPTX    │────────▶│ GPT-5视觉   │────────▶│ 数据库存储   │
│ - file.pptx │         │ 提取XML     │         │ HTML生成    │         │ - templates │
│ - 100MB限制 │         │ 生成截图    │         │ React转换   │         │ - layout_codes│
└─────────────┘         │ 字体分析    │         │ 代码清理    │         │ - 模板可选择 │
                        └─────────────┘         └─────────────┘         └─────────────┘
        │                         │                        │                        │
        ▼                         ▼                        ▼                        ▼
    前端上传              后端文件处理              AI视觉识别               数据库持久化
```

### 核心数据结构转换

```
PPTX文件 ──────────── SlideData ──────────── HTML字符串 ──────────── React组件代码
    │                    │                    │                       │
    ├─ slide_1.xml      ├─ slide_number: 1   ├─ <div class="...">    ├─ const Slide1 = 
    ├─ slide_2.xml      ├─ xml_content       ├─   <h1>Title</h1>     │   ({ data }) => {
    └─ slide_3.xml      ├─ screenshot_url    ├─   <p>Content</p>     │     return (
                        └─ normalized_fonts   └─ </div>               │       <div>...</div>
                                                                     │     );
                                                                     └─   };
```

## 🔍 技术亮点和优势

### 1. **智能视觉识别**
- 使用 GPT-5 Responses API 进行高质量的视觉理解
- 结合XML结构信息和视觉截图，确保转换准确性
- 支持复杂布局、图片、图表等多种元素

### 2. **字体处理机制**
- 智能字体名称标准化，处理各种命名变体
- 自动匹配Google Fonts，降低字体依赖问题
- 支持自定义字体上传和管理

### 3. **渐进式处理**
- 逐张幻灯片处理，避免系统过载
- 错误重试机制，提高成功率
- 实时进度反馈，优化用户体验

### 4. **组件化架构**
- 生成的React组件可直接在模板系统中使用
- 保持与内置模板一致的接口和数据结构
- 支持动态数据注入和样式定制

### 5. **容错设计**
- 多层错误处理和重试机制
- 部分失败不影响整体流程
- 详细的错误信息和恢复建议

这套上传模板系统展现了现代AI应用的完整链路：从文件处理、视觉识别、代码生成到最终的模板复用，每个环节都有完善的技术实现和用户体验设计。