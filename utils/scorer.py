from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
def analyze_resume(resume_text):
    prompt = f"Analyze this resume: {resume_text}"
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    from pdf_reader import extract_text_from_pdf
    resume_text = extract_text_from_pdf("sample_resumes/sample_resume.pdf")
    analysis = analyze_resume(resume_text)
    print(analysis)