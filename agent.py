import os
import json
import fitz
from docx import Document
from groq import Groq
from dotenv import load_dotenv
import streamlit as st
load_dotenv()

# Works locally (reads .env) AND on Streamlit Cloud (reads st.secrets)
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)
# ── Extract text from uploaded file ──────────────────────────────────────────

def extract_text_from_pdf(file_path):
    """Opens a PDF and pulls out all the text from every page."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_text_from_docx(file_path):
    """Opens a Word doc and pulls out all paragraph text."""
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text

def extract_resume_text(file_path):
    """Decides which extractor to use based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Please upload PDF or DOCX.")

# ── The AI agent ──────────────────────────────────────────────────────────────

def analyze_resume(resume_text, job_role="Software Engineer / AI-ML Engineer"):
    """
    Sends resume text to Groq and gets back structured analysis.
    Returns a Python dictionary with all the analysis results.
    """

    system_prompt = """You are an expert resume reviewer and ATS specialist 
with 10 years of experience in tech hiring for AI/ML and software engineering roles.

You return ONLY a valid JSON object — no markdown, no explanation, nothing outside the JSON.
Be honest, specific, and actionable. Never give vague feedback."""

    user_prompt = f"""Analyze this resume for the role: {job_role}

RESUME TEXT:
{resume_text}

Return ONLY a valid JSON object with EXACTLY this structure:

{{
  "ats_score": <integer 0-100>,
  "ats_verdict": "<Poor / Needs Work / Average / Good / Excellent>",
  "overall_score": <integer 0-100>,
  
  "sections_found": {{
    "contact_info": <true or false>,
    "education": <true or false>,
    "skills": <true or false>,
    "experience": <true or false>,
    "projects": <true or false>,
    "summary": <true or false>,
    "certifications": <true or false>
  }},
  
  "missing_sections": ["<section name>"],
  
  "ats_issues": [
    "<specific issue that would cause ATS to reject this resume>"
  ],
  
  "keywords_present": ["<relevant keyword found in resume>"],
  
  "keywords_missing": ["<important keyword missing for this role>"],
  
  "section_feedback": {{
    "contact_info": "<specific feedback>",
    "education": "<specific feedback>",
    "skills": "<specific feedback>",
    "experience": "<specific feedback>",
    "projects": "<specific feedback>"
  }},
  
  "top_improvements": [
    {{
      "priority": "<High / Medium / Low>",
      "area": "<which section>",
      "issue": "<what is wrong>",
      "fix": "<exactly what to do>"
    }}
  ],
  
  "strengths": ["<something genuinely strong about this resume>"],
  
  "summary": "<3-4 sentence honest overall assessment>"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # free, fast, high quality
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,      # lower = more consistent, structured output
        max_tokens=2000,
    )

    # Get raw response text
    raw_response = response.choices[0].message.content.strip()

    # Clean up in case model added ```json ... ```
    if "```json" in raw_response:
        raw_response = raw_response.split("```json")[1].split("```")[0].strip()
    elif "```" in raw_response:
        raw_response = raw_response.split("```")[1].split("```")[0].strip()

    # Find JSON object in case model added text before/after
    start = raw_response.find("{")
    end = raw_response.rfind("}") + 1
    if start != -1 and end != 0:
        raw_response = raw_response[start:end]

    result = json.loads(raw_response)
    return result