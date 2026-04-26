from datetime import datetime, timezone

from services.firebase_init import get_firestore


def log_service_event(order: dict, event_type: str, amount: float, manager_identity: dict) -> None:
    get_firestore().collection("service_events").add(
        {
            "upload_id": order.get("id", ""),
            "user_id": order.get("user_id", ""),
            "customer_name": order.get("customer_name", ""),
            "customer_email": order.get("customer_email", ""),
            "service_name": order.get("service_name", ""),
            "event_type": event_type,
            "amount": float(amount),
            "pickup_code": order.get("pickup_code", ""),
            "created_at": datetime.now(timezone.utc),
            "manager_email": manager_identity.get("email", ""),
            "manager_name": manager_identity.get("name", ""),
        }
    )
