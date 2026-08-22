from functools import lru_cache

from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384


class EmbeddingService:
    """
    Embedding service for NyayaSetu AI RAG.

    Model:
        all-MiniLM-L6-v2

    Output:
        384-dimensional vector

    The same model must be used for:
        1. Document embeddings
        2. Query embeddings
    """

    def __init__(
        self,
        model_name: str = MODEL_NAME,
    ):
        self.model_name = model_name

        self.model = SentenceTransformer(
            model_name
        )

        actual_dimension = (
            self.model.get_sentence_embedding_dimension()
        )

        if actual_dimension != EMBEDDING_DIMENSION:
            raise RuntimeError(
                "Embedding dimension mismatch. "
                f"Expected {EMBEDDING_DIMENSION}, "
                f"got {actual_dimension}."
            )

    @property
    def dimension(self) -> int:
        """
        Return the embedding vector dimension.
        """
        return EMBEDDING_DIMENSION

    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding for one piece of text.
        """

        if not text or not text.strip():
            raise ValueError(
                "Text cannot be empty."
            )

        embedding = self.model.encode(
            text.strip(),
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple documents/chunks.
        """

        if not texts:
            return []

        cleaned_texts = [
            text.strip()
            for text in texts
            if text and text.strip()
        ]

        if not cleaned_texts:
            return []

        embeddings = self.model.encode(
            cleaned_texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    """
    Create one reusable embedding model instance.

    This prevents loading the 90 MB model repeatedly.
    """

    return EmbeddingService()