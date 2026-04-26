import base64

import streamlit as st

from components.service_form import render_optional_notes
from services.catalog import get_photo_size_options
from services.photo_layout import build_images_to_pdf, build_photo_sheet
from services.upload_helpers import estimate_total


PRINT_STYLE_OPTIONS = ["Single side", "Double side", "Color mix"]
PHOTO_FINISH_OPTIONS = ["Original", "White background", "Blue background", "Matte finish", "Glossy finish"]
PHOTO_OUTPUT_OPTIONS = ["JPG", "PDF"]
PDF_CONVERSION_OPTIONS = ["Merge into one PDF", "Separate PDFs"]
DEFAULT_COLOR_MODE = "Black & White"


def apply_upload_page_styles() -> None:
    st.markdown(
        """
        <style>
            .upload-section-head {
                display: flex;
                align-items: center;
                gap: 0.7rem;
                margin: 0.35rem 0 0.18rem;
            }
            .upload-section-icon {
                width: 1rem;
                height: 1rem;
                border-radius: 999px;
                background:
                    radial-gradient(circle at 30% 30%, #fff7ed 0%, #f59e0b 42%, rgba(245,158,11,0.08) 43%),
                    linear-gradient(135deg, #3b2a1f 0%, #b45309 100%);
                box-shadow: 0 0 0 8px rgba(180, 83, 9, 0.10);
                flex: 0 0 auto;
            }
            .upload-section-title {
                color: #2f2219;
                font-size: 1.22rem;
                font-weight: 900;
                line-height: 1.1;
            }
            .upload-section-caption {
                color: #756457;
                font-size: 0.88rem;
                margin: 0 0 0.85rem 1.7rem;
            }
            .upload-file-card {
                background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(255,250,242,0.95) 100%);
                border: 1.4px solid rgba(64,45,31,0.32);
                border-radius: 20px;
                padding: 0.9rem 1rem 0.95rem;
                box-shadow: 0 10px 24px rgba(64,45,31,0.08);
                margin-bottom: 0.8rem;
            }
            .upload-file-topline {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 0.8rem;
                margin-bottom: 0.65rem;
            }
            .upload-file-name {
                color: #2f2219;
                font-size: 1rem;
                font-weight: 800;
                line-height: 1.25;
                word-break: break-word;
            }
            .upload-file-badge {
                background: #ffedd5;
                color: #92400e;
                border: 1px solid rgba(64,45,31,0.24);
                border-radius: 999px;
                padding: 0.22rem 0.58rem;
                font-size: 0.74rem;
                font-weight: 800;
                white-space: nowrap;
            }
            .upload-mini-label {
                color: #756457;
                font-size: 0.74rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.04em;
                margin-bottom: 0.26rem;
            }
            .upload-note-chip {
                display: inline-block;
                background: #ffedd5;
                color: #92400e;
                border: 1px solid rgba(64,45,31,0.24);
                border-radius: 999px;
                padding: 0.18rem 0.54rem;
                font-size: 0.74rem;
                font-weight: 800;
                margin-bottom: 0.35rem;
            }
            .service-guide-panel {
                position: sticky;
                top: 1rem;
            }
            .service-guide-panel,
            .service-guide-panel p,
            .service-guide-panel li,
            .service-guide-panel span,
            .service-guide-panel div,
            .service-guide-panel [data-testid="stMarkdownContainer"],
            .service-guide-panel [data-testid="stMarkdownContainer"] p,
            .service-guide-panel [data-testid="stCaptionContainer"] {
                color: #2f2219 !important;
            }
            .service-guide-panel [data-testid="stCaptionContainer"],
            .service-guide-panel small {
                color: #756457 !important;
            }
            .service-guide-panel [role="radiogroup"] label,
            .service-guide-panel [role="radiogroup"] label * {
                color: #2f2219 !important;
            }
            .service-guide-panel [data-testid="stRadio"] {
                background: rgba(255,255,255,0.72);
                border: 1.2px solid rgba(64,45,31,0.22);
                border-radius: 18px;
                padding: 0.4rem 0.55rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def translate_finish_options(language: str) -> list[str]:
    if language == "hi":
        return ["मूल", "सफेद बैकग्राउंड", "नीला बैकग्राउंड", "मैट फिनिश", "ग्लॉसी फिनिश"]
    if language == "mr":
        return ["मूळ", "पांढरी पार्श्वभूमी", "निळी पार्श्वभूमी", "मॅट फिनिश", "ग्लॉसी फिनिश"]
    return PHOTO_FINISH_OPTIONS


def render_upload_section_heading(title: str, caption: str) -> None:
    st.markdown(
        f"""
        <div class="upload-section-head">
            <div class="upload-section-icon"></div>
            <div class="upload-section-title">{title}</div>
        </div>
        <div class="upload-section-caption">{caption}</div>
        """,
        unsafe_allow_html=True,
    )


def build_file_overrides(
    uploaded_files: list,
    quantity_label: str,
    show_print_style: bool,
    color_mode_options: list[str] | None = None,
    t=lambda text: text,
) -> list[dict]:
    overrides = []
    if not uploaded_files:
        return overrides

    render_upload_section_heading(
        t("File-wise Settings"),
        t("Adjust each file neatly here. Copies, print side, and color mode stay grouped under the same order."),
    )

    print_style_map = {
        "Single": "Single side",
        "Double": "Double side",
        "Mix": "Color mix",
    }
    reverse_print_style_map = {value: key for key, value in print_style_map.items()}
    color_mode_map = {
        "B/W": "Black & White",
        "Color": "Color",
    }
    reverse_color_mode_map = {value: key for key, value in color_mode_map.items()}

    for index, uploaded_file in enumerate(uploaded_files, start=1):
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="upload-file-topline">
                    <div class="upload-file-name">{uploaded_file.name}</div>
                    <div class="upload-file-badge">File {index} | {round(uploaded_file.size / 1024, 2)} KB</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            controls = st.columns([1.2, 0.7, 1.05, 0.95], gap="small")
            controls[0].markdown(f"<div class='upload-mini-label'>{t('Document Label')}</div>", unsafe_allow_html=True)
            controls[1].markdown(f"<div class='upload-mini-label'>{t('Copies')}</div>", unsafe_allow_html=True)

            document_label = controls[0].text_input(
                f"Document label #{index}",
                value="",
                placeholder=t("Aadhaar card"),
                key=f"file_label_{index}_{uploaded_file.name}",
                label_visibility="collapsed",
            )
            copies = controls[1].number_input(
                f"{quantity_label} #{index}",
                min_value=1,
                max_value=500,
                value=1,
                key=f"file_copies_{index}_{uploaded_file.name}",
                label_visibility="collapsed",
            )

            if show_print_style:
                controls[2].markdown(f"<div class='upload-mini-label'>{t('Side')}</div>", unsafe_allow_html=True)
                print_style_key = controls[2].radio(
                    f"Print style #{index}",
                    list(print_style_map.keys()),
                    index=0,
                    key=f"file_print_style_{index}_{uploaded_file.name}",
                    horizontal=True,
                    label_visibility="collapsed",
                )
                print_style = print_style_map[print_style_key]
            else:
                print_style = ""

            if color_mode_options:
                controls[3].markdown(f"<div class='upload-mini-label'>{t('Mode')}</div>", unsafe_allow_html=True)
                radio_options = [reverse_color_mode_map.get(option, option) for option in color_mode_options]
                default_mode = reverse_color_mode_map.get(DEFAULT_COLOR_MODE, radio_options[0])
                color_mode_key = controls[3].radio(
                    f"Mode #{index}",
                    radio_options,
                    index=radio_options.index(default_mode) if default_mode in radio_options else 0,
                    key=f"file_color_mode_{index}_{uploaded_file.name}",
                    horizontal=True,
                    label_visibility="collapsed",
                )
                color_mode = color_mode_map.get(color_mode_key, color_mode_key)
            else:
                color_mode = ""

            note_parts = []
            if show_print_style:
                note_parts.append(f"{t('Side')}: {reverse_print_style_map.get(print_style, print_style)}")
            if color_mode:
                note_parts.append(f"{t('Mode')}: {reverse_color_mode_map.get(color_mode, color_mode)}")
            if note_parts:
                st.markdown(f"<div class='upload-note-chip'>{' | '.join(note_parts)}</div>", unsafe_allow_html=True)

        overrides.append(
            {
                "file_name": uploaded_file.name,
                "document_label": document_label,
                "copies": int(copies),
                "print_style": print_style,
                "color_mode": color_mode,
            }
        )
    return overrides


def build_document_labels(uploaded_files: list, key_prefix: str) -> list[str]:
    if not uploaded_files:
        return []

    st.markdown("### File Labels")
    st.caption("Give each file a useful name like Aadhaar card, PAN card, receipt, or marksheet. The stored file will use this label.")
    labels = []
    for index, uploaded_file in enumerate(uploaded_files, start=1):
        labels.append(
            st.text_input(
                f"Label for {uploaded_file.name}",
                value="",
                placeholder="Aadhaar card, passport photo, bill receipt...",
                key=f"{key_prefix}_label_{index}_{uploaded_file.name}",
            )
        )
    return labels


def render_service_guidance_panel(
    service_catalog: dict,
    filtered_service_names: list[str],
    service_name: str,
    service_config: dict,
    selected_variant_name: str,
    service_search: str,
    t=lambda text: text,
) -> str:
    with st.container(border=True):
        st.markdown("<div class='service-guide-panel'>", unsafe_allow_html=True)
        render_upload_section_heading(
            t("Service Guide"),
            t("Quick matches, document checklist, and service guidance stay here while the working form remains compact on the left."),
        )

        matches = filtered_service_names[:8]
        if matches:
            default_match_index = matches.index(service_name) if service_name in matches else 0
            clicked_service = st.radio(
                t("Matching services"),
                matches,
                index=default_match_index,
                label_visibility="collapsed",
                captions=[service_catalog[name].get("description", "") for name in matches],
            )
            if clicked_service != service_name:
                st.session_state.selected_service_name = clicked_service
                st.rerun()

        st.markdown(f"#### {service_name}")
        st.caption(service_config.get("description", ""))
        if service_search.strip():
            st.caption(f"{t('Search term')}: `{service_search.strip()}`")

        checklist = service_config.get("checklist", [])
        if checklist:
            st.markdown(f"##### {t('Required documents / guidance')}")
            for item in checklist:
                st.markdown(f"- {item}")

        variants = service_config.get("variants", [])
        if variants:
            st.markdown(f"##### {t('Available options')}")
            for variant in variants:
                st.caption(f"{variant.get('label', '')} - Rs. {float(variant.get('unit_price', 0.0)):.2f}")

        if selected_variant_name:
            st.info(f"{t('Selected option')}: {selected_variant_name}")

        required_upload_labels = service_config.get("required_uploads", [])
        optional_upload_labels = service_config.get("optional_uploads", [])
        checklist_upload_mode = bool(checklist) and not service_config.get("upload_required", True) and not optional_upload_labels and not required_upload_labels
        optional_upload_mode = bool(optional_upload_labels)
        if required_upload_labels:
            st.success(t("This service uses manager-configured required upload slots on the left."))
        elif checklist_upload_mode:
            st.success(t("Upload the required checklist documents from the left-side form."))
        elif optional_upload_mode:
            st.info(t("This service mainly uses booking inputs. Optional document upload is available on the left if needed."))
        elif service_config.get("upload_required", True):
            st.success(t("This service expects files or images."))
        else:
            st.info(t("This service can be created even without file upload."))
        st.markdown("</div>", unsafe_allow_html=True)

    return service_name


def render_photo_service_fields(service_name: str, service_config: dict, uploaded_files: list, t=lambda text: text, language: str = "en") -> tuple[float, dict, list]:
    photo_options = get_photo_size_options()
    label_by_name = {name: label for name, label, _ in photo_options}
    config_by_name = {name: config for name, _, config in photo_options}

    size_name = st.selectbox(
        t("Photo size preset"),
        options=[name for name, _, _ in photo_options],
        format_func=lambda name: label_by_name[name],
    )
    size_config = config_by_name[size_name]

    finish_cols = st.columns(2)
    photo_count = finish_cols[0].number_input(t("Number of photos"), min_value=1, max_value=200, value=8)
    finish_labels = translate_finish_options(language)
    finish_index = 0
    finish_display = finish_cols[1].selectbox(t("Background / finish"), finish_labels, index=finish_index)
    finish = PHOTO_FINISH_OPTIONS[finish_labels.index(finish_display)]

    caption_fields = st.multiselect(
        t("Photo footer fields"),
        [t("Name"), "DOB", "DOP"],
        placeholder=t("Choose footer items to print below each photo"),
        key=f"{service_name}_caption_fields",
    )
    caption = {"enabled": False, "name": "", "dob": "", "dop": ""}
    if caption_fields:
        caption_cols = st.columns(max(1, len(caption_fields)))
        caption["enabled"] = True
        field_column = 0
        if t("Name") in caption_fields:
            caption["name"] = caption_cols[field_column].text_input(t("Name on photo"), placeholder="NAME-XYZ")
            field_column += 1
        if "DOB" in caption_fields:
            caption["dob"] = caption_cols[field_column].text_input("DOB", placeholder="26/03/2001")
            field_column += 1
        if "DOP" in caption_fields:
            caption["dop"] = caption_cols[field_column].text_input("DOP", placeholder="26/03/2021")

    output_cols = st.columns(2)
    output_format = output_cols[0].selectbox(t("Download format"), PHOTO_OUTPUT_OPTIONS)
    output_cols[1].caption(t("JPG is better for smaller files. PDF is better for printing and sharing."))

    info_cols = st.columns([1, 1, 2])
    info_cols[0].metric(t("Rate"), f"Rs. {size_config['unit_price']:.2f}")
    info_cols[1].metric(t("Cut Size"), f"{size_config['width_mm']} x {size_config['height_mm']} mm")
    info_cols[2].caption(size_config.get("description", service_config.get("description", "")))

    generated_uploads = []
    generated_layout = {}
    if uploaded_files:
        try:
            preview_upload, preview_bytes, layout = build_photo_sheet(
                uploaded_files[0],
                size_name,
                size_config,
                int(photo_count),
                finish,
                output_format=output_format,
                caption=caption,
            )
            generated_layout = layout
            encoded = base64.b64encode(preview_bytes).decode("utf-8")
            st.markdown(f"#### {t('Printable Sheet Preview')}")
            preview_cols = st.columns([2, 1])
            with preview_cols[0]:
                st.markdown(
                    f'<img src="data:image/jpeg;base64,{encoded}" style="width:100%;border:1px solid #ddd;border-radius:16px;background:white;" />',
                    unsafe_allow_html=True,
                )
            with preview_cols[1]:
                st.write(f"{t('Sheet file')}: `{preview_upload.name}`")
                st.write(f"{t('Copies on one sheet')}: **{layout['copies_rendered']}**")
                st.write(f"{t('Grid')}: **{layout['columns']} x {layout['rows']}**")
                st.write(f"{t('Output')}: **{layout['output_format']}**")
                st.write(f"{t('Generated size')}: **{layout['generated_size_kb']} KB**")
                if int(photo_count) > layout["capacity"]:
                    st.warning(f"{t('One A4 sheet fits')} {layout['capacity']} {t('copies. Extra copies are trimmed to sheet capacity in the generated preview.')}")
        except Exception as exc:
            st.error(f"{t('Could not build the photo sheet preview')}: {exc}")

    service_request = {
        "service_name": f"{service_name} - {size_name}",
        "copies": int(photo_count),
        "urgent": False,
        "notes": f"Size: {size_name} | Finish: {finish}",
        "unit_price": float(size_config["unit_price"]),
        "service_group": "photo",
        "pricing_mode": "flat",
        "service_meta": {
            "source": "upload_desk",
            "photo_size_name": size_name,
            "photo_width_mm": float(size_config["width_mm"]),
            "photo_height_mm": float(size_config["height_mm"]),
            "photo_finish": finish,
            "output_format": output_format,
            "sheet_capacity": generated_layout.get("capacity", 0),
            "copies_rendered": generated_layout.get("copies_rendered", 0),
            "caption": caption,
        },
        "source_uploads": uploaded_files or [],
        "file_labels": [],
    }

    if uploaded_files:
        try:
            generated = [
                build_photo_sheet(
                    uploaded_file,
                    size_name,
                    size_config,
                    int(photo_count),
                    finish,
                    output_format=output_format,
                    caption=caption,
                )
                for uploaded_file in uploaded_files
            ]
            generated_uploads = [item[0] for item in generated]
            if generated:
                service_request["service_meta"]["sheet_capacity"] = generated[0][2]["capacity"]
                service_request["service_meta"]["copies_rendered"] = generated[0][2]["copies_rendered"]
                service_request["service_meta"]["generated_size_kb"] = generated[0][2]["generated_size_kb"]
        except Exception as exc:
            st.error(f"Unable to prepare photo sheet(s): {exc}")

    estimated_total = estimate_total(service_request["unit_price"], service_request["copies"], False)
    st.info(f"{t('Estimated bill')}: Rs. {estimated_total:.2f}")
    return estimated_total, service_request, generated_uploads


def render_jpg_to_pdf_fields(service_name: str, service_config: dict, uploaded_files: list, t=lambda text: text) -> tuple[float, dict, list]:
    conversion_mode = st.selectbox(t("PDF output"), PDF_CONVERSION_OPTIONS)
    target_size_kb = 0
    if uploaded_files:
        compress_images = st.checkbox(
            t("Compress images before PDF"),
            key="jpg_to_pdf_compress_images",
            help=t("Keep this off to use the original image quality."),
        )
        if compress_images:
            original_size_kb = max(20, min(1000, round(max(uploaded_file.size for uploaded_file in uploaded_files) / 1024)))
            target_size_kb = int(
                st.slider(
                    t("Target size per image (KB)"),
                    min_value=20,
                    max_value=1000,
                    value=original_size_kb,
                    step=10,
                    key="jpg_to_pdf_target_size_kb",
                    help=t("Each image is compressed before being added to the PDF. Final PDF size can be slightly larger."),
                )
            )
    notes = render_optional_notes(
        "Conversion notes",
        "jpg_to_pdf_conversion",
        placeholder=service_config.get("notes_placeholder", t("Add conversion notes...")),
        t=t,
    )
    generated_uploads = []
    file_labels = build_document_labels(uploaded_files, "jpg_to_pdf")

    if uploaded_files:
        try:
            if conversion_mode == "Merge into one PDF":
                generated_upload, preview_bytes, summary = build_images_to_pdf(uploaded_files, target_size_kb or None)
                generated_uploads = [generated_upload]
            else:
                separate_items = [build_images_to_pdf([uploaded_file], target_size_kb or None) for uploaded_file in uploaded_files]
                generated_uploads = [item[0] for item in separate_items]
                preview_bytes = separate_items[0][1]
                summary = {
                    "page_count": len(uploaded_files),
                    "generated_size_kb": round(sum(item[2]["generated_size_kb"] for item in separate_items), 2),
                    "generated_files": len(separate_items),
                    "target_size_kb": target_size_kb or 0,
                }
            encoded = base64.b64encode(preview_bytes).decode("utf-8")
            preview_cols = st.columns([2, 1])
            with preview_cols[0]:
                st.markdown(
                    f'<img src="data:image/jpeg;base64,{encoded}" style="width:100%;border:1px solid #ddd;border-radius:16px;background:white;" />',
                    unsafe_allow_html=True,
                )
            with preview_cols[1]:
                if conversion_mode == "Merge into one PDF":
                    st.write(f"{t('Output file')}: `{generated_uploads[0].name}`")
                else:
                    st.write(f"{t('Output files')}: **{summary['generated_files']} PDFs**")
                st.write(f"{t('Pages')}: **{summary['page_count']}**")
                st.write(f"{t('Generated size')}: **{summary['generated_size_kb']} KB**")
                if target_size_kb:
                    st.write(f"{t('Target per image')}: **{target_size_kb} KB**")
        except Exception as exc:
            st.error(f"{t('Unable to prepare the PDF file')}: {exc}")

    service_request = {
        "service_name": service_name,
        "copies": 1,
        "urgent": False,
        "notes": notes.strip(),
        "unit_price": float(service_config.get("unit_price", 0.0)),
        "service_group": service_config["service_group"],
        "pricing_mode": "flat",
        "service_meta": {
            "source": "upload_desk",
            "conversion_type": "jpg_to_pdf",
            "conversion_mode": "merge" if conversion_mode == "Merge into one PDF" else "separate",
            "page_count": len(uploaded_files or []),
            "target_size_kb": target_size_kb,
        },
        "file_labels": file_labels,
    }
    estimated_total = estimate_total(service_request["unit_price"], 1, False)
    st.info(f"{t('Estimated bill')}: Rs. {estimated_total:.2f}")
    return estimated_total, service_request, generated_uploads
