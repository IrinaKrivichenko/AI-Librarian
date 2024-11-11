# pip3 install PyPDF2==3.0.1

import PyPDF2

def get_pdf_text(path):
    print(path)
    with open(path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        full_text = []
        for page in reader.pages:
            full_text.append(page.extract_text())
    return '\n'.join(filter(None, full_text))  # Удаляем пустые строки, если они есть
