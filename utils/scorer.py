from groq import Groq
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_resume(resume_text):
    prompt = f"Analyze this resume: {resume_text}"
    prompt = f"Analyze this resume and provide detailed feedback: {resume_text}"
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def score_resume(resume_text, job_description=""):
    """Score a resume across multiple categories and return structured results."""
    job_context = f"\n\nJob Description:\n{job_description}" if job_description else ""
    prompt = f"""You are an expert resume evaluator. Analyze this resume and provide a detailed score.

Resume:
{resume_text}{job_context}

Respond ONLY with a JSON object in this exact format (no markdown, no extra text):
{{
  "overall_score": <integer 0-100>,
  "content_score": <integer 0-100>,
  "format_score": <integer 0-100>,
  "style_score": <integer 0-100>,
  "sections_score": <integer 0-100>,
  "skills_score": <integer 0-100>,
  "match_score": <integer 0-100 if job description provided, else null>,
  "strengths": ["<strength1>", "<strength2>", "<strength3>"],
  "improvements": ["<improvement1>", "<improvement2>", "<improvement3>"],
  "verdict": "<one sentence professional verdict>"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: extract JSON from the response
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        # Return a default structure if parsing fails
        return {
            "overall_score": 70,
            "content_score": 70,
            "format_score": 70,
            "style_score": 70,
            "sections_score": 70,
            "skills_score": 70,
            "match_score": None,
            "strengths": ["Resume submitted successfully"],
            "improvements": ["Could not parse detailed analysis"],
            "verdict": "Resume received but detailed analysis unavailable."
        }


def match_resume_to_job(resume_text, job_description):
    """Match a resume against a job description and return match percentage and insights."""
    prompt = f"""You are an expert HR recruiter. Evaluate how well this resume matches the job description.

Resume:
{resume_text}

Job Description:
{job_description}

Respond ONLY with a JSON object (no markdown, no extra text):
{{
  "match_percentage": <integer 0-100>,
  "matched_skills": ["<skill1>", "<skill2>"],
  "missing_skills": ["<skill1>", "<skill2>"],
  "recommendation": "<shortlisted|consider|rejected>",
  "summary": "<2-3 sentence professional summary of the match>"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    raw = response.choices[0].message.content.strip()

    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {
            "match_percentage": 50,
            "matched_skills": [],
            "missing_skills": [],
            "recommendation": "consider",
            "summary": "Match analysis unavailable."
        }


if __name__ == "__main__":
    from pdf_reader import extract_text_from_pdf
    resume_text = extract_text_from_pdf("sample_resumes/sample_resume.pdf")
    analysis = analyze_resume(resume_text)
    print(analysis)
    result = score_resume(resume_text)
    print(result)