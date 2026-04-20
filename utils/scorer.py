from groq import Groq
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_resume(resume_text):
    prompt = f"Analyze this resume: {resume_text}"
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def analyze_resume_structured(resume_text, job_description=""):
    """
    Analyze a resume and return structured data for display.

    Returns a dict with:
      - overall_score (int 0-100)
      - candidate_name (str)
      - summary (str)
      - categories (list of dicts)
      - strengths (list of str)
      - improvements (list of str)
    """
    jd_section = (
        f"\nJob Description:\n{job_description}" if job_description.strip() else ""
    )

    prompt = f"""You are an expert resume reviewer. Analyze the following resume{' against the provided job description' if jd_section else ''} and return a JSON object with EXACTLY this structure (no extra keys, no markdown fences):

{{
  "overall_score": <integer 0-100>,
  "candidate_name": "<full name from resume or 'Unknown Candidate'>",
  "summary": "<2-3 sentence professional summary of the candidate>",
  "categories": [
    {{
      "name": "Content Quality",
      "score": <integer 0-100>,
      "color": "#16c784",
      "passed_items": ["<item1>", "<item2>"],
      "failed_items": ["<item1>"]
    }},
    {{
      "name": "Format & Brevity",
      "score": <integer 0-100>,
      "color": "#00d4ff",
      "passed_items": ["<item1>"],
      "failed_items": ["<item1>"]
    }},
    {{
      "name": "Style",
      "score": <integer 0-100>,
      "color": "#9b59b6",
      "passed_items": ["<item1>"],
      "failed_items": []
    }},
    {{
      "name": "Sections Completeness",
      "score": <integer 0-100>,
      "color": "#ff9f1c",
      "passed_items": ["<item1>"],
      "failed_items": ["<item1>"]
    }},
    {{
      "name": "Skills Highlighting",
      "score": <integer 0-100>,
      "color": "#e74c3c",
      "passed_items": ["<item1>"],
      "failed_items": []
    }}
  ],
  "strengths": ["<strength1>", "<strength2>", "<strength3>"],
  "improvements": ["<improvement1>", "<improvement2>", "<improvement3>"]
}}

Resume:
{resume_text}{jd_section}

Return ONLY the JSON object, nothing else."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()

    # Strip any accidental markdown code fences from the start/end of the response
    raw = re.sub(r"\A```[a-z]*\n?", "", raw)
    raw = re.sub(r"\n?```\Z", "", raw)
    raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: return a basic structure if JSON parsing fails
        data = {
            "overall_score": 50,
            "candidate_name": "Unknown Candidate",
            "summary": raw[:300] if raw else "Analysis could not be parsed.",
            "categories": [
                {"name": "Content Quality", "score": 50, "color": "#16c784", "passed_items": [], "failed_items": []},
                {"name": "Format & Brevity", "score": 50, "color": "#00d4ff", "passed_items": [], "failed_items": []},
                {"name": "Style", "score": 50, "color": "#9b59b6", "passed_items": [], "failed_items": []},
                {"name": "Sections Completeness", "score": 50, "color": "#ff9f1c", "passed_items": [], "failed_items": []},
                {"name": "Skills Highlighting", "score": 50, "color": "#e74c3c", "passed_items": [], "failed_items": []},
            ],
            "strengths": [],
            "improvements": [],
        }

    return data


if __name__ == "__main__":
    from pdf_reader import extract_text_from_pdf
    resume_text = extract_text_from_pdf("sample_resumes/sample_resume.pdf")
    result = analyze_resume_structured(resume_text)
    print(json.dumps(result, indent=2))