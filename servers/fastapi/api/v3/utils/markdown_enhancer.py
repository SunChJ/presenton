"""
V3增强Markdown解析器
基于V2版本改进的Markdown解析功能
"""

import re
from typing import List, Dict, Any, Optional
from ..models.v3_requests import V3PresentationRequest


class EnhancedMarkdownParser:
    """增强的Markdown解析器"""
    
    def __init__(self):
        # 继承V2的解析能力
        from services.v2.markdown_parser import MarkdownOutlineParser
        self.base_parser = MarkdownOutlineParser()
        
        # 增强的内容类型识别
        self.enhanced_content_patterns = {
            "intro": [
                "介绍", "概述", "什么是", "关于", "背景", "前言", "欢迎",
                "introduction", "overview", "about", "background", "welcome"
            ],
            "bullets": [
                "要点", "列表", "包括", "特点", "优势", "功能", "步骤", "方法",
                "points", "features", "benefits", "steps", "methods", "includes"
            ],
            "comparison": [
                "对比", "比较", "vs", "差异", "优劣", "选择", "分析",
                "comparison", "versus", "difference", "pros and cons", "analysis"
            ],
            "chart": [
                "图表", "数据", "统计", "趋势", "分析", "报告",
                "chart", "graph", "data", "statistics", "trends", "analysis", "report"
            ],
            "quote": [
                "引用", "名言", "观点", "证言", "评价", "反馈",
                "quote", "testimonial", "opinion", "review", "feedback"
            ],
            "conclusion": [
                "总结", "结论", "小结", "要点", "回顾", "展望",
                "conclusion", "summary", "recap", "takeaway", "outlook"
            ],
            "thank_you": [
                "谢谢", "感谢", "联系", "问答", "提问", "讨论",
                "thank", "thanks", "contact", "questions", "q&a", "discussion"
            ]
        }
    
    def parse_user_input(
        self, 
        user_input: str, 
        template: str = "modern"
    ) -> Dict[str, Any]:
        """解析用户输入"""
        
        # 检测输入类型
        input_type = self._detect_input_type(user_input)
        
        if input_type == "markdown":
            # 使用V2的Markdown解析器
            parsed = self.base_parser.parse_markdown_outline(user_input, template)
            return self._convert_v2_to_v3_format(parsed)
        else:
            # 处理纯文本输入
            return self._parse_text_input(user_input, template)
    
    def _detect_input_type(self, user_input: str) -> str:
        """检测输入类型"""
        
        # 检查是否包含Markdown标记
        markdown_indicators = [
            r'^#+\s',  # 标题标记
            r'^\*\s',  # 列表标记
            r'^\d+\.\s',  # 数字列表
            r'!\[.*\]\(.*\)',  # 图片标记
            r'\[.*\]\(.*\)',  # 链接标记
        ]
        
        for pattern in markdown_indicators:
            if re.search(pattern, user_input, re.MULTILINE):
                return "markdown"
        
        return "text"
    
    def _convert_v2_to_v3_format(self, v2_parsed) -> Dict[str, Any]:
        """将V2格式转换为V3格式"""
        
        return {
            "title": v2_parsed.title,
            "slides": [
                {
                    "title": slide.title,
                    "content": slide.raw_content,
                    "type": slide.content_type,
                    "suggested_layout": slide.suggested_layout,
                    "content_hints": slide.content_hints
                }
                for slide in v2_parsed.slides
            ],
            "total_slides": v2_parsed.total_slides,
            "template": v2_parsed.template,
            "parsed_type": "markdown"
        }
    
    def _parse_text_input(
        self, 
        user_input: str, 
        template: str
    ) -> Dict[str, Any]:
        """解析纯文本输入"""
        
        # 提取标题
        title = self._extract_title_from_text(user_input)
        
        # 将文本分割为幻灯片
        slides = self._split_text_into_slides(user_input)
        
        # 增强每个幻灯片的内容分析
        enhanced_slides = []
        for i, slide_text in enumerate(slides):
            enhanced_slide = self._enhance_slide_analysis(slide_text, i)
            enhanced_slides.append(enhanced_slide)
        
        return {
            "title": title,
            "slides": enhanced_slides,
            "total_slides": len(enhanced_slides),
            "template": template,
            "parsed_type": "text"
        }
    
    def _extract_title_from_text(self, text: str) -> str:
        """从文本中提取标题"""
        
        lines = text.strip().split('\n')
        
        # 查找第一个非空行作为标题
        for line in lines:
            line = line.strip()
            if line and not line.startswith((' ', '\t')):
                # 限制标题长度
                return line[:50] if len(line) > 50 else line
        
        return "无标题演示文稿"
    
    def _split_text_into_slides(self, text: str) -> List[str]:
        """将文本分割为幻灯片"""
        
        # 基于段落分割
        paragraphs = text.split('\n\n')
        
        # 过滤空段落
        slides = [p.strip() for p in paragraphs if p.strip()]
        
        # 如果段落太少，尝试按句子分割
        if len(slides) < 3:
            sentences = re.split(r'[.!?。！？]\s*', text)
            slides = [s.strip() for s in sentences if s.strip()]
        
        return slides
    
    def _enhance_slide_analysis(
        self, 
        slide_text: str, 
        index: int
    ) -> Dict[str, Any]:
        """增强幻灯片分析"""
        
        # 提取标题
        title = self._extract_slide_title(slide_text, index)
        
        # 分析内容类型
        content_type = self._analyze_enhanced_content_type(slide_text)
        
        # 提取内容提示
        content_hints = self._extract_enhanced_content_hints(slide_text, content_type)
        
        # 建议布局
        suggested_layout = self._suggest_layout_for_type(content_type, index)
        
        return {
            "title": title,
            "content": slide_text,
            "type": content_type,
            "suggested_layout": suggested_layout,
            "content_hints": content_hints,
            "raw_content": slide_text
        }
    
    def _extract_slide_title(self, slide_text: str, index: int) -> str:
        """提取幻灯片标题"""
        
        lines = slide_text.strip().split('\n')
        
        # 查找第一行作为标题
        for line in lines:
            line = line.strip()
            if line:
                # 限制标题长度
                return line[:30] if len(line) > 30 else line
        
        return f"幻灯片 {index + 1}"
    
    def _analyze_enhanced_content_type(self, slide_text: str) -> str:
        """增强的内容类型分析"""
        
        slide_lower = slide_text.lower()
        
        # 计算各种类型的匹配分数
        type_scores = {}
        
        for content_type, keywords in self.enhanced_content_patterns.items():
            score = 0
            for keyword in keywords:
                # 关键词匹配计分
                score += slide_lower.count(keyword.lower()) * 2
                
                # 标题匹配额外加分
                first_line = slide_text.split('\n')[0].lower()
                if keyword.lower() in first_line:
                    score += 5
            
            type_scores[content_type] = score
        
        # 基于结构特征调整分数
        if self._has_bullet_points(slide_text):
            type_scores["bullets"] = type_scores.get("bullets", 0) + 8
        
        if self._has_comparison_structure(slide_text):
            type_scores["comparison"] = type_scores.get("comparison", 0) + 6
        
        if self._has_chart_indicators(slide_text):
            type_scores["chart"] = type_scores.get("chart", 0) + 6
        
        if self._has_quote_structure(slide_text):
            type_scores["quote"] = type_scores.get("quote", 0) + 6
        
        # 位置判断
        if len(slide_text.split('\n')) <= 3:  # 简短内容可能是介绍或总结
            type_scores["intro"] = type_scores.get("intro", 0) + 3
        
        # 返回得分最高的类型，默认为content
        if not type_scores or max(type_scores.values()) == 0:
            return "content"
        
        return max(type_scores, key=type_scores.get)
    
    def _has_bullet_points(self, text: str) -> bool:
        """检测是否包含列表结构"""
        lines = text.split('\n')
        bullet_count = 0
        
        for line in lines:
            line = line.strip()
            if line.startswith(('- ', '* ', '+ ')) or re.match(r'^\d+\.\s', line):
                bullet_count += 1
        
        return bullet_count >= 2
    
    def _has_comparison_structure(self, text: str) -> bool:
        """检测是否包含对比结构"""
        text_lower = text.lower()
        comparison_indicators = [
            "vs", "对比", "比较", "优势", "劣势", "差异", 
            "pros", "cons", "advantage", "disadvantage", "versus"
        ]
        
        return any(indicator in text_lower for indicator in comparison_indicators)
    
    def _has_chart_indicators(self, text: str) -> bool:
        """检测是否包含图表指示器"""
        text_lower = text.lower()
        chart_indicators = [
            "图表", "数据", "统计", "趋势", "分析", "报告",
            "chart", "graph", "data", "statistics", "trends"
        ]
        
        return any(indicator in text_lower for indicator in chart_indicators)
    
    def _has_quote_structure(self, text: str) -> bool:
        """检测是否包含引用结构"""
        quote_indicators = ['"', '"', '"', '「', '」', '——', '--']
        return any(indicator in text for indicator in quote_indicators)
    
    def _extract_enhanced_content_hints(
        self, 
        slide_text: str, 
        content_type: str
    ) -> Dict[str, Any]:
        """提取增强的内容提示"""
        
        hints = {
            "content_type": content_type,
            "word_count": len(slide_text.split()),
            "has_lists": self._has_bullet_points(slide_text),
            "has_images": bool(re.search(r'!\[.*\]\(.*\)', slide_text)),
            "has_links": bool(re.search(r'\[.*\]\(.*\)', slide_text))
        }
        
        # 根据内容类型提取特定信息
        if content_type == "bullets":
            hints["bullet_points"] = self._extract_bullet_points(slide_text)
        elif content_type == "comparison":
            hints["comparison_items"] = self._extract_comparison_items(slide_text)
        elif content_type == "chart":
            hints["data_suggestions"] = self._extract_data_suggestions(slide_text)
        
        return hints
    
    def _extract_bullet_points(self, text: str) -> List[str]:
        """提取项目符号要点"""
        bullet_points = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith(('- ', '* ', '+ ')):
                bullet_points.append(line[2:].strip())
            elif re.match(r'^\d+\.\s', line):
                bullet_points.append(re.sub(r'^\d+\.\s', '', line).strip())
        
        return bullet_points[:6]  # 限制最多6个要点
    
    def _extract_comparison_items(self, text: str) -> Dict[str, List[str]]:
        """提取对比项目"""
        # 简单的对比提取逻辑，可以根据需要扩展
        return {
            "left_items": [],
            "right_items": [],
            "comparison_title": "对比分析"
        }
    
    def _extract_data_suggestions(self, text: str) -> List[str]:
        """提取数据建议"""
        data_keywords = [
            "增长", "下降", "上升", "变化", "趋势", "比例", "百分比",
            "growth", "decline", "increase", "change", "trend", "percentage"
        ]
        
        suggestions = []
        text_lower = text.lower()
        
        for keyword in data_keywords:
            if keyword in text_lower:
                suggestions.append(f"包含{keyword}相关的数据可视化")
        
        return suggestions[:3]  # 限制建议数量
    
    def _suggest_layout_for_type(self, content_type: str, index: int) -> str:
        """根据内容类型建议布局"""
        
        # 第一张幻灯片优先使用intro类型
        if index == 0:
            return "intro-slide"
        
        # 根据内容类型匹配布局
        layout_mapping = {
            "intro": "intro-slide",
            "bullets": "list-slide",
            "comparison": "comparison-slide",
            "chart": "chart-slide",
            "quote": "quote-slide",
            "conclusion": "summary-slide",
            "thank_you": "thank-you-slide"
        }
        
        return layout_mapping.get(content_type, "content-slide")
