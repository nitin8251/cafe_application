import json
from functools import lru_cache
from pathlib import Path


CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
SERVICE_CATALOG_PATH = CONFIG_DIR / "service_catalog.json"
PHOTO_SIZES_PATH = CONFIG_DIR / "photo_sizes.json"


@lru_cache(maxsize=4)
def _load_json(path: str) -> dict:
    with Path(path).open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def get_service_catalog() -> dict:
    return _load_json(str(SERVICE_CATALOG_PATH))


def get_photo_sizes() -> dict:
    return _load_json(str(PHOTO_SIZES_PATH))


@lru_cache(maxsize=4)
def get_photo_size_options() -> list[tuple[str, str, dict]]:
    options = []
    for name, config in get_photo_sizes().items():
        width_mm = config.get("width_mm")
        height_mm = config.get("height_mm")
        label = f"{name} ({width_mm} x {height_mm} mm)" if width_mm and height_mm else name
        options.append((name, label, config))
    return options


@lru_cache(maxsize=4)
def get_service_groups() -> list[str]:
    groups = {config.get("service_group", "other") for config in get_service_catalog().values()}
    return sorted(group for group in groups if group)


def _write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as file_handle:
        json.dump(payload, file_handle, indent=2, ensure_ascii=True)
        file_handle.write("\n")
    _load_json.cache_clear()
    get_photo_size_options.cache_clear()
    get_service_groups.cache_clear()


def save_service_catalog(catalog: dict) -> None:
    _write_json(SERVICE_CATALOG_PATH, catalog)


def save_photo_sizes(photo_sizes: dict) -> None:
    _write_json(PHOTO_SIZES_PATH, photo_sizes)


SERVICE_CATALOG = get_service_catalog()
PHOTO_SIZES = get_photo_sizes()
