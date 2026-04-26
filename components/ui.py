import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --shell-ink: #25143f;
                --shell-muted: #74658c;
                --shell-panel: rgba(255,255,255,0.82);
                --shell-panel-strong: rgba(255,255,255,0.94);
                --shell-border: rgba(50, 35, 72, 0.42);
                --shell-border-soft: rgba(50, 35, 72, 0.26);
                --shell-shadow: 0 18px 46px rgba(88, 28, 135, 0.10);
                --shell-accent: #7c3aed;
                --shell-accent-soft: rgba(124, 58, 237, 0.13);
            }
            .stApp {
                background:
                    radial-gradient(circle at top right, rgba(196, 181, 253, 0.34), transparent 24%),
                    radial-gradient(circle at bottom left, rgba(216, 180, 254, 0.24), transparent 22%),
                    linear-gradient(180deg, #fbf7ff 0%, #f5edff 48%, #f0e7ff 100%);
                color: var(--shell-ink) !important;
            }
            .stApp,
            .stApp p,
            .stApp label,
            .stApp span,
            .stApp li,
            .stApp div[data-testid="stMarkdownContainer"],
            .stApp [data-testid="stMarkdownContainer"] p,
            .stApp [data-testid="stCaptionContainer"],
            .stApp [data-testid="stWidgetLabel"],
            .stApp [data-testid="stWidgetLabel"] p {
                color: var(--shell-ink) !important;
            }
            .stApp [data-testid="stCaptionContainer"],
            .stApp small {
                color: var(--shell-muted) !important;
            }
            .block-container {
                max-width: 1180px;
                padding-top: 0.85rem;
                padding-bottom: 2.4rem;
            }
            .shell-banner {
                position: relative;
                overflow: hidden;
                background:
                    radial-gradient(circle at top right, rgba(255,255,255,0.46), transparent 22%),
                    linear-gradient(135deg, #8b5cf6 0%, #a78bfa 48%, #c084fc 100%);
                border: 1px solid rgba(50,35,72,0.42);
                border-radius: 24px;
                color: white;
                padding: 0.95rem 1.3rem;
                box-shadow: 0 24px 50px rgba(124, 58, 237, 0.18);
                margin-bottom: 0.75rem;
            }
            .shell-title {
                font-size: 2rem;
                font-weight: 900;
                letter-spacing: 0.02em;
                margin-bottom: 0;
            }
            .page-intro {
                background: var(--shell-panel);
                border: 1.4px solid var(--shell-border);
                border-radius: 22px;
                padding: 1rem 1.05rem;
                margin-bottom: 0.95rem;
                box-shadow: var(--shell-shadow);
                backdrop-filter: blur(10px);
            }
            .page-eyebrow {
                color: var(--shell-accent);
                font-size: 0.76rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-bottom: 0.22rem;
            }
            .page-title {
                color: #25143f;
                font-size: 1.25rem;
                font-weight: 900;
                margin-bottom: 0.12rem;
            }
            .page-caption {
                color: #5b4b76;
                font-size: 0.93rem;
                line-height: 1.45;
            }
            .metric-strip {
                background: var(--shell-panel-strong);
                border: 1.4px solid var(--shell-border);
                border-radius: 18px;
                padding: 0.85rem 0.95rem;
                box-shadow: 0 12px 26px rgba(148, 163, 184, 0.08);
            }
            .metric-strip-label {
                color: #74658c;
                font-size: 0.74rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.2rem;
            }
            .metric-strip-value {
                color: #25143f;
                font-size: 1.2rem;
                font-weight: 900;
            }
            .metric-strip-sub {
                color: #5b4b76;
                font-size: 0.82rem;
                margin-top: 0.15rem;
            }
            .stTextInput > div > div,
            .stTextArea textarea,
            .stSelectbox [data-baseweb="select"],
            .stMultiSelect [data-baseweb="select"],
            .stNumberInput input,
            .stDateInput input {
                border-radius: 16px !important;
                border: 1.4px solid var(--shell-border) !important;
                background: rgba(255,255,255,0.92) !important;
                box-shadow: 0 8px 18px rgba(88, 28, 135, 0.05) !important;
            }
            .stSelectbox [data-baseweb="select"] *,
            .stMultiSelect [data-baseweb="select"] *,
            .stSelectbox [data-baseweb="select"] svg,
            .stMultiSelect [data-baseweb="select"] svg {
                color: #25143f !important;
                fill: #25143f !important;
            }
            .stTextInput input,
            .stTextArea textarea,
            .stNumberInput input,
            .stDateInput input {
                color: #25143f !important;
                -webkit-text-fill-color: #25143f !important;
            }
            .stTextInput input::placeholder,
            .stTextArea textarea::placeholder,
            .stNumberInput input::placeholder {
                color: #7b6b95 !important;
                opacity: 1 !important;
            }
            .stFileUploader [data-testid="stFileUploaderDropzone"] {
                border: 1.6px solid var(--shell-border) !important;
                background: rgba(255,255,255,0.90) !important;
                border-radius: 16px !important;
                min-height: 4.2rem !important;
                box-shadow: 0 8px 18px rgba(88, 28, 135, 0.05) !important;
            }
            .stFileUploader [data-testid="stFileUploaderDropzone"] * {
                color: #25143f !important;
            }
            .stFileUploader [data-testid="stFileUploaderDropzone"] button {
                border: 1.4px solid rgba(50,35,72,0.52) !important;
                background: rgba(255,255,255,0.95) !important;
                color: #25143f !important;
            }
            .stButton > button, .stDownloadButton > button, button[kind="primary"] {
                border-radius: 14px !important;
                font-weight: 800 !important;
                border: 1.4px solid rgba(50,35,72,0.42) !important;
                color: #25143f !important;
                background: rgba(255,255,255,0.95) !important;
                transition: transform 0.16s ease, box-shadow 0.16s ease !important;
            }
            .stButton > button p,
            .stButton > button span,
            .stDownloadButton > button p,
            .stDownloadButton > button span {
                color: #25143f !important;
            }
            button[kind="primary"] {
                background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%) !important;
                color: #ffffff !important;
            }
            button[kind="primary"] p,
            button[kind="primary"] span {
                color: #ffffff !important;
            }
            .stButton > button:hover, .stDownloadButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 10px 20px rgba(15, 23, 42, 0.10) !important;
            }
            div[data-baseweb="tab-list"] button {
                border-radius: 12px !important;
                font-weight: 700 !important;
                color: #4c1d95 !important;
                background: rgba(255,255,255,0.72) !important;
                border: 1px solid rgba(50,35,72,0.28) !important;
            }
            div[data-baseweb="tab-list"] {
                gap: 0.35rem;
                overflow-x: auto !important;
                scrollbar-width: thin;
            }
            div[data-baseweb="tab-list"] button[aria-selected="true"] {
                background: rgba(124, 58, 237, 0.16) !important;
                color: #5b21b6 !important;
            }
            div[data-testid="stAlert"] {
                background: rgba(255,255,255,0.90) !important;
                border: 1px solid var(--shell-border-soft) !important;
                color: #25143f !important;
            }
            div[data-testid="stAlert"] * {
                color: #25143f !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background: rgba(255,255,255,0.66) !important;
                border-color: var(--shell-border-soft) !important;
            }
            section[data-testid="stSidebar"] {
                background:
                    radial-gradient(circle at top left, rgba(216,180,254,0.42), transparent 28%),
                    linear-gradient(180deg, #faf5ff 0%, #f3e8ff 100%);
                color: #25143f;
                border-right: 1px solid rgba(167, 139, 250, 0.22);
            }
            section[data-testid="stSidebar"] * {
                color: inherit;
            }
            .sidebar-panel {
                background: rgba(255,255,255,0.62);
                border: 1.4px solid var(--shell-border);
                border-radius: 20px;
                padding: 0.95rem 0.95rem 0.9rem;
                margin: 0.7rem 0 0.9rem;
                box-shadow: 0 14px 30px rgba(124,58,237,0.10);
            }
            .sidebar-panel-title {
                font-size: 1.02rem;
                font-weight: 900;
                margin-bottom: 0.22rem;
                color: #25143f;
            }
            .sidebar-panel-caption {
                font-size: 0.84rem;
                line-height: 1.45;
                color: #5b4b76;
                margin-bottom: 0.7rem;
            }
            section[data-testid="stSidebar"] .stTextInput > label,
            section[data-testid="stSidebar"] .stTextInput [data-testid="stWidgetLabel"],
            section[data-testid="stSidebar"] .stMarkdown,
            section[data-testid="stSidebar"] p,
            section[data-testid="stSidebar"] label {
                color: #25143f !important;
            }
            section[data-testid="stSidebar"] .stTextInput input {
                background: rgba(255,255,255,0.96) !important;
                color: #25143f !important;
                border: 1.4px solid var(--shell-border) !important;
            }
            section[data-testid="stSidebar"] .stButton > button {
                background: rgba(255,255,255,0.96) !important;
                color: #4c1d95 !important;
                min-height: 2.7rem !important;
                width: 100% !important;
                border-color: rgba(50,35,72,0.42) !important;
            }
            section[data-testid="stSidebar"] .stButton > button p,
            section[data-testid="stSidebar"] .stButton > button span {
                color: #4c1d95 !important;
            }
            section[data-testid="stSidebar"] .stButton > button:disabled,
            section[data-testid="stSidebar"] .stButton > button[disabled] {
                background: rgba(255,255,255,0.88) !important;
                color: #6d5a87 !important;
                opacity: 1 !important;
            }
            section[data-testid="stSidebar"] .stTextInput input::placeholder {
                color: #8b7aa6 !important;
                opacity: 1 !important;
            }
            @media (max-width: 640px) {
                .block-container {
                    padding-left: 0.8rem !important;
                    padding-right: 0.8rem !important;
                    max-width: 100vw !important;
                }
                .shell-banner {
                    border-radius: 18px;
                    padding: 0.8rem 0.95rem;
                }
                .shell-title {
                    font-size: 1.35rem;
                    line-height: 1.15;
                    word-break: break-word;
                }
                div[data-testid="stHorizontalBlock"] {
                    gap: 0.45rem !important;
                }
                .stButton > button {
                    min-height: 2.65rem !important;
                    padding-left: 0.55rem !important;
                    padding-right: 0.55rem !important;
                }
                .stFileUploader [data-testid="stFileUploaderDropzone"] {
                    min-height: 3.8rem !important;
                    padding: 0.65rem !important;
                }
                section[data-testid="stSidebar"] {
                    min-width: min(92vw, 360px) !important;
                    max-width: min(92vw, 360px) !important;
                }
                .sidebar-panel {
                    padding: 0.8rem !important;
                    border-radius: 18px !important;
                }
            }
            @media (max-width: 900px) {
                .shell-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_shell_banner(app_title: str, identity: dict, is_manager: bool) -> None:
    st.markdown(
        f"""
        <div class="shell-banner">
            <div class="shell-title">{app_title}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_workspace_nav(options: list[str], default: str, captions: dict[str, str]) -> str:
    selected = st.segmented_control("Workspace", options, default=default, selection_mode="single", label_visibility="collapsed")
    if selected:
        st.caption(captions.get(selected, ""))
    return selected or default


def render_page_intro(title: str, caption: str, eyebrow: str = "Workspace") -> None:
    st.markdown(
        f"""
        <div class="page-intro">
            <div class="page-eyebrow">{eyebrow}</div>
            <div class="page-title">{title}</div>
            <div class="page-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_strip(items: list[dict]) -> None:
    columns = st.columns(len(items))
    for column, item in zip(columns, items):
        column.markdown(
            f"""
            <div class="metric-strip">
                <div class="metric-strip-label">{item.get('label', '')}</div>
                <div class="metric-strip-value">{item.get('value', '-')}</div>
                <div class="metric-strip-sub">{item.get('subvalue', '')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
