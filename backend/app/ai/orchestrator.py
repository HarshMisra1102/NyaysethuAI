from typing import Any

from app.ai.intent_classifier import (
    Intent,
    IntentClassifier,
)

from app.ai.entity_extractor import (
    EntityExtractor,
)

from app.ai.agents.rights_agent import (
    RightsAgent,
)

from app.ai.agents.rti_agent import (
    RTIAgent,
)

from app.ai.agents.scheme_agent import (
    SchemeAgent,
)

from app.ai.agents.document_agent import (
    DocumentAgent,
)

from app.ai.rag.embeddings import (
    get_embedding_service,
)

from app.ai.rag.retriever import (
    VectorRetriever,
)

from app.core.database import (
    AsyncSessionLocal,
)

from app.schemas.chat import (
    ChatAIResponse,
    Evidence,
    Citation,
    ActionStep,
)


class AIOrchestrator:
    """
    Central AI orchestration layer for NyayaSetu.

    Pipeline:

        User Query
            ↓
        Intent Classification
            ↓
        Entity Extraction
            ↓
        RAG Retrieval
            ↓
        Evidence Filtering
            ↓
        Agent Routing
            ↓
        Agent Execution
            ↓
        Response Adapter
            ↓
        ChatAIResponse
    """

    # Minimum cosine similarity required for evidence.
    #
    # This is intentionally lower than 0.30 because some valid
    # legal/civic queries can have weaker semantic similarity.
    MIN_SIMILARITY = 0.20

    # Maximum number of evidence chunks passed to an agent.
    MAX_EVIDENCE = 5

    def __init__(self, llm=None):

        # ==================================================
        # INTELLIGENCE
        # ==================================================

        self.intent_classifier = IntentClassifier()

        self.entity_extractor = EntityExtractor()

        # ==================================================
        # RAG
        # ==================================================

        self.embedding_service = get_embedding_service()

        self.retriever = VectorRetriever(
            embedding_service=self.embedding_service
        )

        # ==================================================
        # AGENTS
        # ==================================================

        self.rights_agent = RightsAgent(
            llm=llm
        )

        self.rti_agent = RTIAgent(
            llm=llm
        )

        self.scheme_agent = SchemeAgent(
            llm=llm
        )

        self.document_agent = DocumentAgent(
            llm=llm
        )

    # ======================================================
    # MAIN PIPELINE
    # ======================================================

    async def process(
        self,
        message: str,
        case_id: int | None = None,
        user_id: int | None = None,
    ) -> ChatAIResponse:

        if not message or not message.strip():
            raise ValueError(
                "Message cannot be empty."
            )

        message = message.strip()

        # --------------------------------------------------
        # 1. INTENT
        # --------------------------------------------------

        intent = self.intent_classifier.classify(
            message
        )

        # --------------------------------------------------
        # 2. ENTITIES
        # --------------------------------------------------

        entities = self.entity_extractor.extract(
            message
        )

        # --------------------------------------------------
        # 3. RAG RETRIEVAL
        # --------------------------------------------------

        evidence = await self._retrieve(
            query=message,
            intent=intent,
            entities=entities,
            top_k=8,
            min_similarity=self.MIN_SIMILARITY,
        )

        # --------------------------------------------------
        # 4. AGENT
        # --------------------------------------------------

        agent_response = await self._run_agent(
            intent=intent,
            message=message,
            evidence=evidence,
        )

        # --------------------------------------------------
        # 5. FINAL RESPONSE
        # --------------------------------------------------

        return self._build_chat_response(
            agent_response=agent_response,
            evidence=evidence,
        )

    # ======================================================
    # RAG RETRIEVAL
    # ======================================================

    async def _retrieve(
        self,
        query: str,
        intent: Intent,
        entities: Any = None,
        top_k: int = 8,
        min_similarity: float = 0.20,
    ) -> list[dict]:

        if not query or not query.strip():
            return []

        # --------------------------------------------------
        # Retrieve from vector database
        # --------------------------------------------------

        async with AsyncSessionLocal() as db:

            chunks = await self.retriever.search(
                db=db,
                query=query,
                top_k=top_k,
            )

        if not chunks:
            return []

        # --------------------------------------------------
        # Similarity filtering
        # --------------------------------------------------

        filtered = []

        for chunk in chunks:

            similarity = float(
                chunk.similarity
            )

            if similarity < min_similarity:
                continue

            filtered.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "content": chunk.content,
                    "page_number": chunk.page_number,
                    "similarity": similarity,
                    "score": similarity,
                }
            )

        # --------------------------------------------------
        # Intent-aware evidence filtering
        #
        # This does NOT replace semantic search.
        # It only helps prevent obviously unrelated
        # evidence from reaching the agent.
        # --------------------------------------------------

        filtered = self._apply_intent_filter(
            filtered,
            intent,
            query,
        )

        # --------------------------------------------------
        # Sort by relevance
        # --------------------------------------------------

        filtered.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        # --------------------------------------------------
        # Limit evidence passed to Gemini
        # --------------------------------------------------

        return filtered[: self.MAX_EVIDENCE]

    # ======================================================
    # INTENT-AWARE FILTERING
    # ======================================================

    def _apply_intent_filter(
        self,
        evidence: list[dict],
        intent: Intent,
        query: str,
    ) -> list[dict]:

        if not evidence:
            return []

        query_lower = query.lower()

        # --------------------------------------------------
        # RTI
        # --------------------------------------------------

        if intent == Intent.RTI:

            keywords = [
                "rti",
                "right to information",
                "public authority",
                "information request",
                "information commission",
            ]

            return self._prefer_keyword_evidence(
                evidence,
                keywords,
            )

        # --------------------------------------------------
        # RIGHTS
        # --------------------------------------------------

        if intent == Intent.RIGHTS:

            keywords = [
                "landlord",
                "tenant",
                "tenancy",
                "rent",
                "security deposit",
                "consumer",
                "refund",
                "defective product",
                "consumer rights",
                "redressal",
            ]

            return self._prefer_keyword_evidence(
                evidence,
                keywords,
            )

        # --------------------------------------------------
        # GOVERNMENT SCHEMES
        # --------------------------------------------------

        if intent == Intent.SCHEME:

            keywords = [
                "government scheme",
                "scheme",
                "eligibility",
                "welfare",
                "government service",
                "benefit",
                "application",
            ]

            return self._prefer_keyword_evidence(
                evidence,
                keywords,
            )

        # --------------------------------------------------
        # DOCUMENT
        # --------------------------------------------------

        if intent == Intent.DOCUMENT:

            keywords = [
                "document",
                "notice",
                "order",
                "circular",
                "government notice",
                "issuing authority",
                "deadline",
                "instructions",
            ]

            return self._prefer_keyword_evidence(
                evidence,
                keywords,
            )

        return evidence

    # ======================================================
    # KEYWORD EVIDENCE PRIORITIZATION
    # ======================================================

    def _prefer_keyword_evidence(
        self,
        evidence: list[dict],
        keywords: list[str],
    ) -> list[dict]:

        if not evidence:
            return []

        matched = []
        unmatched = []

        for item in evidence:

            content = item.get(
                "content",
                "",
            ).lower()

            match_count = sum(
                1
                for keyword in keywords
                if keyword.lower() in content
            )

            item["keyword_matches"] = match_count

            if match_count > 0:
                # Small relevance bonus.
                item["score"] = (
                    float(item["similarity"])
                    + min(
                        match_count * 0.02,
                        0.10,
                    )
                )

                matched.append(item)

            else:
                unmatched.append(item)

        # If keyword filtering finds useful evidence,
        # prioritize it.
        if matched:

            matched.sort(
                key=lambda item: item["score"],
                reverse=True,
            )

            # Keep a small number of semantic-only
            # results as backup.
            unmatched.sort(
                key=lambda item: item["score"],
                reverse=True,
            )

            return (
                matched
                + unmatched[:2]
            )

        # Important:
        # Do NOT return zero evidence simply because
        # keyword matching failed.
        #
        # Semantic similarity is still useful.
        evidence.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return evidence

    # ======================================================
    # AGENT ROUTER
    # ======================================================

    async def _run_agent(
        self,
        intent: Intent,
        message: str,
        evidence: list[dict],
    ) -> dict:

        if intent == Intent.RIGHTS:

            return await self.rights_agent.run(
                query=message,
                evidence=evidence,
            )

        if intent == Intent.RTI:

            return await self.rti_agent.run(
                query=message,
                evidence=evidence,
            )

        if intent == Intent.SCHEME:

            return await self.scheme_agent.run(
                query=message,
                evidence=evidence,
            )

        if intent == Intent.DOCUMENT:

            return await self.document_agent.run(
                query=message,
                evidence=evidence,
            )

        # --------------------------------------------------
        # Fallback
        # --------------------------------------------------

        return {
            "issue": message,

            "category": "General Civic Query",

            "summary": (
                "The system could not confidently "
                "identify the type of civic or legal "
                "request."
            ),

            "possible_rights": [],

            "action_plan": [
                "Provide more details about your issue.",
                (
                    "Mention the relevant government "
                    "department, document, scheme, "
                    "or dispute if known."
                ),
            ],

            "required_documents": [],

            "disclaimer": (
                "NyayaSetu provides general information "
                "and is not a substitute for professional "
                "legal advice."
            ),
        }

    # ======================================================
    # RESPONSE ADAPTER
    # ======================================================

    def _build_chat_response(
        self,
        agent_response: dict,
        evidence: list[dict],
    ) -> ChatAIResponse:

        # --------------------------------------------------
        # Evidence conversion
        # --------------------------------------------------

        response_evidence = []

        sources = []

        for item in evidence:

            document_id = item.get(
                "document_id"
            )

            chunk_id = item.get(
                "chunk_id"
            )

            page_number = item.get(
                "page_number"
            )

            score = item.get(
                "score",
                item.get("similarity"),
            )

            content = item.get(
                "content",
                "",
            )

            citation = Citation(
                title=(
                    f"NyayaSetu Knowledge "
                    f"Document {document_id}"
                ),
                url=None,
                source_type="knowledge_base",
                document_id=document_id,
                page_number=page_number,
            )

            evidence_item = Evidence(
                content=content,
                document_id=document_id,
                chunk_id=chunk_id,
                page_number=page_number,
                score=score,
                source=citation,
            )

            response_evidence.append(
                evidence_item
            )

            sources.append(
                citation
            )

        # --------------------------------------------------
        # Action plan conversion
        # --------------------------------------------------

        action_plan = []

        raw_action_plan = agent_response.get(
            "action_plan",
            [],
        )

        for index, action in enumerate(
            raw_action_plan,
            start=1,
        ):

            # Agent returns a simple string.
            if isinstance(action, str):

                action_plan.append(
                    ActionStep(
                        step=index,
                        title=f"Step {index}",
                        description=action,
                    )
                )

            # Agent returns structured data.
            elif isinstance(action, dict):

                action_plan.append(
                    ActionStep(
                        step=int(
                            action.get(
                                "step",
                                index,
                            )
                        ),
                        title=str(
                            action.get(
                                "title",
                                f"Step {index}",
                            )
                        ),
                        description=str(
                            action.get(
                                "description",
                                action.get(
                                    "text",
                                    "",
                                ),
                            )
                        ),
                    )
                )

        # --------------------------------------------------
        # Final Pydantic response
        # --------------------------------------------------

        return ChatAIResponse(

            issue=agent_response.get(
                "issue"
            ),

            category=agent_response.get(
                "category"
            ),

            summary=agent_response.get(
                "summary",
                "",
            ),

            possible_rights=agent_response.get(
                "possible_rights",
                [],
            ),

            evidence=response_evidence,

            action_plan=action_plan,

            required_documents=agent_response.get(
                "required_documents",
                [],
            ),

            sources=sources,

            disclaimer=agent_response.get(
                "disclaimer",
                (
                    "NyayaSetu provides general "
                    "information and is not a substitute "
                    "for professional legal advice."
                ),
            ),
        )


# ==========================================================
# MEMBER 2 INTEGRATION INTERFACE
# ==========================================================

async def process_query(
    request,
    user_id: int,
) -> ChatAIResponse:
    """
    Public AI integration boundary.

    AIService should call:

        await process_query(
            request,
            user_id,
        )

    Input:
        request.case_id
        request.message
        user_id

    Output:
        ChatAIResponse
    """

    orchestrator = AIOrchestrator()

    return await orchestrator.process(
        message=request.message,
        case_id=request.case_id,
        user_id=user_id,
    )