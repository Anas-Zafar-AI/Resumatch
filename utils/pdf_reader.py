import pdfplumber
import os

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def load_all_resumes(folder_path):
    resumes = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            full_path = os.path.join(folder_path, filename)
            resumes[filename] = extract_text_from_pdf(full_path)
    return resumes