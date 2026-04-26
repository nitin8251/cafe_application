from collections import Counter

import streamlit as st

from components.ui import render_metric_strip, render_page_intro
from services.manager_service import get_all_uploads, get_top_customers, summarize_uploads


def render_dashboard_page(identity: dict, is_manager: bool) -> None:
    render_page_intro(
        "Business Dashboard",
        "A compact sales and queue view for the counter team. This page stays focused on revenue, pressure, and repeat-customer movement.",
        eyebrow="Manager Analytics",
    )

    if not is_manager:
        st.warning("Manager access is required for dashboard analytics.")
        return

    uploads = get_all_uploads()
    summary = summarize_uploads(uploads)
    render_metric_strip(
        [
            {"label": "Revenue", "value": f"Rs. {summary['revenue']:.2f}", "subvalue": "Completed order value"},
            {"label": "Completed", "value": summary["completed_orders"], "subvalue": "Jobs delivered"},
            {"label": "Pending", "value": summary["pending_orders"], "subvalue": "Live queue load"},
            {"label": "Guest Orders", "value": summary["guest_orders"], "subvalue": "Walk-in activity"},
        ]
    )

    if not uploads:
        st.caption("No uploads yet.")
        return

    service_counts = Counter(row.get("service_name", "Unknown") for row in uploads)
    locked_jobs = [row for row in uploads if row.get("locked_until")]

    top_left, top_right = st.columns([1.3, 1])
    with top_left:
        st.markdown("### Service Mix")
        st.bar_chart(service_counts)

    with top_right:
        render_metric_strip(
            [
                {"label": "Locked", "value": len(locked_jobs), "subvalue": "Retention protected"},
                {"label": "Average Ticket", "value": f"Rs. {summary['average_order_value']:.2f}", "subvalue": "Completed jobs only"},
            ]
        )

    st.markdown("### Repeat Customers")
    top_customers = get_top_customers(limit=8)
    if not top_customers:
        st.caption("No customer history yet.")
    else:
        rows = []
        for customer in top_customers:
            rows.append(
                {
                    "Customer": customer.get("display_name", "Customer"),
                    "Uploads": customer.get("upload_count", 0),
                    "Prints": customer.get("print_count", 0),
                    "Spend": round(customer.get("total_spent", 0.0), 2),
                    "Tier": customer.get("customer_tier", "new"),
                }
            )
        st.dataframe(rows, use_container_width=True, hide_index=True)

    st.markdown("### Manager Attention")
    st.markdown("#### Locked Retention")
    if locked_jobs:
        for row in locked_jobs[:10]:
            st.write(f"{row['customer_name']} | {row['file_name']} | until {row.get('locked_until')}")
    else:
        st.caption("No locked files right now.")
