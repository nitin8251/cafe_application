import json
from datetime import datetime, timezone
from pathlib import Path

from services.catalog import get_service_catalog


KNOWLEDGE_PATH = Path("cafe_data") / "desk_knowledge.json"
KNOWLEDGE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _default_entries() -> list[dict]:
    service_catalog = get_service_catalog()
    defaults = []
    for service_name, config in service_catalog.items():
        checklist = config.get("checklist", [])
        defaults.append(
            {
                "id": service_name.lower().replace(" ", "_").replace("/", "_"),
                "title": service_name,
                "service_group": config.get("service_group", "other"),
                "summary": config.get("description", ""),
                "procedure_steps": checklist,
                "useful_links": [],
                "required_docs": checklist,
                "desk_notes": config.get("notes_placeholder", ""),
                "owner": "Counter Team",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return defaults


def load_knowledge_entries() -> list[dict]:
    if not KNOWLEDGE_PATH.exists():
        entries = _default_entries()
        save_knowledge_entries(entries)
        return entries

    try:
        payload = json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        entries = _default_entries()
        save_knowledge_entries(entries)
        return entries

    entries = payload.get("entries", []) if isinstance(payload, dict) else payload
    return entries if isinstance(entries, list) else _default_entries()


def save_knowledge_entries(entries: list[dict]) -> None:
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "entries": entries,
    }
    KNOWLEDGE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def upsert_knowledge_entry(entry: dict) -> None:
    entries = load_knowledge_entries()
    updated = False
    normalized = {
        **entry,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    for index, current in enumerate(entries):
        if current.get("id") == normalized.get("id"):
            entries[index] = normalized
            updated = True
            break
    if not updated:
        entries.append(normalized)
    save_knowledge_entries(entries)


def summarize_knowledge(entries: list[dict]) -> dict:
    total_links = sum(len(entry.get("useful_links", [])) for entry in entries)
    with_links = sum(1 for entry in entries if entry.get("useful_links"))
    with_steps = sum(1 for entry in entries if entry.get("procedure_steps"))
    return {
        "total_entries": len(entries),
        "total_links": total_links,
        "with_links": with_links,
        "with_steps": with_steps,
    }
