import re
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path, max_pages=5):
    doc = fitz.open(pdf_path)
    text = ""

    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        text += page.get_text()

    return text

def extract_sections(pdf_path, max_pages=10):
    doc = fitz.open(pdf_path)
    text = ""

    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        text += page.get_text()

    # 简单按章节切分
    sections = re.split(r'\n\d+\.\s+', text)

    return sections