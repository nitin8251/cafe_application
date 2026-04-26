from datetime import datetime, timezone

import streamlit as st

from services.firebase_init import get_firestore


def _coerce_datetime(value) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    return datetime.min.replace(tzinfo=timezone.utc)


@st.cache_data(show_spinner=False, ttl=5)
def get_orders_by_pickup_code(pickup_code: str) -> list[dict]:
    docs = (
        get_firestore()
        .collection("uploads")
        .where("pickup_code", "==", pickup_code.strip())
        .stream()
    )
    rows = []
    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        rows.append(item)
    rows.sort(key=lambda row: (_coerce_datetime(row.get("uploaded_at")), row.get("file_name", "")))
    return rows


def filter_orders_for_customer(orders: list[dict], customer_name: str) -> list[dict]:
    name = customer_name.strip().lower()
    if not name:
        return orders
    return [order for order in orders if order.get("customer_name", "").strip().lower() == name]
