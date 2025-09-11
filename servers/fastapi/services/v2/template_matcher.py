from typing import Dict, List, Optional
from models.v2.markdown_ppt_request import ParsedSlideOutline, TemplateMatchingResult
from utils.get_layout_by_name import get_layout_by_name


class TemplateModuleMatcher:
    """模板模块智能匹配器
    
    根据解析后的内容类型，智能选择最合适的模板布局组件
    """
    
    def __init__(self):
        # 定义内容类型到布局组件的映射规则
        self.layout_mapping = {
            "modern": {
                "intro": [
                    "modern-intro-slide",
                    "modern-about-company", 
                    "modern-product-overview"
                ],
                "bullets": [
                    "modern-solution-slide",
                    "modern-market-validation",
                    "modern-team-slide"
                ],
                "comparison": [
                    "modern-market-size",
                    "modern-solution-slide"
                ],
                "image_content": [
                    "modern-product-overview",
                    "modern-market-validation"
                ],
                "quote": [
                    "modern-market-validation",
                    "modern-team-slide"
                ],
                "conclusion": [
                    "modern-team-slide",
                    "modern-solution-slide"
                ],
                "thank_you": [
                    "modern-team-slide"
                ]
            },
            "general": {
                "intro": [
                    "general-intro-slide",
                    "general-basic-info"
                ],
                "bullets": [
                    "general-bullet-icons-only",
                    "general-bullet-with-icons",
                    "general-numbered-bullets"
                ],
                "comparison": [
                    "general-chart-with-bullets"
                ],
                "image_content": [
                    "general-metrics-with-image",
                    "general-intro-slide"
                ],
                "quote": [
                    "general-quote-slide"
                ],
                "conclusion": [
                    "general-basic-info"
                ],
                "thank_you": [
                    "general-team-slide"
                ]
            },
            "classic": {
                "intro": ["classic-type1"],
                "bullets": ["classic-type3", "classic-type6"],
                "comparison": ["classic-type7"],
                "image_content": ["classic-type8"],
                "quote": ["classic-type6"],
                "conclusion": ["classic-type3"],
                "thank_you": ["classic-type1"]
            }
        }
    
    async def match_template_modules(
        self, 
        parsed_slides: List[ParsedSlideOutline], 
        template: str = "modern"
    ) -> List[TemplateMatchingResult]:
        """为每张幻灯片匹配最合适的模板布局
        
        Args:
            parsed_slides: 解析后的幻灯片列表
            template: 目标模板类型
            
        Returns:
            List[TemplateMatchingResult]: 匹配结果列表
        """
        
        # 获取模板的可用布局
        template_layouts = await self._get_template_layouts(template)
        
        matching_results = []
        
        for i, slide in enumerate(parsed_slides):
            result = await self._match_single_slide(
                slide, i, template, template_layouts
            )
            matching_results.append(result)
        
        # 优化整体匹配结果，避免重复使用相同布局
        optimized_results = self._optimize_layout_distribution(matching_results)
        
        return optimized_results
    
    async def _get_template_layouts(self, template: str) -> Dict:
        """获取指定模板的所有可用布局"""
        try:
            layout_model = await get_layout_by_name(template)
            return {
                slide.id: slide for slide in layout_model.slides
            }
        except Exception as e:
            print(f"Failed to get template layouts for {template}: {e}")
            return {}
    
    async def _match_single_slide(
        self, 
        slide: ParsedSlideOutline, 
        index: int,
        template: str,
        available_layouts: Dict
    ) -> TemplateMatchingResult:
        """为单张幻灯片匹配布局"""
        
        content_type = slide.content_type
        
        # 获取该内容类型的推荐布局列表
        recommended_layouts = self.layout_mapping.get(template, {}).get(
            content_type, 
            self.layout_mapping.get("general", {}).get(content_type, [])
        )
        
        # 计算匹配分数
        best_match = None
        best_score = 0
        best_reasoning = "默认匹配"
        
        for layout_id in recommended_layouts:
            if layout_id in available_layouts:
                score = self._calculate_match_score(
                    slide, available_layouts[layout_id], content_type
                )
                
                if score > best_score:
                    best_score = score
                    best_match = layout_id
                    best_reasoning = f"基于内容类型'{content_type}'的最佳匹配"
        
        # 如果没有找到合适的，使用默认布局
        if not best_match:
            best_match = self._get_fallback_layout(template, content_type)
            best_score = 0.5
            best_reasoning = f"使用{template}模板的默认布局"
        
        return TemplateMatchingResult(
            slide_index=index,
            matched_layout_id=best_match,
            confidence=min(best_score, 1.0),
            reasoning=best_reasoning
        )
    
    def _calculate_match_score(
        self, 
        slide: ParsedSlideOutline, 
        layout_info: Dict,
        content_type: str
    ) -> float:
        """计算布局匹配分数"""
        
        score = 0.0
        
        # 基础内容类型匹配分数
        base_score = 0.7
        score += base_score
        
        # 根据内容提示调整分数
        hints = slide.content_hints
        
        # 如果有列表内容且布局支持列表，加分
        if hints.get("has_lists") and "bullet" in layout_info.get("name", "").lower():
            score += 0.2
        
        # 根据内容长度调整
        word_count = hints.get("word_count", 0)
        if word_count > 50 and "intro" in layout_info.get("name", "").lower():
            score += 0.1
        elif word_count < 20 and "basic" in layout_info.get("name", "").lower():
            score += 0.1
        
        # 特殊内容类型的额外匹配逻辑
        if content_type == "image_content":
            if any(keyword in layout_info.get("description", "").lower() 
                   for keyword in ["image", "visual", "chart"]):
                score += 0.15
        
        if content_type == "comparison":
            if any(keyword in layout_info.get("name", "").lower() 
                   for keyword in ["comparison", "chart", "metrics"]):
                score += 0.15
        
        return score
    
    def _get_fallback_layout(self, template: str, content_type: str) -> str:
        """获取后备布局"""
        
        fallback_mapping = {
            "modern": "modern-solution-slide",
            "general": "general-bullet-with-icons", 
            "classic": "classic-type3"
        }
        
        return fallback_mapping.get(template, "general-bullet-with-icons")
    
    def _optimize_layout_distribution(
        self, 
        results: List[TemplateMatchingResult]
    ) -> List[TemplateMatchingResult]:
        """优化布局分布，避免过度重复使用相同布局"""
        
        if len(results) <= 1:
            return results
        
        # 统计布局使用频率
        layout_usage = {}
        for result in results:
            layout_id = result.matched_layout_id
            layout_usage[layout_id] = layout_usage.get(layout_id, 0) + 1
        
        # 如果某个布局使用过多，进行调整
        max_usage = max(layout_usage.values())
        if max_usage > len(results) // 2:  # 超过一半的幻灯片使用相同布局
            
            # 找到过度使用的布局
            overused_layouts = [
                layout for layout, count in layout_usage.items() 
                if count > len(results) // 3
            ]
            
            # 为过度使用的布局寻找替代方案
            for i, result in enumerate(results):
                if result.matched_layout_id in overused_layouts and i > 0:
                    # 尝试使用前一个不同的布局或默认布局
                    if results[i-1].matched_layout_id != result.matched_layout_id:
                        continue  # 保持多样性
                    
                    # 寻找替代布局
                    alternative = self._find_alternative_layout(
                        result, results[:i]
                    )
                    
                    if alternative:
                        result.matched_layout_id = alternative
                        result.confidence *= 0.9  # 稍微降低置信度
                        result.reasoning += " (已优化布局分布)"
        
        return results
    
    def _find_alternative_layout(
        self, 
        current_result: TemplateMatchingResult,
        previous_results: List[TemplateMatchingResult]
    ) -> Optional[str]:
        """为过度使用的布局寻找替代方案"""
        
        used_layouts = {r.matched_layout_id for r in previous_results}
        
        # 简单的替代策略：尝试使用其他相似的布局
        current_layout = current_result.matched_layout_id
        
        if "modern" in current_layout:
            alternatives = [
                "modern-product-overview", 
                "modern-market-validation",
                "modern-solution-slide"
            ]
        elif "general" in current_layout:
            alternatives = [
                "general-bullet-with-icons",
                "general-numbered-bullets", 
                "general-basic-info"
            ]
        else:
            alternatives = ["general-bullet-with-icons"]
        
        # 返回第一个未使用的替代布局
        for alt in alternatives:
            if alt not in used_layouts and alt != current_layout:
                return alt
        
        return None