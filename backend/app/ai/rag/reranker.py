from dataclasses import dataclass

from app.ai.rag.retriever import RetrievedChunk


@dataclass
class RerankedChunk:
    chunk_id: int
    document_id: int
    content: str
    page_number: int | None
    similarity: float
    final_score: float


class Reranker:
    """
    Second-stage ranking for retrieved RAG chunks.

    Stage 1:
        pgvector semantic similarity

    Stage 2:
        semantic + lexical relevance
    """

    def rerank(
        self,
        query: str,
        chunks: list[RetrievedChunk],
        top_k: int = 5,
    ) -> list[RerankedChunk]:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if not chunks:
            return []

        query_terms = self._tokenize(query)

        results: list[RerankedChunk] = []

        for chunk in chunks:

            content_terms = self._tokenize(
                chunk.content
            )

            keyword_overlap = self._keyword_overlap(
                query_terms,
                content_terms,
            )

            semantic_score = max(
                0.0,
                min(1.0, chunk.similarity),
            )

            final_score = (
                0.8 * semantic_score
                + 0.2 * keyword_overlap
            )

            results.append(
                RerankedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    page_number=chunk.page_number,
                    similarity=semantic_score,
                    final_score=final_score,
                )
            )

        results.sort(
            key=lambda item: item.final_score,
            reverse=True,
        )

        return results[:top_k]

    @staticmethod
    def _tokenize(text: str) -> set[str]:

        return {
            word.strip(".,!?;:()[]{}\"'")
            for word in text.lower().split()
            if len(word) > 2
        }

    @staticmethod
    def _keyword_overlap(
        query_terms: set[str],
        content_terms: set[str],
    ) -> float:

        if not query_terms:
            return 0.0

        overlap = query_terms.intersection(
            content_terms
        )

        return len(overlap) / len(query_terms)