import streamlit as st

from components.ui import render_metric_strip, render_page_intro
from services.catalog import get_photo_sizes, get_service_catalog, save_photo_sizes, save_service_catalog


def _service_rows(category: str | None = None) -> list[dict]:
    rows = []
    for name, config in get_service_catalog().items():
        if category and config.get("service_group", "") != category:
            continue
        options = " | ".join(
            f"{variant.get('label', '').strip()}:{float(variant.get('unit_price', 0.0)):.2f}"
            for variant in config.get("variants", [])
            if variant.get("label")
        )
        color_modes = " | ".join(
            f"{mode.get('label', '').strip()}:{float(mode.get('unit_price', 0.0)):.2f}"
            for mode in config.get("color_modes", [])
            if mode.get("label")
        )
        custom_inputs = " | ".join(
            " ; ".join(
                part for part in [
                    str(field.get("label", "")).strip(),
                    str(field.get("type", "text")).strip(),
                    "required" if field.get("required") else "",
                    f"options={','.join(field.get('options', []))}" if field.get("options") else "",
                ] if part
            )
            for field in config.get("custom_inputs", [])
            if field.get("label")
        )
        required_uploads = " | ".join(str(item).strip() for item in config.get("required_uploads", []) if str(item).strip())
        optional_uploads = " | ".join(str(item).strip() for item in config.get("optional_uploads", []) if str(item).strip())
        rows.append(
            {
                "Service Name": name,
                "Rate": float(config.get("unit_price", 0.0)),
                "Description": config.get("description", ""),
                "Pricing Mode": config.get("pricing_mode", "per_unit"),
                "Quantity Label": config.get("quantity_label", "Copies / quantity"),
                "Upload Required": bool(config.get("upload_required", True)),
                "Print Style": bool(config.get("show_print_style", False)),
                "Custom Rate": bool(config.get("allow_custom_rate", False)),
                "Options": options,
                "Color Modes": color_modes,
                "Required Uploads": required_uploads,
                "Optional Uploads": optional_uploads,
                "Custom Inputs": custom_inputs,
            }
        )
    return rows


def _photo_rows() -> list[dict]:
    return [
        {
            "Photo Size": name,
            "Rate": float(config.get("unit_price", 0.0)),
            "Width (mm)": float(config.get("width_mm", 0.0)),
            "Height (mm)": float(config.get("height_mm", 0.0)),
            "Description": config.get("description", ""),
        }
        for name, config in get_photo_sizes().items()
    ]


def _parse_labeled_rates(text: str, service_name: str, label: str) -> tuple[bool, list[dict] | str]:
    items = []
    if not text.strip():
        return True, items
    for chunk in text.split("|"):
        option = chunk.strip()
        if not option:
            continue
        if ":" not in option:
            return False, f"{label} must look like Label:Rate for {service_name}."
        item_label, item_rate = option.split(":", 1)
        try:
            parsed_rate = round(float(item_rate.strip()), 2)
        except ValueError:
            return False, f"{label} rate must be numeric for {service_name}."
        items.append({"label": item_label.strip(), "unit_price": parsed_rate})
    return True, items


def _parse_simple_list(text: str) -> list[str]:
    return [item.strip() for item in str(text).split("|") if item.strip()]


def _parse_custom_inputs(text: str, service_name: str) -> tuple[bool, list[dict] | str]:
    if not text.strip():
        return True, []

    items = []
    for chunk in text.split("|"):
        entry = chunk.strip()
        if not entry:
            continue
        parts = [part.strip() for part in entry.split(";") if part.strip()]
        if len(parts) < 2:
            return False, f"Custom inputs must look like Label ; type ; required for {service_name}."
        field = {"label": parts[0], "type": parts[1].lower()}
        for extra in parts[2:]:
            lowered = extra.lower()
            if lowered == "required":
                field["required"] = True
            elif lowered.startswith("options="):
                field["options"] = [item.strip() for item in extra.split("=", 1)[1].split(",") if item.strip()]
        items.append(field)
    return True, items


