import streamlit as st
import shutil
import base64
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

# ============================================================
# CONFIG
# ============================================================
APP_TITLE = "ANJLEE DIGITAL SERVICES"
UPLOAD_ROOT = Path("cafe_uploads")
DATA_ROOT = Path("cafe_data")
RETENTION_DAYS = 3
MANAGER_PASSWORD = "CafeManager@123"
SUPPORTED_PREVIEW_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}

UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
DATA_ROOT.mkdir(parents=True, exist_ok=True)

# ============================================================
# PAGE SETUP
# ============================================================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🖨️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# STYLES - MOBILE FIRST / SIMPLE / LIGHT
# ============================================================
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(180deg, #fffefd 0%, #f6f8fc 100%);
            color: #1f2937;
        }
        .block-container {
            max-width: 760px;
            padding-top: 1rem;
            padding-bottom: 2rem;
        }
        div[data-testid="stSidebar"] {
            background: #ffffff;
        }
        .top-card {
            background: linear-gradient(135deg, #ffffff 0%, #eef4ff 100%);
            border: 1px solid #dbe7ff;
            border-radius: 24px;
            padding: 1.2rem;
            box-shadow: 0 10px 28px rgba(37, 99, 235, 0.08);
            margin-bottom: 1rem;
        }
        .brand-title {
            font-size: 1.65rem;
            font-weight: 900;
            color: #111827;
            line-height: 1.15;
        }
        .brand-subtitle {
            color: #6b7280;
            font-size: 0.95rem;
            margin-top: 0.35rem;
            line-height: 1.45;
        }
        .pill-row {
            margin-top: 0.8rem;
        }
        .pill {
            display: inline-block;
            background: #ffffff;
            border: 1px solid #dbe7ff;
            color: #2563eb;
            border-radius: 999px;
            padding: 0.35rem 0.7rem;
            font-size: 0.82rem;
            font-weight: 700;
            margin: 0 0.4rem 0.45rem 0;
        }
        .section-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 22px;
            padding: 1rem;
            box-shadow: 0 10px 24px rgba(17, 24, 39, 0.04);
            margin-bottom: 1rem;
        }
        .section-title {
            font-size: 1.1rem;
            font-weight: 800;
            color: #111827;
            margin-bottom: 0.2rem;
        }
        .section-subtitle {
            font-size: 0.93rem;
            color: #6b7280;
            margin-bottom: 0.85rem;
            line-height: 1.45;
        }
        .mini-step {
            background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%);
            border: 1px solid #e5eefc;
            border-radius: 18px;
            padding: 0.9rem;
            margin-bottom: 0.7rem;
        }
        .mini-step-title {
            font-weight: 800;
            color: #111827;
            margin-bottom: 0.15rem;
        }
        .mini-step-text {
            color: #6b7280;
            font-size: 0.92rem;
            line-height: 1.4;
        }
        .metric-box {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 0.9rem;
            text-align: center;
            margin-bottom: 0.8rem;
        }
        .metric-value {
            font-size: 1.55rem;
            font-weight: 900;
            color: #111827;
            line-height: 1.05;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #6b7280;
            margin-top: 0.2rem;
        }
        .notice {
            background: #eff6ff;
            border: 1px solid #cfe0ff;
            color: #1e3a8a;
            border-radius: 18px;
            padding: 0.85rem 1rem;
            font-size: 0.92rem;
            line-height: 1.45;
        }
        .stButton > button, .stDownloadButton > button, button[kind="primary"] {
            width: 100% !important;
            height: 3rem !important;
            border: none !important;
            border-radius: 14px !important;
            background: linear-gradient(135deg, #2563eb, #4f8cff) !important;
            color: white !important;
            font-weight: 800 !important;
            box-shadow: 0 10px 20px rgba(37, 99, 235, 0.18) !important;
        }
        .stTextInput input, .stTextArea textarea {
            border-radius: 14px !important;
            border: 1px solid #d1d5db !important;
            background: #ffffff !important;
        }
        .stFileUploader {
            border: 1px dashed #cbd5e1;
            background: #fbfdff;
            border-radius: 16px;
            padding: 0.4rem;
        }
        div[data-testid="stForm"] {
            background: transparent;
            border: none;
            padding: 0;
        }
        .tiny-muted {
            color: #6b7280;
            font-size: 0.88rem;
        }
        @media (max-width: 640px) {
            .block-container {
                padding-top: 0.75rem;
                padding-left: 0.8rem;
                padding-right: 0.8rem;
            }
            .brand-title {
                font-size: 1.35rem;
            }
            iframe {
                min-height: 360px !important;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HELPERS
# ============================================================
def cleanup_old_folders() -> None:
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    for item in UPLOAD_ROOT.iterdir():
        if not item.is_dir():
            continue
        try:
            folder_date = datetime.strptime(item.name, "%Y-%m-%d")
            if folder_date < cutoff:
                shutil.rmtree(item, ignore_errors=True)
        except ValueError:
            continue


def sanitize_name(name: str) -> str:
    safe = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in name.strip())
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe.strip("_") or "guest"


def get_month_log_path(date_obj: datetime | None = None) -> Path:
    dt = date_obj or datetime.now()
    return DATA_ROOT / f"print_log_{dt.strftime('%Y-%m')}.json"


def load_print_log(date_obj: datetime | None = None) -> List[Dict]:
    path = get_month_log_path(date_obj)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_print_log(entries: List[Dict], date_obj: datetime | None = None) -> None:
    path = get_month_log_path(date_obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def cleanup_old_logs() -> None:
    cutoff = datetime.now() - timedelta(days=31)
    for item in DATA_ROOT.glob("print_log_*.json"):
        try:
            month_str = item.stem.replace("print_log_", "")
            dt = datetime.strptime(month_str + "-01", "%Y-%m-%d")
            if dt < cutoff.replace(day=1):
                item.unlink(missing_ok=True)
        except Exception:
            continue


def add_print_log(file_record: Dict) -> None:
    entries = load_print_log()
    entries.append(
        {
            "printed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date_folder": file_record["date"],
            "user_folder": file_record["user_folder"],
            "filename": file_record["filename"],
            "path": str(file_record["path"]),
        }
    )
    save_print_log(entries)


def save_uploaded_files(customer_name: str, uploaded_files: List) -> List[Path]:
    today_str = datetime.now().strftime("%Y-%m-%d")
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_name = sanitize_name(customer_name)
    target_dir = UPLOAD_ROOT / today_str / f"{clean_name}_{timestamp_str}"
    target_dir.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    for uploaded_file in uploaded_files:
        destination = target_dir / uploaded_file.name
        with open(destination, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_paths.append(destination)
    return saved_paths


def get_all_uploaded_files() -> List[Dict]:
    rows = []
    for date_folder in sorted(UPLOAD_ROOT.iterdir(), reverse=True):
        if not date_folder.is_dir():
            continue
        for user_folder in sorted(date_folder.iterdir(), reverse=True):
            if not user_folder.is_dir():
                continue
            for file_path in sorted(user_folder.iterdir()):
                if file_path.is_file():
                    stat = file_path.stat()
                    rows.append(
                        {
                            "date": date_folder.name,
                            "user_folder": user_folder.name,
                            "filename": file_path.name,
                            "path": file_path,
                            "size_kb": round(stat.st_size / 1024, 2),
                            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                            "suffix": file_path.suffix.lower(),
                        }
                    )
    return rows


def file_to_base64(file_path: Path) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_mime_type(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return "application/pdf"
    if suffix == ".png":
        return "image/png"
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".txt":
        return "text/plain"
    return "application/octet-stream"


def render_print_button(file_record: Dict, key: str) -> None:
    file_path = file_record["path"]
    if file_path.suffix.lower() not in SUPPORTED_PREVIEW_EXTENSIONS:
        st.info("Print in browser works for PDF, image, and text files.")
        return

    if file_path.suffix.lower() == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text_content = f.read().replace("`", "\\`")
        html = f"""
        <script>
        function print_file_{key}() {{
            const win = window.open('', '_blank');
            win.document.write(`
                <html><head><title>{file_path.name}</title></head>
                <body style="font-family:Arial;padding:24px;white-space:pre-wrap;">{text_content}
                <script>window.onload=function(){{window.print();}};<\/script>
                </body></html>`);
            win.document.close();
        }}
        </script>
        <button onclick="print_file_{key}()" style="width:100%;padding:0.75rem 1rem;border:none;border-radius:14px;background:linear-gradient(135deg,#f59e0b,#fbbf24);color:white;font-weight:800;cursor:pointer;">🖨 Print in Browser</button>
        """
        st.components.v1.html(html, height=58)
        if st.button("Count print", key=f"count_print_{key}", use_container_width=True):
            add_print_log(file_record)
            st.success("Print count saved.")
        return

    mime_type = get_mime_type(file_path)
    encoded = file_to_base64(file_path)
    data_url = f"data:{mime_type};base64,{encoded}"
    html = f"""
    <script>
    function print_file_{key}() {{
        const fileUrl = '{data_url}';
        const win = window.open('', '_blank');
        win.document.write(`
            <html><head><title>{file_path.name}</title>
            <style>html,body{{margin:0;height:100%;}} iframe{{border:none;width:100%;height:100vh;}}</style>
            </head><body>
            <iframe src="${{fileUrl}}" onload="setTimeout(function(){{document.querySelector('iframe').contentWindow.focus();document.querySelector('iframe').contentWindow.print();}},700)"></iframe>
            </body></html>`);
        win.document.close();
    }}
    </script>
    <button onclick="print_file_{key}()" style="width:100%;padding:0.75rem 1rem;border:none;border-radius:14px;background:linear-gradient(135deg,#f59e0b,#fbbf24);color:white;font-weight:800;cursor:pointer;">🖨 Print in Browser</button>
    """
    st.components.v1.html(html, height=58)
    if st.button("Count print", key=f"count_print_{key}", use_container_width=True):
        add_print_log(file_record)
        st.success("Print count saved.")


def preview_file(file_path: Path) -> None:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        encoded = file_to_base64(file_path)
        st.markdown(f'<iframe src="data:application/pdf;base64,{encoded}" width="100%" height="420"></iframe>', unsafe_allow_html=True)
    elif suffix in {".png", ".jpg", ".jpeg"}:
        st.image(str(file_path), use_container_width=True)
    elif suffix == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            st.text_area("Preview", f.read(), height=220)
    else:
        st.caption("Preview unavailable for this file type.")


def require_manager_login() -> bool:
    if st.session_state.get("manager_logged_in", False):
        return True
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Manager Login</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Only staff can open uploads and dashboard.</div>', unsafe_allow_html=True)
    password = st.text_input("Manager password", type="password", placeholder="Enter password")
    if st.button("Login", use_container_width=True):
        if password == MANAGER_PASSWORD:
            st.session_state.manager_logged_in = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.markdown('</div>', unsafe_allow_html=True)
    return False


def logout_button() -> None:
    if st.button("Logout", use_container_width=True):
        st.session_state.manager_logged_in = False
        st.rerun()


# ============================================================
# INIT
# ============================================================
if "manager_logged_in" not in st.session_state:
    st.session_state.manager_logged_in = False

cleanup_old_folders()
cleanup_old_logs()
files = get_all_uploaded_files()
print_entries = load_print_log()

# ============================================================
# TOP NAV
# ============================================================
page = st.segmented_control(
    "Menu",
    ["Upload", "Manager", "Dashboard"],
    default="Upload",
)

# ============================================================
# HEADER
# ============================================================
st.markdown(
    f"""
    <div class="top-card">
        <div style="font-size:2.2rem; margin-bottom:0.25rem;">🖨️</div>
        <div class="brand-title">{APP_TITLE}</div>
        <div class="brand-subtitle">Upload files quickly. Staff can securely view, download, and print them.</div>
        <div class="pill-row">
            <span class="pill">Simple</span>
            <span class="pill">Mobile friendly</span>
            <span class="pill">Manager only access</span>
            <span class="pill">3 day retention</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# PAGE: UPLOAD
# ============================================================
if page == "Upload":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Upload your files</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Just enter your name and upload your document. That is all.</div>', unsafe_allow_html=True)

    st.markdown('<div class="mini-step"><div class="mini-step-title">📱 Open link</div><div class="mini-step-text">Scan the QR code outside the shop.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="mini-step"><div class="mini-step-title">🧑 Enter name</div><div class="mini-step-text">Staff can identify your files quickly.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="mini-step"><div class="mini-step-title">📄 Upload file</div><div class="mini-step-text">Your files stay for up to 3 days only.</div></div>', unsafe_allow_html=True)

    with st.form("upload_form", clear_on_submit=True):
        customer_name = st.text_input("Your name", placeholder="e.g. Priya Sharma")
        uploaded_files = st.file_uploader("Choose file(s)", accept_multiple_files=True)
        submitted = st.form_submit_button("Submit Files", use_container_width=True)

        if submitted:
            if not customer_name.strip():
                st.error("Please enter your name.")
            elif not uploaded_files:
                st.error("Please choose at least one file.")
            else:
                saved = save_uploaded_files(customer_name, uploaded_files)
                st.success(f"Uploaded {len(saved)} file(s) successfully.")
                st.info("Your files were sent to ANJLEE DIGITAL SERVICES.")

    st.markdown('<div class="notice">🔒 Other customers cannot see your files. Only management can access them.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# PAGE: MANAGER
# ============================================================
elif page == "Manager":
    if require_manager_login():
        st.markdown(f'<div class="metric-box"><div class="metric-value">{len(files)}</div><div class="metric-label">Files available</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-box"><div class="metric-value">{len(print_entries)}</div><div class="metric-label">Prints this month</div></div>', unsafe_allow_html=True)
        logout_button()
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Manager files</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Open a file card to preview, download, or print.</div>', unsafe_allow_html=True)

        if not files:
            st.info("No files uploaded yet.")
        else:
            query = st.text_input("Search files", placeholder="Search by filename or customer name")
            filtered = [
                row for row in files
                if not query
                or query.lower() in row["filename"].lower()
                or query.lower() in row["user_folder"].lower()
                or query.lower() in row["date"].lower()
            ]

            for idx, item in enumerate(filtered):
                with st.expander(f"📄 {item['filename']}"):
                    st.write(f"**Customer folder:** {item['user_folder']}")
                    st.write(f"**Date:** {item['date']}")
                    st.write(f"**Size:** {item['size_kb']} KB")
                    st.write(f"**Updated:** {item['modified']}")

                    with open(item["path"], "rb") as f:
                        raw = f.read()

                    st.download_button(
                        "Download file",
                        data=raw,
                        file_name=item["filename"],
                        mime=get_mime_type(item["path"]),
                        key=f"download_{idx}",
                        use_container_width=True,
                    )
                    render_print_button(item, key=f"print_{idx}")

                    if item["suffix"] in SUPPORTED_PREVIEW_EXTENSIONS:
                        st.markdown('<div class="tiny-muted">Preview</div>', unsafe_allow_html=True)
                        preview_file(item["path"])
                    else:
                        st.caption("Preview available for PDF, image, and text files only.")
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# PAGE: DASHBOARD
# ============================================================
else:
    if require_manager_login():
        entries = load_print_log()
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_prints = sum(1 for e in entries if e["printed_at"].startswith(today_str))
        unique_files = len(set((e["date_folder"], e["user_folder"], e["filename"]) for e in entries))

        st.markdown(f'<div class="metric-box"><div class="metric-value">{len(entries)}</div><div class="metric-label">Month print count</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-box"><div class="metric-value">{today_prints}</div><div class="metric-label">Today print count</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-box"><div class="metric-value">{unique_files}</div><div class="metric-label">Unique printed files</div></div>', unsafe_allow_html=True)
        logout_button()
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Print dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Monthly print activity saved in a JSON log.</div>', unsafe_allow_html=True)

        if not entries:
            st.info("No print entries yet.")
        else:
            by_day = {}
            for e in entries:
                day = e["printed_at"].split(" ")[0]
                by_day[day] = by_day.get(day, 0) + 1

            day_rows = [{"Date": k, "Prints": v} for k, v in sorted(by_day.items())]
            st.dataframe(day_rows, use_container_width=True, hide_index=True)
            st.dataframe(entries, use_container_width=True, hide_index=True)

            current_month_log = get_month_log_path()
            with open(current_month_log, "rb") as f:
                st.download_button(
                    "Download monthly JSON log",
                    data=f.read(),
                    file_name=current_month_log.name,
                    mime="application/json",
                    use_container_width=True,
                )
        st.markdown('</div>', unsafe_allow_html=True)