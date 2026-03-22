import os
import json
import fitz
import streamlit as st
from docx import Document
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Works locally AND on Streamlit Cloud
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

# Extract text from uploaded file 

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text

def extract_resume_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Please upload PDF or DOCX.")

# Tool functions (what the agent can actually do)
def extract_resume_sections(resume_text):
    """Tool 1: Break resume into individual sections for focused analysis."""
    prompt = f"""Extract and return the following sections from this resume as a JSON object.
If a section is missing, set its value to null.

Resume:
{resume_text}

Return ONLY this JSON, no extra text:
{{
    "contact_info": "<all contact details>",
    "summary": "<professional summary if present>",
    "education": "<all education details>",
    "experience": "<all work experience>",
    "projects": "<all projects>",
    "skills": "<all skills listed>",
    "certifications": "<certifications if present>"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1500,
    )
    raw = response.choices[0].message.content.strip()
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    return json.loads(raw[start:end])

def search_job_requirements(job_role):
    """Tool 2: Search current job market requirements for the role using LLM knowledge."""
    prompt = f"""You are a job market expert. List the current in-demand requirements for: {job_role}

Return ONLY this JSON, no extra text:
{{
    "must_have_skills": ["<skill1>", "<skill2>"],
    "good_to_have_skills": ["<skill1>", "<skill2>"],
    "typical_experience": "<what experience level is expected>",
    "important_keywords": ["<keyword1>", "<keyword2>"],
    "common_ats_keywords": ["<keyword1>", "<keyword2>"],
    "industry_certifications": ["<cert1>", "<cert2>"]
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1000,
    )
    raw = response.choices[0].message.content.strip()
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    return json.loads(raw[start:end])

def check_ats_compatibility(resume_text, sections):
    """Tool 3: Check resume for ATS compatibility issues."""
    prompt = f"""You are an ATS expert. Analyze this resume for ATS compatibility issues.

Resume text:
{resume_text}

Sections found: {json.dumps(sections)}

Return ONLY this JSON, no extra text:
{{
    "ats_score": <integer 0-100>,
    "ats_verdict": "<Poor / Needs Work / Average / Good / Excellent>",
    "formatting_issues": ["<specific issue>"],
    "missing_sections": ["<section name>"],
    "structure_problems": ["<specific problem>"],
    "ats_positive": ["<what is working well for ATS>"]
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1000,
    )
    raw = response.choices[0].message.content.strip()
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    return json.loads(raw[start:end])

def compare_keywords(sections, job_requirements):
    """Tool 4: Compare resume keywords against job requirements."""
    prompt = f"""Compare the resume sections against job requirements and identify keyword gaps.

Resume sections:
{json.dumps(sections)}

Job requirements:
{json.dumps(job_requirements)}

Return ONLY this JSON, no extra text:
{{
    "keywords_present": ["<keyword found in resume>"],
    "keywords_missing": ["<important keyword missing>"],
    "skills_match_score": <integer 0-100>,
    "skills_present": ["<required skill found>"],
    "skills_missing": ["<required skill missing>"],
    "recommendations": ["<specific recommendation to add missing keywords naturally>"]
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1000,
    )
    raw = response.choices[0].message.content.strip()
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    return json.loads(raw[start:end])

def generate_final_analysis(sections, ats_result, keyword_result, job_requirements, job_role):
    """Tool 5: Synthesize everything into final prioritized recommendations."""
    prompt = f"""You are a senior career coach. Based on all analysis results, generate final recommendations.

Job role: {job_role}
ATS Analysis: {json.dumps(ats_result)}
Keyword Analysis: {json.dumps(keyword_result)}
Job Requirements: {json.dumps(job_requirements)}
Resume Sections: {json.dumps(sections)}

Return ONLY this JSON, no extra text:
{{
    "overall_score": <integer 0-100>,
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
    "strengths": ["<something genuinely strong>"],
    "summary": "<3-4 sentence honest overall assessment>"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1500,
    )
    raw = response.choices[0].message.content.strip()
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    return json.loads(raw[start:end])

# The Agent Loop 
def analyze_resume(resume_text, job_role="Software Engineer / AI-ML Engineer"):
    """
    True agent loop — LLM decides which tools to call and synthesizes
    results from multiple specialized tools into a final analysis.
    """

    # Agent state — builds up as tools run
    state = {
        "resume_text": resume_text,
        "job_role": job_role,
        "sections": None,
        "job_requirements": None,
        "ats_result": None,
        "keyword_result": None,
        "final_analysis": None,
        "steps_taken": []
    }

    # System prompt that drives the agent's decision making
    system_prompt = """You are a resume analysis agent. You have access to these tools:
1. extract_sections - extracts resume sections for focused analysis
2. search_requirements - finds current job market requirements  
3. check_ats - checks ATS compatibility
4. compare_keywords - compares resume against job requirements
5. generate_analysis - synthesizes everything into final recommendations

Decide which tools to call based on what information you have.
Always respond with a JSON object indicating your next action.

If you need to call a tool:
{"action": "use_tool", "tool": "<tool_name>", "reason": "<why you need this>"}

If you have enough information to finish:
{"action": "complete", "reason": "<why you have enough info>"}"""

    # Agent loop — runs until agent decides it's done
    max_steps = 6  # safety limit
    step = 0

    while step < max_steps:
        step += 1

        # Build context of what the agent knows so far
        context = f"""Job role: {job_role}

What I have so far:
- Resume sections extracted: {state['sections'] is not None}
- Job requirements found: {state['job_requirements'] is not None}
- ATS check done: {state['ats_result'] is not None}
- Keyword comparison done: {state['keyword_result'] is not None}
- Final analysis done: {state['final_analysis'] is not None}

Steps taken: {state['steps_taken']}

Decide your next action."""

        # Ask the agent what to do next
        decision_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            temperature=0.1,
            max_tokens=200,
        )

        raw_decision = decision_response.choices[0].message.content.strip()

        # Parse agent's decision
        try:
            if "```json" in raw_decision:
                raw_decision = raw_decision.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_decision:
                raw_decision = raw_decision.split("```")[1].split("```")[0].strip()
            start = raw_decision.find("{")
            end = raw_decision.rfind("}") + 1
            decision = json.loads(raw_decision[start:end])
        except:
            # If parsing fails, follow default sequence
            if state["sections"] is None:
                decision = {"action": "use_tool", "tool": "extract_sections"}
            elif state["job_requirements"] is None:
                decision = {"action": "use_tool", "tool": "search_requirements"}
            elif state["ats_result"] is None:
                decision = {"action": "use_tool", "tool": "check_ats"}
            elif state["keyword_result"] is None:
                decision = {"action": "use_tool", "tool": "compare_keywords"}
            elif state["final_analysis"] is None:
                decision = {"action": "use_tool", "tool": "generate_analysis"}
            else:
                decision = {"action": "complete"}

        # Agent decided it's done
        if decision.get("action") == "complete":
            break

        # Agent chose a tool — execute it
        tool = decision.get("tool", "")
        state["steps_taken"].append(tool)

        if tool == "extract_sections" and state["sections"] is None:
            state["sections"] = extract_resume_sections(resume_text)

        elif tool == "search_requirements" and state["job_requirements"] is None:
            state["job_requirements"] = search_job_requirements(job_role)

        elif tool == "check_ats" and state["ats_result"] is None:
            if state["sections"] is None:
                state["sections"] = extract_resume_sections(resume_text)
            state["ats_result"] = check_ats_compatibility(
                resume_text, state["sections"]
            )

        elif tool == "compare_keywords" and state["keyword_result"] is None:
            if state["sections"] is None:
                state["sections"] = extract_resume_sections(resume_text)
            if state["job_requirements"] is None:
                state["job_requirements"] = search_job_requirements(job_role)
            state["keyword_result"] = compare_keywords(
                state["sections"], state["job_requirements"]
            )

        elif tool == "generate_analysis" and state["final_analysis"] is None:
            # Make sure all previous tools have run before final synthesis
            if state["sections"] is None:
                state["sections"] = extract_resume_sections(resume_text)
            if state["job_requirements"] is None:
                state["job_requirements"] = search_job_requirements(job_role)
            if state["ats_result"] is None:
                state["ats_result"] = check_ats_compatibility(
                    resume_text, state["sections"]
                )
            if state["keyword_result"] is None:
                state["keyword_result"] = compare_keywords(
                    state["sections"], state["job_requirements"]
                )
            state["final_analysis"] = generate_final_analysis(
                state["sections"],
                state["ats_result"],
                state["keyword_result"],
                state["job_requirements"],
                job_role
            )
            break

        else:
            # Agent tried to call a tool already done — move to complete
            break

    # Combine all results into the final structure app.py expects
    sections_found = {
        "contact_info": state["sections"].get("contact_info") is not None if state["sections"] else False,
        "education": state["sections"].get("education") is not None if state["sections"] else False,
        "skills": state["sections"].get("skills") is not None if state["sections"] else False,
        "experience": state["sections"].get("experience") is not None if state["sections"] else False,
        "projects": state["sections"].get("projects") is not None if state["sections"] else False,
        "summary": state["sections"].get("summary") is not None if state["sections"] else False,
        "certifications": state["sections"].get("certifications") is not None if state["sections"] else False,
    }

    return {
        "ats_score": state["ats_result"].get("ats_score", 0) if state["ats_result"] else 0,
        "ats_verdict": state["ats_result"].get("ats_verdict", "N/A") if state["ats_result"] else "N/A",
        "overall_score": state["final_analysis"].get("overall_score", 0) if state["final_analysis"] else 0,
        "sections_found": sections_found,
        "missing_sections": state["ats_result"].get("missing_sections", []) if state["ats_result"] else [],
        "ats_issues": (state["ats_result"].get("formatting_issues", []) +
                      state["ats_result"].get("structure_problems", [])) if state["ats_result"] else [],
        "keywords_present": state["keyword_result"].get("keywords_present", []) if state["keyword_result"] else [],
        "keywords_missing": state["keyword_result"].get("keywords_missing", []) if state["keyword_result"] else [],
        "section_feedback": state["final_analysis"].get("section_feedback", {}) if state["final_analysis"] else {},
        "top_improvements": state["final_analysis"].get("top_improvements", []) if state["final_analysis"] else [],
        "strengths": state["final_analysis"].get("strengths", []) if state["final_analysis"] else [],
        "summary": state["final_analysis"].get("summary", "") if state["final_analysis"] else "",
        "agent_steps": state["steps_taken"]
    }