def _save_service_rows(rows: list[dict], category: str) -> tuple[bool, str]:
    catalog = get_service_catalog()
    updated_catalog = dict(catalog)
    category_names = {name for name, config in catalog.items() if config.get("service_group", "") == category}

    for row in rows:
        name = str(row.get("Service Name", "")).strip()
        if not name:
            return False, "Every service row needs a service name."
        try:
            rate = round(float(row.get("Rate", 0.0)), 2)
        except (TypeError, ValueError):
            return False, f"Rate must be numeric for {name}."
        if rate < 0:
            return False, f"Rate cannot be negative for {name}."

        ok, variants = _parse_labeled_rates(str(row.get("Options", "")), name, "Options")
        if not ok:
            return False, variants
        ok, color_modes = _parse_labeled_rates(str(row.get("Color Modes", "")), name, "Color modes")
        if not ok:
            return False, color_modes
        ok, custom_inputs = _parse_custom_inputs(str(row.get("Custom Inputs", "")), name)
        if not ok:
            return False, custom_inputs

        base = dict(catalog.get(name, {}))
        base.update(
            {
                "unit_price": rate,
                "service_group": category,
                "description": str(row.get("Description", "")).strip(),
                "pricing_mode": str(row.get("Pricing Mode", "per_unit")).strip().lower() or "per_unit",
                "quantity_label": str(row.get("Quantity Label", "")).strip() or "Copies / quantity",
                "upload_required": bool(row.get("Upload Required", True)),
                "show_print_style": bool(row.get("Print Style", False)),
                "allow_custom_rate": bool(row.get("Custom Rate", False)),
            }
        )
        if variants:
            base["variants"] = variants
        else:
            base.pop("variants", None)
        if color_modes:
            base["color_modes"] = color_modes
            base["show_color_mode"] = True
        else:
            base.pop("color_modes", None)
            base.pop("show_color_mode", None)
        if custom_inputs:
            base["custom_inputs"] = custom_inputs
        else:
            base.pop("custom_inputs", None)

        required_uploads = _parse_simple_list(str(row.get("Required Uploads", "")))
        optional_uploads = _parse_simple_list(str(row.get("Optional Uploads", "")))
        if required_uploads:
            base["required_uploads"] = required_uploads
        else:
            base.pop("required_uploads", None)
        if optional_uploads:
            base["optional_uploads"] = optional_uploads
        else:
            base.pop("optional_uploads", None)

        updated_catalog[name] = base
        category_names.discard(name)

    save_service_catalog(updated_catalog)
    return True, f"{category.replace('_', ' ').title()} rates updated."


def _save_photo_rows(rows: list[dict]) -> tuple[bool, str]:
    cleaned = {}
    for row in rows:
        name = str(row.get("Photo Size", "")).strip()
        description = str(row.get("Description", "")).strip()
        if not name:
            return False, "Every photo size row needs a name."
        try:
            rate = round(float(row.get("Rate", 0.0)), 2)
            width_mm = float(row.get("Width (mm)", 0.0))
            height_mm = float(row.get("Height (mm)", 0.0))
        except (TypeError, ValueError):
            return False, f"Photo size values must be numeric for {name}."
        if rate < 0 or width_mm <= 0 or height_mm <= 0:
            return False, f"Rate, width, and height must be positive for {name}."
        cleaned[name] = {
            "unit_price": rate,
            "width_mm": width_mm,
            "height_mm": height_mm,
            "description": description,
        }
    save_photo_sizes(cleaned)
    return True, "Photo size rates updated."


def _rate_list_rows(category: str) -> list[dict]:
    rows = []
    for name, config in get_service_catalog().items():
        if config.get("service_group", "") != category:
            continue
        rows.append(
            {
                "Service": name,
                "Base Rate": round(float(config.get("unit_price", 0.0)), 2),
                "Mode": config.get("pricing_mode", "per_unit"),
            }
        )
    return rows


def _service_item_rows(items: list[str]) -> list[dict]:
    return [{"Label": item} for item in items]


def _service_input_rows(config: dict) -> list[dict]:
    rows = []
    for field in config.get("custom_inputs", []):
        rows.append(
            {
                "Label": field.get("label", ""),
                "Type": field.get("type", "text"),
                "Required": bool(field.get("required", False)),
                "Options": ", ".join(field.get("options", [])),
            }
        )
    return rows


def _parse_line_items(text: str) -> list[str]:
    return [line.strip() for line in str(text).splitlines() if line.strip()]


def _create_service(service_name: str, category: str, description: str, base_rate: float, pricing_mode: str, upload_required: bool) -> tuple[bool, str]:
    catalog = get_service_catalog()
    normalized_name = service_name.strip()
    if not normalized_name:
        return False, "Service name is required."
    if normalized_name in catalog:
        return False, f"{normalized_name} already exists."

    catalog[normalized_name] = {
        "unit_price": round(float(base_rate), 2),
        "service_group": category,
        "description": description.strip(),
        "pricing_mode": pricing_mode,
        "quantity_label": "Jobs" if pricing_mode == "flat" else "Copies / quantity",
        "upload_required": bool(upload_required),
        "checklist": [],
        "required_uploads": [],
        "optional_uploads": [],
    }
    save_service_catalog(catalog)
    return True, f"{normalized_name} created."


