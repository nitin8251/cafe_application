from datetime import datetime
from uuid import uuid4
from services.firebase_init import get_firestore, get_bucket


def upload_file_to_firebase(customer_name: str, uploaded_file):
    db = get_firestore()
    bucket = get_bucket()

    now = datetime.now()
    upload_id = str(uuid4())
    safe_name = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in customer_name.strip())
    folder = f"{safe_name}_{now.strftime('%Y%m%d_%H%M%S')}"
    storage_path = f"uploads/{now.strftime('%Y-%m-%d')}/{folder}/{uploaded_file.name}"

    blob = bucket.blob(storage_path)
    blob.upload_from_file(
        uploaded_file,
        content_type=uploaded_file.type or "application/octet-stream"
    )
    blob.make_public()

    doc = {
        "customer_name": customer_name,
        "customer_slug": folder,
        "file_name": uploaded_file.name,
        "storage_path": storage_path,
        "file_url": blob.public_url,
        "size_kb": round(uploaded_file.size / 1024, 2),
        "content_type": uploaded_file.type or "application/octet-stream",
        "uploaded_at": now,
        "status": "uploaded",
    }

    db.collection("uploads").document(upload_id).set(doc)
    return upload_id, doc