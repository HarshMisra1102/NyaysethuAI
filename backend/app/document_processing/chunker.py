from app.ai.rag.chunker import TextChunk, TextChunker
from app.document_processing.cleaner import clean_text
from app.document_processing.pdf_extractor import PDFPage


def chunk_document_pages(
    pages: list[PDFPage],
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[TextChunk]:

    chunker = TextChunker(
        chunk_size=chunk_size,
        overlap=overlap,
    )

    results: list[TextChunk] = []

    global_index = 0

    for page in pages:

        cleaned = clean_text(page.text)

        page_chunks = chunker.chunk_text(
            cleaned,
            page_number=page.page_number,
        )

        for chunk in page_chunks:

            results.append(
                TextChunk(
                    content=chunk.content,
                    chunk_index=global_index,
                    page_number=chunk.page_number,
                )
            )

            global_index += 1

    return results