def _save_service_builder(service_name: str, checklist_text: str, required_text: str, optional_text: str, input_rows: list[dict]) -> tuple[bool, str]:
    catalog = get_service_catalog()
    if service_name not in catalog:
        return False, "Service not found."

    service = dict(catalog[service_name])
    service["checklist"] = _parse_line_items(checklist_text)
    required_uploads = _parse_line_items(required_text)
    optional_uploads = _parse_line_items(optional_text)
    custom_inputs = []
    for row in input_rows:
        label = str(row.get("Label", "")).strip()
        if not label:
            continue
        field_type = str(row.get("Type", "text")).strip().lower() or "text"
        field = {
            "label": label,
            "type": field_type,
            "required": bool(row.get("Required", False)),
        }
        options_text = str(row.get("Options", "")).strip()
        if options_text:
            field["options"] = [item.strip() for item in options_text.split(",") if item.strip()]
        custom_inputs.append(field)

    if required_uploads:
        service["required_uploads"] = required_uploads
    else:
        service.pop("required_uploads", None)
    if optional_uploads:
        service["optional_uploads"] = optional_uploads
    else:
        service.pop("optional_uploads", None)
    if custom_inputs:
        service["custom_inputs"] = custom_inputs
    else:
        service.pop("custom_inputs", None)

    catalog[service_name] = service
    save_service_catalog(catalog)
    return True, f"{service_name} builder updated."


