from dataclasses import dataclass


@dataclass
class TextChunk:
    content: str
    chunk_index: int
    page_number: int | None = None


class TextChunker:

    def __init__(
        self,
        chunk_size: int = 1000,
        overlap: int = 150,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive.")

        if overlap < 0:
            raise ValueError("overlap cannot be negative.")

        if overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(
        self,
        text: str,
        page_number: int | None = None,
    ) -> list[TextChunk]:

        text = text.strip()

        if not text:
            return []

        chunks: list[TextChunk] = []

        start = 0
        index = 0
        text_length = len(text)

        while start < text_length:

            end = min(
                start + self.chunk_size,
                text_length,
            )

            chunk = text[start:end]

            # Avoid breaking words when possible.
            if end < text_length:
                last_space = chunk.rfind(" ")

                if last_space > self.chunk_size // 2:
                    end = start + last_space
                    chunk = text[start:end]

            chunk = chunk.strip()

            if chunk:
                chunks.append(
                    TextChunk(
                        content=chunk,
                        chunk_index=index,
                        page_number=page_number,
                    )
                )

                index += 1

            if end >= text_length:
                break

            start = max(
                end - self.overlap,
                start + 1,
            )

        return chunks