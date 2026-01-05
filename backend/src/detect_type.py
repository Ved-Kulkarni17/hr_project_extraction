import re
from pypdf import PdfReader

def detect_pdf_type(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""

    for page in reader.pages[:1]:
        extracted = page.extract_text()
        if extracted:
            text += extracted

    if len(text.strip()) < 50:
        return "image"   # ignored for now

    # form-like: many "Label Value" or "Label : Value"
    form_lines = re.findall(r"^[A-Za-z ]+\s+.+$", text, re.MULTILINE)
    colon_lines = re.findall(r".+:\s+.+", text)

    if len(form_lines) + len(colon_lines) >= 3:
        return "form"

    return "text"