def render_rates_page(is_manager: bool) -> None:
    render_page_intro(
        "Rates Control",
        "Manager-friendly pricing panel for per-unit print/xerox, photo presets, and service desk rates.",
        eyebrow="Manager Pricing",
    )

    if not is_manager:
        st.warning("Manager access is required to update rates.")
        return

    catalog = get_service_catalog()
    photo_sizes = get_photo_sizes()
    categories = sorted({config.get("service_group", "other") for config in catalog.values() if config.get("service_group")})

    render_metric_strip(
        [
            {"label": "Services", "value": len(catalog), "subvalue": "Live catalog entries"},
            {"label": "Categories", "value": len(categories), "subvalue": "Manager rate groups"},
            {"label": "Photo Sizes", "value": len(photo_sizes), "subvalue": "Preset photo outputs"},
        ]
    )

    service_tab, photo_tab = st.tabs(["Service Rates", "Photo Sizes"])

    with service_tab:
        top_cols = st.columns([1.05, 1.35], gap="large")
        selected_category = top_cols[0].selectbox(
            "Rate category",
            categories,
            format_func=lambda value: value.replace("_", " ").title(),
        )
        category_rows = _service_rows(selected_category)
        top_cols[1].markdown("### Current Rate List")
        top_cols[1].dataframe(_rate_list_rows(selected_category), use_container_width=True, hide_index=True)

        st.markdown("### Edit Category")
        st.caption("Keep the editor focused on one category at a time so managers can update rates faster.")
        service_rows = st.data_editor(
            category_rows,
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
            column_config={
                "Service Name": st.column_config.TextColumn(required=True),
                "Rate": st.column_config.NumberColumn(min_value=0.0, step=1.0, format="%.2f"),
                "Description": st.column_config.TextColumn(width="large"),
                "Pricing Mode": st.column_config.SelectboxColumn(options=["per_unit", "flat"]),
                "Quantity Label": st.column_config.TextColumn(),
                "Upload Required": st.column_config.CheckboxColumn(),
                "Print Style": st.column_config.CheckboxColumn(),
                "Custom Rate": st.column_config.CheckboxColumn(),
                "Options": st.column_config.TextColumn(help="Use Label:Rate | Label:Rate for service variants."),
                "Color Modes": st.column_config.TextColumn(help="Use Black & White:5 | Color:10 for file-wise print pricing."),
                "Required Uploads": st.column_config.TextColumn(help="Use Document 1 | Document 2 for required upload slots."),
                "Optional Uploads": st.column_config.TextColumn(help="Use Driving licence | ID proof for optional uploads."),
                "Custom Inputs": st.column_config.TextColumn(help="Use Label ; type ; required | Label ; select ; options=Yes,No"),
            },
            key=f"service_rates_editor_{selected_category}",
        )
        if st.button(f"Save {selected_category.replace('_', ' ').title()} Rates", type="primary", use_container_width=True):
            ok, message = _save_service_rows(service_rows, selected_category)
            if ok:
                st.success(message)
                st.rerun()
            st.error(message)

        st.markdown("### Plug-and-Play Service Builder")
        st.caption("Create a service, define document names, and control its upload/input flow without touching code.")
        create_cols = st.columns([1.2, 0.8, 0.8, 0.8, 0.8], gap="small")
        new_service_name = create_cols[0].text_input("New service name", placeholder="Passport Renewal")
        new_service_category = create_cols[1].selectbox(
            "Category",
            categories,
            format_func=lambda value: value.replace("_", " ").title(),
            key=f"new_service_category_{selected_category}",
        )
        new_service_rate = create_cols[2].number_input("Base rate", min_value=0.0, value=100.0, step=10.0)
        new_service_mode = create_cols[3].selectbox("Pricing mode", ["flat", "per_unit"])
        new_service_upload_required = create_cols[4].checkbox("Main upload", value=False, help="Turn this on if the service should use the normal file upload flow.")
        new_service_description = st.text_input("New service description", placeholder="Short explanation for customers and manager guidance.")
        if st.button("Create Service", type="primary", use_container_width=True):
            ok, message = _create_service(
                new_service_name,
                new_service_category,
                new_service_description,
                new_service_rate,
                new_service_mode,
                new_service_upload_required,
            )
            if ok:
                st.session_state[f"builder_service_{selected_category}"] = new_service_name.strip()
                st.success(message)
                st.rerun()
            st.error(message)

        category_service_names = [row["Service Name"] for row in category_rows]
        selected_service_name = st.selectbox("Builder service", category_service_names, key=f"builder_service_{selected_category}")
        selected_service = get_service_catalog()[selected_service_name]

        builder_cols = st.columns(2, gap="large")
        with builder_cols[0]:
            checklist_text = st.text_area(
                "Checklist / guidance",
                value="\n".join(selected_service.get("checklist", [])),
                height=180,
                help="One item per line. This is the guidance shown to the customer.",
                key=f"builder_checklist_{selected_service_name}",
            )
            required_text = st.text_area(
                "Required document names",
                value="\n".join(selected_service.get("required_uploads", [])),
                height=180,
                help="One document name per line. These become the customer-facing required upload boxes.",
                key=f"builder_required_uploads_{selected_service_name}",
            )
            optional_text = st.text_area(
                "Optional document names",
                value="\n".join(selected_service.get("optional_uploads", [])),
                height=120,
                help="One optional document per line. These appear in the optional upload area.",
                key=f"builder_optional_uploads_{selected_service_name}",
            )
        with builder_cols[1]:
            st.markdown("#### Dynamic Inputs")
            st.caption("Add the non-file fields this service needs, such as mobile number, amount, route, or application ID.")
            input_rows = st.data_editor(
                _service_input_rows(selected_service),
                use_container_width=True,
                num_rows="dynamic",
                hide_index=True,
                column_config={
                    "Label": st.column_config.TextColumn(required=True),
                    "Type": st.column_config.SelectboxColumn(options=["text", "textarea", "number", "date", "select"]),
                    "Required": st.column_config.CheckboxColumn(),
                    "Options": st.column_config.TextColumn(help="Only for select fields. Use Yes, No style values."),
                },
                key=f"builder_inputs_{selected_service_name}",
            )
            if st.button(f"Save {selected_service_name} Builder", type="primary", use_container_width=True):
                ok, message = _save_service_builder(selected_service_name, checklist_text, required_text, optional_text, input_rows)
                if ok:
                    st.success(message)
                    st.rerun()
                st.error(message)

    with photo_tab:
        preview_cols = st.columns([1, 1.2], gap="large")
        preview_cols[0].markdown("### Photo Size Control")
        preview_cols[0].caption("Manage passport, stamp, and sheet sizes here.")
        preview_cols[1].dataframe(
            [{"Photo Size": name, "Rate": float(config.get("unit_price", 0.0))} for name, config in photo_sizes.items()],
            use_container_width=True,
            hide_index=True,
        )

        photo_rows = st.data_editor(
            _photo_rows(),
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
            column_config={
                "Photo Size": st.column_config.TextColumn(required=True),
                "Rate": st.column_config.NumberColumn(min_value=0.0, step=1.0, format="%.2f"),
                "Width (mm)": st.column_config.NumberColumn(min_value=1.0, step=1.0, format="%.0f"),
                "Height (mm)": st.column_config.NumberColumn(min_value=1.0, step=1.0, format="%.0f"),
                "Description": st.column_config.TextColumn(),
            },
            key="photo_rates_editor",
        )
        if st.button("Save Photo Size Rates", type="primary", use_container_width=True):
            ok, message = _save_photo_rows(photo_rows)
            if ok:
                st.success(message)
                st.rerun()
            st.error(message)
