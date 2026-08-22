from dataclasses import dataclass

from app.ai.rag.reranker import RerankedChunk


@dataclass
class EvidenceItem:
    chunk_id: int
    document_id: int
    content: str
    page_number: int | None
    score: float


def build_evidence(
    chunks: list[RerankedChunk],
) -> list[EvidenceItem]:

    return [
        EvidenceItem(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            content=chunk.content,
            page_number=chunk.page_number,
            score=chunk.final_score,
        )
        for chunk in chunks
    ]