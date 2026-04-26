import base64
import html
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from components.ui import render_metric_strip, render_page_intro
from services.catalog import get_photo_sizes
from services.manager_service import (
    approve_order,
    cleanup_expired_uploads,
    complete_order,
    delete_order,
    delete_completed_orders_within_hours,
    extend_retention,
    get_all_uploads,
    get_retention_watchlists,
    summarize_uploads,
    set_order_printing,
)
from services.order_views import (
    build_batch_map as build_batch_map_data,
    coerce_datetime as coerce_datetime_value,
    group_orders_by_date,
    matches_search as matches_order_search,
)
from services.photo_layout import build_merged_photo_document


MERGED_JOB_ROOT = Path("streamlit_uploads") / "merged_jobs"
MERGED_JOB_ROOT.mkdir(parents=True, exist_ok=True)
ORDER_PAGE_SIZE = 5


def _apply_manager_table_styles() -> None:
    st.markdown(
        """
        <style>
            .manager-table-head {
                display: grid;
                grid-template-columns: 3.8fr 1fr 0.85fr 2.2fr;
                gap: 0.65rem;
                background: linear-gradient(180deg, rgba(255,255,255,0.92) 0%, rgba(250,245,255,0.98) 100%);
                border: 1px solid rgba(167, 139, 250, 0.28);
                border-radius: 18px;
                box-shadow: 0 8px 24px rgba(124, 58, 237, 0.10);
                padding: 0.8rem 1rem;
                margin: 0.8rem 0 1rem;
            }
            .manager-table-head div {
                font-size: 0.78rem;
                font-weight: 800;
                color: #4c1d95;
                text-transform: uppercase;
                letter-spacing: 0.04em;
            }
            .manager-cell-label {
                color: #74658c;
                font-size: 0.72rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.03em;
                margin-bottom: 0.12rem;
            }
            .manager-cell-value {
                color: #25143f;
                font-size: 0.96rem;
                font-weight: 700;
                line-height: 1.25;
            }
            .manager-cell-sub {
                color: #5b4b76;
                font-size: 0.82rem;
                margin-top: 0.12rem;
                line-height: 1.25;
            }
            .manager-cell-badge {
                display: inline-block;
                margin-top: 0.3rem;
                padding: 0.16rem 0.48rem;
                border-radius: 999px;
                background: #f3e8ff;
                color: #6d28d9;
                font-size: 0.74rem;
                font-weight: 800;
            }
            .manager-job-card {
                padding-right: 0.35rem;
            }
            .manager-job-topline {
                display: flex;
                gap: 0.45rem;
                align-items: center;
                flex-wrap: wrap;
                margin-bottom: 0.16rem;
            }
            .manager-job-title {
                color: #25143f;
                font-size: 1rem;
                font-weight: 800;
                line-height: 1.2;
            }
            .manager-job-chip {
                display: inline-block;
                padding: 0.14rem 0.45rem;
                border-radius: 999px;
                background: #f3e8ff;
                color: #5b21b6;
                font-size: 0.72rem;
                font-weight: 800;
            }
            .manager-job-subline {
                color: #5b4b76;
                font-size: 0.84rem;
                line-height: 1.3;
                margin-top: 0.08rem;
            }
            .manager-job-meta {
                color: #7c3aed;
                font-size: 0.78rem;
                font-weight: 700;
                margin-top: 0.16rem;
            }
            .manager-status-pill {
                display: inline-block;
                margin-top: 0.28rem;
                padding: 0.18rem 0.55rem;
                border-radius: 999px;
                font-size: 0.74rem;
                font-weight: 800;
            }
            .manager-status-uploaded {
                background: #ede9fe;
                color: #5b21b6;
            }
            .manager-status-approved {
                background: #f5d0fe;
                color: #86198f;
            }
            .manager-status-printing {
                background: #fce7f3;
                color: #be185d;
            }
            .manager-status-completed {
                background: #dcfce7;
                color: #166534;
            }
            .manager-row-wrap {
                margin-bottom: 0.65rem;
            }
            div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:has(.manager-row-wrap) {
                border-radius: 20px !important;
                border: 1px solid rgba(167, 139, 250, 0.24) !important;
                background:
                    linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(250,245,255,0.97) 56%, rgba(245,243,255,0.94) 100%) !important;
                box-shadow: 0 12px 30px rgba(124, 58, 237, 0.09);
                padding: 0.3rem 0.35rem !important;
            }
            .manager-row-wrap [data-testid="stButton"] button,
            .manager-row-wrap [data-testid="stDownloadButton"] button {
                min-height: 2.15rem;
                border-radius: 12px !important;
                font-weight: 700 !important;
                white-space: nowrap !important;
                line-height: 1.05 !important;
                padding: 0.34rem 0.42rem !important;
                font-size: 0.78rem !important;
                box-shadow: none !important;
            }
            .manager-summary-card {
                background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(250,245,255,0.96) 100%);
                border: 1px solid rgba(167, 139, 250, 0.24);
                border-radius: 18px;
                box-shadow: 0 10px 28px rgba(124, 58, 237, 0.09);
                padding: 0.9rem 1rem;
            }
            .manager-summary-title {
                color: #74658c;
                font-size: 0.74rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.55rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_header_row() -> None:
    st.markdown(
        """
        <div class="manager-table-head">
            <div>Job</div>
            <div>Status / Retention</div>
            <div>Amount</div>
            <div>Actions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_text_cell(primary: str, secondary: str = "", tertiary: str = "") -> None:
    lines = [f"<div style='font-weight:700; color:#0f172a'>{primary or '-'}</div>"]
    if secondary:
        lines.append(f"<div style='color:#475569; font-size:0.88rem'>{secondary}</div>")
    if tertiary:
        lines.append(f"<div style='color:#0f766e; font-size:0.8rem; font-weight:600'>{tertiary}</div>")
    st.markdown("".join(lines), unsafe_allow_html=True)


def _render_labeled_cell(label: str, value: str, subvalue: str = "", badge: str = "") -> None:
    bits = [
        f"<div class='manager-cell-label'>{label}</div>",
        f"<div class='manager-cell-value'>{value or '-'}</div>",
    ]
    if subvalue:
        bits.append(f"<div class='manager-cell-sub'>{subvalue}</div>")
    if badge:
        bits.append(f"<div class='manager-cell-badge'>{badge}</div>")
    st.markdown("".join(bits), unsafe_allow_html=True)


def _render_job_cell(order: dict, batch_info: dict) -> None:
    service_meta = order.get("service_meta", {})
    finish = service_meta.get("photo_finish", "")
    print_style = service_meta.get("print_style", "")
    color_mode = service_meta.get("color_mode", "")
    detail_parts = [
        f"Customer: {order.get('customer_name', '-')}",
        f"Email/Mode: {order.get('customer_email') or order.get('identity_mode', 'guest').title()}",
        f"Pickup Code: {batch_info['pickup_code']}",
        f"Batch: File {batch_info['position']} of {batch_info['count']}",
        f"File: {order.get('original_file_name') or order.get('file_name', '-')}",
        f"Service: {order.get('service_name', '-')}",
        f"Copies: {order.get('copies', 1)}",
    ]
    if print_style:
        detail_parts.append(f"Print Style: {print_style}")
    if color_mode:
        detail_parts.append(f"Color Mode: {color_mode}")
    if finish:
        detail_parts.append(f"Photo Finish: {finish}")
    tooltip = "&#10;".join(detail_parts)

    meta_bits = [f"{order.get('copies', 1)} copies"]
    if color_mode:
        meta_bits.append(color_mode)
    if print_style:
        meta_bits.append(print_style)
    elif finish:
        meta_bits.append(finish)

    badge = "Regular" if order.get("customer_tier") == "regular" else "Guest" if order.get("identity_mode") == "guest" else ""
    badge_chip = f"<span class='manager-job-chip'>{badge}</span>" if badge else ""
    batch_chip = f"<span class='manager-job-chip'>{batch_info['pickup_code']}</span>"

    st.markdown(
        f"""
        <div class="manager-job-card" title="{tooltip}">
            <div class="manager-job-topline">
                <div class="manager-job-title">{order.get('customer_name', '-')}</div>
                {batch_chip}
                {badge_chip}
            </div>
            <div class="manager-job-subline">{_file_display_name(order)} • {order.get('service_name', '-')}</div>
            <div class="manager-job-subline">{order.get('customer_email') or order.get('identity_mode', 'guest').title()} • File {batch_info['position']} of {batch_info['count']}</div>
            <div class="manager-job-meta">{' | '.join(meta_bits)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_job_cell_safe(order: dict, batch_info: dict) -> None:
    service_meta = order.get("service_meta", {})
    finish = service_meta.get("photo_finish", "")
    print_style = service_meta.get("print_style", "")
    color_mode = service_meta.get("color_mode", "")

    detail_parts = [
        f"Customer: {order.get('customer_name', '-')}",
        f"Email/Mode: {order.get('customer_email') or order.get('identity_mode', 'guest').title()}",
        f"Pickup Code: {batch_info['pickup_code']}",
        f"Batch: File {batch_info['position']} of {batch_info['count']}",
        f"File: {order.get('original_file_name') or order.get('file_name', '-')}",
        f"Service: {order.get('service_name', '-')}",
        f"Copies: {order.get('copies', 1)}",
    ]
    if print_style:
        detail_parts.append(f"Print Style: {print_style}")
    if color_mode:
        detail_parts.append(f"Color Mode: {color_mode}")
    if finish:
        detail_parts.append(f"Photo Finish: {finish}")

    tooltip = "&#10;".join(html.escape(part, quote=True) for part in detail_parts)
    chips = [f"<span class='manager-job-chip'>{html.escape(str(batch_info['pickup_code']))}</span>"]
    if order.get("customer_tier") == "regular":
        chips.append("<span class='manager-job-chip'>Regular</span>")
    elif order.get("identity_mode") == "guest":
        chips.append("<span class='manager-job-chip'>Guest</span>")
    meta_bits = [f"{order.get('copies', 1)} copies"]
    if color_mode:
        meta_bits.append(color_mode)
    if print_style:
        meta_bits.append(print_style)
    elif finish:
        meta_bits.append(finish)

    customer_name = html.escape(str(order.get("customer_name", "-")))
    file_name = html.escape(_file_display_name(order))
    service_name = html.escape(str(order.get("service_name", "-")))
    identity_label = html.escape(order.get("customer_email") or order.get("identity_mode", "guest").title())
    meta_line = html.escape(" | ".join(meta_bits))

    st.markdown(
        (
            f"<div class='manager-job-card' title='{tooltip}'>"
            f"<div class='manager-job-topline'><div class='manager-job-title'>{customer_name}</div>{''.join(chips)}</div>"
            f"<div class='manager-job-subline'>{file_name} | {service_name}</div>"
            f"<div class='manager-job-subline'>{identity_label} | File {batch_info['position']} of {batch_info['count']}</div>"
            f"<div class='manager-job-meta'>{meta_line}</div>"
            f"</div>"
        ),
        unsafe_allow_html=True,
    )


def _format_timestamp(value) -> str:
    if not isinstance(value, datetime):
        return "-"
    localized = value.astimezone()
    return localized.strftime("%d %b %Y, %I:%M %p")


def _file_display_name(order: dict) -> str:
    file_name = order.get("file_name", "-")
    if len(file_name) <= 34:
        return file_name
    suffix = Path(file_name).suffix
    return f"{file_name[:28]}...{suffix}"


def _status_badge(status: str) -> str:
    mapping = {
        "uploaded": ("Uploaded", "manager-status-uploaded"),
        "approved": ("Approved", "manager-status-approved"),
        "printing": ("Printing", "manager-status-printing"),
        "completed": ("Completed", "manager-status-completed"),
    }
    label, css_class = mapping.get(status, (status.title(), "manager-status-uploaded"))
    return f"<span class='manager-status-pill {css_class}'>{label}</span>"


def _has_local_preview(order: dict) -> bool:
    local_file_path = order.get("local_file_path")
    return bool(local_file_path and Path(local_file_path).exists() and Path(local_file_path).is_file())


def _start_action_label(order: dict) -> str:
    if order.get("service_group") in {"print", "xerox", "photo"}:
        return "Start Print"
    return "Start Job"


def _render_local_preview(order: dict) -> None:
    local_file_path = order.get("local_file_path")
    if not local_file_path:
        st.caption("No local file path available.")
        return

    local_path = Path(local_file_path)
    if not local_path.exists() or not local_path.is_file():
        st.warning("Local file is missing from the Streamlit storage folder.")
        return

    suffix = local_path.suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        st.image(str(local_path), use_container_width=True)
        return

    if suffix == ".txt":
        st.text_area("Text preview", _cached_text_preview(str(local_path), local_path.stat().st_mtime), height=220)
        return

    if suffix == ".pdf":
        encoded = _cached_pdf_preview(str(local_path), local_path.stat().st_mtime)
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{encoded}" width="100%" height="520"></iframe>',
            unsafe_allow_html=True,
        )
        return

    st.caption("Preview is available for PDF, image, and text files.")


@st.cache_data(show_spinner=False)
def _cached_text_preview(local_file_path: str, modified_time: float) -> str:
    return Path(local_file_path).read_text(encoding="utf-8", errors="ignore")


@st.cache_data(show_spinner=False)
def _cached_pdf_preview(local_file_path: str, modified_time: float) -> str:
    return base64.b64encode(Path(local_file_path).read_bytes()).decode("utf-8")


def _render_download_button(order: dict, button_key: str, label: str = "File") -> None:
    local_file_path = order.get("local_file_path")
    if not local_file_path:
        return

    local_path = Path(local_file_path)
    if not local_path.exists() or not local_path.is_file():
        return

    try:
        with local_path.open("rb") as file_handle:
            st.download_button(
                label,
                data=file_handle.read(),
                file_name=order.get("file_name", local_path.name),
                mime=order.get("content_type", "application/octet-stream"),
                key=button_key,
                use_container_width=True,
            )
    except PermissionError:
        st.caption("File unavailable")


@st.cache_data(show_spinner=False)
def _cached_binary_base64(local_file_path: str, modified_time: float) -> str:
    return base64.b64encode(Path(local_file_path).read_bytes()).decode("utf-8")


def _render_print_window(order: dict) -> None:
    if not order or not _has_local_preview(order):
        return

    local_path = Path(order["local_file_path"])
    suffix = local_path.suffix.lower()
    modified_time = local_path.stat().st_mtime

    if suffix == ".pdf":
        mime_type = "application/pdf"
        content_html = (
            f'<iframe src="data:{mime_type};base64,{_cached_binary_base64(str(local_path), modified_time)}" '
            'style="width:100%;height:100vh;border:none;"></iframe>'
        )
    elif suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        mime_type = order.get("content_type") or "image/jpeg"
        content_html = (
            f'<div style="display:flex;align-items:center;justify-content:center;height:100vh;background:white;">'
            f'<img src="data:{mime_type};base64,{_cached_binary_base64(str(local_path), modified_time)}" '
            'style="max-width:100%;max-height:100%;object-fit:contain;" />'
            "</div>"
        )
    elif suffix == ".txt":
        escaped_text = json.dumps(_cached_text_preview(str(local_path), modified_time))
        content_html = (
            "<pre id='print-text' style=\"white-space:pre-wrap;font-family:Consolas,monospace;padding:24px;\">"
            "</pre>"
            f"<script>document.getElementById('print-text').textContent = {escaped_text};</script>"
        )
    else:
        return

    popup_title = json.dumps(f"Print {order.get('file_name', 'Document')}")
    printable_html = json.dumps(
        f"""
        <!doctype html>
        <html>
        <head>
            <title>{order.get('file_name', 'Print')}</title>
            <style>
                html, body {{
                    margin: 0;
                    padding: 0;
                    background: white;
                }}
            </style>
        </head>
        <body>
            {content_html}
        </body>
        </html>
        """
    )
    components.html(
        f"""
        <script>
        const popup = window.open("", "_blank", "width=1000,height=800");
        if (popup) {{
            popup.document.open();
            popup.document.write({printable_html});
            popup.document.close();
            popup.document.title = {popup_title};
            setTimeout(() => {{
                popup.focus();
                popup.print();
            }}, 450);
        }}
        </script>
        """,
        height=0,
    )
    st.info("Print window opened. If nothing appeared, allow pop-ups for this app and click Print again.")


def _render_print_dialog(orders: list[dict]) -> None:
    temp_order = st.session_state.get("print_dialog_temp_order")
    if temp_order:
        st.session_state.print_dialog_temp_order = None
        _render_print_window(temp_order)
        return

    print_id = st.session_state.get("print_dialog_order_id")
    if not print_id:
        return

    order = next((item for item in orders if item["id"] == print_id), None)
    st.session_state.print_dialog_order_id = None
    _render_print_window(order)


def _photo_merge_candidates(orders: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for order in orders:
        service_meta = order.get("service_meta", {})
        size_name = service_meta.get("photo_size_name")
        if (
            order.get("service_group") == "photo"
            and size_name
            and order.get("status") in {"uploaded", "approved", "printing"}
            and order.get("source_file_path")
            and Path(order["source_file_path"]).is_file()
        ):
            grouped[size_name].append(order)
    return {size: rows for size, rows in grouped.items() if len(rows) >= 2}


def _build_merged_photo_job(selected_orders: list[dict], size_name: str) -> dict:
    photo_sizes = get_photo_sizes()
    size_config = photo_sizes[size_name]
    generated, merged_bytes, summary = build_merged_photo_document(selected_orders, size_name, size_config)
    target_path = MERGED_JOB_ROOT / generated.name
    counter = 1
    while target_path.exists():
        target_path = MERGED_JOB_ROOT / f"{target_path.stem}_{counter}{target_path.suffix}"
        counter += 1
    target_path.write_bytes(merged_bytes)
    return {
        "id": f"merged::{target_path.stem}",
        "customer_name": "Merged Photo Job",
        "file_name": target_path.name,
        "service_name": f"Merged {size_name}",
        "local_file_path": str(target_path.resolve()),
        "content_type": generated.type,
        "summary": summary,
        "source_orders": selected_orders,
    }


def _render_photo_merge_studio(pending_orders: list[dict], manager_identity: dict) -> None:
    candidates_by_size = _photo_merge_candidates(pending_orders)
    if not candidates_by_size:
        return

    st.markdown("### Photo Merge Studio")
    st.caption("Combine compatible passport photo jobs into one printable file when you want to save paper.")

    available_sizes = sorted(candidates_by_size.keys())
    selected_size = st.selectbox("Merge photo size", available_sizes, key="photo_merge_size")
    size_orders = candidates_by_size[selected_size]

    option_labels = {}
    for order in size_orders:
        finish = order.get("service_meta", {}).get("photo_finish", "Original")
        option_labels[order["id"]] = (
            f"{order.get('pickup_code', '-')} | {order.get('customer_name', '-')} | "
            f"{order.get('copies', 1)} photos | {finish}"
        )

    selected_ids = st.multiselect(
        "Select photo jobs to merge",
        options=[order["id"] for order in size_orders],
        format_func=lambda order_id: option_labels[order_id],
        help="Pick at least two compatible photo jobs. The app will create one printable merged PDF for the manager.",
        key=f"photo_merge_pick_{selected_size}",
    )

    selected_orders = [order for order in size_orders if order["id"] in selected_ids]
    if selected_orders:
        total_photos = sum(int(order.get("copies", 1)) for order in selected_orders)
        st.caption(
            f"{len(selected_orders)} job(s) selected | {total_photos} photo copy/copies total | "
            f"same cut size: {selected_size}"
        )

    action_cols = st.columns([1.15, 1, 1, 1.2])
    if action_cols[0].button(
        "Build merged print file",
        use_container_width=True,
        type="primary",
        disabled=len(selected_orders) < 2,
        key=f"build_merge_{selected_size}",
    ):
        merged_order = _build_merged_photo_job(selected_orders, selected_size)
        st.session_state.merged_photo_job = merged_order
        for order in selected_orders:
            if order.get("status") == "uploaded":
                approve_order(order["id"], manager_identity)
            set_order_printing(order["id"], manager_identity)
        st.rerun()

    merged_order = st.session_state.get("merged_photo_job")
    if not merged_order:
        return

    summary = merged_order.get("summary", {})
    st.success(
        f"Merged file ready: {summary.get('orders_merged', 0)} job(s), "
        f"{summary.get('total_photos', 0)} photo copy/copies, {summary.get('page_count', 0)} page(s)."
    )

    output_cols = st.columns(4)
    if output_cols[0].button("Preview merged", use_container_width=True, key="preview_merged_photo_job"):
        _open_preview(merged_order)
    with output_cols[1]:
        _render_download_button(merged_order, "download_merged_photo_job", label="Download merged")
    if output_cols[2].button("Print merged", use_container_width=True, key="print_merged_photo_job", type="primary"):
        st.session_state.print_dialog_temp_order = merged_order
        st.rerun()
    if output_cols[3].button("Clear merged", use_container_width=True, key="clear_merged_photo_job"):
        local_file_path = merged_order.get("local_file_path")
        if local_file_path and Path(local_file_path).is_file():
            Path(local_file_path).unlink(missing_ok=True)
        st.session_state.merged_photo_job = None
        st.rerun()


def _build_batch_map(orders: list[dict]) -> dict[str, dict]:
    return build_batch_map_data(orders)


def _render_batch_summary(orders: list[dict]) -> None:
    if not orders:
        return

    batch_rows = []
    for (customer_name, pickup_code), count in Counter(
        (order.get("customer_name", "Unknown"), order.get("pickup_code", "-")) for order in orders
    ).items():
        batch_rows.append({"Customer": customer_name, "Pickup Code": pickup_code, "Files": count})

    st.dataframe(batch_rows, use_container_width=True, hide_index=True)


def _coerce_datetime(value) -> datetime:
    return coerce_datetime_value(value)


def _order_uploaded_date(order: dict) -> datetime:
    return _coerce_datetime(order.get("uploaded_at"))


def _date_groups(
    orders: list[dict],
    prefix: str,
    date_field: str = "uploaded_at",
) -> list[tuple[str, str, list[dict], datetime.date]]:
    return group_orders_by_date(orders, prefix, date_field=date_field)


def _render_date_overview(groups: list[tuple[str, str, list[dict], datetime.date]], prefix: str) -> None:
    today = datetime.now().astimezone().date()
    yesterday = today - timedelta(days=1)
    today_count = sum(len(rows) for _, _, rows, upload_date in groups if upload_date == today)
    yesterday_count = sum(len(rows) for _, _, rows, upload_date in groups if upload_date == yesterday)
    older_count = sum(len(rows) for _, _, rows, upload_date in groups if upload_date not in {today, yesterday})

    count_cols = st.columns(3)
    count_cols[0].metric(f"Today {prefix}", today_count)
    count_cols[1].metric(f"Yesterday {prefix}", yesterday_count)
    count_cols[2].metric(f"Older {prefix}", older_count)

    with st.expander(f"{prefix} Date Index", expanded=False):
        if not groups:
            st.caption(f"No {prefix.lower()} jobs to index.")
            return

        index_lines = [
            "| Date Bucket | Orders | Open |",
            "| --- | ---: | --- |",
        ]
        for title, anchor, rows, upload_date in groups:
            if upload_date == today:
                short_date = "Today"
            elif upload_date == yesterday:
                short_date = "Yesterday"
            else:
                short_date = upload_date.strftime("%d %b %Y")
            index_lines.append(f"| {title} | {len(rows)} | [Go to {short_date}](#{anchor}) |")
        st.markdown("\n".join(index_lines))


def _open_preview(order: dict) -> None:
    _render_preview_dialog(order)


def _matches_search(row: dict, term: str) -> bool:
    return matches_order_search(row, term)


def _paginate_orders(orders: list[dict], section_key: str) -> list[dict]:
    total_orders = len(orders)
    if total_orders <= ORDER_PAGE_SIZE:
        return orders

    total_pages = (total_orders + ORDER_PAGE_SIZE - 1) // ORDER_PAGE_SIZE
    page_key = f"page_{section_key}"
    current_page = int(st.session_state.get(page_key, 1))
    current_page = max(1, min(current_page, total_pages))
    st.session_state[page_key] = current_page

    start = (current_page - 1) * ORDER_PAGE_SIZE
    end = start + ORDER_PAGE_SIZE

    nav_cols = st.columns([1, 1.4, 1, 3], vertical_alignment="center")
    if nav_cols[0].button("Prev", key=f"{page_key}_prev", use_container_width=True, disabled=current_page <= 1):
        st.session_state[page_key] = current_page - 1
        st.rerun()
    nav_cols[1].caption(f"Page {current_page} of {total_pages} | Showing {start + 1}-{min(end, total_orders)} of {total_orders}")
    if nav_cols[2].button("Next", key=f"{page_key}_next", use_container_width=True, disabled=current_page >= total_pages):
        st.session_state[page_key] = current_page + 1
        st.rerun()

    return orders[start:end]


def _render_order_table(
    title: str,
    orders: list[dict],
    manager_identity: dict,
    section_key: str,
    allow_print_actions: bool = True,
) -> None:
    st.markdown(f"### {title}")
    if not orders:
        st.caption(f"No {title.lower()} right now.")
        return

    st.caption("Each row is one live work item. Shared pickup codes show which files belong to the same customer batch.")
    batch_map = _build_batch_map(orders)
    visible_orders = _paginate_orders(orders, section_key)

    _render_header_row()

    for index, order in enumerate(visible_orders, start=1):
        batch_info = batch_map.get(order["id"], {"pickup_code": "-", "count": 1, "position": 1})
        with st.container(border=True):
            st.markdown("<div class='manager-row-wrap'>", unsafe_allow_html=True)
            row = st.columns([3.8, 1.0, 0.85, 1.8])

            with row[0]:
                _render_job_cell_safe(order, batch_info)

            retention_label = (
                f"Locked until {_format_timestamp(order['locked_until'])}"
                if order.get("locked_until")
                else f"Expires {_format_timestamp(order.get('expires_at'))}"
            )
            with row[1]:
                st.markdown("<div class='manager-cell-label'>Status</div>", unsafe_allow_html=True)
                st.markdown(_status_badge(order.get("status", "uploaded")), unsafe_allow_html=True)
                st.markdown(f"<div class='manager-cell-sub'>{retention_label}</div>", unsafe_allow_html=True)

            with row[2]:
                _render_labeled_cell("Amount", f"Rs. {order.get('total_price', 0):.2f}", order.get("service_group", "-").title())

            preview_key = f"preview_{section_key}_{index}_{order['id']}"
            has_local_file = _has_local_preview(order)
            with row[3]:
                st.markdown("<div class='manager-cell-label'>Actions</div>", unsafe_allow_html=True)
                top_actions = st.columns(3)
                if top_actions[0].button(
                    "View",
                    key=preview_key,
                    use_container_width=True,
                    type="secondary",
                    disabled=not has_local_file,
                    help="Open file preview",
                ):
                    _open_preview(order)

                with top_actions[1]:
                    _render_download_button(order, f"download_{section_key}_{index}_{order['id']}", label="Save")

                if allow_print_actions and order["status"] in {"uploaded", "approved"}:
                    if top_actions[2].button(
                        "Start",
                        key=f"print_{section_key}_{index}_{order['id']}",
                        use_container_width=True,
                        type="primary",
                        help=_start_action_label(order),
                    ):
                        if order["status"] == "uploaded":
                            approve_order(order["id"], manager_identity)
                        set_order_printing(order["id"], manager_identity)
                        if has_local_file:
                            st.session_state.print_dialog_order_id = order["id"]
                        st.rerun()
                elif allow_print_actions and order["status"] == "printing":
                    top_actions[2].button("Active", key=f"active_{section_key}_{index}_{order['id']}", use_container_width=True, disabled=True)
                else:
                    top_actions[2].empty()

                bottom_actions = st.columns(3)
                if bottom_actions[0].button("Drop", key=f"delete_{section_key}_{index}_{order['id']}", use_container_width=True, help="Delete this order"):
                    delete_order(order["id"], manager_identity)
                    st.rerun()

                if order["status"] != "expired":
                    if bottom_actions[1].button("Hold", key=f"lock_{section_key}_{index}_{order['id']}", use_container_width=True, help="Lock retention for 7 days"):
                        extend_retention(order["id"], manager_identity, days=7)
                        st.rerun()
                else:
                    bottom_actions[1].empty()

                if order["status"] in {"approved", "printing"} or (not has_local_file and order["status"] == "uploaded"):
                    if bottom_actions[2].button("Done", key=f"done_{section_key}_{index}_{order['id']}", use_container_width=True, help="Mark this order completed"):
                        complete_order(order["id"], manager_identity)
                        st.rerun()
                else:
                    bottom_actions[2].empty()
            st.markdown("</div>", unsafe_allow_html=True)


@st.dialog("File Preview", width="large")
def _render_preview_dialog(order: dict) -> None:
    st.caption(f"{order['customer_name']} | {order['file_name']} | {order.get('service_name', '-')}")
    _render_local_preview(order)
    if st.button("Close Preview", use_container_width=True):
        st.rerun()


def render_manager_page(identity: dict, manager_identity: dict, is_manager: bool) -> None:
    _apply_manager_table_styles()

    if not is_manager:
        st.warning("Manager access is required for this page.")
        return

    uploads = get_all_uploads()
    cleaned = cleanup_expired_uploads(uploads)
    if cleaned:
        uploads = get_all_uploads()
    if cleaned:
        st.info(f"Auto-cleanup removed {cleaned} expired file(s) from local storage.")
    expiring_soon, locked_files = get_retention_watchlists(uploads)

    render_page_intro(
        "Operations Desk",
        "Only the current work should appear here: active pending jobs, merged photo jobs, and completed history by date.",
        eyebrow="Manager Workflow",
    )

    if expiring_soon:
        with st.expander("Expiring Soon", expanded=False):
            for order in expiring_soon[:5]:
                st.write(f"{order['customer_name']} | {order['file_name']} | expires: {order.get('expires_at')}")

    search = st.text_input("Search customer, email, file, or pickup code")
    uploads = [row for row in uploads if _matches_search(row, search)]
    locked_files = [row for row in locked_files if _matches_search(row, search)]

    service_groups = sorted({row.get("service_group", "other") for row in uploads if row.get("service_group")})
    service_focus = "All"
    if service_groups:
        service_focus = st.segmented_control(
            "Service focus",
            ["All"] + [group.replace("_", " ").title() for group in service_groups],
            default="All",
        )
        if service_focus and service_focus != "All":
            selected_group = service_focus.lower().replace(" ", "_")
            uploads = [row for row in uploads if row.get("service_group") == selected_group]
            locked_files = [row for row in locked_files if row.get("service_group") == selected_group]

    summary = summarize_uploads(uploads)
    render_metric_strip(
        [
            {"label": "Pending", "value": summary["pending_orders"], "subvalue": "Visible live desk load"},
            {"label": "Completed", "value": summary["completed_orders"], "subvalue": "Visible finished work"},
            {"label": "Locked", "value": len(locked_files), "subvalue": "Visible retention protected"},
        ]
    )
    if search or service_focus != "All":
        filter_bits = []
        if search:
            filter_bits.append(f"search: {search}")
        if service_focus != "All":
            filter_bits.append(f"service: {service_focus}")
        st.caption(f"Showing filtered results by {' | '.join(filter_bits)}")

    _render_print_dialog(uploads)

    pending_orders = [row for row in uploads if row.get("status") in {"uploaded", "approved", "printing"}]
    completed_orders = [row for row in uploads if row.get("status") == "completed"]
    pending_groups = _date_groups(pending_orders, "Pending", date_field="uploaded_at")
    completed_groups = _date_groups(completed_orders, "Completed", date_field="completed_at")

    pending_tab, completed_tab = st.tabs(["Pending Orders", "Completed Orders"])

    with pending_tab:
        _render_photo_merge_studio(pending_orders, manager_identity)
        _render_date_overview(pending_groups, "Pending")
        if pending_groups:
            for title, anchor, day_orders, upload_date in pending_groups:
                default_open = upload_date >= datetime.now().astimezone().date() - timedelta(days=1)
                st.markdown(f"<div id='{anchor}'></div>", unsafe_allow_html=True)
                with st.expander(f"{title} ({len(day_orders)})", expanded=default_open):
                    _render_order_table("Pending Orders", day_orders, manager_identity, f"{anchor}_pending")
        else:
            st.caption("No pending jobs right now.")

    with completed_tab:
        recent_completed_3h = len(
            [
                row for row in completed_orders
                if row.get("completed_at") and row.get("completed_at") >= datetime.now(timezone.utc) - timedelta(hours=3)
            ]
        )
        recent_completed_6h = len(
            [
                row for row in completed_orders
                if row.get("completed_at") and row.get("completed_at") >= datetime.now(timezone.utc) - timedelta(hours=6)
            ]
        )
        bulk_cols = st.columns([1, 1, 2], gap="small")
        if bulk_cols[0].button(f"Delete last 3h ({recent_completed_3h})", use_container_width=True, key="delete_completed_3h"):
            deleted = delete_completed_orders_within_hours(3, manager_identity)
            if deleted:
                st.success(f"Deleted {deleted} completed order file(s) from the last 3 hours.")
            else:
                st.info("No completed files found in the last 3 hours.")
            st.rerun()
        if bulk_cols[1].button(f"Delete last 6h ({recent_completed_6h})", use_container_width=True, key="delete_completed_6h"):
            deleted = delete_completed_orders_within_hours(6, manager_identity)
            if deleted:
                st.success(f"Deleted {deleted} completed order file(s) from the last 6 hours.")
            else:
                st.info("No completed files found in the last 6 hours.")
            st.rerun()
        bulk_cols[2].caption("Bulk delete removes the local file and the completed order record for recently finished work only.")
        _render_date_overview(completed_groups, "Completed")
        if completed_groups:
            for title, anchor, day_orders, upload_date in completed_groups:
                default_open = upload_date >= datetime.now().astimezone().date() - timedelta(days=1)
                st.markdown(f"<div id='{anchor}'></div>", unsafe_allow_html=True)
                with st.expander(f"{title} ({len(day_orders)})", expanded=default_open):
                    _render_order_table(title, day_orders, manager_identity, anchor, allow_print_actions=False)
        else:
            st.caption("No completed jobs right now.")
