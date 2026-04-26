from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from services.firebase_init import get_firestore
from services.manager_service import invalidate_data_caches
from services.user_service import increment_upload_stats, upsert_user_profile

LOCAL_UPLOAD_ROOT = Path("streamlit_uploads")
LOCAL_UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)


def _now():
    return datetime.now(timezone.utc)


def _sanitize(value: str) -> str:
    safe = "".join(char if char.isalnum() or char in ("_", "-") else "_" for char in value.strip())
    return safe.strip("_") or "customer"


def _safe_file_name(file_name: str) -> str:
    suffix = Path(file_name).suffix
    stem = Path(file_name).stem
    cleaned_stem = _sanitize(stem) or "file"
    return f"{cleaned_stem}{suffix.lower()}"


def _storage_file_name(customer_name: str, pickup_code: str, document_label: str, original_file_name: str) -> str:
    suffix = Path(original_file_name).suffix.lower() or ".bin"
    label = _sanitize(document_label) if document_label else _sanitize(Path(original_file_name).stem)
    return f"{_sanitize(customer_name)}_{_sanitize(pickup_code)}_{label}{suffix}"


def _price_for_upload(service_request: dict) -> float:
    base_total = float(service_request["unit_price"]) * int(service_request["copies"])
    if service_request.get("urgent"):
        base_total *= 1.25
    return round(base_total, 2)


def submit_uploads(identity: dict, customer_name: str, customer_phone: str, uploaded_files: list, service_request: dict) -> dict:
    db = get_firestore()
    user_profile = upsert_user_profile(identity, customer_name, customer_phone)
    pickup_code = f"ADS-{uuid4().hex[:6].upper()}"
    estimated_total = 0.0
    upload_ids = []
    stored_file_count = 0
    customer_slug = _sanitize(customer_name)
    storage_warnings = []

    attachments = uploaded_files or [None]
    file_overrides = service_request.get("file_overrides", [])
    source_uploads = service_request.get("source_uploads", [])
    file_labels = service_request.get("file_labels", [])

    for index, uploaded_file in enumerate(attachments):
        upload_id = str(uuid4())
        now = _now()
        folder = f"{customer_slug}_{now.strftime('%Y%m%d_%H%M%S')}"
        file_override = file_overrides[index] if index < len(file_overrides) else {}
        document_label = str(file_override.get("document_label") or (file_labels[index] if index < len(file_labels) else "")).strip()
        safe_file_name = "No file attachment"
        original_file_name = ""
        relative_storage_path = None
        local_file_path = None
        source_relative_storage_path = None
        source_local_file_path = None
        source_original_name = ""
        file_url = ""
        storage_status = "service_only"
        storage_error = ""
        content_type = "text/plain"
        size_kb = 0.0

        if uploaded_file is not None:
            safe_file_name = _storage_file_name(customer_name, pickup_code, document_label, uploaded_file.name)
            original_file_name = uploaded_file.name
            relative_storage_path = Path(now.strftime('%Y-%m-%d')) / folder / safe_file_name
            local_file_path = LOCAL_UPLOAD_ROOT / relative_storage_path
            local_file_path.parent.mkdir(parents=True, exist_ok=True)
            local_file_path.write_bytes(uploaded_file.getvalue())
            storage_status = "local"
            content_type = uploaded_file.type or "application/octet-stream"
            size_kb = round(uploaded_file.size / 1024, 2)
            stored_file_count += 1

        source_upload = source_uploads[index] if index < len(source_uploads) else None
        if source_upload is not None:
            safe_source_name = _storage_file_name(customer_name, pickup_code, document_label or source_upload.name, source_upload.name)
            source_original_name = source_upload.name
            source_relative_storage_path = Path(now.strftime('%Y-%m-%d')) / folder / f"source_{safe_source_name}"
            source_local_file_path = LOCAL_UPLOAD_ROOT / source_relative_storage_path
            source_local_file_path.parent.mkdir(parents=True, exist_ok=True)
            source_local_file_path.write_bytes(source_upload.getvalue())

        copies = int(file_override.get("copies", service_request["copies"]))
        effective_unit_price = float(file_override.get("unit_price", service_request["unit_price"]))
        total_price = _price_for_upload({**service_request, "copies": copies, "unit_price": effective_unit_price})
        estimated_total += total_price
        expires_at = now + timedelta(days=3)
        service_meta = dict(service_request.get("service_meta", {}))
        if file_override.get("print_style"):
            service_meta["print_style"] = file_override["print_style"]
        if file_override.get("color_mode"):
            service_meta["color_mode"] = file_override["color_mode"]
        if uploaded_file is not None:
            service_meta["file_sequence"] = index + 1

        document = {
            "user_id": user_profile["id"],
            "customer_name": customer_name,
            "customer_email": user_profile.get("email", ""),
            "customer_phone": user_profile.get("phone_number", ""),
            "customer_tier": user_profile.get("customer_tier", "new"),
            "identity_mode": identity["identity_mode"],
            "pickup_code": pickup_code,
            "service_name": service_request["service_name"],
            "service_group": service_request["service_group"],
            "copies": copies,
            "urgent": bool(service_request.get("urgent")),
            "notes": service_request.get("notes", ""),
            "unit_price": effective_unit_price,
            "total_price": total_price,
            "file_name": safe_file_name,
            "original_file_name": original_file_name,
            "document_label": document_label,
            "file_url": file_url,
            "storage_path": str(relative_storage_path).replace("\\", "/") if relative_storage_path is not None else "",
            "local_file_path": str(local_file_path.resolve()) if local_file_path is not None else "",
            "source_storage_path": str(source_relative_storage_path).replace("\\", "/") if source_relative_storage_path is not None else "",
            "source_file_path": str(source_local_file_path.resolve()) if source_local_file_path is not None else "",
            "source_original_name": source_original_name,
            "storage_status": storage_status,
            "storage_error": storage_error,
            "content_type": content_type,
            "size_kb": size_kb,
            "status": "uploaded",
            "uploaded_at": now,
            "expires_at": expires_at,
            "locked_until": None,
            "service_meta": service_meta,
            "queue_rank": 0 if service_request.get("urgent") else 1,
        }
        db.collection("uploads").document(upload_id).set(document)
        upload_ids.append(upload_id)

    increment_upload_stats(user_profile["id"], uploaded_files=stored_file_count or 1)
    invalidate_data_caches()

    customer_snapshot = get_firestore().collection("users").document(user_profile["id"]).get().to_dict() or {}
    return {
        "upload_ids": upload_ids,
        "pickup_code": pickup_code,
        "estimated_total": estimated_total,
        "customer_tier": customer_snapshot.get("customer_tier", "new"),
        "stored_file_count": stored_file_count,
        "storage_warnings": storage_warnings,
    }
