from datetime import datetime
from services.firebase_init import get_firestore


def add_print_log(upload_id: str, file_name: str, customer_name: str):
    db = get_firestore()
    db.collection("print_logs").add({
        "upload_id": upload_id,
        "file_name": file_name,
        "customer_name": customer_name,
        "printed_at": datetime.now(),
        "printed_by": "manager"
    })