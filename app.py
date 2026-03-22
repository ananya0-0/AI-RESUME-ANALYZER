import streamlit as st
import tempfile
import os
from agent import extract_resume_text, analyze_resume

#Page config 

st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# Header

st.title("📄 AI Resume Analyzer")
st.markdown("Upload your resume and get an ATS score, keyword analysis, and improvement suggestions.")
st.divider()

# Sidebar

with st.sidebar:
    st.header("⚙️ Settings")
    job_role = st.text_input(
        "Target Job Role",
        value="Software Engineer / AI-ML Engineer",
        help="The role you're applying for. This affects keyword analysis."
    )
    st.markdown("---")
    st.markdown("**Supported formats:** PDF, DOCX")
    st.markdown("**Model:** Groq LLaMA 3.3 70B (fast)") 

# File upload 

uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx", "doc"],
    help="Your resume will be analyzed locally — not stored anywhere."
)

if uploaded_file is not None:
    if st.button("🔍 Analyze Resume", type="primary", use_container_width=True):

        # Save uploaded file to a temp location so our functions can read it
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(uploaded_file.name)[1]
        ) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            # extract text 
            with st.spinner("Reading your resume..."):
                resume_text = extract_resume_text(tmp_path)

            if not resume_text.strip():
                st.error("Could not extract text from this file. Make sure it's not a scanned image PDF.")
                st.stop()

            # Run analysis
            with st.spinner("Analyzing with AI... this takes 10-20 seconds"):
                result = analyze_resume(resume_text, job_role)

            # Display results 

            st.success("Analysis complete!")
            if "agent_steps" in result:
                with st.expander("🤖 Agent steps taken"):
                    for i, step in enumerate(result["agent_steps"], 1):
                        st.markdown(f"`Step {i}:` {step}")
            st.divider()

            # Score cards at the top
            col1, col2, col3 = st.columns(3)

            with col1:
                ats = result.get("ats_score", 0)
                color = "🔴" if ats < 50 else "🟡" if ats < 75 else "🟢"
                st.metric(f"{color} ATS Score", f"{ats}/100", result.get("ats_verdict", ""))

            with col2:
                overall = result.get("overall_score", 0)
                color = "🔴" if overall < 50 else "🟡" if overall < 75 else "🟢"
                st.metric(f"{color} Overall Score", f"{overall}/100")

            with col3:
                sections = result.get("sections_found", {})
                found = sum(1 for v in sections.values() if v)
                total = len(sections)
                st.metric("📋 Sections Found", f"{found}/{total}")

            st.divider()

            # Summary
            st.subheader("📝 Overall Assessment")
            st.info(result.get("summary", "No summary available."))

            # Two column layout for main content
            left, right = st.columns(2)

            with left:
                # Strengths
                st.subheader("✅ Strengths")
                strengths = result.get("strengths", [])
                if strengths:
                    for s in strengths:
                        st.success(s)
                else:
                    st.write("No specific strengths identified.")

                # Sections checklist
                st.subheader("📋 Sections Checklist")
                for section, present in result.get("sections_found", {}).items():
                    label = section.replace("_", " ").title()
                    if present:
                        st.markdown(f"✅ {label}")
                    else:
                        st.markdown(f"❌ {label} — **missing**")

                # Keywords present
                st.subheader("🔑 Keywords Found")
                keywords = result.get("keywords_present", [])
                if keywords:
                    st.markdown(" ".join([f"`{k}`" for k in keywords]))
                else:
                    st.write("No strong keywords detected.")

            with right:
                # ATS issues
                st.subheader("⚠️ ATS Issues")
                ats_issues = result.get("ats_issues", [])
                if ats_issues:
                    for issue in ats_issues:
                        st.warning(issue)
                else:
                    st.success("No major ATS issues found!")

                # Missing keywords
                st.subheader("🔍 Missing Keywords")
                missing_kw = result.get("keywords_missing", [])
                if missing_kw:
                    st.markdown(" ".join([f"`{k}`" for k in missing_kw]))
                    st.caption("Consider adding these keywords naturally in your experience/skills sections.")
                else:
                    st.success("Good keyword coverage!")

                # Section-level feedback
                st.subheader("🔎 Section Feedback")
                for section, feedback in result.get("section_feedback", {}).items():
                    label = section.replace("_", " ").title()
                    with st.expander(f"{label}"):
                        st.write(feedback)

            st.divider()

            # Top improvements — full width
            st.subheader("🚀 Top Improvements (Priority Order)")
            improvements = result.get("top_improvements", [])
            for i, tip in enumerate(improvements, 1):
                priority = tip.get("priority", "Medium")
                color = "🔴" if priority == "High" else "🟡" if priority == "Medium" else "🟢"
                with st.expander(f"{color} #{i} [{priority}] {tip.get('area', '')} — {tip.get('issue', '')}"):
                    st.markdown(f"**Problem:** {tip.get('issue', '')}")
                    st.markdown(f"**How to fix:** {tip.get('fix', '')}")

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")
            st.caption("Common issues: invalid API key in .env, unsupported file format, or network error.")

        finally:
            # Clean up temp file
            os.unlink(tmp_path)

else:
    st.info("👆 Upload your resume above to get started.")