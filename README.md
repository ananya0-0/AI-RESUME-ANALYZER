# 📄 AI Resume Analyzer Agent

An agentic AI system that autonomously analyzes resumes using a multi-step 
reasoning loop — built with Python, Groq LLaMA 3.3 70B, and Streamlit.

---

## 🔗 Live Demo

**[ai-resume-analyzer-c5cfxwkxeszman8xee5rhf.streamlit.app](https://ai-resume-analyzer-c5cfxwkxeszman8xee5rhf.streamlit.app)**

---

## 🤖 How the Agent Works

This is a true AI agent — not just a single API call. The agent runs an 
autonomous loop, deciding which tools to use and in what order, until it 
has enough information to deliver a complete analysis.
```
User uploads resume + target role
            ↓
    ┌─────────────────────────┐
    │      AGENT LOOP         │
    │                         │
    │  Agent decides next     │
    │  tool based on what     │◄──┐
    │  it knows so far        │   │
    └────────────┬────────────┘   │
                 ↓                │
    ┌────────────────────────┐    │
    │  Tool 1: Extract       │    │
    │  Resume Sections       │    │
    └────────────┬───────────┘    │
                 ↓                │
    ┌────────────────────────┐    │
    │  Tool 2: Search Job    │    │
    │  Market Requirements   │    │
    └────────────┬───────────┘    │
                 ↓                │
    ┌────────────────────────┐    │
    │  Tool 3: Check ATS     │    │
    │  Compatibility         │    │
    └────────────┬───────────┘    │
                 ↓                │
    ┌────────────────────────┐    │
    │  Tool 4: Compare       │    │
    │  Keywords & Skills     │    │
    └────────────┬───────────┘    │
                 ↓                │
    ┌────────────────────────┐    │
    │  Tool 5: Generate      │    │
    │  Final Analysis        │    │
    └────────────┬───────────┘    │
                 ↓                │
         Has enough info? ────────┘
                 ↓ Yes
         Final Report
```

---

## ✨ Features

- **True Agent Loop** — LLM autonomously decides which tools to call and 
  in what order at every step
- **ATS Compatibility Score** — rates your resume 0-100 based on how well 
  it passes Applicant Tracking Systems
- **Job Market Awareness** — searches current requirements for your target 
  role, not just generic advice
- **Deep Section Analysis** — each resume section analyzed individually 
  for focused feedback
- **Keyword Gap Analysis** — compares your resume keywords against real 
  job market requirements
- **Prioritized Improvements** — specific fixes ranked High / Medium / Low
- **Agent Transparency** — shows exactly which tools the agent used and 
  in what order
- **Multi-role Support** — works for any job role, tailored analysis every time
- **Format Support** — PDF and DOCX

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend UI | Streamlit |
| AI Model | LLaMA 3.3 70B via Groq API |
| Agent Framework | Custom agent loop (no LangChain) |
| PDF Parsing | PyMuPDF (fitz) |
| DOCX Parsing | python-docx |
| Environment | python-dotenv |
| Deployment | Streamlit Community Cloud |
| Language | Python 3.11 |

---

## 🧠 Agent Architecture

The agent is built from scratch without any framework like LangChain.
It uses a state machine pattern:

**State** — tracks what the agent knows so far:
```python
state = {
    "sections": None,          # extracted resume sections
    "job_requirements": None,  # current market requirements
    "ats_result": None,        # ATS compatibility check
    "keyword_result": None,    # keyword gap analysis
    "final_analysis": None,    # synthesized recommendations
    "steps_taken": []          # audit trail of agent decisions
}
```

**Loop** — at each step, the LLM looks at the current state and decides:
```python
{"action": "use_tool", "tool": "check_ats", "reason": "..."}
# or
{"action": "complete", "reason": "have enough information"}
```

**Tools** — 5 specialized functions the agent can call:

| Tool | What it does |
|---|---|
| `extract_sections` | Breaks resume into labeled sections |
| `search_requirements` | Finds current job market requirements |
| `check_ats` | Checks formatting and ATS compatibility |
| `compare_keywords` | Gaps between resume and job requirements |
| `generate_analysis` | Synthesizes everything into final report |

---

## ⚙️ Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/ananya0-0/AI-RESUME-ANALYZER.git
cd AI-RESUME-ANALYZER
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get a free Groq API key
- Go to [console.groq.com](https://console.groq.com)
- Sign up free — no credit card needed
- Create an API key

### 5. Set up environment variables
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 6. Run the app
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 📁 Project Structure
```
AI-RESUME-ANALYZER/
├── agent.py            # Agent loop + 5 tool functions
├── app.py              # Streamlit UI
├── requirements.txt    # Dependencies
├── .env                # API key (not uploaded)
├── .gitignore          # Excludes venv, .env, pycache
└── README.md           # This file
```

---

## ⚠️ Resume Format Note

Upload a **text-based PDF** (exported from Word or Google Docs) or a 
**.docx file**. Scanned image PDFs cannot be parsed — by this tool or 
by real ATS systems.

---

## 🔮 Roadmap

- [ ] Job description comparison — paste actual job posting for direct matching
- [ ] Resume rewrite suggestions — auto-generate improved bullet points
- [ ] Multi-resume comparison
- [ ] Export full report as PDF
