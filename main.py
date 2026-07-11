"""
main.py — Streamlit Web Interface
===================================
Professional, dark-themed AI Data Analysis Assistant.
Covers all 5 challenge steps plus bonus features:
  CSV upload, modern UI, multiple charts, dark mode,
  export chart as PNG, export analysis as PDF,
  multi-agent AI integration.
"""

import streamlit as st
import os
import io
from dotenv import load_dotenv

import analysis
import visualization
import ai_helper
import importlib

# Force reload local modules so Streamlit doesn't cache old versions
importlib.reload(analysis)
importlib.reload(visualization)
importlib.reload(ai_helper)

# ---------------------------------------------------------------------------
# Environment & page config
# ---------------------------------------------------------------------------
load_dotenv()

st.set_page_config(
    page_title="AI Data Analysis Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"
if "bg_color" not in st.session_state:
    st.session_state.bg_color = "#0f0c29"

# ---------------------------------------------------------------------------
# Header & Theme Toggle (Navbar style)
# ---------------------------------------------------------------------------
header_col, theme_col = st.columns([4, 1])

with header_col:
    st.markdown("""
    <div class="main-header" style="text-align: left; padding: 10px 0;">
        <div class="main-title" style="font-size: 2.2rem;"><i class="fas fa-microscope"></i> AI Data Analysis Assistant</div>
        <div class="main-subtitle">Multi-Agent Intelligence · Automated Insights · Beautiful Charts</div>
    </div>
    """, unsafe_allow_html=True)

with theme_col:
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    theme = st.selectbox("Theme Mode", ["Dark", "Light"], index=0 if st.session_state.theme == "Dark" else 1, label_visibility="collapsed")
    default_bg = "#0f0c29" if theme == "Dark" else "#ffffff"
    bg_color = st.color_picker("Background Color", default_bg, label_visibility="collapsed")
    st.session_state.theme = theme
    st.session_state.bg_color = bg_color

# ---------------------------------------------------------------------------
# Custom CSS — Dynamic theme based on user selection
# ---------------------------------------------------------------------------
is_light = st.session_state.theme == "Light"
text_color = "#1e293b" if is_light else "#ffffff"
card_bg = "#ffffff" if is_light else "rgba(255,255,255,0.04)"
card_border = "rgba(139,92,246,0.3)" if is_light else "rgba(139,92,246,0.12)"
input_bg = "#ffffff" if is_light else "rgba(255,255,255,0.05)"
input_border = "#cbd5e1" if is_light else "rgba(139,92,246,0.2)"
sidebar_bg = "#f1f5f9" if is_light else st.session_state.bg_color
popover_bg = "#ffffff" if is_light else "#1a1a2e"
chat_user_bg = "#ede9fe" if is_light else "rgba(139,92,246,0.15)"
chat_bot_bg = "#f8fafc" if is_light else "rgba(255,255,255,0.05)"
subtitle_color = "#64748b" if is_light else "rgba(196,181,253,0.7)"
expander_bg = "#ffffff" if is_light else "rgba(255,255,255,0.03)"
tab_text = "#475569" if is_light else "#c4b5fd"
metric_label_color = "#64748b" if is_light else text_color

st.markdown(f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, .stApp {{
        font-family: 'Inter', sans-serif !important;
        background: {st.session_state.bg_color} !important;
        color: {text_color} !important;
    }}

    /* All text elements */
    h1, h2, h3, h4, h5, h6, p, span, label, li, td, th, div {{
        color: {text_color} !important;
    }}

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        border-right: 1px solid rgba(139,92,246,0.15);
    }}
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {{
        color: {text_color} !important;
    }}

    /* ---- Header ---- */
    .main-header {{ text-align: left; padding: 10px 0; }}
    .main-title {{
        background: linear-gradient(90deg, #a78bfa, #818cf8, #6366f1, #818cf8);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        animation: gradientShift 6s ease infinite;
    }}
    @keyframes gradientShift {{
        0%   {{ background-position: 0% 50%; }}
        50%  {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    .main-subtitle {{ color: {subtitle_color} !important; font-size: 1.05rem; }}

    /* ---- Metric Cards ---- */
    .metric-row {{ display: flex; gap: 16px; flex-wrap: wrap; }}
    .metric-card {{
        flex: 1; min-width: 140px;
        background: {card_bg};
        border-radius: 14px; padding: 22px 18px; text-align: center;
        border: 1px solid {card_border};
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .metric-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 30px rgba(139,92,246,0.25); }}
    .metric-value {{ font-size: 2.2rem; font-weight: 700; color: #a78bfa !important; }}
    .metric-label {{ font-size: 0.78rem; text-transform: uppercase; letter-spacing: 1.2px; color: {metric_label_color} !important; }}

    /* ---- Section Headers ---- */
    .section-header {{ font-size: 1.35rem; font-weight: 700; color: #c4b5fd !important; margin: 28px 0 10px 0; }}

    /* ---- Agent Badges ---- */
    .agent-badge {{
        display: inline-block; padding: 3px 12px; border-radius: 20px;
        font-size: 0.72rem; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;
    }}
    .badge-analyst  {{ background: rgba(34,197,94,0.15); color: #4ade80 !important; border: 1px solid rgba(34,197,94,0.3); }}
    .badge-explainer {{ background: rgba(96,165,250,0.15); color: #93c5fd !important; border: 1px solid rgba(96,165,250,0.3); }}
    .badge-insight  {{ background: rgba(251,146,60,0.15); color: #fdba74 !important; border: 1px solid rgba(251,146,60,0.3); }}

    /* ---- AI Answer Boxes ---- */
    .ai-answer {{
        background: {card_bg};
        color: {text_color} !important;
        border-left: 3px solid #8b5cf6; border-radius: 0 12px 12px 0;
        padding: 16px 20px; margin: 10px 0; line-height: 1.6;
    }}
    .ai-answer * {{ color: {text_color} !important; }}

    /* ---- Input Fields & Chat Input ---- */
    .stTextInput > div > div,
    .stTextInput > div > div > input,
    .stTextArea textarea,
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="input"] input,
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] div,
    [data-testid="stChatInput"] textarea {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
    }}
    .stTextInput > div > div > input::placeholder,
    .stTextArea textarea::placeholder,
    [data-testid="stChatInput"] textarea::placeholder {{
        color: {'#94a3b8' if is_light else '#64748b'} !important;
        -webkit-text-fill-color: {'#94a3b8' if is_light else '#64748b'} !important;
    }}

    /* ---- Select / Dropdown Boxes (Including Theme Toggle) ---- */
    [data-testid="stSelectbox"] div,
    div[data-baseweb="select"] div,
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] *,
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[data-testid="stVirtualDropdown"],
    div[data-testid="stVirtualDropdown"] *,
    [data-baseweb="menu"] li,
    ul[role="listbox"] li {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
    }}
    [data-testid="stSelectbox"] p,
    [data-testid="stSelectbox"] span,
    [data-testid="stSelectbox"] label {{
        color: {text_color} !important;
        background-color: transparent !important;
    }}
    [data-testid="stSelectbox"] svg {{
        fill: {text_color} !important;
        color: {text_color} !important;
    }}
    [data-baseweb="menu"] li:hover,
    ul[role="listbox"] li:hover,
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"],
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="popover"] li[aria-selected="true"],
    [data-testid="stSelectbox"] li:hover {{
        background-color: {'#f1f5f9' if is_light else 'rgba(139,92,246,0.2)'} !important;
        color: {text_color} !important;
    }}
    [data-baseweb="menu"] li:hover *,
    ul[role="listbox"] li:hover *,
    li[role="option"]:hover *,
    li[role="option"][aria-selected="true"] *,
    div[data-baseweb="popover"] li:hover *,
    div[data-baseweb="popover"] li[aria-selected="true"] *,
    [data-testid="stSelectbox"] li:hover * {{
        color: {text_color} !important;
    }}

    /* ---- Buttons ---- */
    button[data-testid*="baseButton"],
    .stButton button,
    .stDownloadButton button,
    button[kind="primary"],
    button[kind="secondary"],
    button {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid {card_border} !important;
        transition: all 0.3s;
    }}
    button[data-testid*="baseButton"] *,
    .stButton button *,
    .stDownloadButton button *,
    button * {{
        color: {text_color} !important;
        background-color: transparent !important;
    }}
    button[data-testid*="baseButton"]:hover,
    button:hover,
    .stButton button:hover {{
        background-color: {input_bg} !important;
        border-color: #a78bfa !important;
        transform: scale(1.02);
    }}
    button[data-testid*="baseButton"]:hover *,
    button:hover *,
    .stButton button:hover * {{
        color: {text_color} !important;
    }}
    /* Disable Streamlit's dark overlay on hover */
    button:hover::before,
    .stButton button:hover::before,
    button[data-testid*="baseButton"]:hover::before {{
        display: none !important;
        background-color: transparent !important;
    }}

    /* ---- File Uploader ---- */
    [data-testid="stFileUploader"] {{
        background-color: transparent !important;
    }}
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploaderDropzone"] div {{
        background-color: {input_bg} !important;
        border-color: {input_border} !important;
    }}
    [data-testid="stFileUploaderDropzone"] * {{
        color: {text_color} !important;
    }}
    [data-testid="stFileUploaderDropzone"] button {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid {card_border} !important;
    }}

    /* ---- Expanders ---- */
    details[data-testid="stExpander"] {{
        background-color: {expander_bg} !important;
        border: 1px solid {card_border} !important;
        border-radius: 10px !important;
    }}
    details[data-testid="stExpander"] > summary ~ div {{
        background-color: {expander_bg} !important;
    }}
    details[data-testid="stExpander"] *,
    details[data-testid="stExpander"] > summary ~ div * {{
        color: {text_color} !important;
    }}

    /* ---- JSON display ---- */
    [data-testid="stJson"] {{
        background-color: transparent !important;
    }}
    [data-testid="stJson"] *,
    .react-json-view,
    .react-json-view * {{
        color: {text_color} !important;
        background-color: transparent !important;
    }}

    /* ---- Tabs ---- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {tab_text} !important;
        background-color: transparent !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: #8b5cf6 !important;
        border-bottom: 2px solid #8b5cf6 !important;
    }}

    /* ---- Chat Messages (inside popover widget) ---- */
    [data-testid="stChatMessage"] {{
        background-color: {chat_bot_bg} !important;
        border-radius: 10px !important;
        margin-bottom: 4px;
    }}
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] div,
    [data-testid="stChatMessage"] span {{
        color: {text_color} !important;
        background-color: transparent !important;
    }}

    /* ---- Color Picker ---- */
    .stColorPicker label {{
        color: {text_color} !important;
    }}

    /* ---- Popover (Chat Widget) ---- */
    div[data-testid="stPopoverBody"] {{
        background-color: {popover_bg} !important;
        color: {text_color} !important;
    }}
    div[data-testid="stPopoverBody"] p,
    div[data-testid="stPopoverBody"] span,
    div[data-testid="stPopoverBody"] div,
    div[data-testid="stPopoverBody"] h4 {{
        color: {text_color} !important;
    }}

    /* ---- Spinner / Status messages ---- */
    .stSpinner > div {{
        color: {text_color} !important;
    }}
    .stAlert p, .stAlert div {{
        color: {text_color} !important;
    }}

    /* ---- Welcome Card ---- */
    .welcome-text {{
        color: {subtitle_color} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### <i class='fas fa-cog'></i> Configuration", unsafe_allow_html=True)
    st.markdown("---")

    model_options = [
        "Groq Llama 3.1 8B",
        "Groq Llama 3.3 70B",
        "Azure ChatGPT-4o-mini",
        "Gemini Medium (3.5 Flash)",
        "Gemini Low (3.1 Flash Lite)"
    ]
    selected_model = st.selectbox("🧠 Select AI Model", model_options, index=0)

    st.markdown("---")
    st.markdown("### <i class='fas fa-folder-open'></i> Upload Dataset", unsafe_allow_html=True)
    uploaded_files = st.sidebar.file_uploader(
        "Drop your dataset file here",
        type=["csv", "xlsx", "xls", "json", "parquet"],
        accept_multiple_files=True
    )
    
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
        
    # Save uploaded files to disk
    if uploaded_files:
        for uf in uploaded_files:
            with open(os.path.join("uploads", uf.name), "wb") as f:
                f.write(uf.getbuffer())
                
    # Read from disk to persist across F5
    supported_ext = (".csv", ".xlsx", ".xls", ".json", ".parquet")
    available_files = [f for f in os.listdir("uploads") if f.endswith(supported_ext)]
    active_file = None
    
    if available_files:
        selected_name = st.selectbox("Select Active Dataset", available_files)
        active_file = os.path.join("uploads", selected_name)

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:rgba(196,181,253,0.4);font-size:0.75rem;'>"
        "Powered by Azure OpenAI · GPT-4o-mini<br>Multi-Agent Architecture</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Helper — generate PDF report
# ---------------------------------------------------------------------------
def _safe_pdf_text(text):
    """Strip emojis and non-ASCII characters that crash FPDF"""
    if not isinstance(text, str):
        text = str(text)
    return text.encode('ascii', 'ignore').decode('ascii')

def _build_pdf_report(info, summary, quality, insights_text):
    """Create an in-memory PDF with the analysis results."""
    from fpdf import FPDF
    import textwrap

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 14, "AI Data Analysis Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)

    # Dataset Overview
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Dataset Overview", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Rows: {info['total_rows']}   |   Columns: {info['total_columns']}", new_x="LMARGIN", new_y="NEXT")
    
    col_str = _safe_pdf_text(f"Columns: {', '.join(info['columns'])}")
    for w_line in textwrap.wrap(col_str, width=80):
        pdf.cell(0, 7, w_line, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Data Quality
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Data Quality", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Completeness: {quality['completeness_score']}%   |   Duplicates: {quality['duplicate_rows']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Statistical Summary
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Statistical Summary (Numerical)", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for col_name, stats in summary.get("numerical", {}).items():
        line = _safe_pdf_text(f"{col_name}: mean={stats.get('mean','N/A')}, max={stats.get('max','N/A')}, min={stats.get('min','N/A')}")
        for w_line in textwrap.wrap(line, width=90):
            pdf.cell(0, 7, w_line, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # AI Insights
    if insights_text:
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "AI-Generated Insights", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        # Clean markdown formatting for PDF
        clean = insights_text.replace("**", "").replace("🔍", "-")
        for line in clean.split("\n"):
            line = line.strip()
            if line:
                safe_line = _safe_pdf_text(line)
                for w_line in textwrap.wrap(safe_line, width=85):
                    pdf.cell(0, 7, w_line, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    return pdf.output()


# ====================================================================
# MAIN CONTENT — only when a CSV is uploaded
# ====================================================================
if active_file is not None:
    # Step 1: Load dataset
    df, error = analysis.load_data(active_file)

    if error:
        st.error(f"❌ Failed to load dataset: {error}")
        st.stop()

    # Compute all analysis artefacts
    info = analysis.get_dataset_info(df)
    summary = analysis.get_statistical_summary(df)
    quality = analysis.get_data_quality_report(df)
    col_hints = analysis.get_column_hints(df)
    corr_matrix = analysis.get_correlation_matrix(df)
    sample_data = df.head(50).to_json(orient="records")

    # ------------------------------------------------------------------
    # Step 1 & 2 — Dataset Overview
    # ------------------------------------------------------------------
    st.markdown('<div class="section-header"><i class="fas fa-chart-line"></i> Dataset Overview</div>', unsafe_allow_html=True)

    # Metric cards
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-value">{info['total_rows']:,}</div>
            <div class="metric-label">Total Rows</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{info['total_columns']}</div>
            <div class="metric-label">Columns</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{quality['completeness_score']}%</div>
            <div class="metric-label">Completeness</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{quality['duplicate_rows']}</div>
            <div class="metric-label">Duplicates</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")  # spacer

    # Expanders for detail
    with st.expander("🔎 Column Details & Data Types", expanded=False):
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Data Types**")
            st.json(info["data_types"])
        with col_b:
            st.markdown("**Missing Values**")
            st.json(info["missing_values"])

    with st.expander("📈 Statistical Summary", expanded=False):
        if summary["numerical"]:
            st.markdown("**Numerical Features**")
            st.json(summary["numerical"])
        if summary["categorical"]:
            st.markdown("**Categorical Features (Top 15 per column)**")
            st.json(summary["categorical"])

    with st.expander("🩺 Data Quality Report", expanded=False):
        st.json(quality)

    # ------------------------------------------------------------------
    # Step 3 — Ask the Data  (AI Q&A)
    # ------------------------------------------------------------------
    st.markdown('<div class="section-header"><i class="fas fa-comments"></i> Ask the Data</div>', unsafe_allow_html=True)

    if not selected_model:
        st.warning("⚠️ Select an AI model from the sidebar to enable AI features.")
    else:
        # Predefined questions (for judges)
        st.markdown("**Judges' Questions (Editable):**")
        
        file_key = os.path.basename(active_file)
        for i, default_q in enumerate(["Which product generated the highest sales?", "What is the average age of customers?", "Which category appears most frequently?"], start=1):
            if f"in{i}_{file_key}" not in st.session_state:
                st.session_state[f"in{i}_{file_key}"] = default_q

        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("✨ Auto-Suggest Questions", help="Use AI to generate questions based on this dataset"):
                with st.spinner("Generating..."):
                    sq = ai_helper.generate_suggested_questions(info, summary, selected_model=selected_model, sample_data=sample_data)
                    if sq and len(sq) >= 3:
                        st.session_state[f"in1_{file_key}"] = sq[0]
                        st.session_state[f"in2_{file_key}"] = sq[1]
                        st.session_state[f"in3_{file_key}"] = sq[2]
                        st.rerun()

        qcol_input1, qcol_btn1 = st.columns([4, 1])
        with qcol_input1:
            q1 = st.text_input("Question 1", key=f"in1_{file_key}", label_visibility="collapsed")
        with qcol_btn1:
            ask_q1 = st.button("🏆 Ask Q1", use_container_width=True)

        qcol_input2, qcol_btn2 = st.columns([4, 1])
        with qcol_input2:
            q2 = st.text_input("Question 2", key=f"in2_{file_key}", label_visibility="collapsed")
        with qcol_btn2:
            ask_q2 = st.button("📊 Ask Q2", use_container_width=True)

        qcol_input3, qcol_btn3 = st.columns([4, 1])
        with qcol_input3:
            q3 = st.text_input("Question 3", key=f"in3_{file_key}", label_visibility="collapsed")
        with qcol_btn3:
            ask_q3 = st.button("📂 Ask Q3", use_container_width=True)

        # --- Session-state cached Q&A to prevent duplicate API calls on reload ---
        ans_cache_key = f"ans_cache_{file_key}"
        if ans_cache_key not in st.session_state:
            st.session_state[ans_cache_key] = {}  # {q_index: {"q": ..., "a": ...}}

        if ask_q1:
            with st.spinner("🤖 DataBot is analysing…"):
                ans = ai_helper.answer_data_question(info, summary, q1, col_hints, selected_model=selected_model, sample_data=sample_data, corr_matrix=corr_matrix)
            st.session_state[ans_cache_key]["q1"] = {"q": q1, "a": ans}

        if ask_q2:
            with st.spinner("🤖 DataBot is analysing…"):
                ans = ai_helper.answer_data_question(info, summary, q2, col_hints, selected_model=selected_model, sample_data=sample_data, corr_matrix=corr_matrix)
            st.session_state[ans_cache_key]["q2"] = {"q": q2, "a": ans}

        if ask_q3:
            with st.spinner("🤖 DataBot is analysing…"):
                ans = ai_helper.answer_data_question(info, summary, q3, col_hints, selected_model=selected_model, sample_data=sample_data, corr_matrix=corr_matrix)
            st.session_state[ans_cache_key]["q3"] = {"q": q3, "a": ans}

        # Display all cached answers (persists across reloads)
        for qk in ["q1", "q2", "q3"]:
            if qk in st.session_state.get(ans_cache_key, {}):
                cached = st.session_state[ans_cache_key][qk]
                st.markdown(f'<span class="agent-badge badge-analyst"><i class="fas fa-robot"></i> DataBot</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="ai-answer"><strong>Q:</strong> {cached["q"]}<br><br><strong>A:</strong> {cached["a"]}</div>', unsafe_allow_html=True)

        # Custom question
        st.markdown("")
        user_q = st.text_input("💡 Ask a custom question about the dataset:", placeholder="e.g., What is the total revenue by region?")
        if st.button("Ask DataBot 🚀", use_container_width=False):
            if user_q.strip():
                with st.spinner("🤖 DataBot is analysing…"):
                    ans = ai_helper.answer_data_question(info, summary, user_q, col_hints, selected_model=selected_model, sample_data=sample_data, corr_matrix=corr_matrix)
                st.session_state[ans_cache_key]["custom"] = {"q": user_q, "a": ans}

        # Show cached custom answer
        if "custom" in st.session_state.get(ans_cache_key, {}):
            cached = st.session_state[ans_cache_key]["custom"]
            st.markdown(f'<span class="agent-badge badge-analyst"><i class="fas fa-robot"></i> DataBot</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="ai-answer"><strong>Q:</strong> {cached["q"]}<br><br><strong>A:</strong> {cached["a"]}</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # Step 4 & 5 — Charts + AI Explanations
    # ------------------------------------------------------------------
    st.markdown('<div class="section-header"><i class="fas fa-chart-area"></i> Automated Visualisations</div>', unsafe_allow_html=True)

    with st.spinner("Generating charts…"):
        charts = visualization.generate_all_charts(df)

    if not charts:
        st.info("No suitable columns found to generate charts for this dataset.")
    else:
        # Display friendly tab names
        tab_labels = {
            "bar_chart": "Bar Chart",
            "pie_chart": "Pie Chart",
            "histogram": "Histogram",
            "correlation_heatmap": "Correlation",
        }
        available = list(charts.keys())
        tabs = st.tabs([tab_labels.get(k, k) for k in available])

        for tab, chart_key in zip(tabs, available):
            with tab:
                chart_data = charts[chart_key]
                st.pyplot(chart_data["fig"])

                # Download chart as PNG (bonus feature)
                chart_path = os.path.join("charts", f"{chart_key}.png")
                if os.path.exists(chart_path):
                    with open(chart_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Chart as PNG",
                            data=f.read(),
                            file_name=f"{chart_key}.png",
                            mime="image/png",
                            key=f"dl_{chart_key}",
                        )

                # AI chart explanation (Step 5) — cached in session_state
                expl_cache_key = f"chart_expl_{file_key}_{chart_key}"
                if expl_cache_key not in st.session_state:
                    with st.spinner("ChartBot is explaining…"):
                        st.session_state[expl_cache_key] = ai_helper.explain_chart(chart_data["metadata"], selected_model=selected_model)
                explanation = st.session_state[expl_cache_key]
                st.markdown(f'<span class="agent-badge badge-explainer"><i class="fas fa-paint-brush"></i> ChartBot</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="ai-answer">{explanation}</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # Proactive Insights (Agent 3)
    # ------------------------------------------------------------------
    st.markdown('<div class="section-header"><i class="fas fa-lightbulb"></i> AI-Generated Insights</div>', unsafe_allow_html=True)

    # Cache insights in session_state to avoid duplicate API calls on reload
    insight_cache_key = f"insights_{file_key}"
    if insight_cache_key not in st.session_state:
        with st.spinner("InsightBot is discovering patterns…"):
            st.session_state[insight_cache_key] = ai_helper.generate_insights(info, summary, col_hints, selected_model=selected_model)
    insights_text = st.session_state[insight_cache_key]
    st.markdown(f'<span class="agent-badge badge-insight"><i class="fas fa-lightbulb"></i> InsightBot</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="ai-answer">{insights_text}</div>', unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # DataBot Live Chat Assistant (Floating Widget)
    # ------------------------------------------------------------------
    file_key = os.path.basename(active_file)
    chat_key = f"chat_history_{file_key}"
    
    if chat_key not in st.session_state:
        st.session_state[chat_key] = [{"role": "assistant", "content": "Hi! I'm DataBot. You can ask me anything about the loaded dataset."}]
        
    st.markdown(f"""
    <style>
        div[data-testid="stPopover"] {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 70px !important;
            z-index: 99999;
        }}
        div[data-testid="stPopover"] > button {{
            border-radius: 50% !important;
            width: 70px !important;
            height: 70px !important;
            padding: 0 !important;
            font-size: 38px !important;
            box-shadow: 0 8px 25px rgba(139,92,246,0.5) !important;
            background: linear-gradient(135deg, #8b5cf6, #6366f1) !important;
            color: white !important;
            border: none !important;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.3s ease;
        }}
        div[data-testid="stPopover"] > button:hover {{
            transform: scale(1.1);
            box-shadow: 0 10px 30px rgba(139,92,246,0.7) !important;
        }}
        div[data-testid="stPopoverBody"] {{
            width: 340px !important;
            height: 500px !important;
            border-radius: 12px !important;
            padding: 15px !important;
            border: 1px solid rgba(139,92,246,0.3) !important;
            background-color: {popover_bg} !important;
            color: {text_color} !important;
        }}
        div[data-testid="stPopoverBody"] [data-testid="stChatMessage"] {{
            background-color: {chat_bot_bg} !important;
        }}
        div[data-testid="stPopoverBody"] [data-testid="stChatMessage"] p,
        div[data-testid="stPopoverBody"] [data-testid="stChatMessage"] div,
        div[data-testid="stPopoverBody"] [data-testid="stChatMessage"] span {{
            color: {text_color} !important;
        }}
        div[data-testid="stPopoverBody"] [data-testid="stChatInput"] {{
            background-color: {input_bg} !important;
            border-color: {input_border} !important;
        }}
        div[data-testid="stPopoverBody"] [data-testid="stChatInput"] textarea {{
            color: {text_color} !important;
            -webkit-text-fill-color: {text_color} !important;
            background-color: {input_bg} !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    with st.popover("🤖", help="Open DataBot Chat", use_container_width=False):
        st.markdown("<h4 style='margin-top:0; color:#a78bfa;'><i class='fas fa-robot'></i> DataBot Live Chat</h4>", unsafe_allow_html=True)
        chat_container = st.container(height=330)
        with chat_container:
            for msg in st.session_state[chat_key]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    
        if prompt := st.chat_input("Ask a question about your data...", key="popover_chat"):
            st.session_state[chat_key].append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Analysing..."):
                        response = ai_helper.answer_data_question(info, summary, prompt, col_hints, selected_model=selected_model, sample_data=sample_data, corr_matrix=corr_matrix)
                        st.markdown(response)
            st.session_state[chat_key].append({"role": "assistant", "content": response})

    # ------------------------------------------------------------------
    # Export — PDF report (bonus feature)
    # ------------------------------------------------------------------
    st.markdown('<div class="section-header"><i class="fas fa-file-pdf"></i> Export Analysis</div>', unsafe_allow_html=True)

    try:
        pdf_bytes = _build_pdf_report(info, summary, quality, insights_text)
        st.download_button(
            label="⬇️ Download Full Report as PDF",
            data=bytes(pdf_bytes),
            file_name="analysis_report.pdf",
            mime="application/pdf",
        )
    except Exception as e:
        st.warning(f"PDF export unavailable: {e}")

else:
    # ------------------------------------------------------------------
    # Welcome screen
    # ------------------------------------------------------------------
    st.markdown("""
    <div class="welcome-card">
        <div class="welcome-icon">🔬</div>
        <div style="font-size:1.5rem;font-weight:700;color:#c4b5fd;margin-bottom:10px;">
            Welcome to the AI Data Analysis Assistant
        </div>
        <div class="welcome-text">
            Upload a CSV file in the sidebar to get started.<br>
            The assistant will automatically analyse your data,<br>
            generate beautiful charts, and answer your questions<br>
            using a team of specialised AI agents.
        </div>
    </div>
    """, unsafe_allow_html=True)
