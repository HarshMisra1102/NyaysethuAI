from app.ai.orchestrator import AIOrchestrator
from app.schemas.chat import (
    ChatAIResponse,
    ChatRequest,
)


class AIService:
    """
    Backend-facing interface for the AI system.

    FastAPI communicates with the AI layer through
    this service instead of directly accessing agents,
    RAG, Gemini, or the orchestrator internals.
    """

    def __init__(
        self,
        orchestrator: AIOrchestrator,
    ):
        self.orchestrator = orchestrator

    async def process_query(
        self,
        request: ChatRequest,
        user_id: int,
    ) -> ChatAIResponse:

        return await self.orchestrator.process(
            message=request.message,
            case_id=request.case_id,
            user_id=user_id,
        )