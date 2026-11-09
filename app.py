import streamlit as st
from dotenv import load_dotenv
from granite_client import generate_learning_content
import datetime, os

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LearnEase AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
for key, default in {
    "page": "dashboard",
    "learn_output": None,
    "learn_topic": "",
    "session_count": 0,
    "recent_activity": [],
    "notification": None,
    "notification_type": "success",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base & reset ───────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ── App background — dark emerald ──────────────────────────────────── */
.stApp {
    background: #111C1A !important;
    color: #F1F5F2 !important;
}

.main .block-container,
section.main > div,
[data-testid="stAppViewContainer"] > section {
    background: #111C1A !important;
}

.stApp p, .stApp li, .stApp span, .stApp div {
    color: inherit;
}

/* ── Sidebar ─────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0B1512 !important;
    border-right: 1px solid #30483C !important;
}
[data-testid="stSidebar"] > div:first-child {
    background: transparent !important;
}
[data-testid="stSidebar"],
[data-testid="stSidebar"] * {
    color: #A6B8AC !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label {
    color: #A6B8AC !important;
}

/* ── Sidebar nav button overlay (invisible click target) ────────────── */
/* ── Sidebar nav buttons — styled as full-width nav items ───────────── */
[data-testid="stSidebar"] .stButton {
    margin-bottom: 0.1rem !important;
    margin-top: 0 !important;
}
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    padding: 0.55rem 1rem 0.55rem 1.1rem !important;
    text-align: left !important;
    color: #A6B8AC !important;
    font-weight: 400 !important;
    font-size: 0.9rem !important;
    cursor: pointer !important;
    transition: background 0.15s, color 0.15s !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
}
[data-testid="stSidebar"] .stButton > button p {
    color: inherit !important;
    font-size: 0.9rem !important;
    font-weight: inherit !important;
    margin: 0 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(32,168,117,0.10) !important;
    color: #F1F5F2 !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover p {
    color: #F1F5F2 !important;
}
/* Active nav item — scoped style injected inline before each button */
[data-testid="stSidebar"] .nav-active > button {
    background: #21362D !important;
    border-left: 3px solid #20A875 !important;
    border-right: none !important;
    border-top: none !important;
    border-bottom: none !important;
    padding-left: 0.85rem !important;
    color: #F1F5F2 !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .nav-active > button p {
    color: #F1F5F2 !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .nav-active > button:hover {
    background: #21362D !important;
    color: #F1F5F2 !important;
}

