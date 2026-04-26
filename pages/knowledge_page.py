from datetime import datetime

import streamlit as st

from components.ui import render_metric_strip, render_page_intro
from services.catalog import get_service_catalog, get_service_groups
from services.knowledge_service import load_knowledge_entries, summarize_knowledge, upsert_knowledge_entry


def _apply_knowledge_styles() -> None:
    st.markdown(
        """
        <style>
            .knowledge-card {
                background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(255,250,242,0.96) 100%);
                border: 1px solid rgba(64,45,31,0.22);
                border-radius: 20px;
                padding: 1rem 1rem 0.9rem;
                box-shadow: 0 12px 28px rgba(64,45,31,0.08);
                margin-bottom: 0.9rem;
            }
            .knowledge-topline {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 0.7rem;
                flex-wrap: wrap;
                margin-bottom: 0.35rem;
            }
            .knowledge-title {
                color: #2f2219;
                font-size: 1.02rem;
                font-weight: 900;
            }
            .knowledge-chip {
                display: inline-block;
                border-radius: 999px;
                background: #ffedd5;
                color: #92400e;
                border: 1px solid rgba(64,45,31,0.18);
                padding: 0.18rem 0.55rem;
                font-size: 0.74rem;
                font-weight: 800;
            }
            .knowledge-summary {
                color: #756457;
                font-size: 0.9rem;
                line-height: 1.45;
                margin-bottom: 0.6rem;
            }
            .knowledge-mini {
                color: #756457;
                font-size: 0.74rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin: 0.5rem 0 0.22rem;
            }
            .knowledge-meta {
                color: #756457;
                font-size: 0.78rem;
                margin-top: 0.65rem;
            }
            @media (max-width: 640px) {
                .knowledge-card {
                    padding: 0.82rem 0.82rem 0.76rem;
                }
                .knowledge-title {
                    font-size: 0.96rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _parse_lines(raw_text: str) -> list[str]:
    return [line.strip() for line in raw_text.splitlines() if line.strip()]


def _format_updated_at(value: str) -> str:
    if not value:
        return "-"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone().strftime("%d %b %Y, %I:%M %p")
    except ValueError:
        return value


def _render_card(entry: dict) -> None:
    link_items = entry.get("useful_links", [])
    step_items = entry.get("procedure_steps", [])
    doc_items = entry.get("required_docs", [])

    st.markdown(
        f"""
        <div class="knowledge-card">
            <div class="knowledge-topline">
                <div class="knowledge-title">{entry.get('title', 'Desk Note')}</div>
                <div class="knowledge-chip">{entry.get('service_group', 'other').replace('_', ' ').title()}</div>
            </div>
            <div class="knowledge-summary">{entry.get('summary', '')}</div>
        """,
        unsafe_allow_html=True,
    )

    if step_items:
        st.markdown("<div class='knowledge-mini'>Procedure</div>", unsafe_allow_html=True)
        for step in step_items:
            st.markdown(f"- {step}")

    if doc_items:
        st.markdown("<div class='knowledge-mini'>Required Documents</div>", unsafe_allow_html=True)
        for item in doc_items:
            st.markdown(f"- {item}")

    if link_items:
        st.markdown("<div class='knowledge-mini'>Useful Links</div>", unsafe_allow_html=True)
        for link in link_items:
            label, _, url = link.partition("|")
            display_label = label.strip() or url.strip()
            display_url = url.strip() if url.strip() else label.strip()
            if display_url:
                st.markdown(f"- [{display_label}]({display_url})")

    if entry.get("desk_notes"):
        st.markdown("<div class='knowledge-mini'>Desk Notes</div>", unsafe_allow_html=True)
        st.caption(entry.get("desk_notes"))

    st.markdown(
        f"<div class='knowledge-meta'>Owner: {entry.get('owner', 'Counter Team')} | Updated: {_format_updated_at(entry.get('updated_at', ''))}</div></div>",
        unsafe_allow_html=True,
    )


def render_knowledge_page(is_manager: bool) -> None:
    _apply_knowledge_styles()
    render_page_intro(
        "Knowledge Desk",
        "Keep desk procedures, useful links, and handover notes in one place so any team member can finish customer work with confidence.",
        eyebrow="Desk Transfer",
    )

    if not is_manager:
        st.warning("Manager access is required for desk knowledge.")
        return

    service_catalog = get_service_catalog()
    entries = load_knowledge_entries()
    summary = summarize_knowledge(entries)
    render_metric_strip(
        [
            {"label": "Knowledge Cards", "value": summary["total_entries"], "subvalue": "Saved service guides"},
            {"label": "Useful Links", "value": summary["total_links"], "subvalue": "Quick open references"},
            {"label": "Ready Procedures", "value": summary["with_steps"], "subvalue": "Cards with usable steps"},
            {"label": "Linked Services", "value": summary["with_links"], "subvalue": "Cards with live links"},
        ]
    )

    st.markdown("### Save or Update Desk Procedure")
    editor_cols = st.columns([1.1, 0.9], gap="large")
    with editor_cols[0]:
        service_name = st.selectbox("Service", list(service_catalog.keys()))
        base_config = service_catalog[service_name]
        entry_id = service_name.lower().replace(" ", "_").replace("/", "_")
        current_entry = next((item for item in entries if item.get("id") == entry_id), None)

        title = st.text_input("Card title", value=(current_entry or {}).get("title", service_name))
        summary_text = st.text_area(
            "Short summary",
            value=(current_entry or {}).get("summary", base_config.get("description", "")),
            placeholder="Explain the desk task in one short paragraph.",
            height=100,
        )
        procedure_steps = st.text_area(
            "Procedure steps",
            value="\n".join((current_entry or {}).get("procedure_steps", base_config.get("checklist", []))),
            placeholder="One step per line",
            height=160,
        )
    with editor_cols[1]:
        required_docs = st.text_area(
            "Required documents",
            value="\n".join((current_entry or {}).get("required_docs", base_config.get("checklist", []))),
            placeholder="One document or requirement per line",
            height=140,
        )
        useful_links = st.text_area(
            "Useful links",
            value="\n".join((current_entry or {}).get("useful_links", [])),
            placeholder="Use one line per link: Label | https://example.com",
            height=120,
        )
        owner = st.text_input("Owner / desk name", value=(current_entry or {}).get("owner", "Counter Team"))
        desk_notes = st.text_area(
            "Desk notes",
            value=(current_entry or {}).get("desk_notes", base_config.get("notes_placeholder", "")),
            placeholder="Write practical notes for the next person on the desk.",
            height=90,
        )

    save_cols = st.columns([1, 2])
    if save_cols[0].button("Save Knowledge Card", use_container_width=True, type="primary"):
        upsert_knowledge_entry(
            {
                "id": entry_id,
                "title": title.strip() or service_name,
                "service_group": base_config.get("service_group", "other"),
                "summary": summary_text.strip(),
                "procedure_steps": _parse_lines(procedure_steps),
                "useful_links": _parse_lines(useful_links),
                "required_docs": _parse_lines(required_docs),
                "desk_notes": desk_notes.strip(),
                "owner": owner.strip() or "Counter Team",
            }
        )
        st.success("Knowledge card saved.")
        st.rerun()
    save_cols[1].caption("Keep links, portal steps, and supporting notes here so another operator can continue the order without confusion.")

    st.markdown("### Saved Knowledge Cards")
    filter_cols = st.columns([1, 1])
    group_options = ["All"] + [group.replace("_", " ").title() for group in get_service_groups()]
    selected_group = filter_cols[0].selectbox("Filter by service group", group_options)
    search_term = filter_cols[1].text_input("Search title, notes, or steps")

    filtered_entries = []
    for entry in entries:
        if selected_group != "All" and entry.get("service_group", "").replace("_", " ").title() != selected_group:
            continue
        if search_term:
            haystack = " ".join(
                [
                    entry.get("title", ""),
                    entry.get("summary", ""),
                    " ".join(entry.get("procedure_steps", [])),
                    " ".join(entry.get("required_docs", [])),
                    " ".join(entry.get("useful_links", [])),
                    entry.get("desk_notes", ""),
                ]
            ).lower()
            if search_term.lower() not in haystack:
                continue
        filtered_entries.append(entry)

    if not filtered_entries:
        st.caption("No knowledge cards matched that filter.")
        return

    left_col, right_col = st.columns(2, gap="large")
    for index, entry in enumerate(filtered_entries):
        with left_col if index % 2 == 0 else right_col:
            _render_card(entry)
