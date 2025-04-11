import docx2txt
import fitz  # PyMuPDF

def parse_resume(file):
    if file.filename.endswith('.pdf'):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return " ".join(page.get_text() for page in doc)
    elif file.filename.endswith('.docx'):
        return docx2txt.process(file)
    else:
        return ""
