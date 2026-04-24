from services.firebase_init import get_firestore


def get_all_uploads():
    db = get_firestore()
    docs = db.collection("uploads").order_by("uploaded_at", direction="DESCENDING").stream()
    rows = []
    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        rows.append(item)
    return rows


def get_print_logs():
    db = get_firestore()
    docs = db.collection("print_logs").order_by("printed_at", direction="DESCENDING").stream()
    rows = []
    for doc in docs:
        item = doc.to_dict()
        item["id"] = doc.id
        rows.append(item)
    return rows