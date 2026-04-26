from datetime import datetime, timedelta, timezone
from pathlib import Path

from firebase_admin import firestore
import streamlit as st

from services.firebase_init import get_firestore
from services.print_service import log_service_event
from services.user_service import record_completed_service


def _now():
    return datetime.now(timezone.utc)


def _is_protected(order: dict, now: datetime | None = None) -> bool:
    now = now or _now()
    locked_until = order.get("locked_until")
    return bool(locked_until and locked_until > now)


@st.cache_data(show_spinner=False, ttl=3)
def get_all_uploads(status: str | None = None) -> list[dict]:
    db = get_firestore()
    query = db.collection("uploads")
    if status:
        query = query.where("status", "==", status)
    docs = query.stream()

    rows = []
    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        rows.append(item)

    rows.sort(
        key=lambda row: (
            row.get("queue_rank", 1),
            row.get("uploaded_at") or datetime.min.replace(tzinfo=timezone.utc),
        ),
        reverse=False,
    )
    return rows


@st.cache_data(show_spinner=False, ttl=10)
def get_top_customers(limit: int = 5) -> list[dict]:
    docs = (
        get_firestore()
        .collection("users")
        .order_by("total_spent", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    rows = []
    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        rows.append(item)
    return rows


def invalidate_data_caches() -> None:
    get_all_uploads.clear()
    get_top_customers.clear()
    try:
        from services.status_service import get_orders_by_pickup_code

        get_orders_by_pickup_code.clear()
    except Exception:
        pass


def summarize_uploads(uploads: list[dict]) -> dict:
    completed = [row for row in uploads if row.get("status") == "completed"]
    pending = [row for row in uploads if row.get("status") in {"uploaded", "approved", "printing"}]
    guest_jobs = [row for row in uploads if row.get("identity_mode") == "guest"]
    revenue = round(sum(row.get("total_price", 0.0) for row in completed), 2)
    return {
        "revenue": revenue,
        "completed_orders": len(completed),
        "pending_orders": len(pending),
        "guest_orders": len(guest_jobs),
        "average_order_value": round(revenue / len(completed), 2) if completed else 0.0,
    }


def cleanup_expired_uploads(uploads: list[dict] | None = None) -> int:
    now = _now()
    uploads = uploads or get_all_uploads()
    deleted_count = 0

    for order in uploads:
        if order.get("status") == "completed" and _is_protected(order, now):
            continue
        if _is_protected(order, now):
            continue
        expires_at = order.get("expires_at")
        if not expires_at or expires_at > now:
            continue

        local_file_path = order.get("local_file_path")
        if local_file_path:
            local_path = Path(local_file_path)
            if local_path.exists():
                local_path.unlink(missing_ok=True)
                parent = local_path.parent
                while parent.name != "streamlit_uploads" and parent.exists():
                    try:
                        parent.rmdir()
                    except OSError:
                        break
                    parent = parent.parent

        source_file_path = order.get("source_file_path")
        if source_file_path:
            source_path = Path(source_file_path)
            if source_path.exists() and source_path.is_file():
                source_path.unlink(missing_ok=True)

        get_firestore().collection("uploads").document(order["id"]).set(
            {
                "status": "expired",
                "expired_at": now,
                "local_file_path": "",
                "source_file_path": "",
                "storage_status": "expired",
            },
            merge=True,
        )
        deleted_count += 1

    if deleted_count:
        invalidate_data_caches()
    return deleted_count


def get_service_events(limit: int = 25) -> list[dict]:
    docs = (
        get_firestore()
        .collection("service_events")
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    rows = []
    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        rows.append(item)
    return rows


def _get_upload(upload_id: str) -> tuple:
    db = get_firestore()
    doc_ref = db.collection("uploads").document(upload_id)
    snapshot = doc_ref.get()
    if not snapshot.exists:
        raise ValueError("Upload not found.")
    order = snapshot.to_dict()
    order["id"] = upload_id
    return doc_ref, order


def _remove_order_files(order: dict) -> None:
    local_file_path = order.get("local_file_path")
    if local_file_path:
        local_path = Path(local_file_path)
        if local_path.exists():
            local_path.unlink(missing_ok=True)
            parent = local_path.parent
            while parent.name != "streamlit_uploads" and parent.exists():
                try:
                    parent.rmdir()
                except OSError:
                    break
                parent = parent.parent

    source_file_path = order.get("source_file_path")
    if source_file_path:
        source_path = Path(source_file_path)
        if source_path.exists() and source_path.is_file():
            source_path.unlink(missing_ok=True)


def approve_order(upload_id: str, manager_identity: dict) -> None:
    doc_ref, order = _get_upload(upload_id)
    doc_ref.set(
        {
            "status": "approved",
            "approved_at": _now(),
            "approved_by": manager_identity.get("email") or manager_identity.get("name", "manager"),
        },
        merge=True,
    )
    log_service_event(order, "approved", 0.0, manager_identity)
    invalidate_data_caches()


def set_order_printing(upload_id: str, manager_identity: dict) -> None:
    doc_ref, order = _get_upload(upload_id)
    doc_ref.set(
        {
            "status": "printing",
            "printing_started_at": _now(),
            "printing_started_by": manager_identity.get("email") or manager_identity.get("name", "manager"),
        },
        merge=True,
    )
    log_service_event(order, "printing", 0.0, manager_identity)
    invalidate_data_caches()


def complete_order(upload_id: str, manager_identity: dict) -> None:
    doc_ref, order = _get_upload(upload_id)
    doc_ref.set(
        {
            "status": "completed",
            "completed_at": _now(),
            "completed_by": manager_identity.get("email") or manager_identity.get("name", "manager"),
        },
        merge=True,
    )
    record_completed_service(
        order["user_id"],
        order.get("total_price", 0.0),
        order.get("service_group") == "print",
    )
    log_service_event(order, "completed", order.get("total_price", 0.0), manager_identity)
    invalidate_data_caches()


def delete_order(upload_id: str, manager_identity: dict) -> None:
    doc_ref, order = _get_upload(upload_id)
    _remove_order_files(order)

    log_service_event(order, "deleted", 0.0, manager_identity)
    doc_ref.delete()
    invalidate_data_caches()


def delete_completed_orders_within_hours(hours: int, manager_identity: dict) -> int:
    cutoff = _now() - timedelta(hours=hours)
    orders = get_all_uploads(status="completed")
    deleted_count = 0

    for order in orders:
        completed_at = order.get("completed_at")
        if not completed_at or completed_at < cutoff:
            continue
        _remove_order_files(order)
        log_service_event(order, f"bulk_deleted_{hours}h", 0.0, manager_identity)
        get_firestore().collection("uploads").document(order["id"]).delete()
        deleted_count += 1

    if deleted_count:
        invalidate_data_caches()
    return deleted_count


def extend_retention(upload_id: str, manager_identity: dict, days: int = 7) -> None:
    doc_ref, order = _get_upload(upload_id)
    base = order.get("locked_until") or _now()
    if base < _now():
        base = _now()
    locked_until = base + timedelta(days=days)
    doc_ref.set(
        {
            "locked_until": locked_until,
            "retention_extended_by": manager_identity.get("email") or manager_identity.get("name", "manager"),
            "retention_extended_at": _now(),
        },
        merge=True,
    )
    log_service_event(order, "retention_extended", 0.0, manager_identity)
    invalidate_data_caches()


def get_retention_watchlists(uploads: list[dict] | None = None) -> tuple[list[dict], list[dict]]:
    now = _now()
    uploads = uploads or get_all_uploads()
    expiring_soon = []
    locked_files = []

    for order in uploads:
        expires_at = order.get("expires_at")
        locked_until = order.get("locked_until")

        if order.get("status") == "expired":
            continue

        if locked_until:
            locked_files.append(order)

        if order.get("status") in {"completed"}:
            continue

        if not locked_until and expires_at and expires_at <= now + timedelta(days=1):
            expiring_soon.append(order)

    expiring_soon.sort(key=lambda row: row.get("expires_at") or now)
    locked_files.sort(key=lambda row: row.get("locked_until") or now, reverse=True)
    return expiring_soon, locked_files


def get_dashboard_summary() -> dict:
    return summarize_uploads(get_all_uploads())
