from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.ai.rag.embeddings import EmbeddingService


@dataclass
class ExtractedPage:
    """
    Represents text extracted from one document page.
    """

    page_number: int | None
    text: str


@dataclass
class DocumentChunkData:
    """
    Represents one chunk ready to be stored in DocumentChunk.
    """

    content: str
    page_number: int | None
    chunk_index: int
    embedding: list[float]


class DocumentIngestionService:
    """
    Handles document text extraction, cleaning, chunking,
    and embedding generation.

    Database persistence is intentionally handled separately.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService | None = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
    ):
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.embedding_service = (
            embedding_service
            or EmbeddingService()
        )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    # ==========================================================
    # TEXT CLEANING
    # ==========================================================

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Normalize extracted text while preserving paragraphs.
        """

        if not text:
            return ""

        lines = []

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            lines.append(line)

        cleaned = "\n".join(lines)

        return cleaned.strip()

    # ==========================================================
    # TEXT EXTRACTION
    # ==========================================================

    def extract_text(
        self,
        file_path: str | Path,
    ) -> list[ExtractedPage]:
        """
        Extract text from TXT or PDF files.

        PDF extraction uses PyMuPDF (fitz).
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {path}"
            )

        suffix = path.suffix.lower()

        # --------------------------------------------------
        # TXT
        # --------------------------------------------------

        if suffix == ".txt":

            text = path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            cleaned = self.clean_text(text)

            if not cleaned:
                return []

            return [
                ExtractedPage(
                    page_number=None,
                    text=cleaned,
                )
            ]

        # --------------------------------------------------
        # PDF
        # --------------------------------------------------

        if suffix == ".pdf":

            try:
                import fitz
            except ImportError as exc:
                raise RuntimeError(
                    "PyMuPDF is required for PDF extraction. "
                    "Install it with: pip install pymupdf"
                ) from exc

            pages: list[ExtractedPage] = []

            with fitz.open(path) as document:

                for page_index, page in enumerate(
                    document
                ):

                    text = page.get_text("text")

                    cleaned = self.clean_text(text)

                    if not cleaned:
                        continue

                    pages.append(
                        ExtractedPage(
                            page_number=page_index + 1,
                            text=cleaned,
                        )
                    )

            return pages

        raise ValueError(
            "Unsupported document type. "
            "Supported formats: .pdf, .txt"
        )

    # ==========================================================
    # CHUNKING
    # ==========================================================

    def chunk_pages(
        self,
        pages: list[ExtractedPage],
    ) -> list[tuple[str, int | None]]:
        """
        Split extracted pages into overlapping chunks.

        Returns:
            [
                (chunk_text, page_number),
                ...
            ]
        """

        chunks: list[tuple[str, int | None]] = []

        for page in pages:

            text = page.text

            if not text:
                continue

            start = 0
            text_length = len(text)

            while start < text_length:

                end = min(
                    start + self.chunk_size,
                    text_length,
                )

                chunk = text[start:end].strip()

                if chunk:
                    chunks.append(
                        (
                            chunk,
                            page.page_number,
                        )
                    )

                if end >= text_length:
                    break

                start = end - self.chunk_overlap

        return chunks

    # ==========================================================
    # EMBEDDINGS
    # ==========================================================

    def create_chunks(
        self,
        pages: list[ExtractedPage],
    ) -> list[DocumentChunkData]:
        """
        Create chunks and generate embeddings for each chunk.
        """

        raw_chunks = self.chunk_pages(pages)

        if not raw_chunks:
            return []

        texts = [
            chunk_text
            for chunk_text, _ in raw_chunks
        ]

        embeddings = (
            self.embedding_service.embed_documents(
                texts
            )
        )

        if len(embeddings) != len(raw_chunks):
            raise RuntimeError(
                "Embedding count does not match "
                "chunk count."
            )

        result: list[DocumentChunkData] = []

        for index, (
            (content, page_number),
            embedding,
        ) in enumerate(
            zip(
                raw_chunks,
                embeddings,
            )
        ):

            result.append(
                DocumentChunkData(
                    content=content,
                    page_number=page_number,
                    chunk_index=index,
                    embedding=embedding,
                )
            )

        return result

    # ==========================================================
    # COMPLETE PIPELINE
    # ==========================================================

    def process_file(
        self,
        file_path: str | Path,
    ) -> list[DocumentChunkData]:
        """
        Complete document ingestion pipeline:

        file
          ↓
        extraction
          ↓
        cleaning
          ↓
        chunking
          ↓
        embeddings
        """

        pages = self.extract_text(
            file_path
        )

        if not pages:
            raise ValueError(
                "No readable text was found in the document."
            )

        return self.create_chunks(
            pages
        )