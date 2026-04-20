import streamlit as st
import sys
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Path setup so utils can be imported regardless of cwd
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))

from pdf_reader import extract_text_from_pdf  # noqa: E402
from scorer import analyze_resume_structured  # noqa: E402

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ResuMatch — AI Resume Screener",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — Professional Light Theme
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global reset ── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ── Main background ── */
    .stApp {
        background: #f0f4f8;
    }

    /* ── Hide default Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e8ecf0;
        box-shadow: 2px 0 12px rgba(0,0,0,.05);
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
    }

    /* ── Metric cards ── */
    .metric-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 24px 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,.06);
        border: 1px solid #f0f2f5;
        height: 100%;
        transition: transform .2s, box-shadow .2s;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0,0,0,.10);
    }
    .metric-dot {
        width: 10px; height: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    .metric-label {
        font-size: 13px;
        font-weight: 500;
        color: #8a94a6;
        letter-spacing: .3px;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 36px;
        font-weight: 700;
        color: #1a2236;
        line-height: 1.2;
        margin: 8px 0 4px;
    }
    .metric-change {
        font-size: 12px;
        font-weight: 500;
        color: #16c784;
    }
    .metric-change.negative { color: #e74c3c; }

    /* ── Section header ── */
    .section-header {
        font-size: 20px;
        font-weight: 700;
        color: #1a2236;
        margin: 0 0 4px;
    }
    .section-sub {
        font-size: 13px;
        color: #8a94a6;
        margin: 0 0 20px;
    }

    /* ── White card wrapper ── */
    .white-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,.06);
        border: 1px solid #f0f2f5;
        margin-bottom: 20px;
    }

    /* ── Candidate row ── */
    .candidate-row {
        display: flex;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f5f7fa;
        gap: 14px;
    }
    .candidate-row:last-child { border-bottom: none; }
    .candidate-avatar {
        width: 40px; height: 40px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 15px; font-weight: 700; color: #fff;
        flex-shrink: 0;
    }
    .candidate-name { font-size: 14px; font-weight: 600; color: #1a2236; }
    .candidate-role { font-size: 12px; color: #8a94a6; }
    .score-badge {
        margin-left: auto;
        font-size: 13px; font-weight: 700;
        padding: 4px 12px; border-radius: 20px;
    }

    /* ── Upload zone ── */
    .upload-zone {
        background: linear-gradient(135deg, #f0fdf7 0%, #f0f4ff 100%);
        border: 2px dashed #16c784;
        border-radius: 20px;
        padding: 48px 32px;
        text-align: center;
        cursor: pointer;
        transition: border-color .2s, background .2s;
    }
    .upload-zone:hover {
        border-color: #00d4ff;
        background: linear-gradient(135deg, #e6faf3 0%, #e8eeff 100%);
    }
    .upload-icon { font-size: 48px; margin-bottom: 16px; }
    .upload-title { font-size: 22px; font-weight: 700; color: #1a2236; margin: 0 0 8px; }
    .upload-sub { font-size: 14px; color: #8a94a6; }

    /* ── Score circle ── */
    .score-circle-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px 0;
    }
    .score-ring {
        position: relative;
        width: 160px; height: 160px;
    }
    .score-ring svg { transform: rotate(-90deg); }
    .score-ring-text {
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
    }
    .score-number { font-size: 38px; font-weight: 800; color: #1a2236; line-height: 1; }
    .score-label { font-size: 12px; color: #8a94a6; margin-top: 4px; }

    /* ── Category bar ── */
    .category-row {
        margin-bottom: 16px;
    }
    .category-header {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 6px;
    }
    .category-name { font-size: 13px; font-weight: 600; color: #1a2236; }
    .category-score { font-size: 13px; font-weight: 700; }
    .bar-bg {
        background: #f0f2f5;
        border-radius: 99px;
        height: 8px;
        overflow: hidden;
    }
    .bar-fill {
        height: 100%;
        border-radius: 99px;
        transition: width .6s ease;
    }

    /* ── Check / cross list ── */
    .check-item {
        font-size: 13px; color: #1a2236;
        padding: 4px 0;
        display: flex; align-items: flex-start; gap: 8px;
    }
    .check-icon { flex-shrink: 0; }

    /* ── Insight cards ── */
    .insight-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
        border-left: 4px solid #16c784;
        font-size: 13px;
        color: #1a2236;
    }
    .insight-card.improvement { border-left-color: #ff9f1c; }

    /* ── Nav button override ── */
    div[data-testid="stButton"] > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all .2s !important;
    }

    /* ── Page title gradient ── */
    .page-title {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(90deg, #16c784, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        display: inline-block;
        margin: 0;
    }
    .page-subtitle {
        font-size: 14px;
        color: #8a94a6;
        margin: 2px 0 24px;
        font-weight: 400;
    }

    /* ── Streamlit file-uploader cleanup ── */
    [data-testid="stFileUploader"] {
        border: none !important;
        background: transparent !important;
    }

    /* ── Tag pill ── */
    .tag-pill {
        display: inline-block;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        margin: 2px 3px 2px 0;
    }

    /* ── Status badges ── */
    .status-badge {
        font-size: 11px; font-weight: 600;
        padding: 3px 10px; border-radius: 20px;
        display: inline-block;
    }
    .status-green  { background: #e6faf3; color: #16c784; }
    .status-orange { background: #fff4e5; color: #ff9f1c; }
    .status-red    { background: #fdecea; color: #e74c3c; }
    .status-blue   { background: #e5f8ff; color: #00a8cc; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "candidates" not in st.session_state:
    st.session_state.candidates = [
        {"name": "Sarah Johnson", "role": "Software Engineer", "score": 87, "date": "2026-04-18", "color": "#16c784"},
        {"name": "Marcus Lee",    "role": "Data Scientist",     "score": 74, "date": "2026-04-17", "color": "#00d4ff"},
        {"name": "Priya Sharma",  "role": "Product Manager",    "score": 91, "date": "2026-04-16", "color": "#9b59b6"},
        {"name": "David Chen",    "role": "DevOps Engineer",    "score": 62, "date": "2026-04-15", "color": "#ff9f1c"},
    ]
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = os.getenv("GROQ_API_KEY", "")

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    # Logo / brand
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:28px;">
            <div style="width:38px;height:38px;border-radius:10px;
                        background:linear-gradient(135deg,#16c784,#00d4ff);
                        display:flex;align-items:center;justify-content:center;
                        font-size:18px;font-weight:900;color:#fff;">R</div>
            <div>
                <div style="font-size:17px;font-weight:800;color:#1a2236;line-height:1;">ResuMatch</div>
                <div style="font-size:11px;color:#8a94a6;font-weight:400;">AI Resume Screener</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav_items = [
        ("🏠", "Dashboard"),
        ("🔍", "Screen Candidates"),
        ("📊", "Analytics"),
        ("⚙️", "Settings"),
    ]

    for icon, label in nav_items:
        active = st.session_state.page == label
        btn_style = (
            "background:linear-gradient(90deg,#16c784,#00d4ff);color:#fff;"
            if active
            else "background:#f5f7fa;color:#1a2236;"
        )
        if st.button(
            f"{icon}  {label}",
            key=f"nav_{label}",
            use_container_width=True,
            type="primary" if active else "secondary",
        ):
            st.session_state.page = label
            st.rerun()

    st.markdown("<hr style='border:none;border-top:1px solid #f0f2f5;margin:20px 0;'>", unsafe_allow_html=True)

    # Quick stats in sidebar
    total = len(st.session_state.candidates)
    avg_score = (
        sum(c["score"] for c in st.session_state.candidates) // total if total else 0
    )
    st.markdown(
        f"""
        <div style="background:#f8f9fb;border-radius:12px;padding:14px 16px;">
            <div style="font-size:12px;color:#8a94a6;font-weight:600;text-transform:uppercase;letter-spacing:.4px;margin-bottom:10px;">Quick Stats</div>
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-size:13px;color:#1a2236;">Total Screened</span>
                <span style="font-size:13px;font-weight:700;color:#16c784;">{total}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="font-size:13px;color:#1a2236;">Avg Score</span>
                <span style="font-size:13px;font-weight:700;color:#00d4ff;">{avg_score}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def score_color(score: int) -> str:
    if score >= 80:
        return "#16c784"
    if score >= 60:
        return "#ff9f1c"
    return "#e74c3c"


def score_status(score: int) -> str:
    if score >= 80:
        return '<span class="status-badge status-green">Excellent</span>'
    if score >= 60:
        return '<span class="status-badge status-orange">Good</span>'
    return '<span class="status-badge status-red">Needs Work</span>'


def render_score_circle(score: int, size: int = 160):
    r = 60
    cx = cy = size // 2
    circumference = 2 * 3.14159 * r
    dash = circumference * score / 100
    color = score_color(score)
    return f"""
    <div class="score-circle-wrapper">
        <div class="score-ring" style="width:{size}px;height:{size}px;">
            <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
                <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#f0f2f5" stroke-width="14"/>
                <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="14"
                        stroke-dasharray="{dash:.1f} {circumference:.1f}"
                        stroke-linecap="round"/>
            </svg>
            <div class="score-ring-text">
                <div class="score-number" style="color:{color};">{score}</div>
                <div class="score-label">/ 100</div>
            </div>
        </div>
        <div style="margin-top:10px;font-size:14px;font-weight:600;color:#1a2236;">Resume Score</div>
    </div>
    """


def render_category_bar(name: str, score: int, color: str):
    return f"""
    <div class="category-row">
        <div class="category-header">
            <span class="category-name">{name}</span>
            <span class="category-score" style="color:{color};">{score}%</span>
        </div>
        <div class="bar-bg">
            <div class="bar-fill" style="width:{score}%;background:{color};"></div>
        </div>
    </div>
    """


def render_check_items(items: list, passed: bool = True):
    icon = "✅" if passed else "❌"
    return "".join(
        f'<div class="check-item"><span class="check-icon">{icon}</span><span>{item}</span></div>'
        for item in items
    )

# ---------------------------------------------------------------------------
# Page: Dashboard
# ---------------------------------------------------------------------------

def page_dashboard():
    st.markdown(
        '<p class="page-title">Dashboard</p>'
        '<p class="page-subtitle">Recruitment intelligence platform</p>',
        unsafe_allow_html=True,
    )

    # ── Metric cards ──
    metrics = [
        ("Total Resumes",    str(len(st.session_state.candidates)), "+3 this week",  "#16c784", True),
        ("Avg Score",        f"{sum(c['score'] for c in st.session_state.candidates) // max(len(st.session_state.candidates),1)}",
                             "+5 pts vs last week",                                  "#00d4ff", True),
        ("Top Candidates",   str(sum(1 for c in st.session_state.candidates if c["score"] >= 80)),
                             "Score ≥ 80",                                            "#9b59b6", True),
        ("Needs Review",     str(sum(1 for c in st.session_state.candidates if c["score"] < 60)),
                             "Score < 60",                                            "#ff9f1c", False),
    ]

    cols = st.columns(4, gap="medium")
    for col, (label, value, change, color, positive) in zip(cols, metrics):
        with col:
            change_cls = "" if positive else "negative"
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">
                        <span class="metric-dot" style="background:{color};"></span>{label}
                    </div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-change {change_cls}">{change}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Recent candidates ──
    col_left, col_right = st.columns([3, 2], gap="medium")

    with col_left:
        st.markdown(
            '<div class="white-card">'
            '<div class="section-header">Recent Candidates</div>'
            '<div class="section-sub">Latest resume screenings</div>',
            unsafe_allow_html=True,
        )

        for c in st.session_state.candidates:
            initials = "".join(p[0].upper() for p in c["name"].split()[:2])
            s_color = score_color(c["score"])
            badge_bg = "#e6faf3" if c["score"] >= 80 else ("#fff4e5" if c["score"] >= 60 else "#fdecea")
            st.markdown(
                f"""
                <div class="candidate-row">
                    <div class="candidate-avatar" style="background:{c['color']};">{initials}</div>
                    <div>
                        <div class="candidate-name">{c['name']}</div>
                        <div class="candidate-role">{c['role']} · {c['date']}</div>
                    </div>
                    <div class="score-badge" style="background:{badge_bg};color:{s_color};">
                        {c['score']}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown(
            '<div class="white-card">'
            '<div class="section-header">Score Distribution</div>'
            '<div class="section-sub">Candidates by performance tier</div>',
            unsafe_allow_html=True,
        )

        tiers = [
            ("Excellent (80-100)", sum(1 for c in st.session_state.candidates if c["score"] >= 80), "#16c784"),
            ("Good (60-79)",       sum(1 for c in st.session_state.candidates if 60 <= c["score"] < 80), "#ff9f1c"),
            ("Needs Work (<60)",   sum(1 for c in st.session_state.candidates if c["score"] < 60), "#e74c3c"),
        ]
        total_c = max(len(st.session_state.candidates), 1)
        for tier_name, count, color in tiers:
            pct = int(count / total_c * 100)
            st.markdown(
                f"""
                <div style="margin-bottom:16px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
                        <span style="font-size:13px;font-weight:500;color:#1a2236;">{tier_name}</span>
                        <span style="font-size:13px;font-weight:700;color:{color};">{count}</span>
                    </div>
                    <div class="bar-bg">
                        <div class="bar-fill" style="width:{pct}%;background:{color};"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # Quick-action card
        st.markdown(
            """
            <div style="background:linear-gradient(135deg,#e6faf3,#e5f8ff);
                        border-radius:16px;padding:20px;border:1px solid #d0f0e6;">
                <div style="font-size:15px;font-weight:700;color:#1a2236;margin-bottom:6px;">
                    🚀 Screen a Resume
                </div>
                <div style="font-size:13px;color:#5a6478;">
                    Upload a PDF to get an instant AI-powered analysis and score.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to Screener →", use_container_width=True, type="primary"):
            st.session_state.page = "Screen Candidates"
            st.rerun()

# ---------------------------------------------------------------------------
# Page: Screen Candidates
# ---------------------------------------------------------------------------

def page_screen():
    st.markdown(
        '<p class="page-title">Screen Candidates</p>'
        '<p class="page-subtitle">Upload a resume PDF for instant AI analysis</p>',
        unsafe_allow_html=True,
    )

    col_upload, col_result = st.columns([1, 1], gap="large")

    with col_upload:
        st.markdown(
            """
            <div class="upload-zone">
                <div class="upload-icon">📄</div>
                <div class="upload-title">Is your resume good enough?</div>
                <div class="upload-sub">Drop your PDF here or click to browse.<br>
                    Get an instant score and detailed feedback.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            label_visibility="collapsed",
        )

        job_description = st.text_area(
            "Job Description (optional)",
            placeholder="Paste the job description here to get a tailored analysis…",
            height=130,
        )

        api_key = st.session_state.groq_api_key or os.getenv("GROQ_API_KEY", "")
        if not api_key:
            st.warning("⚠️ No GROQ_API_KEY found. Add it in **Settings** or your `.env` file.")

        analyze_btn = st.button(
            "✦  Analyze Resume",
            use_container_width=True,
            type="primary",
            disabled=(uploaded_file is None or not api_key),
        )

        if analyze_btn and uploaded_file and api_key:
            with st.spinner("Analyzing resume with AI…"):
                try:
                    pdf_bytes = uploaded_file.read()
                    resume_text = extract_text_from_pdf(pdf_bytes)
                    if not resume_text.strip():
                        st.error("Could not extract text from this PDF. Please try another file.")
                    else:
                        result = analyze_resume_structured(resume_text, job_description)
                        st.session_state.analysis_result = result

                        # Add to candidates list
                        new_candidate = {
                            "name": result.get("candidate_name", uploaded_file.name),
                            "role": "Screened via Upload",
                            "score": result.get("overall_score", 0),
                            "date": datetime.today().strftime("%Y-%m-%d"),
                            "color": score_color(result.get("overall_score", 0)),
                        }
                        st.session_state.candidates.insert(0, new_candidate)
                        st.success("Analysis complete! 🎉")
                        st.rerun()
                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")

    with col_result:
        result = st.session_state.analysis_result
        if result is None:
            st.markdown(
                """
                <div class="white-card" style="text-align:center;padding:60px 32px;color:#8a94a6;">
                    <div style="font-size:56px;margin-bottom:16px;">📋</div>
                    <div style="font-size:18px;font-weight:600;color:#1a2236;margin-bottom:8px;">
                        No Analysis Yet
                    </div>
                    <div style="font-size:14px;">
                        Upload a resume PDF and click <strong>Analyze Resume</strong>
                        to see detailed results here.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            overall = result.get("overall_score", 0)
            name = result.get("candidate_name", "Candidate")
            summary = result.get("summary", "")

            # Score header card
            st.markdown(
                f"""
                <div class="white-card" style="margin-bottom:16px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;">
                        <div>
                            <div style="font-size:20px;font-weight:800;color:#1a2236;">{name}</div>
                            <div style="font-size:13px;color:#8a94a6;margin-top:2px;">{summary[:160]}{"…" if len(summary)>160 else ""}</div>
                        </div>
                        {render_score_circle(overall, 140)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Category breakdown
            categories = result.get("categories", [])
            cat_html = "".join(
                render_category_bar(c["name"], c["score"], c.get("color", "#16c784"))
                for c in categories
            )
            st.markdown(
                f'<div class="white-card"><div class="section-header" style="margin-bottom:16px;">Category Breakdown</div>'
                f"{cat_html}</div>",
                unsafe_allow_html=True,
            )

            # Checks and improvements
            col_a, col_b = st.columns(2, gap="medium")
            with col_a:
                strengths = result.get("strengths", [])
                items_html = render_check_items(strengths, passed=True)
                st.markdown(
                    f'<div class="white-card"><div class="section-header" style="font-size:15px;margin-bottom:12px;">✅ Strengths</div>'
                    f"{items_html}</div>",
                    unsafe_allow_html=True,
                )

            with col_b:
                improvements = result.get("improvements", [])
                items_html = render_check_items(improvements, passed=False)
                st.markdown(
                    f'<div class="white-card"><div class="section-header" style="font-size:15px;margin-bottom:12px;">🔧 Improvements</div>'
                    f"{items_html}</div>",
                    unsafe_allow_html=True,
                )

            # Per-category detail
            with st.expander("📂 Detailed Category Feedback", expanded=False):
                for cat in categories:
                    color = cat.get("color", "#16c784")
                    st.markdown(
                        f"""
                        <div style="border-left:4px solid {color};padding:12px 16px;
                                    background:#f8f9fb;border-radius:0 10px 10px 0;margin-bottom:12px;">
                            <div style="font-size:14px;font-weight:700;color:#1a2236;margin-bottom:6px;">
                                {cat['name']} — <span style="color:{color};">{cat['score']}%</span>
                            </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    passed = cat.get("passed_items", [])
                    failed = cat.get("failed_items", [])
                    if passed:
                        st.markdown(render_check_items(passed, True), unsafe_allow_html=True)
                    if failed:
                        st.markdown(render_check_items(failed, False), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            if st.button("🔄 Clear Analysis", use_container_width=False):
                st.session_state.analysis_result = None
                st.rerun()

# ---------------------------------------------------------------------------
# Page: Analytics
# ---------------------------------------------------------------------------

def page_analytics():
    st.markdown(
        '<p class="page-title">Analytics</p>'
        '<p class="page-subtitle">Insights from your screening history</p>',
        unsafe_allow_html=True,
    )

    candidates = st.session_state.candidates
    if not candidates:
        st.info("No candidates screened yet. Go to **Screen Candidates** to get started.")
        return

    scores = [c["score"] for c in candidates]
    avg = sum(scores) / len(scores)

    # Summary row
    summary_cols = st.columns(3, gap="medium")
    summaries = [
        ("📋 Total Screened",  str(len(candidates)), "#16c784"),
        ("📈 Average Score",   f"{avg:.1f}",         "#00d4ff"),
        ("🏆 Highest Score",   str(max(scores)),     "#9b59b6"),
    ]
    for scol, (label, val, color) in zip(summary_cols, summaries):
        with scol:
            st.markdown(
                f"""
                <div class="metric-card" style="text-align:center;">
                    <div style="font-size:24px;margin-bottom:6px;">{label.split()[0]}</div>
                    <div class="metric-label">{' '.join(label.split()[1:])}</div>
                    <div class="metric-value" style="font-size:28px;color:{color};">{val}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Candidate score table
    st.markdown(
        '<div class="white-card">'
        '<div class="section-header">All Candidates</div>'
        '<div class="section-sub">Full screening history</div>',
        unsafe_allow_html=True,
    )

    header_html = """
    <div style="display:flex;padding:8px 0;border-bottom:2px solid #f0f2f5;
                font-size:11px;font-weight:700;color:#8a94a6;text-transform:uppercase;letter-spacing:.5px;">
        <div style="flex:2;">Candidate</div>
        <div style="flex:2;">Role</div>
        <div style="flex:1;">Date</div>
        <div style="flex:1;text-align:right;">Score</div>
    </div>
    """
    rows_html = ""
    for c in candidates:
        s_color = score_color(c["score"])
        badge_bg = "#e6faf3" if c["score"] >= 80 else ("#fff4e5" if c["score"] >= 60 else "#fdecea")
        initials = "".join(p[0].upper() for p in c["name"].split()[:2])
        rows_html += f"""
        <div style="display:flex;align-items:center;padding:10px 0;border-bottom:1px solid #f5f7fa;">
            <div style="flex:2;display:flex;align-items:center;gap:10px;">
                <div style="width:32px;height:32px;border-radius:50%;background:{c['color']};
                             display:flex;align-items:center;justify-content:center;
                             font-size:12px;font-weight:700;color:#fff;flex-shrink:0;">{initials}</div>
                <span style="font-size:13px;font-weight:600;color:#1a2236;">{c['name']}</span>
            </div>
            <div style="flex:2;font-size:13px;color:#5a6478;">{c['role']}</div>
            <div style="flex:1;font-size:12px;color:#8a94a6;">{c['date']}</div>
            <div style="flex:1;text-align:right;">
                <span class="score-badge" style="background:{badge_bg};color:{s_color};">{c['score']}%</span>
            </div>
        </div>
        """
    st.markdown(header_html + rows_html + "</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Page: Settings
# ---------------------------------------------------------------------------

def page_settings():
    st.markdown(
        '<p class="page-title">Settings</p>'
        '<p class="page-subtitle">Configure your ResuMatch workspace</p>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown("#### 🔑 API Configuration")

    new_key = st.text_input(
        "Groq API Key",
        value=st.session_state.groq_api_key,
        type="password",
        placeholder="gsk_…",
        help="Get your free API key at console.groq.com",
    )
    if new_key != st.session_state.groq_api_key:
        st.session_state.groq_api_key = new_key
        os.environ["GROQ_API_KEY"] = new_key

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown("#### 🗂️ Data Management")
    if st.button("🗑️  Clear All Candidates", type="secondary"):
        st.session_state.candidates = []
        st.session_state.analysis_result = None
        st.success("Candidate history cleared.")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="white-card">', unsafe_allow_html=True)
    st.markdown("#### ℹ️ About ResuMatch")
    st.markdown(
        """
        **ResuMatch** is an AI-powered resume screening platform built with:
        - 🤖 **Groq LLM** (`llama-3.3-70b-versatile`) for intelligent analysis
        - 📄 **pdfplumber** for accurate PDF text extraction
        - 🎨 **Streamlit** for the web interface

        Built as a professional SaaS-quality tool with light theme design.
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
page = st.session_state.page
if page == "Dashboard":
    page_dashboard()
elif page == "Screen Candidates":
    page_screen()
elif page == "Analytics":
    page_analytics()
elif page == "Settings":
    page_settings()
