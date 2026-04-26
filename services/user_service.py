from datetime import datetime, timezone

from services.firebase_init import get_firestore


def now_utc():
    return datetime.now(timezone.utc)


def get_user_document(user_id: str) -> dict | None:
    doc = get_firestore().collection("users").document(user_id).get()
    if not doc.exists:
        return None
    item = doc.to_dict()
    item["id"] = doc.id
    return item


def upsert_user_profile(identity: dict, customer_name: str, customer_phone: str = "") -> dict:
    db = get_firestore()
    user_id = identity["user_id"]
    doc_ref = db.collection("users").document(user_id)
    existing = doc_ref.get().to_dict() or {}
    upload_count = int(existing.get("upload_count", 0))
    customer_tier = "regular" if upload_count >= 2 else "new"

    profile = {
        "display_name": customer_name,
        "email": identity.get("email", ""),
        "phone_number": customer_phone.strip(),
        "identity_mode": identity["identity_mode"],
        "guest_id": user_id if identity["identity_mode"] == "guest" else "",
        "upload_count": upload_count,
        "uploaded_file_count": int(existing.get("uploaded_file_count", 0)),
        "print_count": int(existing.get("print_count", 0)),
        "services_completed": int(existing.get("services_completed", 0)),
        "total_spent": float(existing.get("total_spent", 0.0)),
        "customer_tier": customer_tier,
        "last_seen_at": now_utc(),
        "created_at": existing.get("created_at") or now_utc(),
    }
    doc_ref.set(profile, merge=True)
    profile["id"] = user_id
    return profile


def increment_upload_count(user_id: str) -> None:
    increment_upload_stats(user_id, uploaded_files=1)


def increment_upload_stats(user_id: str, uploaded_files: int = 1) -> None:
    db = get_firestore()
    doc_ref = db.collection("users").document(user_id)
    existing = doc_ref.get().to_dict() or {}
    count = int(existing.get("upload_count", 0)) + 1
    file_count = int(existing.get("uploaded_file_count", 0)) + max(int(uploaded_files), 0)
    doc_ref.set(
        {
            "upload_count": count,
            "uploaded_file_count": file_count,
            "customer_tier": "regular" if count >= 3 else "new",
            "last_seen_at": now_utc(),
        },
        merge=True,
    )


def record_completed_service(user_id: str, amount: float, is_print_job: bool) -> None:
    db = get_firestore()
    doc_ref = db.collection("users").document(user_id)
    existing = doc_ref.get().to_dict() or {}
    payload = {
        "services_completed": int(existing.get("services_completed", 0)) + 1,
        "total_spent": float(existing.get("total_spent", 0.0)) + float(amount),
        "last_seen_at": now_utc(),
    }
    if is_print_job:
        payload["print_count"] = int(existing.get("print_count", 0)) + 1
    doc_ref.set(payload, merge=True)
