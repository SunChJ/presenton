import re
from typing import List, Dict, Any
from models.v2.markdown_ppt_request import ParsedSlideOutline, ParsedMarkdownOutline


class MarkdownOutlineParser:
    """Markdown大纲解析器
    
    负责将用户提供的Markdown格式大纲解析成结构化的幻灯片数据
    """
    
    def __init__(self):
        # 定义不同内容类型的关键词匹配规则
        self.content_type_patterns = {
            "intro": [
                "介绍", "概述", "什么是", "关于", "背景", "前言", 
                "introduction", "overview", "about", "background"
            ],
            "bullets": [
                "要点", "列表", "包括", "特点", "优势", "功能", "步骤",
                "points", "features", "benefits", "steps", "includes"
            ],
            "comparison": [
                "对比", "比较", "vs", "差异", "优劣", "选择",
                "comparison", "versus", "difference", "pros and cons"
            ],
            "image_content": [
                "案例", "示例", "图表", "数据", "展示", "演示",
                "example", "case", "chart", "data", "demo", "showcase"
            ],
            "quote": [
                "引用", "名言", "观点", "证言", "评价",
                "quote", "testimonial", "opinion", "review"
            ],
            "conclusion": [
                "总结", "结论", "小结", "要点", "回顾",
                "conclusion", "summary", "recap", "takeaway"
            ],
            "thank_you": [
                "谢谢", "感谢", "联系", "问答", "提问",
                "thank", "contact", "questions", "q&a"
            ]
        }
    
    def parse_markdown_outline(self, markdown_content: str, template: str = "modern", layout_model=None) -> ParsedMarkdownOutline:
        """解析Markdown大纲为结构化数据
        
        Args:
            markdown_content: 原始Markdown内容
            template: 目标模板类型
            layout_model: 模板布局信息（可选，用于智能匹配）
            
        Returns:
            ParsedMarkdownOutline: 解析后的结构化大纲
        """
        # 1. 提取主标题
        main_title = self._extract_main_title(markdown_content)
        
        # 2. 解析幻灯片结构
        slide_sections = self._split_into_slides(markdown_content)
        
        # 3. 处理每个幻灯片段落
        parsed_slides = []
        for i, section in enumerate(slide_sections):
            parsed_slide = self._parse_slide_section(section, i, template, layout_model)
            parsed_slides.append(parsed_slide)
        
        return ParsedMarkdownOutline(
            title=main_title,
            slides=parsed_slides,
            total_slides=len(parsed_slides),
            template=template
        )
    
    def _extract_main_title(self, markdown_content: str) -> str:
        """提取主标题"""
        lines = markdown_content.strip().split('\n')
        
        # 查找第一个 # 标题
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        
        # 如果没找到，使用第一行非空内容
        for line in lines:
            line = line.strip()
            if line:
                return line
        
        return "无标题演示文稿"
    
    def _split_into_slides(self, markdown_content: str) -> List[str]:
        """将Markdown内容按幻灯片分割"""
        
        # 按## 或更高级别标题分割
        sections = re.split(r'\n(?=##\s)', markdown_content)
        
        # 过滤掉空白段落和只有主标题的段落
        slide_sections = []
        for section in sections:
            section = section.strip()
            if section and not section.startswith('# '):
                slide_sections.append(section)
            elif section and section.startswith('# ') and '\n' in section:
                # 如果主标题段落还有其他内容，保留除标题外的部分
                content_after_title = '\n'.join(section.split('\n')[1:]).strip()
                if content_after_title:
                    slide_sections.append(content_after_title)
        
        return slide_sections
    
    def _parse_slide_section(self, section: str, index: int, template: str, layout_model=None) -> ParsedSlideOutline:
        """解析单个幻灯片段落"""
        
        lines = section.strip().split('\n')
        
        # 提取标题（第一行## 标题）
        title = "幻灯片 " + str(index + 1)
        for line in lines:
            line = line.strip()
            if line.startswith('## '):
                title = line[3:].strip()
                break
            elif line.startswith('### '):
                title = line[4:].strip()
                break
        
        # 分析内容类型
        content_type = self._detect_content_type(section)
        
        # 智能匹配布局类型
        suggested_layout = self._match_layout_by_content(content_type, section, index, template, layout_model)
        
        # 生成内容提示
        content_hints = self._generate_content_hints(section, content_type)
        
        return ParsedSlideOutline(
            title=title,
            content_type=content_type,
            raw_content=section,
            suggested_layout=suggested_layout,
            content_hints=content_hints
        )
    
    def _detect_content_type(self, section: str) -> str:
        """检测内容类型"""
        
        section_lower = section.lower()
        
        # 统计各种类型的匹配分数
        type_scores = {}
        
        for content_type, keywords in self.content_type_patterns.items():
            score = 0
            for keyword in keywords:
                # 关键词匹配计分
                score += section_lower.count(keyword.lower()) * 2
                
                # 标题匹配额外加分
                if keyword.lower() in section_lower.split('\n')[0].lower():
                    score += 5
            
            type_scores[content_type] = score
        
        # 基于结构特征调整分数
        if self._has_bullet_points(section):
            type_scores["bullets"] = type_scores.get("bullets", 0) + 8
        
        if self._has_comparison_structure(section):
            type_scores["comparison"] = type_scores.get("comparison", 0) + 6
        
        if self._has_quote_structure(section):
            type_scores["quote"] = type_scores.get("quote", 0) + 6
        
        # 位置判断
        lines = section.strip().split('\n')
        if len(lines) <= 3:  # 简短内容可能是介绍或总结
            type_scores["intro"] = type_scores.get("intro", 0) + 3
        
        # 返回得分最高的类型，默认为bullets
        if not type_scores or max(type_scores.values()) == 0:
            return "bullets"
        
        return max(type_scores, key=type_scores.get)
    
    def _has_bullet_points(self, section: str) -> bool:
        """检测是否包含列表结构"""
        lines = section.split('\n')
        bullet_count = 0
        
        for line in lines:
            line = line.strip()
            if line.startswith(('- ', '* ', '+ ')) or re.match(r'^\d+\.\s', line):
                bullet_count += 1
        
        return bullet_count >= 2
    
    def _has_comparison_structure(self, section: str) -> bool:
        """检测是否包含对比结构"""
        section_lower = section.lower()
        comparison_indicators = [
            "vs", "对比", "比较", "优势", "劣势", "差异", 
            "pros", "cons", "advantage", "disadvantage"
        ]
        
        return any(indicator in section_lower for indicator in comparison_indicators)
    
    def _has_quote_structure(self, section: str) -> bool:
        """检测是否包含引用结构"""
        quote_indicators = ['"', '"', '"', '「', '」', '——', '--']
        return any(indicator in section for indicator in quote_indicators)
    
    def _generate_content_hints(self, section: str, content_type: str) -> Dict[str, Any]:
        """根据内容类型和原始内容生成内容提示"""
        
        hints = {
            "content_type": content_type,
            "word_count": len(section.split()),
            "has_lists": self._has_bullet_points(section),
        }
        
        # 提取关键信息
        if content_type == "bullets":
            hints["bullet_points"] = self._extract_bullet_points(section)
        
        elif content_type == "comparison":
            hints["comparison_items"] = self._extract_comparison_items(section)
        
        elif content_type == "intro":
            hints["intro_elements"] = self._extract_intro_elements(section)
        
        elif content_type == "image_content":
            hints["visual_suggestions"] = self._extract_visual_suggestions(section)
        
        return hints
    
    def _extract_bullet_points(self, section: str) -> List[str]:
        """提取项目符号要点"""
        bullet_points = []
        lines = section.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith(('- ', '* ', '+ ')):
                bullet_points.append(line[2:].strip())
            elif re.match(r'^\d+\.\s', line):
                bullet_points.append(re.sub(r'^\d+\.\s', '', line).strip())
        
        return bullet_points[:6]  # 限制最多6个要点
    
    def _extract_comparison_items(self, section: str) -> Dict[str, List[str]]:
        """提取对比项目"""
        # 简单的对比提取逻辑，可以根据需要扩展
        return {
            "left_items": [],
            "right_items": [],
            "comparison_title": "对比分析"
        }
    
    def _extract_intro_elements(self, section: str) -> Dict[str, str]:
        """提取介绍元素"""
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        
        return {
            "main_description": ' '.join(lines[1:3]) if len(lines) > 1 else "",
            "key_points": lines[1:4] if len(lines) > 1 else []
        }
    
    def _extract_visual_suggestions(self, section: str) -> List[str]:
        """提取视觉建议"""
        visual_keywords = [
            "图表", "数据", "案例", "示例", "演示", "展示",
            "chart", "graph", "data", "example", "demo", "showcase"
        ]
        
        suggestions = []
        section_lower = section.lower()
        
        for keyword in visual_keywords:
            if keyword in section_lower:
                suggestions.append(f"包含{keyword}相关的视觉元素")
        
        return suggestions[:3]  # 限制建议数量
    
    def _match_layout_by_content(self, content_type: str, section: str, index: int, template: str, layout_model) -> str:
        """根据内容类型智能匹配布局
        
        Args:
            content_type: 检测到的内容类型
            section: 原始内容段落
            index: 幻灯片索引 
            template: 模板名称
            layout_model: 布局模型信息
            
        Returns:
            str: 匹配的布局ID
        """
        
        if not layout_model or not layout_model.slides:
            # 回退到基本匹配
            return f"{template}:content-slide"
            
        available_layouts = layout_model.slides
        
        # 第一张幻灯片优先使用intro类型
        if index == 0:
            for layout in available_layouts:
                if any(keyword in layout.id.lower() or keyword in layout.name.lower() 
                      for keyword in ["intro", "介绍", "title", "cover"]):
                    return layout.id
        
        # 最后一张幻灯片优先使用thank you类型  
        if content_type == "thank_you":
            for layout in available_layouts:
                if any(keyword in layout.id.lower() or keyword in layout.name.lower()
                      for keyword in ["thank", "谢谢", "contact", "end"]):
                    return layout.id
        
        # 根据内容类型匹配具体布局
        content_layout_mapping = {
            "intro": ["intro", "about", "overview", "介绍", "概述"],
            "bullets": ["content", "bullets", "list", "要点", "列表"],
            "comparison": ["comparison", "vs", "对比", "比较"],
            "image_content": ["product", "showcase", "demo", "案例", "展示"],
            "quote": ["testimonial", "quote", "引用", "证言"],
            "conclusion": ["summary", "conclusion", "总结", "结论"]
        }
        
        target_keywords = content_layout_mapping.get(content_type, ["content", "slide"])
        
        # 尝试精确匹配
        for layout in available_layouts:
            layout_text = (layout.id + " " + layout.name + " " + layout.description).lower()
            for keyword in target_keywords:
                if keyword in layout_text:
                    return layout.id
        
        # 如果没有精确匹配，使用通用内容布局
        for layout in available_layouts:
            if any(keyword in layout.id.lower() or keyword in layout.name.lower()
                  for keyword in ["content", "slide", "general"]):
                return layout.id
        
        # 最终回退：使用第一个可用布局
        return available_layouts[0].id if available_layouts else f"{template}:default-slide"