import pdfplumber
import io


def extract_text_from_pdf(pdf_source):
    """Extract text from a PDF file path or BytesIO object."""
    text = ""
    if isinstance(pdf_source, (bytes, bytearray)):
        pdf_source = io.BytesIO(pdf_source)
    with pdfplumber.open(pdf_source) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


if __name__ == "__main__":
    text = extract_text_from_pdf("sample_resumes/sample_resume.pdf")
    print(text)