/* ── Cards ────────────────────────────────────────────────────────────── */
.card {
    background: #192823;
    border: 1px solid #30483C;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-sm {
    background: #192823;
    border: 1px solid #30483C;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.75rem;
}
.card-accent {
    background: linear-gradient(135deg, #192823 0%, #21362D 100%);
    border: 1px solid #20A875;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.feature-card {
    background: #192823;
    border: 1px solid #30483C;
    border-radius: 14px;
    padding: 1.4rem;
    text-align: center;
    height: 100%;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.feature-card:hover {
    border-color: #20A875;
    box-shadow: 0 4px 20px rgba(32,168,117,0.12);
}

/* ── Typography helpers ───────────────────────────────────────────────── */
.page-title {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #20A875 0%, #27C98B 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 0.3rem;
}
.page-subtitle {
    color: #A6B8AC !important;
    font-size: 1rem;
    font-weight: 400;
    margin-bottom: 1.5rem;
}
.section-label {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #20A875 !important;
    margin-bottom: 0.4rem;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(135deg, #27C98B 0%, #20A875 60%, #1a8c62 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 0.5rem;
}
.hero-sub {
    font-size: 1.1rem;
    color: #A6B8AC !important;
    line-height: 1.7;
    margin-bottom: 1.5rem;
}
.stat-number {
    font-size: 2rem;
    font-weight: 700;
    color: #20A875;
}
.stat-label {
    font-size: 0.8rem;
    color: #A6B8AC !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Streamlit native widget labels ──────────────────────────────────── */
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stFileUploader label,
.stRadio label,
div[data-testid="stWidgetLabel"] p,
div[data-testid="stWidgetLabel"] {
    color: #F1F5F2 !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #A6B8AC !important;
}
.stTooltipIcon {
    color: #A6B8AC !important;
}

/* ── Buttons ──────────────────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.15s ease !important;
}
/* Primary — emerald green */
.stButton > button[data-testid="baseButton-primary"],
.stButton > button[kind="primary"] {
    background: #20A875 !important;
    border: none !important;
    color: #ffffff !important;
}
.stButton > button[data-testid="baseButton-primary"] p,
.stButton > button[kind="primary"] p {
    color: #ffffff !important;
    font-weight: 600 !important;
}
.stButton > button[data-testid="baseButton-primary"]:hover,
.stButton > button[kind="primary"]:hover {
    background: #27C98B !important;
    box-shadow: 0 4px 20px rgba(32,168,117,0.40) !important;
    color: #ffffff !important;
}
/* Secondary */
.stButton > button[data-testid="baseButton-secondary"],
.stButton > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid #30483C !important;
    color: #A6B8AC !important;
}
.stButton > button[data-testid="baseButton-secondary"] p,
.stButton > button[kind="secondary"] p {
    color: #A6B8AC !important;
}
.stButton > button[data-testid="baseButton-secondary"]:hover,
.stButton > button[kind="secondary"]:hover {
    border-color: #20A875 !important;
    color: #F1F5F2 !important;
    background: rgba(32,168,117,0.08) !important;
}
.stButton > button[data-testid="baseButton-secondary"]:hover p,
.stButton > button[kind="secondary"]:hover p {
    color: #F1F5F2 !important;
}
/* Default (unlabelled) buttons */
.stButton > button:not([kind="primary"]):not([kind="secondary"]):not([data-testid="baseButton-primary"]):not([data-testid="baseButton-secondary"]) {
    background: transparent !important;
    border: 1px solid #30483C !important;
    color: #A6B8AC !important;
}
.stButton > button:not([kind="primary"]):not([kind="secondary"]):not([data-testid="baseButton-primary"]):not([data-testid="baseButton-secondary"]) p {
    color: #A6B8AC !important;
}
.stButton > button:not([kind="primary"]):not([kind="secondary"]):not([data-testid="baseButton-primary"]):not([data-testid="baseButton-secondary"]):hover {
    border-color: #20A875 !important;
    color: #F1F5F2 !important;
}
/* Download button */
.stDownloadButton > button {
    background: #21362D !important;
    border: 1px solid #20A875 !important;
    color: #27C98B !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stDownloadButton > button p { color: #27C98B !important; }
.stDownloadButton > button:hover {
    background: #20A875 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 16px rgba(32,168,117,0.35) !important;
}
.stDownloadButton > button:hover p { color: #ffffff !important; }

/* ── Inputs — text & textarea ─────────────────────────────────────────── */
.stTextInput input,
.stTextInput > div > div > input,
.stTextArea textarea,
.stTextArea > div > div > textarea {
    background: #192823 !important;
    border: 1px solid #30483C !important;
    border-radius: 8px !important;
    color: #F1F5F2 !important;
    font-size: 0.95rem !important;
}
.stTextInput input:focus,
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #20A875 !important;
    box-shadow: 0 0 0 2px rgba(32,168,117,0.20) !important;
    outline: none !important;
}
.stTextInput > div,
.stTextArea > div {
    background: transparent !important;
}

/* ── Selectbox ────────────────────────────────────────────────────────── */
.stSelectbox > div > div {
    background: #192823 !important;
    border: 1px solid #30483C !important;
    border-radius: 8px !important;
}
.stSelectbox [data-baseweb="select"] > div,
.stSelectbox [data-baseweb="select"] > div > div {
    background: #192823 !important;
    border: none !important;
    color: #F1F5F2 !important;
}
.stSelectbox [data-baseweb="select"] span,
.stSelectbox [data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
.stSelectbox [data-baseweb="select"] div {
    color: #F1F5F2 !important;
    background: transparent !important;
}
.stSelectbox [data-baseweb="select"] svg {
    fill: #A6B8AC !important;
}
.stSelectbox [data-baseweb="select"] > div:focus-within {
    border-color: #20A875 !important;
    box-shadow: 0 0 0 2px rgba(32,168,117,0.20) !important;
}
/* Dropdown popup — force readable text and background */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
[role="listbox"] {
    background-color: #192823 !important;
    color: #F1F5F2 !important;
    border: 1px solid #30483C !important;
    border-radius: 10px !important;
}

[data-baseweb="popover"] *,
[data-baseweb="menu"] *,
[role="listbox"] * {
    color: #F1F5F2 !important;
}

[data-baseweb="popover"] [role="option"],
[data-baseweb="menu"] [role="option"],
[role="listbox"] [role="option"] {
    background-color: #192823 !important;
    color: #F1F5F2 !important;
}

[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="menu"] [role="option"]:hover,
[role="listbox"] [role="option"]:hover {
    background-color: #21362D !important;
    color: #FFFFFF !important;
}

[data-baseweb="popover"] [aria-selected="true"],
[data-baseweb="menu"] [aria-selected="true"],
[role="listbox"] [aria-selected="true"] {
    background-color: #21362D !important;
    color: #27C98B !important;
}

/* ── File uploader ────────────────────────────────────────────────────── */
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploadDropzone"] {
    background: #192823 !important;
    border: 1.5px dashed #30483C !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploaderDropzone"]:hover,
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #20A875 !important;
    background: #21362D !important;
}
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploadDropzone"] p,
[data-testid="stFileUploadDropzone"] span,
[data-testid="stFileUploadDropzone"] small {
    color: #A6B8AC !important;
}
[data-testid="stFileUploaderFileName"],
[data-testid="stFileUploader"] span {
    color: #27C98B !important;
}

/* ── Tabs ─────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #0B1512 !important;
    border-radius: 10px !important;
    padding: 0.3rem !important;
    gap: 0.2rem !important;
    border: 1px solid #30483C !important;
    flex-wrap: wrap !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    color: #A6B8AC !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    padding: 0.45rem 0.8rem !important;
    transition: background 0.15s, color 0.15s !important;
    min-width: 0 !important;
    white-space: nowrap !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #F1F5F2 !important;
    background: rgba(32,168,117,0.12) !important;
}
/* Active tab — emerald solid */
.stTabs [aria-selected="true"] {
    background: #20A875 !important;
    color: #ffffff !important;
}
.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span {
    color: #ffffff !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.2rem !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] p,
.stTabs [data-baseweb="tab-panel"] li,
.stTabs [data-baseweb="tab-panel"] span,
.stTabs [data-baseweb="tab-panel"] h1,
.stTabs [data-baseweb="tab-panel"] h2,
.stTabs [data-baseweb="tab-panel"] h3,
.stTabs [data-baseweb="tab-panel"] strong,
.stTabs [data-baseweb="tab-panel"] em {
    color: #F1F5F2 !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background: transparent !important;
}
.stTabs [data-baseweb="tab-border"] {
    background: #30483C !important;
}

/* ── Expanders ────────────────────────────────────────────────────────── */
details > summary,
[data-testid="stExpander"] summary,
.streamlit-expanderHeader {
    background: #192823 !important;
    border: 1px solid #30483C !important;
    border-radius: 10px !important;
    color: #F1F5F2 !important;
    font-weight: 600 !important;
}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color: #F1F5F2 !important;
}
[data-testid="stExpander"] > div:last-child,
.streamlit-expanderContent {
    background: #0B1512 !important;
    border: 1px solid #30483C !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
    color: #F1F5F2 !important;
}
[data-testid="stExpander"] > div:last-child p,
[data-testid="stExpander"] > div:last-child span,
[data-testid="stExpander"] > div:last-child textarea {
    color: #F1F5F2 !important;
}

/* ── Text area inside expander ────────────────────────────────────────── */
.stTextArea textarea {
    background: #192823 !important;
    color: #F1F5F2 !important;
    border: 1px solid #30483C !important;
    border-radius: 6px !important;
}

/* ── Spinner ─────────────────────────────────────────────────────────── */
.stSpinner p, .stSpinner > div {
    color: #A6B8AC !important;
}

/* ── Notifications ────────────────────────────────────────────────────── */
.notif-success {
    background: #0d1f18;
    border: 1px solid #20A875;
    border-left: 4px solid #27C98B;
    border-radius: 10px;
    padding: 0.85rem 1.2rem;
    color: #27C98B !important;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}
.notif-error {
    background: #1f0d0d;
    border: 1px solid #7f1d1d;
    border-left: 4px solid #ef4444;
    border-radius: 10px;
    padding: 0.85rem 1.2rem;
    color: #fca5a5 !important;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}
.notif-warning {
    background: #1a1508;
    border: 1px solid #92400e;
    border-left: 4px solid #f59e0b;
    border-radius: 10px;
    padding: 0.85rem 1.2rem;
    color: #fde68a !important;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

/* ── Streamlit native alerts ──────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
}
[data-testid="stAlert"] p {
    color: inherit !important;
}

/* ── AI-connected status badge ───────────────────────────────────────── */
.status-connected {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #0d1f18;
    border: 1px solid #20A875;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    color: #27C98B !important;
    font-weight: 500;
}
.status-dot {
    width: 7px; height: 7px;
    background: #20A875;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 6px #20A875;
}

/* ── Footer ───────────────────────────────────────────────────────────── */
.footer-text {
    text-align: center;
    color: #A6B8AC !important;
    font-size: 0.78rem;
    padding: 1.5rem 0 0.5rem;
    border-top: 1px solid #30483C;
    line-height: 1.7;
}

/* ── Divider ──────────────────────────────────────────────────────────── */
hr { border-color: #30483C !important; }

/* ── Scrollbar ────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #111C1A; }
::-webkit-scrollbar-thumb { background: #30483C; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #20A875; }

/* ── Hide default Streamlit branding ──────────────────────────────────── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

/* ── Global markdown text ─────────────────────────────────────────────── */
.stMarkdown p,
.stMarkdown li,
.stMarkdown h1,
.stMarkdown h2,
.stMarkdown h3,
.stMarkdown h4,
.stMarkdown strong,
.stMarkdown em,
.stMarkdown code {
    color: #F1F5F2 !important;
}
.stMarkdown h1, .stMarkdown h2 { color: #ffffff !important; }
.stMarkdown h3 { color: #F1F5F2 !important; }
.stMarkdown code {
    background: #21362D !important;
    color: #27C98B !important;
    border-radius: 4px;
    padding: 0.1em 0.4em;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def extract_text_from_upload(uploaded):
    """Extract plain text from an uploaded PDF or DOCX. Returns (text, error)."""
    name = uploaded.name.lower()
    try:
        if name.endswith(".pdf"):
            import fitz
            data = uploaded.read()
            doc = fitz.open(stream=data, filetype="pdf")
            pages = [page.get_text() for page in doc]
            doc.close()
            text = "\n".join(pages).strip()
            if not text:
                return None, "The PDF appears to contain no extractable text (it may be scanned/image-only)."
            return text, None
        elif name.endswith(".docx"):
            import docx as _docx
            import io
            document = _docx.Document(io.BytesIO(uploaded.read()))
            paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
            text = "\n".join(paragraphs).strip()
            if not text:
                return None, "The DOCX file appears to contain no readable text."
            return text, None
        else:
            return None, f"Unsupported file type: {uploaded.name}"
    except Exception as exc:
        return None, f"Could not extract text from '{uploaded.name}': {exc}"


def check_api_configured():
    """Return True only if real (non-placeholder) env credentials are set."""
    api_key = os.getenv("IBM_CLOUD_API_KEY", "").strip()
    project_id = os.getenv("WATSONX_PROJECT_ID", "").strip()
    return (
        bool(api_key) and not api_key.startswith("your_")
        and bool(project_id) and not project_id.startswith("your_")
    )


def nav_button(label, icon, page_key, current_page):
    """
    Render a single styled Streamlit button as a sidebar nav item.
    Active item gets the emerald-left-border treatment; inactive items are
    transparent. A scoped <style> block targets the button by its aria-label
    so no extra HTML overlay is needed.
    """
    is_active = current_page == page_key
    btn_label = f"{icon}  {label}"

    if is_active:
        active_css = f"""
        <style>
        [data-testid="stSidebar"] button[aria-label="{btn_label}"],
        [data-testid="stSidebar"] button[kind="secondary"][title="{btn_label}"] {{
            background: #21362D !important;
            border-left: 3px solid #20A875 !important;
            border-right: none !important;
            border-top: none !important;
            border-bottom: none !important;
            border-radius: 8px !important;
            padding: 0.55rem 1rem 0.55rem 0.85rem !important;
            color: #F1F5F2 !important;
            font-weight: 600 !important;
        }}
        [data-testid="stSidebar"] button[aria-label="{btn_label}"] p,
        [data-testid="stSidebar"] button[aria-label="{btn_label}"] span {{
            color: #F1F5F2 !important;
            font-weight: 600 !important;
        }}
        </style>"""
        st.markdown(active_css, unsafe_allow_html=True)

    if st.button(
        btn_label,
        key=f"nav_{page_key}",
        use_container_width=True,
    ):
        st.session_state["page"] = page_key
        st.rerun()

def show_notification():
    if st.session_state["notification"]:
        msg = st.session_state["notification"]
        ntype = st.session_state["notification_type"]
        css_class = f"notif-{ntype}"
        icons = {"success": "✅", "error": "❌", "warning": "⚠️"}
        st.markdown(f'<div class="{css_class}">{icons.get(ntype,"ℹ️")} {msg}</div>', unsafe_allow_html=True)
        st.session_state["notification"] = None


def parse_study_pack_sections(raw_text):
    """
    Parse the 7-section study-pack output from the AI into a dict.
    Returns {section_name: content_str}. Returns None if parsing fails or
    fewer than 2 sections have non-empty content (triggers raw-markdown fallback).

    Handles the common Llama pattern of emitting a Table-of-Contents listing of all
    seven headings (with no content) before the actual body — by keeping only the
    LAST occurrence of each section heading when building the content slices.
    """
    import re
    sections_order = [
        "Definition",
        "Simple Explanation",
        "Key Points",
        "Important Terms",
        "Real-Life Examples",
        "Exam Questions and Answers",
        "Revision Summary",
    ]
    # Match numbered headings like "1. Definition", "## 1. Definition", "### 2. Key Points", etc.
    pattern = re.compile(
        r"(?:#+\s*)?(?:\d+\.\s*)(" + "|".join(re.escape(s) for s in sections_order) + r")\s*\n",
        re.IGNORECASE
    )
    matches = list(pattern.finditer(raw_text))
    if len(matches) < 2:
        return None  # Couldn't parse — return None to signal fall-through

    # Keep only the LAST occurrence of each canonical section name.
    # This eliminates TOC entries (which have no content after them) and ensures
    # we slice from the real content headings.
    last_match_for = {}
    for m in matches:
        sec_name = m.group(1).title()
        canonical = next((s for s in sections_order if s.lower() == sec_name.lower()), sec_name)
        last_match_for[canonical] = m  # later match overwrites earlier (TOC) match

    # Re-order by match position so slicing is sequential
    ordered_matches = sorted(last_match_for.values(), key=lambda m: m.start())

    result = {}
    for i, match in enumerate(ordered_matches):
        sec_name = match.group(1).title()
        canonical = next((s for s in sections_order if s.lower() == sec_name.lower()), sec_name)
        start = match.end()
        end = ordered_matches[i + 1].start() if i + 1 < len(ordered_matches) else len(raw_text)
        result[canonical] = raw_text[start:end].strip()

    # If fewer than 2 sections have actual content, parsing is unreliable — signal fallback
    non_empty = sum(1 for v in result.values() if v)
    if non_empty < 2:
        return None

    return result


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Branding
    st.markdown("""
    <div style="padding: 1rem 0.5rem 1.5rem; border-bottom: 1px solid #30483C; margin-bottom: 1.5rem;">
        <div style="font-size: 1.5rem; font-weight: 800; background: linear-gradient(135deg,#27C98B,#20A875); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; line-height: 1.2;">
            🎓 LearnEase AI
        </div>
        <div style="color: #A6B8AC; font-size: 0.78rem; margin-top: 0.3rem; font-weight: 400;">
            AI-Powered Learning Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    # API status badge
    if check_api_configured():
        st.markdown("""
        <div style="margin-bottom: 1.5rem; padding-left: 0.5rem;">
            <span class="status-connected">
                <span class="status-dot"></span> AI Service Connected
            </span>
        </div>
        """, unsafe_allow_html=True)

    # Navigation
    st.markdown('<div style="color: #20A875; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; padding-left: 0.5rem; margin-bottom: 0.5rem;">Navigation</div>', unsafe_allow_html=True)

    current = st.session_state["page"]
    nav_button("Dashboard", "🏠", "dashboard", current)
    nav_button("Create Study Pack", "✨", "create", current)
    nav_button("How It Works", "💡", "how_it_works", current)
    nav_button("About the Project", "ℹ️", "about", current)

    # Session stats
    count = st.session_state["session_count"]
    if count > 0:
        st.markdown(f"""
        <div style="margin-top: 2rem; padding: 1rem; background: #0B1512; border: 1px solid #30483C; border-radius: 10px;">
            <div style="color: #20A875; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.75rem;">Session Stats</div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <div style="font-size: 1.5rem; font-weight: 700; color: #27C98B;">{count}</div>
                <div style="color: #A6B8AC; font-size: 0.8rem;">study pack{'' if count==1 else 's'} generated</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="flex: 1;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #30483C; color: #A6B8AC; font-size: 0.7rem; text-align: center; line-height: 1.6;">
        Powered by IBM watsonx.ai Runtime<br>Llama 3.3 70B Instruct
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def page_dashboard():
    show_notification()

    # Hero
    st.markdown("""
    <div class="card-accent" style="padding: 2.5rem; margin-bottom: 1.5rem; text-align: center;">
        <div class="hero-title">Learn Smarter. Understand Faster.</div>
        <div class="hero-sub" style="max-width: 620px; margin: 0 auto;">
            LearnEase AI transforms complex academic topics into clear, structured study materials
            — instantly, using advanced AI. Upload your notes, paste content, or just enter a topic.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✨ Create Study Pack Now", type="primary", use_container_width=False, key="hero_cta"):
        st.session_state["page"] = "create"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards
    st.markdown('<p class="section-label">What LearnEase AI Generates</p>', unsafe_allow_html=True)

    features = [
        ("📖", "AI Content Simplification", "Complex topics explained in plain language tailored to your learning level."),
        ("📝", "Smart Study Notes", "Structured, revision-ready notes with key concepts and definitions."),
        ("🔑", "Important Terms", "A focused glossary of critical vocabulary for every topic."),
        ("🌍", "Real-Life Examples", "Concrete, relatable examples that make abstract concepts tangible."),
        ("📋", "Exam Preparation", "Practice questions and model answers matched to exam style."),
        ("⚡", "Quick Revision", "Bullet-point summaries for last-minute, effective revision."),
    ]

    col1, col2, col3 = st.columns(3, gap="medium")
    cols = [col1, col2, col3]
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="feature-card">
                <div style="font-size: 1.8rem; margin-bottom: 0.6rem;">{icon}</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: #27C98B; margin-bottom: 0.4rem;">{title}</div>
                <div style="font-size: 0.82rem; color: #A6B8AC; line-height: 1.6;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick start samples
    st.markdown('<p class="section-label">Quick Start — Try a Sample Topic</p>', unsafe_allow_html=True)
    sample_topics = [
        "Machine Learning", "Photosynthesis", "Newton's Laws of Motion",
        "Database Normalization", "Linked Lists", "The French Revolution",
    ]
    cols_s = st.columns(6)
    for i, topic in enumerate(sample_topics):
        with cols_s[i]:
            if st.button(topic, key=f"sample_{i}", use_container_width=True):
                st.session_state["sample_topic"] = topic
                st.session_state["page"] = "create"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent activity
    if st.session_state["recent_activity"]:
        st.markdown('<p class="section-label">Recent Activity (This Session)</p>', unsafe_allow_html=True)
        for entry in reversed(st.session_state["recent_activity"][-5:]):
            st.markdown(f"""
            <div class="card-sm" style="display: flex; align-items: center; gap: 1rem;">
                <div style="font-size: 1.2rem;">📘</div>
                <div>
                    <div style="color: #F1F5F2; font-size: 0.88rem; font-weight: 500;">{entry['topic']}</div>
                    <div style="color: #A6B8AC; font-size: 0.75rem;">{entry['level']} · {entry['type']} · {entry['time']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Tech stack
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">Technology Stack</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="card" style="display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center; padding: 1.2rem 1.5rem;">
        <span style="background:#192823; border:1px solid #30483C; color:#27C98B; border-radius:6px; padding:0.3rem 0.75rem; font-size:0.8rem; font-weight:500;">🐍 Python</span>
        <span style="background:#192823; border:1px solid #30483C; color:#27C98B; border-radius:6px; padding:0.3rem 0.75rem; font-size:0.8rem; font-weight:500;">⚡ Streamlit</span>
        <span style="background:#192823; border:1px solid #20A875; color:#F1F5F2; border-radius:6px; padding:0.3rem 0.75rem; font-size:0.8rem; font-weight:500;">🤖 IBM watsonx.ai Runtime</span>
        <span style="background:#192823; border:1px solid #20A875; color:#F1F5F2; border-radius:6px; padding:0.3rem 0.75rem; font-size:0.8rem; font-weight:500;">🦙 Llama 3.3 70B Instruct</span>
        <span style="background:#192823; border:1px solid #30483C; color:#A6B8AC; border-radius:6px; padding:0.3rem 0.75rem; font-size:0.8rem; font-weight:500;">📄 PyMuPDF</span>
        <span style="background:#192823; border:1px solid #30483C; color:#A6B8AC; border-radius:6px; padding:0.3rem 0.75rem; font-size:0.8rem; font-weight:500;">📝 python-docx</span>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="footer-text">
        LearnEase AI — AI-Powered Course Content Simplification Agent<br>
        <span style="color: #A6B8AC;">⚠️ Responsible AI: Always verify AI-generated content against your course materials and faculty notes.</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: CREATE STUDY PACK
# ─────────────────────────────────────────────────────────────────────────────
def page_create():
    show_notification()

    st.markdown('<div class="page-title">Create Study Pack</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Enter a topic, paste your notes, or upload a document to get started.</div>', unsafe_allow_html=True)

    # Pre-fill sample topic if navigated from dashboard
    default_topic = st.session_state.pop("sample_topic", "")

    # ── Input card ──────────────────────────────────────────────────────────
    
    st.markdown('<p class="section-label">Step 1 — Provide Your Content</p>', unsafe_allow_html=True)

    topic = st.text_input(
        "Academic Topic",
        value=default_topic,
        placeholder="e.g. Machine Learning, Photosynthesis, Database Normalization",
        help="Enter the topic you want to study. You can also provide detailed text below.",
        key="input_topic",
    )

    material = st.text_area(
        "Paste Study Material (optional)",
        height=160,
        placeholder="Paste lecture notes, textbook excerpts, or any relevant text here...",
        key="input_material",
    )
    if material:
        word_count = len(material.split())
        st.markdown(f'<div style="color:#A6B8AC; font-size:0.75rem; text-align:right; margin-top:-0.5rem;">{word_count} words</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload a Course Document (optional)",
        type=["pdf", "docx"],
        help="Upload a PDF or DOCX file. Extracted text will be used as source material.",
        key="input_upload",
    )
    if uploaded_file:
        st.markdown(f'<div style="color:#27C98B; font-size:0.82rem; margin-top:0.3rem;">📎 {uploaded_file.name} ({round(uploaded_file.size/1024,1)} KB) ready for processing.</div>', unsafe_allow_html=True)


    # ── Preferences card ────────────────────────────────────────────────────
    st.markdown('<p class="section-label">Step 2 — Learning Preferences</p>', unsafe_allow_html=True)

    col_l, col_t = st.columns(2, gap="medium")
    with col_l:
        level = st.selectbox(
            "Learner Level",
            ["Beginner", "Intermediate", "Exam-focused"],
            help="Beginner: simple language. Intermediate: balanced depth. Exam-focused: exam-oriented structure.",
            key="input_level",
        )
    with col_t:
        output_type = st.selectbox(
            "Output Type",
            ["Complete study pack", "Simple explanation", "Structured notes", "Examples", "Practice questions and answers", "Quick summary"],
            help="Complete study pack includes all seven sections. Other options generate a focused output.",
            key="input_output_type",
        )
    # ── Generate button ──────────────────────────────────────────────────────
    col_gen, col_clr = st.columns([5, 1], gap="small")
    with col_gen:
        generate_clicked = st.button("✨ Generate Study Pack", type="primary", use_container_width=True, key="btn_generate")
    with col_clr:
        clear_clicked = st.button("🗑️ Clear", type="secondary", use_container_width=True, key="btn_clear")

    if clear_clicked:
        for k in ["learn_output", "learn_topic"]:
            st.session_state[k] = None if k == "learn_output" else ""
        st.rerun()

    if generate_clicked:
        doc_text = None
        if uploaded_file is not None:
            doc_text, err = extract_text_from_upload(uploaded_file)
            if err:
                st.session_state["notification"] = err
                st.session_state["notification_type"] = "error"
                st.rerun()

        source = doc_text or material.strip() or topic.strip()
        if not source:
            st.session_state["notification"] = "Please enter a topic, paste study material, or upload a PDF/DOCX file."
            st.session_state["notification_type"] = "warning"
            st.rerun()
        else:
            with st.spinner("🤖 IBM watsonx.ai is preparing your study material — this may take 20–60 seconds..."):
                try:
                    result = generate_learning_content(source, level, output_type)
                    st.session_state["learn_output"] = result
                    st.session_state["learn_topic"] = topic.strip() or (uploaded_file.name if uploaded_file else "Provided material")
                    st.session_state["learn_level"] = level
                    st.session_state["learn_output_type"] = output_type
                    st.session_state["session_count"] += 1
                    st.session_state["recent_activity"].append({
                        "topic": st.session_state["learn_topic"],
                        "level": level,
                        "type": output_type,
                        "time": datetime.datetime.now().strftime("%H:%M"),
                    })
                    st.session_state["notification"] = f"Study pack for \"{st.session_state['learn_topic']}\" generated successfully!"
                    st.session_state["notification_type"] = "success"
                except Exception as e:
                    st.session_state["notification"] = str(e)
                    st.session_state["notification_type"] = "error"
                    st.rerun()

    # ── Results ──────────────────────────────────────────────────────────────
    if st.session_state.get("learn_output"):
        show_notification()
        raw = st.session_state["learn_output"]
        topic_label = st.session_state.get("learn_topic", "")
        out_type = st.session_state.get("learn_output_type", "Complete study pack")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <div style="font-size: 1.2rem; font-weight: 700; color: #F1F5F2;">📘 {topic_label}</div>
                <div style="color: #A6B8AC; font-size: 0.82rem;">{st.session_state.get('learn_level','')} · {out_type}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Download button
        st.download_button(
            "⬇️ Download Study Pack (.txt)",
            raw,
            file_name=f"LearnEase_{topic_label.replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=False,
            key="dl_btn",
        )

        # For Complete study pack — parse into sections with tabs
        if out_type == "Complete study pack":
            sections = parse_study_pack_sections(raw)
            if sections:
                section_meta = {
                    "Definition": ("📖", "#20A875"),
                    "Simple Explanation": ("💬", "#27C98B"),
                    "Key Points": ("🔑", "#27C98B"),
                    "Important Terms": ("🔤", "#20A875"),
                    "Real-Life Examples": ("🌍", "#27C98B"),
                    "Exam Questions and Answers": ("📋", "#20A875"),
                    "Revision Summary": ("⚡", "#27C98B"),
                }
                tab_labels = [f"{section_meta.get(k, ('📄','#fff'))[0]} {k}" for k in sections]
                tabs = st.tabs(tab_labels)
                for tab, (sec_name, content) in zip(tabs, sections.items()):
                    icon, color = section_meta.get(sec_name, ("📄", "#fff"))
                    with tab:
                        st.markdown(f"""
                        <div style="border-left: 3px solid {color}; padding-left: 1rem; margin-bottom: 0.75rem;">
                            <div style="font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: {color};">{icon} {sec_name}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown(content)
                        # Copy text area
                        with st.expander("📋 Copy this section", expanded=False):
                            st.text_area("", value=content, height=120, key=f"copy_{sec_name}", label_visibility="collapsed")
            else:
                # Parse failed — render full markdown
                st.markdown(raw)
        else:
            # Non-study-pack output — render as markdown directly
            st.markdown(raw)

        st.markdown("""
        <div style="margin-top: 1.5rem; padding: 0.9rem 1.2rem; background: #1a1508; border: 1px solid #92400e; border-left: 3px solid #f59e0b; border-radius: 10px; color: #fde68a; font-size: 0.82rem;">
            ⚠️ <strong>Responsible AI Notice:</strong> This content is AI-generated. Always verify important facts, definitions, and exam answers against your official course materials and faculty notes.
        </div>
        """, unsafe_allow_html=True)
    else:
        show_notification()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: HOW IT WORKS
# ─────────────────────────────────────────────────────────────────────────────
def page_how_it_works():
    st.markdown('<div class="page-title">How It Works</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">LearnEase AI turns raw academic content into structured study material in three steps.</div>', unsafe_allow_html=True)

    steps = [
        ("1", "🔤", "Provide Your Content", "Enter a topic name, paste lecture notes or textbook excerpts, or upload a PDF or DOCX file. LearnEase AI accepts all three input formats."),
        ("2", "⚙️", "Configure Your Preferences", "Choose your learner level (Beginner, Intermediate, or Exam-focused) and the type of output you want — from a complete seven-section study pack to quick bullet-point summaries."),
        ("3", "🤖", "AI Generation via IBM watsonx.ai", "Your input and preferences are sent to the Llama 3.3 70B Instruct model hosted on IBM watsonx.ai Runtime. The model generates precise, structured educational content based on your settings."),
        ("4", "📘", "Review and Download", "Your study material is displayed in a structured, tabbed interface. You can read each section, copy individual parts, or download the complete study pack as a text file."),
    ]

    for num, icon, title, desc in steps:
        st.markdown(f"""
        <div class="card" style="display: flex; gap: 1.5rem; align-items: flex-start;">
            <div style="min-width: 2.8rem; height: 2.8rem; background: #20A875; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; font-weight: 700; color: #fff; flex-shrink: 0;">
                {num}
            </div>
            <div>
                <div style="font-size: 1rem; font-weight: 700; color: #27C98B; margin-bottom: 0.35rem;">{icon} {title}</div>
                <div style="color: #A6B8AC; font-size: 0.88rem; line-height: 1.7;">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">Study Pack Sections</p>', unsafe_allow_html=True)

    pack_sections = [
        ("📖", "Definition", "A single, precise sentence defining the topic."),
        ("💬", "Simple Explanation", "A step-by-step explanation in plain language."),
        ("🔑", "Key Points", "The 5–8 most important facts and concepts as bullet points."),
        ("🔤", "Important Terms", "A concise glossary of critical vocabulary."),
        ("🌍", "Real-Life Examples", "2–3 concrete examples with brief explanations."),
        ("📋", "Exam Questions & Answers", "5 exam-style questions with full model answers."),
        ("⚡", "Revision Summary", "A 3–5 sentence summary of the most important ideas."),
    ]

    col_a, col_b = st.columns(2, gap="medium")
    for i, (icon, name, desc) in enumerate(pack_sections):
        with (col_a if i % 2 == 0 else col_b):
            st.markdown(f"""
            <div class="card-sm" style="display: flex; gap: 0.9rem; align-items: flex-start;">
                <div style="font-size: 1.2rem;">{icon}</div>
                <div>
                    <div style="color: #27C98B; font-weight: 600; font-size: 0.88rem;">{name}</div>
                    <div style="color: #A6B8AC; font-size: 0.8rem; line-height: 1.5;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: ABOUT
# ─────────────────────────────────────────────────────────────────────────────
def page_about():
    st.markdown('<div class="page-title">About the Project</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">LearnEase AI — Final Year Engineering Project</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="card-accent" style="padding: 2rem;">
        <div style="font-size: 1rem; font-weight: 700; color: #27C98B; margin-bottom: 0.75rem;">🎯 Project Overview</div>
        <div style="color: #A6B8AC; line-height: 1.8; font-size: 0.9rem;">
            LearnEase AI is an AI-powered course content simplification agent that helps students overcome the
            challenge of understanding complex academic topics. The system takes raw academic content — whether
            a topic name, pasted notes, or an uploaded document — and transforms it into structured, ready-to-use
            study material tailored to the learner's level and goals.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.markdown("""
        <div class="card">
            <div style="font-size: 0.95rem; font-weight: 700; color: #27C98B; margin-bottom: 0.75rem;">🔧 Technical Implementation</div>
            <ul style="color: #A6B8AC; font-size: 0.85rem; line-height: 1.8; padding-left: 1.2rem; margin: 0;">
                <li>Built with Python and Streamlit</li>
                <li>IBM watsonx.ai Runtime for AI inference</li>
                <li>Llama 3.3 70B Instruct (au-syd region)</li>
                <li>Secure API key management via python-dotenv</li>
                <li>PyMuPDF for PDF text extraction</li>
                <li>python-docx for DOCX text extraction</li>
                <li>Greedy decoding with repetition penalty</li>
                <li>Structured prompt engineering per output type</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <div style="font-size: 0.95rem; font-weight: 700; color: #27C98B; margin-bottom: 0.75rem;">🎓 Educational Value</div>
            <ul style="color: #A6B8AC; font-size: 0.85rem; line-height: 1.8; padding-left: 1.2rem; margin: 0;">
                <li>Supports Beginner, Intermediate, and Exam-focused learners</li>
                <li>Generates seven structured study-pack sections</li>
                <li>Accepts free-text topics, pasted notes, PDFs and DOCX files</li>
                <li>Produces concise definitions, key points, and glossaries</li>
                <li>Creates exam-ready practice questions with model answers</li>
                <li>Provides real-life examples for conceptual understanding</li>
                <li>Generates rapid revision summaries</li>
                <li>Downloadable study material in plain text format</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="margin-top: 0.5rem;">
        <div style="font-size: 0.95rem; font-weight: 700; color: #fde68a; margin-bottom: 0.75rem;">⚠️ Responsible AI Commitment</div>
        <div style="color: #A6B8AC; font-size: 0.85rem; line-height: 1.8;">
            LearnEase AI is designed as a learning aid, not a replacement for human educators or verified course materials.
            AI-generated content may contain inaccuracies. Students are strongly encouraged to cross-reference all generated
            material with official textbooks, lecture notes, and faculty guidance before use in assessments.
            The system does not store any user data or uploaded documents beyond the current session.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tech stack details
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">Technology Stack Details</p>', unsafe_allow_html=True)
    tech = [
        ("🐍", "Python 3.10+", "Core application language"),
        ("⚡", "Streamlit ≥ 1.35", "Web application framework"),
        ("🤖", "IBM watsonx.ai Runtime", "Cloud AI inference platform"),
        ("🦙", "Llama 3.3 70B Instruct", "Large language model (meta-llama)"),
        ("📄", "PyMuPDF ≥ 1.24", "PDF text extraction"),
        ("📝", "python-docx ≥ 1.1", "DOCX text extraction"),
        ("🔐", "python-dotenv", "Secure environment variable management"),
        ("🌐", "IBM Cloud IAM", "API key to Bearer token authentication"),
    ]
    col_t1, col_t2 = st.columns(2, gap="medium")
    for i, (icon, name, role) in enumerate(tech):
        with (col_t1 if i % 2 == 0 else col_t2):
            st.markdown(f"""
            <div class="card-sm" style="display: flex; gap: 0.9rem; align-items: center;">
                <div style="font-size: 1.1rem;">{icon}</div>
                <div>
                    <div style="color: #27C98B; font-weight: 600; font-size: 0.85rem;">{name}</div>
                    <div style="color: #A6B8AC; font-size: 0.78rem;">{role}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class="footer-text">
        LearnEase AI — AI-Powered Course Content Simplification Agent<br>
        <span style="color: #A6B8AC;">Built with IBM watsonx.ai Runtime · Python · Streamlit</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────────────────
page = st.session_state["page"]
if page == "dashboard":
    page_dashboard()
elif page == "create":
    page_create()
elif page == "how_it_works":
    page_how_it_works()
elif page == "about":
    page_about()
else:
    st.session_state["page"] = "dashboard"
    st.rerun()
