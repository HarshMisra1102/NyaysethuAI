from dataclasses import dataclass

import fitz


@dataclass
class PDFPage:
    page_number: int
    text: str


@dataclass
class PDFExtractionResult:
    pages: list[PDFPage]
    total_pages: int
    total_characters: int


def extract_pdf_text(
    file_path: str,
) -> PDFExtractionResult:

    pages: list[PDFPage] = []

    total_characters = 0

    with fitz.open(file_path) as document:

        for index, page in enumerate(document):

            text = page.get_text("text").strip()

            pages.append(
                PDFPage(
                    page_number=index + 1,
                    text=text,
                )
            )

            total_characters += len(text)

        return PDFExtractionResult(
            pages=pages,
            total_pages=len(document),
            total_characters=total_characters,
        )