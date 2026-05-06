# ResuMatch 🤖

> AI-powered resume screening platform that ranks candidates against job descriptions using LLM scoring.

## Overview

ResuMatch is an intelligent recruitment assistant that automates the resume screening process. Upload multiple candidate resumes in PDF format, paste a job description, and let the AI instantly analyze, score, and rank every candidate based on skills match, experience relevance, and overall profile strength.

## Features

- Multi-resume PDF upload and parsing
- AI-powered candidate scoring (0-100)
- Multi-metric analysis: Match Score, ATS Score, Culture Fit, Interview Recommendation
- Skill gap analysis and feedback
- Candidate ranking — highest to lowest
- CSV export for results
- Professional dark-themed dashboard with animated splash screen

## Tech Stack

- Python
- Streamlit
- LangChain
- Groq API (LLaMA 3.3 70B)
- pdfplumber
- python-dotenv

## Setup

```bash
git clone https://github.com/Anas-Zafar-AI/Resumatch.git
cd Resumatch
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file: