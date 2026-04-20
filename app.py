import streamlit as st
import sys
import os
import io
import json
import datetime

# Add utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))

from dotenv import load_dotenv

load_dotenv()

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResuMatch — AI Resume Screening",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Professional CSS ────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Global Reset ── */
* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #0a0a0a !important;
    color: #e8e8e8 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
[data-testid="stToolbar"] { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f0f1a !important;
    border-right: 1px solid #1e1e2e !important;
    padding-top: 1.5rem;
}
[data-testid="stSidebar"] * { color: #c8c8d8 !important; }
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: transparent !important;
    border: none !important;
    color: #9898b8 !important;
    text-align: left !important;
    padding: 0.65rem 1rem !important;
    border-radius: 10px !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #1a1a2e !important;
    color: #16c784 !important;
}

/* ── Main content area ── */
[data-testid="stMainBlockContainer"] {
    padding: 2rem 2.5rem !important;
    max-width: 1400px;
}

/* ── Metric cards ── */
.metric-card {
    background: #111120;
    border: 1px solid #1e1e30;
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
}
.metric-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}
.metric-label {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #7878a8;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
}
.metric-value {
    font-size: 2.6rem;
    font-weight: 800;
    color: #f0f0ff;
    line-height: 1;
}
.metric-sub {
    font-size: 0.78rem;
    color: #5858a8;
    margin-top: 0.4rem;
}

/* ── Section heading ── */
.section-heading {
    font-size: 1.05rem;
    font-weight: 700;
    color: #d0d0e8;
    margin-bottom: 1rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ── Empty state card ── */
.empty-state {
    background: #111120;
    border: 1px dashed #2a2a40;
    border-radius: 16px;
    padding: 3rem;
    text-align: center;
    color: #5858a8;
}

/* ── Candidate row ── */
.candidate-row {
    background: #111120;
    border: 1px solid #1e1e30;
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin-bottom: 0.7rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: background 0.15s;
}
.candidate-row:hover { background: #161628; }
.candidate-name { font-weight: 600; color: #e0e0f0; font-size: 0.95rem; }
.candidate-meta { font-size: 0.78rem; color: #6868a8; margin-top: 0.15rem; }
.score-badge {
    background: #0d2a1e;
    color: #16c784;
    border: 1px solid #16c784;
    border-radius: 20px;
    padding: 0.25rem 0.85rem;
    font-size: 0.82rem;
    font-weight: 700;
}
.score-badge.medium {
    background: #2a1f0d;
    color: #ff9f1c;
    border-color: #ff9f1c;
}
.score-badge.low {
    background: #2a0d10;
    color: #e63946;
    border-color: #e63946;
}

/* ── Upload card ── */
.upload-card {
    background: linear-gradient(135deg, #0d1f18 0%, #131325 100%);
    border: 2px dashed #16c784;
    border-radius: 20px;
    padding: 3.5rem 2rem;
    text-align: center;
    transition: border-color 0.2s;
}
.upload-card:hover { border-color: #00d4ff; }

/* ── Score ring ── */
.score-ring-container {
    display: flex;
    justify-content: center;
    margin: 1.5rem 0;
}
.score-ring {
    position: relative;
    width: 160px;
    height: 160px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.score-ring svg {
    position: absolute;
    top: 0; left: 0;
    transform: rotate(-90deg);
}
.score-ring-inner {
    text-align: center;
    z-index: 1;
}
.score-ring-value {
    font-size: 2.8rem;
    font-weight: 900;
    color: #16c784;
}
.score-ring-label {
    font-size: 0.7rem;
    color: #7878a8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ── Category bars ── */
.category-bar-container { margin-bottom: 1rem; }
.category-bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 0.35rem;
    color: #b0b0d0;
}
.category-bar-bg {
    background: #1a1a2e;
    border-radius: 6px;
    height: 8px;
    overflow: hidden;
}
.category-bar-fill {
    height: 100%;
    border-radius: 6px;
    transition: width 0.6s ease;
}

/* ── Analysis result card ── */
.result-card {
    background: #111120;
    border: 1px solid #1e1e30;
    border-radius: 16px;
    padding: 1.8rem;
    margin-bottom: 1.2rem;
}
.result-card h4 {
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 1rem;
}
.check-item {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    margin-bottom: 0.6rem;
    font-size: 0.88rem;
    color: #c0c0d8;
}
.check-item .icon { flex-shrink: 0; }

/* ── Analytics card ── */
.analytics-card {
    background: #111120;
    border: 1px solid #1e1e30;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* ── Page header ── */
.page-header { margin-bottom: 2rem; }
.page-title {
    font-size: 2.4rem;
    font-weight: 900;
    color: #f0f0ff;
    letter-spacing: -0.02em;
}
.page-subtitle {
    font-size: 0.95rem;
    color: #6868a8;
    margin-top: 0.3rem;
}

/* ── Sidebar logo ── */
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0 1rem 1.5rem;
    border-bottom: 1px solid #1a1a2e;
    margin-bottom: 1rem;
}
.sidebar-logo-text {
    font-size: 1.35rem;
    font-weight: 800;
    background: linear-gradient(135deg, #16c784, #00d4ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.sidebar-logo-icon { font-size: 1.8rem; }

/* ── Streamlit widget overrides ── */
.stTextArea textarea, .stTextInput input {
    background: #0f0f1a !important;
    border: 1px solid #2a2a3e !important;
    color: #e0e0f0 !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #16c784 !important;
    box-shadow: 0 0 0 2px rgba(22,199,132,0.15) !important;
}
div[data-testid="stFileUploader"] {
    background: transparent !important;
}
div[data-testid="stFileUploader"] section {
    background: #0d1f18 !important;
    border: 2px dashed #16c784 !important;
    border-radius: 16px !important;
    color: #16c784 !important;
}
div[data-testid="stFileUploader"] section:hover {
    border-color: #00d4ff !important;
}
.stButton > button {
    background: linear-gradient(135deg, #16c784, #00c070) !important;
    color: #000 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.4rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s ease !important;
    font-size: 0.9rem !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #19e097, #00d4ff) !important;
    box-shadow: 0 4px 20px rgba(22,199,132,0.3) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stSpinner"] > div {
    border-top-color: #16c784 !important;
}
.stSelectbox select, [data-baseweb="select"] {
    background: #0f0f1a !important;
    border-color: #2a2a3e !important;
    color: #e0e0f0 !important;
}
/* Progress bar */
.stProgress > div > div { background: #16c784 !important; }

/* Tabs */
[data-baseweb="tab-list"] { background: #0f0f1a !important; border-radius: 10px; }
[data-baseweb="tab"] { color: #7878a8 !important; font-family: 'Inter', sans-serif !important; }
[aria-selected="true"] { color: #16c784 !important; border-bottom-color: #16c784 !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ─── Session state defaults ──────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "candidates" not in st.session_state:
    st.session_state.candidates = []
if "total_screened" not in st.session_state:
    st.session_state.total_screened = 0
if "shortlisted" not in st.session_state:
    st.session_state.shortlisted = 0
if "top_score" not in st.session_state:
    st.session_state.top_score = 0
if "avg_match" not in st.session_state:
    st.session_state.avg_match = 0


# ─── Helpers ────────────────────────────────────────────────────────────────
def extract_text(uploaded_file):
    """Extract text from an uploaded PDF file."""
    import pdfplumber
    text = ""
    with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def score_color(score):
    if score >= 75:
        return "#16c784"
    elif score >= 50:
        return "#ff9f1c"
    return "#e63946"


def score_badge_class(score):
    if score >= 75:
        return "score-badge"
    elif score >= 50:
        return "score-badge medium"
    return "score-badge low"


def render_score_ring(score, label="Overall Score"):
    """Render an SVG circular progress ring."""
    r = 64
    circ = 2 * 3.14159 * r
    offset = circ * (1 - score / 100)
    color = score_color(score)
    st.markdown(
        f"""
<div class="score-ring-container">
  <div class="score-ring">
    <svg width="160" height="160" viewBox="0 0 160 160">
      <circle cx="80" cy="80" r="{r}" fill="none" stroke="#1a1a2e" stroke-width="10"/>
      <circle cx="80" cy="80" r="{r}" fill="none" stroke="{color}" stroke-width="10"
        stroke-dasharray="{circ:.1f}" stroke-dashoffset="{offset:.1f}"
        stroke-linecap="round"/>
    </svg>
    <div class="score-ring-inner">
      <div class="score-ring-value" style="color:{color}">{score}</div>
      <div class="score-ring-label">{label}</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_category_bar(label, score, color):
    st.markdown(
        f"""
<div class="category-bar-container">
  <div class="category-bar-label">
    <span>{label}</span>
    <span style="color:{color}">{score}/100</span>
  </div>
  <div class="category-bar-bg">
    <div class="category-bar-fill" style="width:{score}%; background:{color}"></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def update_stats(score_data, candidate_name="Unknown"):
    """Update session-state statistics after a resume is scored."""
    overall = score_data.get("overall_score", 0)
    match = score_data.get("match_score") or overall

    entry = {
        "name": candidate_name,
        "score": overall,
        "match": match,
        "timestamp": datetime.datetime.now().strftime("%b %d, %Y %H:%M"),
        "verdict": score_data.get("verdict", ""),
    }
    st.session_state.candidates.insert(0, entry)
    st.session_state.total_screened += 1

    scores = [c["score"] for c in st.session_state.candidates]
    st.session_state.top_score = max(scores)
    st.session_state.avg_match = round(sum(scores) / len(scores))

    shortlisted_count = sum(
        1 for c in st.session_state.candidates if c["score"] >= 70
    )
    st.session_state.shortlisted = shortlisted_count


# ─── Sidebar ─────────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown(
            """
<div class="sidebar-logo">
  <span class="sidebar-logo-icon">🎯</span>
  <span class="sidebar-logo-text">ResuMatch</span>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p style='font-size:0.7rem;color:#3a3a5a;text-transform:uppercase;"
            "letter-spacing:0.12em;padding:0 1rem;margin-bottom:0.5rem;'>Navigation</p>",
            unsafe_allow_html=True,
        )

        pages = [
            ("📊", "Dashboard"),
            ("🔍", "Screen Candidates"),
            ("📈", "Analytics"),
            ("⚙️", "Settings"),
        ]
        for icon, name in pages:
            label = f"{icon}  {name}"
            if st.button(label, key=f"nav_{name}"):
                st.session_state.page = name
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.total_screened > 0:
            st.markdown(
                f"""
<div style="background:#0f0f1a;border-radius:12px;padding:1rem 1.2rem;margin:0 0.5rem;">
  <p style="font-size:0.7rem;color:#5858a8;text-transform:uppercase;
     letter-spacing:0.1em;margin-bottom:0.8rem;">Quick Stats</p>
  <p style="font-size:0.85rem;color:#9898b8;margin-bottom:0.3rem;">
    🗂️ &nbsp;<b style="color:#e0e0f0">{st.session_state.total_screened}</b> screened
  </p>
  <p style="font-size:0.85rem;color:#9898b8;margin-bottom:0.3rem;">
    ✅ &nbsp;<b style="color:#16c784">{st.session_state.shortlisted}</b> shortlisted
  </p>
  <p style="font-size:0.85rem;color:#9898b8;">
    🏆 &nbsp;<b style="color:#ff9f1c">{st.session_state.top_score}</b> top score
  </p>
</div>
""",
                unsafe_allow_html=True,
            )


# ─── Pages ───────────────────────────────────────────────────────────────────
def page_dashboard():
    st.markdown(
        """
<div class="page-header">
  <div class="page-title">Dashboard</div>
  <div class="page-subtitle">Recruitment intelligence platform</div>
</div>
""",
        unsafe_allow_html=True,
    )

    # ── Metric cards ──────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
<div class="metric-card">
  <div class="metric-label">
    <span class="metric-dot" style="background:#f5c518"></span>Resumes Screened
  </div>
  <div class="metric-value">{st.session_state.total_screened}</div>
  <div class="metric-sub">Total resumes analyzed</div>
</div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
<div class="metric-card">
  <div class="metric-label">
    <span class="metric-dot" style="background:#00d4ff"></span>Average Match %
  </div>
  <div class="metric-value">{st.session_state.avg_match}<span style="font-size:1.2rem;color:#5858a8">%</span></div>
  <div class="metric-sub">Across all candidates</div>
</div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
<div class="metric-card">
  <div class="metric-label">
    <span class="metric-dot" style="background:#ff9f1c"></span>Shortlisted
  </div>
  <div class="metric-value">{st.session_state.shortlisted}</div>
  <div class="metric-sub">Score ≥ 70%</div>
</div>""",
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
<div class="metric-card">
  <div class="metric-label">
    <span class="metric-dot" style="background:#e63946"></span>Top Score
  </div>
  <div class="metric-value">{st.session_state.top_score}<span style="font-size:1.2rem;color:#5858a8">/100</span></div>
  <div class="metric-sub">Highest candidate score</div>
</div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Recent candidates ─────────────────────────────────────────────────
    st.markdown(
        '<div class="section-heading">Recent Candidates</div>', unsafe_allow_html=True
    )

    if not st.session_state.candidates:
        st.markdown(
            """
<div class="empty-state">
  <div style="font-size:3rem;margin-bottom:1rem">📄</div>
  <div style="font-size:1rem;font-weight:600;color:#7878a8;margin-bottom:0.5rem">
    No candidates screened yet
  </div>
  <div style="font-size:0.85rem;color:#4a4a6a">
    Go to <b>Screen Candidates</b> to upload and analyze resumes
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        for candidate in st.session_state.candidates[:10]:
            badge_class = score_badge_class(candidate["score"])
            st.markdown(
                f"""
<div class="candidate-row">
  <div>
    <div class="candidate-name">{candidate['name']}</div>
    <div class="candidate-meta">{candidate['timestamp']}</div>
  </div>
  <div>
    <span class="{badge_class}">{candidate['score']}/100</span>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

    # ── Quick actions ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b, _ = st.columns([1, 1, 2])
    with col_a:
        if st.button("🔍  Screen New Resume", key="dash_screen"):
            st.session_state.page = "Screen Candidates"
            st.rerun()
    with col_b:
        if st.button("📈  View Analytics", key="dash_analytics"):
            st.session_state.page = "Analytics"
            st.rerun()


def page_screen_candidates():
    st.markdown(
        """
<div class="page-header">
  <div class="page-title">Screen Candidates</div>
  <div class="page-subtitle">Upload resumes and get AI-powered analysis</div>
</div>
""",
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown(
            """
<div style="background:#111120;border:1px solid #1e1e30;border-radius:16px;padding:1.8rem;">
  <h3 style="font-size:1rem;font-weight:700;color:#d0d0f0;margin-bottom:1.4rem;
     text-transform:uppercase;letter-spacing:0.08em;">📤 Upload Resume</h3>
""",
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader(
            "Drop your PDF here or click to browse",
            type=["pdf"],
            help="Supported format: PDF",
        )

        candidate_name = st.text_input(
            "Candidate Name (optional)",
            placeholder="e.g. John Doe",
        )

        st.markdown(
            '<p style="font-size:0.85rem;color:#5858a8;margin:0.5rem 0 0.3rem;">Job Description <span style="color:#3a3a5a">(optional — improves match accuracy)</span></p>',
            unsafe_allow_html=True,
        )
        job_description = st.text_area(
            "Job Description",
            placeholder="Paste the job description here to get a tailored match score...",
            height=130,
            label_visibility="collapsed",
        )

        analyze_btn = st.button("🚀  Analyze Resume", key="analyze_btn")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        if "current_result" not in st.session_state:
            st.markdown(
                """
<div style="background:linear-gradient(135deg,#0d1f18,#131325);
  border:2px dashed #1e3a2e;border-radius:16px;padding:4rem 2rem;text-align:center;">
  <div style="font-size:3.5rem;margin-bottom:1rem">🎯</div>
  <div style="font-size:1.1rem;font-weight:700;color:#3a6a50;margin-bottom:0.5rem">
    Your analysis will appear here
  </div>
  <div style="font-size:0.85rem;color:#2a4a38">
    Upload a resume and click Analyze to get started
  </div>
</div>
""",
                unsafe_allow_html=True,
            )
        else:
            render_results(st.session_state.current_result)

    # ── Analysis logic ────────────────────────────────────────────────────
    if analyze_btn:
        if not uploaded_file:
            st.warning("⚠️ Please upload a resume PDF first.")
            return
        if not os.getenv("GROQ_API_KEY"):
            st.error("❌ GROQ_API_KEY not set. Please configure your .env file.")
            return

        name = candidate_name.strip() if candidate_name.strip() else "Candidate"
        with st.spinner("🤖 AI is analyzing the resume…"):
            try:
                resume_text = extract_text(uploaded_file)
                if not resume_text:
                    st.error("❌ Could not extract text from PDF. Please check the file.")
                    return

                from scorer import score_resume
                score_data = score_resume(resume_text, job_description)
                score_data["candidate_name"] = name
                score_data["resume_text"] = resume_text

                st.session_state.current_result = score_data
                update_stats(score_data, name)
                st.rerun()
            except Exception as exc:
                st.error(f"❌ Analysis failed: {exc}")


def render_results(data):
    """Render the analysis results panel."""
    overall = data.get("overall_score", 0)
    color = score_color(overall)

    st.markdown(
        f"""
<div style="background:#111120;border:1px solid #1e1e30;border-radius:16px;padding:1.8rem;">
  <h3 style="font-size:1rem;font-weight:700;color:#d0d0f0;margin-bottom:0.2rem;
     text-transform:uppercase;letter-spacing:0.08em;">📊 Analysis Results</h3>
  <p style="font-size:0.8rem;color:#5858a8;margin-bottom:0.5rem">
    {data.get('candidate_name','Candidate')}
  </p>
""",
        unsafe_allow_html=True,
    )

    render_score_ring(overall)

    st.markdown(
        f'<p style="text-align:center;font-size:0.85rem;color:{color};'
        f'font-weight:600;margin-bottom:1.2rem">{data.get("verdict","")}</p>',
        unsafe_allow_html=True,
    )

    # Category bars
    categories = [
        ("Content Quality", data.get("content_score", 70), "#16c784"),
        ("Format & Brevity", data.get("format_score", 70), "#00d4ff"),
        ("Style", data.get("style_score", 70), "#b57bee"),
        ("Sections", data.get("sections_score", 70), "#ff9f1c"),
        ("Skills", data.get("skills_score", 70), "#e63946"),
    ]
    for label, score, cat_color in categories:
        render_category_bar(label, score, cat_color)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Strengths & Improvements
    col_s, col_i = st.columns(2)
    with col_s:
        st.markdown(
            '<div class="result-card"><h4 style="color:#16c784">✅ Strengths</h4>',
            unsafe_allow_html=True,
        )
        for s in data.get("strengths", []):
            st.markdown(
                f'<div class="check-item"><span class="icon">✔</span><span>{s}</span></div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_i:
        st.markdown(
            '<div class="result-card"><h4 style="color:#ff9f1c">⚡ Improvements</h4>',
            unsafe_allow_html=True,
        )
        for imp in data.get("improvements", []):
            st.markdown(
                f'<div class="check-item"><span class="icon">→</span><span>{imp}</span></div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    if data.get("match_score") is not None:
        match = data["match_score"]
        mc = score_color(match)
        st.markdown(
            f"""
<div class="result-card" style="text-align:center;">
  <h4 style="color:#00d4ff">🎯 Job Match Score</h4>
  <div style="font-size:3rem;font-weight:900;color:{mc};margin:0.5rem 0">{match}%</div>
  <div style="font-size:0.82rem;color:#7878a8">Compatibility with provided job description</div>
</div>
""",
            unsafe_allow_html=True,
        )


def page_analytics():
    st.markdown(
        """
<div class="page-header">
  <div class="page-title">Analytics</div>
  <div class="page-subtitle">Insights from your candidate pipeline</div>
</div>
""",
        unsafe_allow_html=True,
    )

    if not st.session_state.candidates:
        st.markdown(
            """
<div class="empty-state">
  <div style="font-size:3rem;margin-bottom:1rem">📈</div>
  <div style="font-size:1rem;font-weight:600;color:#7878a8;margin-bottom:0.5rem">
    No data yet
  </div>
  <div style="font-size:0.85rem;color:#4a4a6a">
    Screen some resumes first to see analytics
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
        return

    # ── Summary row ───────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    shortlisted = [c for c in st.session_state.candidates if c["score"] >= 70]
    consider = [
        c for c in st.session_state.candidates if 50 <= c["score"] < 70
    ]
    rejected = [c for c in st.session_state.candidates if c["score"] < 50]

    with c1:
        st.markdown(
            f"""
<div class="analytics-card" style="border-color:#16c784">
  <div style="font-size:0.75rem;color:#16c784;font-weight:700;
     text-transform:uppercase;letter-spacing:0.1em">Shortlisted</div>
  <div style="font-size:2.5rem;font-weight:900;color:#16c784">{len(shortlisted)}</div>
  <div style="font-size:0.78rem;color:#5858a8">Score ≥ 70</div>
</div>""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
<div class="analytics-card" style="border-color:#ff9f1c">
  <div style="font-size:0.75rem;color:#ff9f1c;font-weight:700;
     text-transform:uppercase;letter-spacing:0.1em">Consider</div>
  <div style="font-size:2.5rem;font-weight:900;color:#ff9f1c">{len(consider)}</div>
  <div style="font-size:0.78rem;color:#5858a8">Score 50–69</div>
</div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
<div class="analytics-card" style="border-color:#e63946">
  <div style="font-size:0.75rem;color:#e63946;font-weight:700;
     text-transform:uppercase;letter-spacing:0.1em">Rejected</div>
  <div style="font-size:2.5rem;font-weight:900;color:#e63946">{len(rejected)}</div>
  <div style="font-size:0.78rem;color:#5858a8">Score &lt; 50</div>
</div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Score distribution bar chart ──────────────────────────────────────
    st.markdown(
        '<div class="section-heading">Score Distribution</div>',
        unsafe_allow_html=True,
    )

    scores = [c["score"] for c in st.session_state.candidates]
    buckets = {"0–49": 0, "50–69": 0, "70–84": 0, "85–100": 0}
    for s in scores:
        if s < 50:
            buckets["0–49"] += 1
        elif s < 70:
            buckets["50–69"] += 1
        elif s < 85:
            buckets["70–84"] += 1
        else:
            buckets["85–100"] += 1

    max_count = max(buckets.values()) if any(buckets.values()) else 1
    bucket_colors = {
        "0–49": "#e63946",
        "50–69": "#ff9f1c",
        "70–84": "#16c784",
        "85–100": "#00d4ff",
    }

    st.markdown(
        '<div class="analytics-card">',
        unsafe_allow_html=True,
    )
    for label, count in buckets.items():
        width = round(count / max_count * 100) if max_count else 0
        st.markdown(
            f"""
<div style="margin-bottom:1rem">
  <div style="display:flex;justify-content:space-between;font-size:0.82rem;
     font-weight:600;color:#a0a0c0;margin-bottom:0.35rem">
    <span>{label}</span><span>{count}</span>
  </div>
  <div style="background:#1a1a2e;border-radius:6px;height:10px;overflow:hidden">
    <div style="width:{width}%;height:100%;background:{bucket_colors[label]};
      border-radius:6px;transition:width 0.6s"></div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── All candidates table ──────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-heading">All Candidates</div>',
        unsafe_allow_html=True,
    )
    for candidate in st.session_state.candidates:
        badge_class = score_badge_class(candidate["score"])
        verdict = candidate.get("verdict", "")
        verdict_snippet = verdict[:60] + "…" if len(verdict) > 60 else verdict
        st.markdown(
            f"""
<div class="candidate-row">
  <div>
    <div class="candidate-name">{candidate['name']}</div>
    <div class="candidate-meta">{candidate['timestamp']} · {verdict_snippet}</div>
  </div>
  <div><span class="{badge_class}">{candidate['score']}/100</span></div>
</div>
""",
            unsafe_allow_html=True,
        )


def page_settings():
    st.markdown(
        """
<div class="page-header">
  <div class="page-title">Settings</div>
  <div class="page-subtitle">Configure your ResuMatch workspace</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="result-card">',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<h4 style="color:#00d4ff;margin-bottom:1rem">🔑 API Configuration</h4>',
        unsafe_allow_html=True,
    )

    api_key = os.getenv("GROQ_API_KEY", "")
    if len(api_key) > 6:
        masked = "•" * 20 + api_key[-6:]
    elif api_key:
        masked = api_key
    else:
        masked = "Not configured"

    st.markdown(
        f'<p style="font-size:0.85rem;color:#9898b8">GROQ API Key: '
        f'<code style="background:#1a1a2e;padding:0.2rem 0.6rem;border-radius:6px;'
        f'color:#16c784">{masked}</code></p>',
        unsafe_allow_html=True,
    )

    if not api_key:
        st.warning(
            "⚠️ GROQ_API_KEY is not set. Create a `.env` file with `GROQ_API_KEY=your_key`."
        )
    else:
        st.success("✅ API key is configured and ready.")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div class="result-card">',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<h4 style="color:#ff9f1c;margin-bottom:1rem">🗑️ Data Management</h4>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-size:0.85rem;color:#7878a8;margin-bottom:1rem">Clear all screening history and reset statistics.</p>',
        unsafe_allow_html=True,
    )
    if st.button("🗑️  Clear All Data", key="clear_data"):
        st.session_state.candidates = []
        st.session_state.total_screened = 0
        st.session_state.shortlisted = 0
        st.session_state.top_score = 0
        st.session_state.avg_match = 0
        if "current_result" in st.session_state:
            del st.session_state["current_result"]
        st.success("✅ All data cleared.")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
<div class="result-card">
  <h4 style="color:#b57bee;margin-bottom:1rem">ℹ️ About ResuMatch</h4>
  <p style="font-size:0.85rem;color:#9898b8;line-height:1.6">
    <b style="color:#e0e0f0">ResuMatch</b> is an AI-powered resume screening platform built with
    <b style="color:#16c784">Streamlit</b> and <b style="color:#00d4ff">Groq LLM</b>.
    It helps recruiters quickly evaluate and rank candidates based on resume quality and
    job fit.<br><br>
    <span style="color:#5858a8">Model: llama-3.3-70b-versatile &nbsp;·&nbsp; Version 2.0</span>
  </p>
</div>
""",
        unsafe_allow_html=True,
    )


# ─── Router ──────────────────────────────────────────────────────────────────
sidebar()

page = st.session_state.page
if page == "Dashboard":
    page_dashboard()
elif page == "Screen Candidates":
    page_screen_candidates()
elif page == "Analytics":
    page_analytics()
elif page == "Settings":
    page_settings()
