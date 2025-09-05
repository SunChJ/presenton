import re
from typing import List, Dict, Any

from .intent_types import Intent, IntentType


class IntentRecognizer:
    """Intent recognition service"""
    
    # Intent keywords mapping
    INTENT_KEYWORDS = {
        IntentType.CREATE_PRESENTATION: [
            "创建", "生成", "制作", "新建", "做一个", "创建一个", 
            "生成一个", "制作一个", "创建演示", "生成演示", "创建PPT", "生成PPT"
        ],
        IntentType.MODIFY_SLIDE: [
            "修改", "更改", "编辑", "调整", "改变", "更新", 
            "修改页面", "编辑页面", "调整页面", "更改内容"
        ],
        IntentType.ADD_CONTENT: [
            "添加", "加入", "插入", "增加", "加上", 
            "添加内容", "加入图片", "插入图表", "增加文字"
        ],
        IntentType.EXPORT_PRESENTATION: [
            "导出", "保存", "下载", "输出", "生成文件",
            "导出PPT", "保存演示", "下载文件", "输出PDF"
        ],
        IntentType.ANALYZE_CONTENT: [
            "分析", "总结", "提取", "概括", "解释", "理解",
            "分析内容", "总结要点", "提取信息"
        ],
        IntentType.CHAT_QUESTION: [
            "什么", "怎么", "如何", "为什么", "哪里", "谁",
            "什么是", "怎么做", "如何使用", "为什么要"
        ]
    }
    
    def __init__(self):
        pass
    
    async def identify(self, message: str) -> Intent:
        """Identify intent from user message"""
        message_lower = message.lower()
        
        # Calculate confidence scores for each intent
        intent_scores = {}
        
        for intent_type, keywords in self.INTENT_KEYWORDS.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in message_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                # Normalize confidence score (0-1)
                confidence = min(score / len(keywords), 1.0)
                intent_scores[intent_type] = {
                    "confidence": confidence,
                    "matched_keywords": matched_keywords
                }
        
        # Find best matching intent
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1]["confidence"])
            intent_type = best_intent[0]
            confidence = best_intent[1]["confidence"]
            
            # Extract parameters based on intent
            parameters = await self._extract_parameters(message, intent_type)
            
            return Intent(
                type=intent_type,
                confidence=confidence,
                parameters=parameters
            )
        
        # Default to unknown intent
        return Intent(
            type=IntentType.UNKNOWN,
            confidence=0.0,
            parameters={}
        )
    
    async def _extract_parameters(self, message: str, intent_type: IntentType) -> Dict[str, Any]:
        """Extract parameters from message based on intent"""
        parameters = {}
        
        if intent_type == IntentType.CREATE_PRESENTATION:
            # Extract topic/subject
            topic_patterns = [
                r"关于(.+?)的演示",
                r"(.+?)的PPT",
                r"主题是(.+)",
                r"讲(.+?)的",
                r"介绍(.+?)的"
            ]
            
            for pattern in topic_patterns:
                match = re.search(pattern, message)
                if match:
                    parameters["topic"] = match.group(1).strip()
                    break
            
            # Extract number of slides
            slide_match = re.search(r"(\d+)页|(\d+)张", message)
            if slide_match:
                parameters["n_slides"] = int(slide_match.group(1) or slide_match.group(2))
        
        elif intent_type == IntentType.MODIFY_SLIDE:
            # Extract slide number
            slide_match = re.search(r"第(\d+)页|第(\d+)张", message)
            if slide_match:
                parameters["slide_number"] = int(slide_match.group(1) or slide_match.group(2))
        
        return parameters