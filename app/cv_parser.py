import io

from pypdf import PdfReader


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Return plain text from a PDF or text file."""
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    return file_bytes.decode("utf-8", errors="ignore").strip()
