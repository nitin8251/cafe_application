import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --shell-ink: #2f2219;
                --shell-muted: #756457;
                --shell-panel: rgba(255,255,255,0.82);
                --shell-panel-strong: rgba(255,255,255,0.94);
                --shell-border: rgba(64, 45, 31, 0.36);
                --shell-border-soft: rgba(64, 45, 31, 0.20);
                --shell-shadow: 0 18px 46px rgba(64, 45, 31, 0.10);
                --shell-accent: #b45309;
                --shell-accent-soft: rgba(180, 83, 9, 0.13);
            }
            .stApp {
                background:
                    radial-gradient(circle at top right, rgba(245, 158, 11, 0.18), transparent 24%),
                    radial-gradient(circle at bottom left, rgba(20, 184, 166, 0.12), transparent 22%),
                    linear-gradient(180deg, #fffaf2 0%, #fbf3e6 48%, #f7ead9 100%);
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
                    radial-gradient(circle at top right, rgba(255,255,255,0.28), transparent 22%),
                    linear-gradient(135deg, #3b2a1f 0%, #7c4a22 54%, #b45309 100%);
                border: 1px solid rgba(64,45,31,0.42);
                border-radius: 24px;
                color: white;
                padding: 0.95rem 1.3rem;
                box-shadow: 0 24px 50px rgba(64, 45, 31, 0.18);
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
                color: #2f2219;
                font-size: 1.25rem;
                font-weight: 900;
                margin-bottom: 0.12rem;
            }
            .page-caption {
                color: #756457;
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
                color: #756457;
                font-size: 0.74rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.2rem;
            }
            .metric-strip-value {
                color: #2f2219;
                font-size: 1.2rem;
                font-weight: 900;
            }
            .metric-strip-sub {
                color: #756457;
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
                box-shadow: 0 8px 18px rgba(64, 45, 31, 0.05) !important;
            }
            .stTextInput input,
            .stTextArea textarea,
            .stNumberInput input,
            .stDateInput input,
            .stSelectbox [data-baseweb="select"],
            .stMultiSelect [data-baseweb="select"],
            .stFileUploader [data-testid="stFileUploaderDropzone"] {
                color-scheme: light !important;
            }
            .stSelectbox [data-baseweb="select"] *,
            .stMultiSelect [data-baseweb="select"] *,
            .stSelectbox [data-baseweb="select"] svg,
            .stMultiSelect [data-baseweb="select"] svg {
                color: #2f2219 !important;
                fill: #2f2219 !important;
            }
            .stTextInput input,
            .stTextArea textarea,
            .stNumberInput input,
            .stDateInput input {
                color: #2f2219 !important;
                -webkit-text-fill-color: #2f2219 !important;
            }
            .stTextInput input::placeholder,
            .stTextArea textarea::placeholder,
            .stNumberInput input::placeholder {
                color: #8a7767 !important;
                opacity: 1 !important;
            }
            .stFileUploader [data-testid="stFileUploaderDropzone"] {
                border: 1.6px solid var(--shell-border) !important;
                background: rgba(255,255,255,0.90) !important;
                border-radius: 16px !important;
                min-height: 4.2rem !important;
                box-shadow: 0 8px 18px rgba(64, 45, 31, 0.05) !important;
            }
            .compact-upload-control {
                max-width: 13.5rem;
                margin-left: auto;
            }
            .compact-upload-control [data-testid="stFileUploaderDropzone"] {
                min-height: 3.35rem !important;
                padding: 0.42rem 0.58rem !important;
                display: flex !important;
                align-items: center !important;
                gap: 0.8rem !important;
            }
            .compact-upload-control [data-testid="stFileUploaderDropzone"] button {
                min-height: 2.25rem !important;
                padding: 0.28rem 0.78rem !important;
            }
            .compact-upload-control [data-testid="stFileUploaderDropzone"] small {
                white-space: nowrap !important;
            }
            .compact-upload-control [data-testid="stFileUploaderDropzone"] [data-testid="stFileUploaderDropzoneInstructions"] {
                min-width: 5.5rem !important;
            }
            .camera-button-cell .stButton > button {
                min-width: 2.75rem !important;
                width: 2.75rem !important;
                min-height: 2.75rem !important;
                padding: 0 !important;
                font-size: 1.05rem !important;
            }
            .stFileUploader [data-testid="stFileUploaderDropzone"] * {
                color: #2f2219 !important;
            }
            .stFileUploader [data-testid="stFileUploaderDropzone"] button {
                border: 1.4px solid rgba(64,45,31,0.48) !important;
                background: rgba(255,255,255,0.95) !important;
                color: #2f2219 !important;
            }
            .stButton > button, .stDownloadButton > button, button[kind="primary"] {
                border-radius: 14px !important;
                font-weight: 800 !important;
                border: 1.4px solid rgba(64,45,31,0.36) !important;
                color: #2f2219 !important;
                background: rgba(255,255,255,0.95) !important;
                transition: transform 0.16s ease, box-shadow 0.16s ease !important;
            }
            .stButton > button p,
            .stButton > button span,
            .stDownloadButton > button p,
            .stDownloadButton > button span {
                color: #2f2219 !important;
            }
            button[kind="primary"] {
                background: linear-gradient(135deg, #b45309 0%, #d97706 100%) !important;
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
                color: #5f3818 !important;
                background: rgba(255,255,255,0.72) !important;
                border: 1px solid rgba(64,45,31,0.26) !important;
            }
            div[data-baseweb="tab-list"] {
                gap: 0.35rem;
                overflow-x: auto !important;
                scrollbar-width: thin;
                padding-bottom: 0.2rem;
            }
            div[data-baseweb="tab-list"]::-webkit-scrollbar {
                height: 6px;
            }
            div[data-baseweb="tab-list"] button[aria-selected="true"] {
                background: rgba(180, 83, 9, 0.14) !important;
                color: #92400e !important;
            }
            div[data-testid="stAlert"] {
                background: rgba(255,255,255,0.90) !important;
                border: 1px solid var(--shell-border-soft) !important;
                color: #2f2219 !important;
            }
            div[data-testid="stAlert"] * {
                color: #2f2219 !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"] {
                background: rgba(255,255,255,0.66) !important;
                border-color: var(--shell-border-soft) !important;
            }
            section[data-testid="stSidebar"] {
                background:
                    radial-gradient(circle at top left, rgba(245,158,11,0.18), transparent 28%),
                    linear-gradient(180deg, #fffaf2 0%, #f7ead9 100%);
                color: #2f2219;
                border-right: 1px solid rgba(64,45,31,0.18);
            }
            section[data-testid="stSidebar"] > div {
                overflow-y: auto !important;
                padding-bottom: 2rem !important;
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
                box-shadow: 0 14px 30px rgba(64,45,31,0.10);
            }
            .sidebar-panel-title {
                font-size: 1.02rem;
                font-weight: 900;
                margin-bottom: 0.22rem;
                color: #2f2219;
            }
            .sidebar-panel-caption {
                font-size: 0.84rem;
                line-height: 1.45;
                color: #756457;
                margin-bottom: 0.7rem;
            }
            section[data-testid="stSidebar"] .stTextInput > label,
            section[data-testid="stSidebar"] .stTextInput [data-testid="stWidgetLabel"],
            section[data-testid="stSidebar"] .stMarkdown,
            section[data-testid="stSidebar"] p,
            section[data-testid="stSidebar"] label {
                color: #2f2219 !important;
            }
            section[data-testid="stSidebar"] .stTextInput input {
                background: rgba(255,255,255,0.96) !important;
                color: #2f2219 !important;
                border: 1.4px solid var(--shell-border) !important;
            }
            section[data-testid="stSidebar"] .stButton > button {
                background: rgba(255,255,255,0.96) !important;
                color: #7c4a22 !important;
                min-height: 2.7rem !important;
                width: 100% !important;
                border-color: rgba(64,45,31,0.36) !important;
            }
            section[data-testid="stSidebar"] .stButton > button p,
            section[data-testid="stSidebar"] .stButton > button span {
                color: #7c4a22 !important;
            }
            section[data-testid="stSidebar"] .stButton > button:disabled,
            section[data-testid="stSidebar"] .stButton > button[disabled] {
                background: rgba(255,255,255,0.88) !important;
                color: #756457 !important;
                opacity: 1 !important;
            }
            section[data-testid="stSidebar"] .stTextInput input::placeholder {
                color: #8a7767 !important;
                opacity: 1 !important;
            }
            @media (max-width: 640px) {
                .block-container {
                    padding-left: 0.72rem !important;
                    padding-right: 0.72rem !important;
                    padding-top: 0.42rem !important;
                    padding-bottom: 1.2rem !important;
                    max-width: 100vw !important;
                }
                .shell-banner {
                    border-radius: 18px;
                    padding: 0.72rem 0.88rem;
                    margin-bottom: 0.55rem;
                }
                .shell-title {
                    font-size: 1.18rem;
                    line-height: 1.15;
                    word-break: break-word;
                }
                .page-intro {
                    padding: 0.82rem 0.88rem !important;
                    border-radius: 18px !important;
                    margin-bottom: 0.72rem !important;
                }
                .page-title {
                    font-size: 1.05rem !important;
                }
                .page-caption {
                    font-size: 0.86rem !important;
                }
                div[data-testid="stHorizontalBlock"] {
                    gap: 0.45rem !important;
                }
                div[data-testid="stHorizontalBlock"] > div {
                    min-width: 0 !important;
                }
                .stButton > button {
                    min-height: 2.65rem !important;
                    padding-left: 0.55rem !important;
                    padding-right: 0.55rem !important;
                }
                .stTextInput input,
                .stNumberInput input,
                .stTextArea textarea,
                .stSelectbox [data-baseweb="select"] {
                    min-height: 2.7rem !important;
                    font-size: 0.96rem !important;
                }
                .stFileUploader [data-testid="stFileUploaderDropzone"] {
                    min-height: 3.45rem !important;
                    padding: 0.52rem !important;
                }
                .compact-upload-control {
                    max-width: none;
                    margin-left: 0;
                }
                .compact-upload-control [data-testid="stFileUploaderDropzone"] {
                    min-height: 3.15rem !important;
                    padding: 0.35rem 0.48rem !important;
                }
                .camera-button-cell .stButton > button {
                    width: 2.45rem !important;
                    min-width: 2.45rem !important;
                    min-height: 2.45rem !important;
                    font-size: 0.95rem !important;
                }
                section[data-testid="stSidebar"] {
                    min-width: min(88vw, 330px) !important;
                    max-width: min(88vw, 330px) !important;
                }
                section[data-testid="stSidebar"] h1 {
                    font-size: 1.08rem !important;
                    line-height: 1.2 !important;
                }
                .sidebar-panel {
                    padding: 0.66rem !important;
                    border-radius: 16px !important;
                    margin: 0.36rem 0 0.48rem !important;
                }
                .sidebar-panel-title {
                    font-size: 0.9rem !important;
                }
                .sidebar-panel-caption {
                    font-size: 0.76rem !important;
                    margin-bottom: 0 !important;
                }
                div[data-testid="stMetric"] {
                    background: rgba(255,255,255,0.72);
                    border: 1px solid rgba(64,45,31,0.16);
                    border-radius: 14px;
                    padding: 0.48rem 0.56rem;
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
