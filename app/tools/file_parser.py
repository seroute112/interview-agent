import os
from docx import Document
from pypdf import PdfReader

def parse_txt(file_path : str) -> str:
    with open(file_path, "r" , encoding="utf-8") as f:
        return f.read()

def parse_pdf(file_path : str) -> str:
    reader = PdfReader(file_path)
    text = []
    for page in reader.pages:
        text.append(page.extract_text() or "")

    return "\n".join(text)

def parse_docx(file_path:str) -> str:
    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)

def parse_file(file_path:str) ->str :
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".txt":
        return parse_txt(file_path)
    if ext == ".pdf":
        return parse_pdf(file_path)
    if ext == ".docx":
        return parse_docx(file_path)

    raise ValueError(f"不支持的文件类型:{ext}")