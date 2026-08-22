from app.ai.orchestrator import AIOrchestrator
from app.schemas.chat import ChatAIResponse, ChatRequest


class AIService:
    """
    Backend-facing interface for the AI system.

    The FastAPI layer communicates with the AI layer
    only through this service.
    """

    def __init__(self, orchestrator: AIOrchestrator):
        self.orchestrator = orchestrator

    async def process_query(
        self,
        request: ChatRequest,
        user_id: int,
    ) -> ChatAIResponse:

        return await self.orchestrator.process_query(
            request=request,
            user_id=user_id,
        )