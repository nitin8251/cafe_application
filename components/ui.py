import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --shell-ink: #0f172a;
                --shell-muted: #64748b;
                --shell-panel: rgba(255,255,255,0.84);
                --shell-panel-strong: rgba(255,255,255,0.92);
                --shell-border: rgba(148, 163, 184, 0.22);
                --shell-shadow: 0 18px 46px rgba(15, 23, 42, 0.08);
                --shell-accent: #ea580c;
                --shell-accent-soft: rgba(234, 88, 12, 0.12);
            }
            .stApp {
                background:
                    radial-gradient(circle at top right, rgba(251, 191, 36, 0.16), transparent 23%),
                    radial-gradient(circle at bottom left, rgba(14, 165, 233, 0.11), transparent 18%),
                    linear-gradient(180deg, #fcfaf6 0%, #f6f1e9 56%, #f4efe6 100%);
                color: var(--shell-ink);
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
                    radial-gradient(circle at top right, rgba(251,191,36,0.28), transparent 18%),
                    linear-gradient(135deg, #111827 0%, #1e293b 40%, #7c2d12 100%);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 24px;
                color: white;
                padding: 0.95rem 1.3rem;
                box-shadow: 0 24px 50px rgba(15, 23, 42, 0.16);
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
                border: 1px solid var(--shell-border);
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
                color: #111827;
                font-size: 1.25rem;
                font-weight: 900;
                margin-bottom: 0.12rem;
            }
            .page-caption {
                color: #475569;
                font-size: 0.93rem;
                line-height: 1.45;
            }
            .metric-strip {
                background: var(--shell-panel-strong);
                border: 1px solid var(--shell-border);
                border-radius: 18px;
                padding: 0.85rem 0.95rem;
                box-shadow: 0 12px 26px rgba(148, 163, 184, 0.08);
            }
            .metric-strip-label {
                color: #64748b;
                font-size: 0.74rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.2rem;
            }
            .metric-strip-value {
                color: #0f172a;
                font-size: 1.2rem;
                font-weight: 900;
            }
            .metric-strip-sub {
                color: #475569;
                font-size: 0.82rem;
                margin-top: 0.15rem;
            }
            .stTextInput > div > div,
            .stTextArea textarea,
            .stSelectbox [data-baseweb="select"],
            .stMultiSelect [data-baseweb="select"],
            .stNumberInput input {
                border-radius: 16px !important;
            }
            .stButton > button, .stDownloadButton > button, button[kind="primary"] {
                border-radius: 14px !important;
                font-weight: 800 !important;
                border: 1px solid rgba(148,163,184,0.18) !important;
                transition: transform 0.16s ease, box-shadow 0.16s ease !important;
            }
            .stButton > button:hover, .stDownloadButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 10px 20px rgba(15, 23, 42, 0.10) !important;
            }
            div[data-baseweb="tab-list"] button {
                border-radius: 12px !important;
                font-weight: 700 !important;
            }
            div[data-baseweb="tab-list"] {
                gap: 0.35rem;
            }
            div[data-baseweb="tab-list"] button[aria-selected="true"] {
                background: rgba(234, 88, 12, 0.10) !important;
                color: #9a3412 !important;
            }
            section[data-testid="stSidebar"] {
                background:
                    linear-gradient(180deg, rgba(15,23,42,0.98) 0%, rgba(30,41,59,0.96) 100%);
                color: white;
            }
            section[data-testid="stSidebar"] * {
                color: inherit;
            }
            .sidebar-panel {
                background: rgba(255,255,255,0.08);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 20px;
                padding: 0.95rem 0.95rem 0.9rem;
                margin: 0.7rem 0 0.9rem;
                box-shadow: 0 14px 30px rgba(0,0,0,0.12);
            }
            .sidebar-panel-title {
                font-size: 1.02rem;
                font-weight: 900;
                margin-bottom: 0.22rem;
                color: #ffffff;
            }
            .sidebar-panel-caption {
                font-size: 0.84rem;
                line-height: 1.45;
                color: rgba(255,255,255,0.74);
                margin-bottom: 0.7rem;
            }
            section[data-testid="stSidebar"] .stTextInput > label,
            section[data-testid="stSidebar"] .stTextInput [data-testid="stWidgetLabel"],
            section[data-testid="stSidebar"] .stMarkdown,
            section[data-testid="stSidebar"] p,
            section[data-testid="stSidebar"] label {
                color: rgba(255,255,255,0.92) !important;
            }
            section[data-testid="stSidebar"] .stTextInput input {
                background: rgba(255,255,255,0.96) !important;
                color: #0f172a !important;
                border: 1px solid rgba(255,255,255,0.18) !important;
            }
            section[data-testid="stSidebar"] .stButton > button {
                min-height: 2.7rem !important;
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
