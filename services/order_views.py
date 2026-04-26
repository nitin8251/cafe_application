from collections import defaultdict
from datetime import datetime, timedelta, timezone


def matches_search(row: dict, term: str) -> bool:
    if not term:
        return True
    lowered = term.lower()
    return (
        lowered in row.get("customer_name", "").lower()
        or lowered in row.get("customer_email", "").lower()
        or lowered in row.get("file_name", "").lower()
        or lowered in row.get("pickup_code", "").lower()
        or lowered in row.get("service_name", "").lower()
    )


def coerce_datetime(value) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    return datetime.min.replace(tzinfo=timezone.utc)


def group_orders_by_date(
    orders: list[dict],
    prefix: str,
    date_field: str = "uploaded_at",
) -> list[tuple[str, str, list[dict], datetime.date]]:
    today = datetime.now().astimezone().date()
    yesterday = today - timedelta(days=1)
    grouped: dict[datetime.date, list[dict]] = defaultdict(list)
    for order in orders:
        grouped[coerce_datetime(order.get(date_field)).astimezone().date()].append(order)

    sections = []
    for upload_date in sorted(grouped.keys(), reverse=True):
        if upload_date == today:
            title = f"Today {prefix}"
            anchor = f"{prefix.lower().replace(' ', '-')}-today"
        elif upload_date == yesterday:
            title = f"Yesterday {prefix}"
            anchor = f"{prefix.lower().replace(' ', '-')}-yesterday"
        else:
            title = f"{prefix} for {upload_date.strftime('%d %b %Y')}"
            anchor = f"{prefix.lower().replace(' ', '-')}-{upload_date.isoformat()}"
        daily_orders = sorted(grouped[upload_date], key=lambda row: (coerce_datetime(row.get(date_field)), row.get("queue_rank", 1)))
        sections.append((title, anchor, daily_orders, upload_date))
    return sections


def build_batch_map(orders: list[dict]) -> dict[str, dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for order in orders:
        grouped[order.get("pickup_code", "-")].append(order)

    batch_map = {}
    for pickup_code, batch_orders in grouped.items():
        sorted_orders = sorted(
            batch_orders,
            key=lambda row: (
                row.get("uploaded_at"),
                row.get("file_name", ""),
                row.get("id", ""),
            ),
        )
        for position, order in enumerate(sorted_orders, start=1):
            batch_map[order["id"]] = {
                "pickup_code": pickup_code,
                "count": len(sorted_orders),
                "position": position,
            }
    return batch_map
