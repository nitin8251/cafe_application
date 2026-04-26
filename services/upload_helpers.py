from math import ceil


DEFAULT_COLOR_MODE = "Black & White"


def service_variant_options(service_config: dict) -> dict[str, dict]:
    return {variant["label"]: variant for variant in service_config.get("variants", [])}


def estimate_total(unit_price: float, quantity: int, urgent: bool = False) -> float:
    total = float(unit_price) * int(quantity)
    if urgent:
        total *= 1.25
    return round(total, 2)


def slab_price(amount: float, slab_size: float, slab_rate: float) -> float:
    slabs = max(1, ceil(float(amount) / float(slab_size)))
    return round(slabs * float(slab_rate), 2)


def multiplier_price(units: float, unit_rate: float) -> float:
    return round(float(units) * float(unit_rate), 2)


def estimate_upload_total(
    unit_price: float,
    urgent: bool = False,
    file_overrides: list[dict] | None = None,
    fallback_quantity: int = 1,
) -> float:
    file_overrides = file_overrides or []
    if file_overrides:
        total = sum(float(item.get("unit_price", unit_price)) * int(item.get("copies", 1)) for item in file_overrides)
        if urgent:
            total *= 1.25
        return round(total, 2)
    return estimate_total(unit_price, fallback_quantity, urgent)


def filter_service_names(service_catalog: dict, selected_group: str, search_term: str) -> list[str]:
    term = search_term.strip().lower()
    names = []
    for name, config in service_catalog.items():
        if selected_group != "all" and config.get("service_group") != selected_group:
            continue
        haystack = " ".join(
            [
                name,
                config.get("description", ""),
                " ".join(config.get("checklist", [])),
                " ".join(variant.get("label", "") for variant in config.get("variants", [])),
            ]
        ).lower()
        if term and term not in haystack:
            continue
        names.append(name)
    return names


def service_suggestions(service_catalog: dict, filtered_service_names: list[str], search_term: str) -> list[str]:
    if not search_term.strip():
        return filtered_service_names[:8]

    term = search_term.strip().lower()
    ranked = []
    for name in filtered_service_names:
        config = service_catalog[name]
        score = 0
        lower_name = name.lower()
        if lower_name.startswith(term):
            score += 5
        if term in lower_name:
            score += 3
        if term in config.get("description", "").lower():
            score += 2
        if any(term in item.lower() for item in config.get("checklist", [])):
            score += 1
        if any(term in variant.get("label", "").lower() for variant in config.get("variants", [])):
            score += 1
        ranked.append((score, name))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [name for _, name in ranked[:8]]
