from pathlib import Path

import fitz
import pytesseract
from PIL import Image


def ocr_pdf(
    file_path: str,
    language: str = "eng",
    dpi: int = 200,
) -> list[dict]:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF not found: {file_path}"
        )

    results: list[dict] = []

    with fitz.open(file_path) as document:

        for page_index, page in enumerate(document):

            pixmap = page.get_pixmap(
                dpi=dpi,
                alpha=False,
            )

            image = Image.frombytes(
                "RGB",
                [pixmap.width, pixmap.height],
                pixmap.samples,
            )

            text = pytesseract.image_to_string(
                image,
                lang=language,
            )

            results.append(
                {
                    "page_number": page_index + 1,
                    "text": text.strip(),
                }
            )

    return results