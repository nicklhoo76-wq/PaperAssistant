import fitz  # PyMuPDF

def load_pdf(path):
    doc = fitz.open(path)
    text = ""

    for page in doc:
        text += page.get_text()

    return text

def load_pdf_with_pages(path):
    doc = fitz.open(path)
    pages = []

    for i, page in enumerate(doc):
        text = page.get_text()
        pages.append((i + 1, text))  # 页码 + 内容

    return pages