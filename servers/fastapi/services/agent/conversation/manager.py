from typing import Dict, List, Any, Optional

from ..core.agent_response import AgentResponse
from ..intent.intent_types import Intent, IntentType


class ConversationManager:
    """Manages conversation flow and response generation"""
    
    FOLLOW_UP_QUESTIONS = {
        IntentType.CREATE_PRESENTATION: [
            "您希望演示文稿有多少页？（建议5-15页）",
            "这个演示的主要受众是什么？",
            "您倾向于什么样的风格？（专业、现代、经典等）"
        ],
        IntentType.MODIFY_SLIDE: [
            "您想修改第几页？",
            "具体要修改哪个部分？（标题、内容、图片等）",
            "希望达到什么效果？"
        ],
        IntentType.ADD_CONTENT: [
            "您想添加什么类型的内容？（文字、图片、图表等）",
            "要添加到第几页？",
            "有具体的内容要求吗？"
        ],
        IntentType.EXPORT_PRESENTATION: [
            "您希望导出为什么格式？（PPTX、PDF）",
            "需要包含演讲备注吗？",
            "有特殊的导出要求吗？"
        ]
    }
    
    def __init__(self):
        pass
    
    async def generate_response(
        self,
        message: str,
        intent: Intent,
        context: List[Dict[str, Any]]
    ) -> AgentResponse:
        """Generate agent response based on intent and context"""
        
        if intent.type == IntentType.CREATE_PRESENTATION:
            return await self._handle_create_presentation(message, intent, context)
        elif intent.type == IntentType.MODIFY_SLIDE:
            return await self._handle_modify_slide(message, intent, context)
        elif intent.type == IntentType.ADD_CONTENT:
            return await self._handle_add_content(message, intent, context)
        elif intent.type == IntentType.EXPORT_PRESENTATION:
            return await self._handle_export_presentation(message, intent, context)
        elif intent.type == IntentType.CHAT_QUESTION:
            return await self._handle_chat_question(message, intent, context)
        else:
            return await self._handle_unknown_intent(message, intent, context)
    
    async def _handle_create_presentation(
        self, message: str, intent: Intent, context: List[Dict]
    ) -> AgentResponse:
        """Handle presentation creation intent"""
        params = intent.parameters
        
        # Check if we have enough parameters
        required_params = ["topic", "n_slides"]
        missing_params = [p for p in required_params if p not in params]
        
        if missing_params:
            follow_up = await self._get_follow_up_question(intent.type, missing_params[0])
            return AgentResponse(
                text=f"好的，我来帮您创建演示文稿。{follow_up}",
                intent=intent.type.value,
                action_required=False,
                follow_up_question=follow_up,
                extracted_params=params,
                confidence=intent.confidence
            )
        
        # All parameters available, ready to create
        return AgentResponse(
            text=f"太好了！我将为您创建一个关于'{params['topic']}'的{params['n_slides']}页演示文稿。",
            intent=intent.type.value,
            action_required=True,
            follow_up_question=None,
            extracted_params=params,
            confidence=intent.confidence
        )
    
    async def _handle_modify_slide(
        self, message: str, intent: Intent, context: List[Dict]
    ) -> AgentResponse:
        """Handle slide modification intent"""
        return AgentResponse(
            text="我可以帮您修改演示文稿。请告诉我具体要修改哪一页的什么内容？",
            intent=intent.type.value,
            action_required=False,
            follow_up_question="您想修改第几页的什么内容？",
            extracted_params=intent.parameters,
            confidence=intent.confidence
        )
    
    async def _handle_add_content(
        self, message: str, intent: Intent, context: List[Dict]
    ) -> AgentResponse:
        """Handle content addition intent"""
        return AgentResponse(
            text="我可以帮您添加内容到演示文稿中。",
            intent=intent.type.value,
            action_required=False,
            follow_up_question="您想添加什么类型的内容？",
            extracted_params=intent.parameters,
            confidence=intent.confidence
        )
    
    async def _handle_export_presentation(
        self, message: str, intent: Intent, context: List[Dict]
    ) -> AgentResponse:
        """Handle presentation export intent"""
        return AgentResponse(
            text="我可以帮您导出演示文稿。",
            intent=intent.type.value,
            action_required=True,
            follow_up_question="您希望导出为什么格式？",
            extracted_params=intent.parameters,
            confidence=intent.confidence
        )
    
    async def _handle_chat_question(
        self, message: str, intent: Intent, context: List[Dict]
    ) -> AgentResponse:
        """Handle general questions"""
        return AgentResponse(
            text="我是您的PPT助手，可以帮您创建、修改和导出演示文稿。您有什么具体需要我帮忙的吗？",
            intent=intent.type.value,
            action_required=False,
            follow_up_question="您需要我帮您做什么？",
            extracted_params=intent.parameters,
            confidence=intent.confidence
        )
    
    async def _handle_unknown_intent(
        self, message: str, intent: Intent, context: List[Dict]
    ) -> AgentResponse:
        """Handle unknown intents"""
        return AgentResponse(
            text="抱歉，我没有完全理解您的意思。我可以帮您创建演示文稿、修改内容、添加元素或导出文件。",
            intent=intent.type.value,
            action_required=False,
            follow_up_question="您希望我帮您做什么？",
            extracted_params=intent.parameters,
            confidence=intent.confidence
        )
    
    async def _get_follow_up_question(self, intent_type: IntentType, missing_param: str) -> str:
        """Get appropriate follow-up question"""
        questions = self.FOLLOW_UP_QUESTIONS.get(intent_type, [])
        
        if intent_type == IntentType.CREATE_PRESENTATION:
            if missing_param == "topic":
                return "请告诉我您想创建什么主题的演示文稿？"
            elif missing_param == "n_slides":
                return "您希望演示文稿有多少页？（建议5-15页）"
        
        return questions[0] if questions else "您能提供更多详细信息吗？"