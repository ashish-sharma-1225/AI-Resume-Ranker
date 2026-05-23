# extractor.py
import io
from PyPDF2 import PdfReader
import pdfplumber

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts text content from a PDF file (in bytes form).
    Returns extracted text as a string.
    """
    text = ""
    try:
        # Try PyPDF2 first
        reader = PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception:
        text = ""

    # If PyPDF2 fails or gives empty, use pdfplumber
    if not text.strip():
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for p in pdf.pages:
                    page_text = p.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception:
            pass

    return text
