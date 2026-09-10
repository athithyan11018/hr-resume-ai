import pymupdf


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from all pages of a PDF."""

    document = pymupdf.open(pdf_path)

    text = []

    for page in document:
        page_text = page.get_text()
        text.append(page_text)

    document.close()

    return "\n".join(text)