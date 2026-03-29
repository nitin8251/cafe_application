import streamlit as st
import os
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
LIGHT_BG = "#f7f4ee"
CARD_BG = "#ffffff"
PRIMARY = "#2f6fed"
SECONDARY = "#ff8a3d"
ACCENT = "#17b890"
TEXT_DARK = "#1f2937"
TEXT_MUTED = "#6b7280"

UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
DATA_ROOT.mkdir(parents=True, exist_ok=True)

# ============================================================
# PAGE SETUP
# ============================================================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# STYLES
# ============================================================
st.markdown(
    f"""
    <style>
        .stApp {{
            background: linear-gradient(180deg, #fffdf9 0%, {LIGHT_BG} 100%);
            color: {TEXT_DARK};
        }}
        .block-container {{
            max-width: 1320px;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }}
        div[data-testid="stSidebar"] {{
            background: #fffaf3;
            border-right: 1px solid #ece7de;
        }}
        .hero {{
            background: linear-gradient(135deg, #ffffff 0%, #fdf7ef 100%);
            border: 1px solid #eee6d8;
            border-radius: 28px;
            padding: 1.6rem 1.8rem;
            box-shadow: 0 18px 42px rgba(47, 111, 237, 0.08);
            margin-bottom: 1.2rem;
        }}
        .soft-card {{
            background: {CARD_BG};
            border: 1px solid #ece7de;
            border-radius: 24px;
            padding: 1.15rem;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
        }}
        .metric-card {{
            background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%);
            border: 1px solid #e8edf7;
            border-radius: 22px;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 10px 20px rgba(47, 111, 237, 0.05);
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: 800;
            color: {TEXT_DARK};
            line-height: 1.05;
        }}
        .metric-label {{
            color: {TEXT_MUTED};
            font-size: 0.92rem;
            margin-top: 0.25rem;
        }}
        .section-title {{
            font-size: 1.22rem;
            font-weight: 800;
            color: {TEXT_DARK};
            margin-bottom: 0.2rem;
        }}
        .section-subtitle {{
            color: {TEXT_MUTED};
            font-size: 0.96rem;
            margin-bottom: 0.8rem;
        }}
        .feature-chip {{
            display:inline-block;
            background:#eef5ff;
            border:1px solid #d9e6ff;
            color:{PRIMARY};
            font-weight:700;
            border-radius:999px;
            padding:0.42rem 0.8rem;
            margin-right:0.45rem;
            margin-top:0.45rem;
            font-size:0.88rem;
        }}
        .guide-box {{
            background: linear-gradient(180deg, #fff 0%, #fff8ef 100%);
            border: 1px solid #f3e3ca;
            border-radius: 22px;
            padding: 1rem;
            height: 100%;
        }}
        .guide-icon {{
            font-size: 2rem;
            margin-bottom: 0.45rem;
        }}
        .guide-title {{
            font-size: 1rem;
            font-weight: 800;
            color: {TEXT_DARK};
            margin-bottom: 0.2rem;
        }}
        .guide-text {{
            color: {TEXT_MUTED};
            font-size: 0.94rem;
            line-height: 1.45;
        }}
        .stButton > button, .stDownloadButton > button, button[kind="primary"] {{
            border-radius: 14px !important;
            height: 3rem !important;
            border: none !important;
            color: white !important;
            font-weight: 700 !important;
            background: linear-gradient(135deg, {PRIMARY}, #5b8cff) !important;
            box-shadow: 0 10px 20px rgba(47, 111, 237, 0.18) !important;
        }}
        .stTextInput input, .stTextArea textarea {{
            border-radius: 14px !important;
            border: 1px solid #d9dde6 !important;
            background: #ffffff !important;
        }}
        .stFileUploader {{
            background: #fcfcfd;
            border-radius: 16px;
            padding: 0.4rem;
            border: 1px dashed #cfd8e3;
        }}
        div[data-testid="stForm"] {{
            background: #fff;
            border: 1px solid #ece7de;
            border-radius: 22px;
            padding: 1rem 1rem 0.6rem 1rem;
        }}
        .info-band {{
            background: linear-gradient(90deg, #eef8ff 0%, #f9fffc 100%);
            border: 1px solid #d5edf6;
            border-radius: 18px;
            padding: 0.9rem 1rem;
            color: {TEXT_DARK};
        }}
        .file-card {{
            background: #fff;
            border: 1px solid #ece7de;
            border-radius: 20px;
            padding: 1rem;
        }}
        .small-muted {{ color: {TEXT_MUTED}; font-size: 0.9rem; }}
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
        st.info("Browser print works for PDF, image, and text files.")
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
        <button onclick="print_file_{key}()" style="width:100%;padding:0.75rem 1rem;border:none;border-radius:14px;background:linear-gradient(135deg,#ff8a3d,#ffb36b);color:white;font-weight:700;cursor:pointer;">🖨 Print in Browser</button>
        """
        st.components.v1.html(html, height=60)
        if st.button("✅ Count This Print", key=f"count_print_{key}", use_container_width=True):
            add_print_log(file_record)
            st.success("Print count added to monthly log.")
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
            <iframe src="${{fileUrl}}" onload="setTimeout(function(){{document.querySelector('iframe').contentWindow.focus();document.querySelector('iframe').contentWindow.print();}},600)"></iframe>
            </body></html>`);
        win.document.close();
    }}
    </script>
    <button onclick="print_file_{key}()" style="width:100%;padding:0.75rem 1rem;border:none;border-radius:14px;background:linear-gradient(135deg,#ff8a3d,#ffb36b);color:white;font-weight:700;cursor:pointer;">🖨 Print in Browser</button>
    """
    st.components.v1.html(html, height=60)
    if st.button("✅ Count This Print", key=f"count_print_{key}", use_container_width=True):
        add_print_log(file_record)
        st.success("Print count added to monthly log.")


def preview_file(file_path: Path) -> None:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        encoded = file_to_base64(file_path)
        st.markdown(f'<iframe src="data:application/pdf;base64,{encoded}" width="100%" height="550"></iframe>', unsafe_allow_html=True)
    elif suffix in {".png", ".jpg", ".jpeg"}:
        st.image(str(file_path), use_container_width=True)
    elif suffix == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            st.text_area("Preview", f.read(), height=280)
    else:
        st.caption("Preview unavailable for this file type.")


def require_manager_login() -> bool:
    if st.session_state.get("manager_logged_in", False):
        return True
    st.markdown('<div class="soft-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Manager Login</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Login to access uploads, print actions, and dashboard analytics.</div>', unsafe_allow_html=True)
    password = st.text_input("Manager password", type="password", placeholder="Enter password")
    if st.button("Login", use_container_width=True):
        if password == MANAGER_PASSWORD:
            st.session_state.manager_logged_in = True
            st.success("Manager login successful.")
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.markdown('</div>', unsafe_allow_html=True)
    return False


def manager_logout_button() -> None:
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
# SIDEBAR
# ============================================================
st.sidebar.markdown(f"## {APP_TITLE}")
st.sidebar.caption("Customer uploads • Manager access • Monthly print tracking")
page = st.sidebar.radio("Pages", ["Cafe Uploads", "Manager", "Dashboard"])
st.sidebar.markdown("---")
st.sidebar.write(f"Retention: **{RETENTION_DAYS} days**")
# st.sidebar.write(f"This month print count: **{len(print_entries)}**")

# ============================================================
# HERO
# ============================================================
st.markdown(
    f"""
    <div class="hero">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap;">
            <div>
                <div style="font-size:2.1rem;font-weight:900;color:{TEXT_DARK};">{APP_TITLE}</div>
                <div style="font-size:1rem;color:{TEXT_MUTED};margin-top:0.25rem;max-width:800px;">
                    A clean and customer-friendly document collection and management portal with secure staff access, 3-day server retention, browser printing, and monthly print analytics.
                </div>
                <div>
                    <span class="feature-chip">Customer upload</span>
                    <span class="feature-chip">Manager only access</span>
                    <span class="feature-chip">Browser print</span>
                    <span class="feature-chip">Monthly JSON tracking</span>
                </div>
            </div>
            <div class="soft-card" style="min-width:310px; padding:1rem 1.1rem;">
                <div style="font-size:0.92rem;color:{TEXT_MUTED};">Storage structure</div>
                <div style="font-weight:800;color:{TEXT_DARK};">uploads / YYYY-MM-DD / username_timestamp / file</div>
                <div style="font-size:0.92rem;color:{TEXT_MUTED};margin-top:0.45rem;">Only management can see uploaded files.</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# PAGE 1: CAFE UPLOADS
# ============================================================
if page == "Cafe Uploads":
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown('<div class="metric-card"><div class="metric-value">Easy</div><div class="metric-label">Simple upload flow</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="metric-card"><div class="metric-value">Private</div><div class="metric-label">Not visible to other users</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="metric-card"><div class="metric-value">3 Days</div><div class="metric-label">Auto file cleanup</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1.25, 1])

    with left:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Upload your files</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Enter your name, choose your files, and submit. The shop team will be able to download and print them from the manager side.</div>', unsafe_allow_html=True)
        with st.form("upload_form", clear_on_submit=True):
            c1, c2 = st.columns([1, 1.4])
            with c1:
                customer_name = st.text_input("Your name", placeholder="e.g. Priya Sharma")
            with c2:
                uploaded_files = st.file_uploader("Choose one or more files", accept_multiple_files=True)
            submitted = st.form_submit_button("Submit Files", use_container_width=True)
            if submitted:
                if not customer_name.strip():
                    st.error("Please enter your name.")
                elif not uploaded_files:
                    st.error("Please select at least one file.")
                else:
                    saved = save_uploaded_files(customer_name, uploaded_files)
                    st.success(f"Uploaded {len(saved)} file(s) successfully.")
                    st.info("Your files have been sent to ANJLEE DIGITAL SERVICES.")
                    st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="guide-box">', unsafe_allow_html=True)
        st.markdown('<div class="guide-icon">📱</div><div class="guide-title">Step 1: Scan the QR</div><div class="guide-text">Open the upload link on your phone by scanning the QR code placed outside the shop.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="guide-box">', unsafe_allow_html=True)
        st.markdown('<div class="guide-icon">🧑</div><div class="guide-title">Step 2: Enter your name</div><div class="guide-text">Your files will be stored under your name and timestamp so the staff can identify them easily.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="guide-box">', unsafe_allow_html=True)
        st.markdown('<div class="guide-icon">📄</div><div class="guide-title">Step 3: Upload documents</div><div class="guide-text">You can upload one or more documents. They remain on the server for up to three days only.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="info-band">🔒 Privacy note: customers cannot browse uploads. Only staff can access them after manager login.</div>', unsafe_allow_html=True)

# ============================================================
# PAGE 2: MANAGER
# ============================================================
elif page == "Manager":
    if require_manager_login():
        top1, top2, top3, top4 = st.columns(4)
        with top1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{len(files)}</div><div class="metric-label">Files available</div></div>', unsafe_allow_html=True)
        with top2:
            today_count = sum(1 for row in files if row["date"] == datetime.now().strftime("%Y-%m-%d"))
            st.markdown(f'<div class="metric-card"><div class="metric-value">{today_count}</div><div class="metric-label">Today uploads</div></div>', unsafe_allow_html=True)
        with top3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{len(print_entries)}</div><div class="metric-label">This month prints</div></div>', unsafe_allow_html=True)
        with top4:
            manager_logout_button()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Manager file access</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Preview customer files, download them to your computer, and open the browser print dialog. After printing, press the count button to track the print.</div>', unsafe_allow_html=True)

        if not files:
            st.info("No uploaded files found.")
        else:
            query = st.text_input("Search files", placeholder="Search by filename, date, or customer folder")
            filtered = [
                row for row in files
                if not query
                or query.lower() in row["filename"].lower()
                or query.lower() in row["user_folder"].lower()
                or query.lower() in row["date"].lower()
            ]

            current_date = None
            for idx, item in enumerate(filtered):
                if current_date != item["date"]:
                    current_date = item["date"]
                    st.markdown(f"### 📅 {current_date}")

                with st.expander(f"📄 {item['filename']} · {item['user_folder']}"):
                    st.markdown('<div class="file-card">', unsafe_allow_html=True)
                    i1, i2, i3 = st.columns(3)
                    with i1:
                        st.write(f"**File:** {item['filename']}")
                    with i2:
                        st.write(f"**Size:** {item['size_kb']} KB")
                    with i3:
                        st.write(f"**Updated:** {item['modified']}")
                    st.caption(f"Stored path: {item['path']}")

                    a1, a2 = st.columns(2)
                    with a1:
                        with open(item["path"], "rb") as f:
                            raw = f.read()
                        st.download_button(
                            "⬇️ Download",
                            data=raw,
                            file_name=item["filename"],
                            mime=get_mime_type(item["path"]),
                            key=f"download_{idx}",
                            use_container_width=True,
                        )
                    with a2:
                        render_print_button(item, key=f"print_{idx}")

                    if item["suffix"] in SUPPORTED_PREVIEW_EXTENSIONS:
                        st.markdown("<div class='small-muted'>Document preview</div>", unsafe_allow_html=True)
                        preview_file(item["path"])
                    else:
                        st.caption("Preview is available for PDF, image, and text files only.")
                    st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# PAGE 3: DASHBOARD
# ============================================================
else:
    if require_manager_login():
        entries = load_print_log()
        total_prints = len(entries)
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_prints = sum(1 for e in entries if e["printed_at"].startswith(today_str))
        unique_files = len(set((e["date_folder"], e["user_folder"], e["filename"]) for e in entries))

        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{total_prints}</div><div class="metric-label">Month print count</div></div>', unsafe_allow_html=True)
        with d2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{today_prints}</div><div class="metric-label">Today print count</div></div>', unsafe_allow_html=True)
        with d3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{unique_files}</div><div class="metric-label">Unique printed files</div></div>', unsafe_allow_html=True)
        with d4:
            manager_logout_button()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Monthly print dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">This page reads the current month JSON log file and helps you monitor shop printing activity.</div>', unsafe_allow_html=True)

        if not entries:
            st.info("No print entries have been logged this month yet.")
        else:
            by_day = {}
            for e in entries:
                day = e["printed_at"].split(" ")[0]
                by_day[day] = by_day.get(day, 0) + 1

            st.markdown("#### Prints by day")
            day_rows = [{"Date": k, "Prints": v} for k, v in sorted(by_day.items())]
            st.dataframe(day_rows, use_container_width=True, hide_index=True)

            st.markdown("#### Print log details")
            st.dataframe(entries, use_container_width=True, hide_index=True)

            current_month_log = get_month_log_path()
            with open(current_month_log, "rb") as f:
                st.download_button(
                    "⬇️ Download current month JSON log",
                    data=f.read(),
                    file_name=current_month_log.name,
                    mime="application/json",
                    use_container_width=True,
                )
        st.markdown('</div>', unsafe_allow_html=True)
