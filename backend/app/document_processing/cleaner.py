import re


def clean_text(text: str) -> str:

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove null bytes
    text = text.replace("\x00", "")

    # Join words split across lines:
    # govern-
    # ment
    # becomes government
    text = re.sub(
        r"(\w)-\n(\w)",
        r"\1\2",
        text,
    )

    # Replace excessive spaces/tabs
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    # Reduce excessive blank lines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    # Remove spaces surrounding newlines
    text = re.sub(
        r" *\n *",
        "\n",
        text,
    )

    return text.strip()