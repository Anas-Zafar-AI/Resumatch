import pdfplumber

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Test karo
if __name__ == "__main__":
    text = extract_text_from_pdf("sample_resumes/sample_resume.pdf")
    print(text)