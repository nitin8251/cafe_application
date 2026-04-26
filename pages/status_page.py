from datetime import datetime

import streamlit as st

from components.ui import render_metric_strip, render_page_intro
from services.status_service import filter_orders_for_customer, get_orders_by_pickup_code


def _format_timestamp(value) -> str:
    if not isinstance(value, datetime):
        return "-"
    return value.astimezone().strftime("%d %b %Y, %I:%M %p")


def _status_message(status: str) -> str:
    messages = {
        "uploaded": "Your request has been received and is waiting in the queue.",
        "approved": "Your request has been reviewed and is ready for processing.",
        "printing": "Your request is currently being processed.",
        "completed": "Your request is completed and ready for delivery or pickup.",
        "expired": "This request has expired from active storage.",
    }
    return messages.get(status, "Status updated.")


def render_status_page(identity: dict) -> None:
    render_page_intro(
        "Track Delivery Status",
        "Use the pickup code to see only the current work state, amount, and last movement. Customers should get a fast answer here, not a complex dashboard.",
        eyebrow="Customer Tracking",
    )

    default_name = identity.get("display_name", "")
    if default_name == "Guest Customer":
        default_name = ""

    with st.form("status_lookup_form", clear_on_submit=False):
        pickup_code = st.text_input("Pickup code", placeholder="Example: ADS-ABC123")
        customer_name = st.text_input(
            "Customer name",
            value=default_name,
            placeholder="Optional, but helps confirm the right order",
        )
        submitted = st.form_submit_button("Check status", use_container_width=True, type="primary")

    if submitted:
        if not pickup_code.strip():
            st.error("Please enter the pickup code.")
            return

        orders = get_orders_by_pickup_code(pickup_code.strip().upper())
        if customer_name.strip():
            orders = filter_orders_for_customer(orders, customer_name)

        if not orders:
            st.warning("No matching order was found for that pickup code.")
            return

        st.success(f"Found {len(orders)} item(s) for pickup code {pickup_code.strip().upper()}.")
        active = len([order for order in orders if order.get("status") in {"uploaded", "approved", "printing"}])
        completed = len([order for order in orders if order.get("status") == "completed"])
        render_metric_strip(
            [
                {"label": "Items", "value": len(orders), "subvalue": "Linked to this pickup code"},
                {"label": "Active", "value": active, "subvalue": "Still in progress"},
                {"label": "Completed", "value": completed, "subvalue": "Ready or delivered"},
            ]
        )
        for order in orders:
            with st.container(border=True):
                top = st.columns([2, 1, 1])
                top[0].markdown(f"**{order.get('service_name', 'Service')}**")
                top[0].caption(order.get("file_name", "No file attachment"))
                top[1].metric("Status", order.get("status", "-").title())
                top[2].metric("Amount", f"Rs. {order.get('total_price', 0.0):.2f}")

                st.write(_status_message(order.get("status", "")))
                info_cols = st.columns(3)
                info_cols[0].caption(f"Created: {_format_timestamp(order.get('uploaded_at'))}")
                info_cols[1].caption(f"Updated: {_format_timestamp(order.get('completed_at') or order.get('printing_started_at') or order.get('approved_at'))}")
                info_cols[2].caption(f"Customer: {order.get('customer_name', '-')}")

                if order.get("notes"):
                    st.caption(f"Notes: {order['notes']}")
