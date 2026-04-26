import base64
from datetime import date
from io import BytesIO
from pathlib import Path
from dataclasses import dataclass

import streamlit as st
from PIL import Image

from custom_components.image_cropper import image_cropper
from services.catalog import get_photo_size_options
from services.photo_layout import build_single_photo_document


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
PHOTO_FINISH_OPTIONS = ["Original", "White background", "Blue background", "Matte finish", "Glossy finish"]


@dataclass
class PreparedUpload:
    name: str
    _content: bytes
    type: str

    @property
    def size(self) -> int:
        return len(self._content)

    def getvalue(self) -> bytes:
        return self._content


def _is_image_upload(uploaded) -> bool:
    content_type = getattr(uploaded, "type", "") or ""
    suffix = Path(getattr(uploaded, "name", "")).suffix.lower()
    return content_type.startswith("image/") or suffix in IMAGE_EXTENSIONS


def _is_photo_document_label(label: str) -> bool:
    normalized = str(label).strip().lower()
    return "photo" in normalized or "passport-size" in normalized or "passport size" in normalized


def prepare_camera_capture(captured, name: str = "camera_capture.jpg", crop_box: tuple[int, int, int, int] | None = None):
    if captured is None:
        return None
    safe_name = Path(name).with_suffix(".jpg").name
    if crop_box:
        image = Image.open(BytesIO(captured.getvalue())).convert("RGB")
        cropped = image.crop(crop_box)
        output = BytesIO()
        cropped.save(output, format="JPEG", quality=95, optimize=True)
        return PreparedUpload(safe_name, output.getvalue(), "image/jpeg")
    return PreparedUpload(safe_name, captured.getvalue(), getattr(captured, "type", "image/jpeg") or "image/jpeg")


def prepare_browser_camera_capture(camera_payload: dict | None, name: str = "camera_capture.jpg"):
    if camera_payload is not None and hasattr(camera_payload, "getvalue"):
        return prepare_camera_capture(camera_payload, name)
    if not camera_payload or not camera_payload.get("dataUrl"):
        return None

    try:
        header, encoded = camera_payload["dataUrl"].split(",", 1)
    except ValueError:
        return None

    mime_type = camera_payload.get("mimeType", "image/jpeg") or "image/jpeg"
    suffix = ".jpg" if "jpeg" in mime_type or "jpg" in mime_type else ".png"
    safe_name = Path(name).with_suffix(suffix).name
    return PreparedUpload(safe_name, base64.b64decode(encoded), mime_type)


def _upload_to_data_url(uploaded) -> str:
    mime_type = getattr(uploaded, "type", "image/jpeg") or "image/jpeg"
    encoded = base64.b64encode(uploaded.getvalue()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def render_image_crop_option(uploaded, key_prefix: str, label: str, t=lambda text: text):
    if uploaded is None or not _is_image_upload(uploaded):
        return uploaded

    crop_enabled = st.checkbox(
        t("Crop image"),
        key=f"{key_prefix}_crop_enabled",
        help=t("Drag the red rectangle over the image and apply crop before creating the order."),
    )
    if not crop_enabled:
        return uploaded

    crop_payload = image_cropper(
        key=f"{key_prefix}_drag_cropper",
        data_url=_upload_to_data_url(uploaded),
        label=label,
        height=480,
    )
    cropped = prepare_browser_camera_capture(crop_payload, f"{Path(uploaded.name).stem}_cropped.jpg")
    if cropped is not None:
        st.success(t("Crop applied. The cropped image will be saved with this order."))
        return cropped

    st.caption(t("Adjust the red crop box and press Apply crop. Until then, the original image is used."))
    return uploaded


def _camera_enabled(key: str) -> bool:
    is_open = bool(st.session_state.get(key, False))
    label = "X" if is_open else "📷"
    help_text = "Close camera" if is_open else "Open camera"
    st.markdown("<div class='camera-button-cell compact-camera-action'>", unsafe_allow_html=True)
    clicked = st.button(label, key=f"{key}_toggle", help=help_text, type="secondary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    if clicked:
        st.session_state[key] = not is_open
        st.rerun()
    return bool(st.session_state.get(key, False))


def render_browser_camera_capture(camera_payload: dict | None, name: str, key_prefix: str, t=lambda text: text):
    return prepare_browser_camera_capture(camera_payload, name)


def render_live_camera(label: str, key: str, t=lambda text: text):
    st.caption(t("Take a document photo. On mobile Chrome, choose the back camera if the browser asks."))
    return st.camera_input(label, key=key, label_visibility="collapsed")


def render_optional_notes(
    label: str,
    key_prefix: str,
    placeholder: str = "",
    button_label: str = "+ Add notes",
    t=lambda text: text,
) -> str:
    open_key = f"{key_prefix}_notes_open"
    if not st.session_state.get(open_key, False):
        if st.button(t(button_label), key=f"{open_key}_button", type="secondary"):
            st.session_state[open_key] = True
            st.rerun()
        return ""

    action_cols = st.columns([1, 0.18], vertical_alignment="bottom")
    with action_cols[0]:
        notes = st.text_area(
            t(label),
            placeholder=placeholder,
            key=f"{key_prefix}_notes",
        )
    with action_cols[1]:
        if st.button("✕", key=f"{open_key}_close", help=t("Close notes"), type="secondary"):
            st.session_state[open_key] = False
            st.rerun()
    return notes


def _encode_image_to_target(image: Image.Image, target_size_kb: int | None = None) -> bytes:
    quality_steps = [95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35]
    target_bytes = int(target_size_kb * 1024) if target_size_kb else 0
    best_bytes = b""

    for quality in quality_steps:
        output = BytesIO()
        image.save(output, format="JPEG", quality=quality, optimize=True)
        encoded = output.getvalue()
        best_bytes = encoded
        if target_bytes and len(encoded) <= target_bytes:
            return encoded

    return best_bytes


def prepare_uploaded_document(uploaded, convert_image_to_pdf: bool = False, target_size_kb: int | None = None):
    if uploaded is None or not _is_image_upload(uploaded):
        return uploaded

    image = Image.open(BytesIO(uploaded.getvalue())).convert("RGB")
    if convert_image_to_pdf:
        output = BytesIO()
        image.save(output, format="PDF", resolution=300)
        pdf_name = f"{Path(uploaded.name).stem}.pdf"
        return PreparedUpload(pdf_name, output.getvalue(), "application/pdf")

    if target_size_kb:
        jpg_name = f"{Path(uploaded.name).stem}.jpg"
        return PreparedUpload(jpg_name, _encode_image_to_target(image, target_size_kb), "image/jpeg")

    return uploaded


def render_document_uploader(
    upload_labels: list[str],
    key_prefix: str,
    title: str,
    caption: str,
    optional: bool = False,
    t=lambda text: text,
) -> tuple[list, list[str]]:
    if not upload_labels:
        return [], []

    st.markdown(f"### {title}")
    st.caption(caption)

    uploads = []
    labels = []
    for index, item in enumerate(upload_labels, start=1):
        with st.container(border=True):
            st.markdown("<div class='required-upload-card'>", unsafe_allow_html=True)
            st.markdown(f"**{item}**")
            st.caption(t("Optional attachment for this service.") if optional else t("Upload the matching proof for this item."))

            captured = None
            camera_state_key = f"{key_prefix}_camera_enabled_{index}"
            st.markdown("<div class='required-upload-actions'>", unsafe_allow_html=True)
            uploaded = st.file_uploader(
                f"{t('Upload')} {item}",
                key=f"{key_prefix}_doc_{index}",
                label_visibility="collapsed",
                accept_multiple_files=False,
                type=None,
            )
            camera_open = _camera_enabled(camera_state_key)
            st.markdown("</div>", unsafe_allow_html=True)
            if camera_open:
                captured = render_live_camera(
                    f"{t('Take photo')} {item}",
                    key=f"{key_prefix}_camera_{index}",
                    t=t,
                )
            if uploaded is None and captured is not None:
                uploaded = render_browser_camera_capture(captured, f"{item}_{index}.jpg", f"{key_prefix}_camera_crop_{index}", t=t)
            if uploaded is not None:
                convert_to_pdf = False
                target_size_kb = 0
                if _is_image_upload(uploaded):
                    uploaded = render_image_crop_option(
                        uploaded,
                        f"{key_prefix}_{index}_{Path(uploaded.name).stem}",
                        t("Crop image"),
                        t=t,
                    )
                    if _is_photo_document_label(item):
                        photo_options = get_photo_size_options()
                        label_by_name = {name: label for name, label, _ in photo_options}
                        config_by_name = {name: config for name, _, config in photo_options}
                        photo_cols = st.columns(3)
                        size_name = photo_cols[0].selectbox(
                            t("Photo size"),
                            options=[name for name, _, _ in photo_options],
                            format_func=lambda name: label_by_name[name],
                            key=f"{key_prefix}_photo_size_{index}",
                        )
                        finish = photo_cols[1].selectbox(
                            t("Background / finish"),
                            PHOTO_FINISH_OPTIONS,
                            key=f"{key_prefix}_photo_finish_{index}",
                        )
                        output_format = photo_cols[2].selectbox(
                            t("Output format"),
                            ["JPG", "PDF"],
                            key=f"{key_prefix}_photo_output_{index}",
                        )
                        resize_photo = False
                        if output_format == "JPG":
                            resize_photo = st.checkbox(
                                t("Resize / compress image"),
                                key=f"{key_prefix}_photo_resize_{index}",
                                help=t("Keep this off to preserve the generated photo file size."),
                            )
                        if output_format == "JPG" and resize_photo:
                            target_size_kb = int(
                                st.slider(
                                    t("Target size (KB)"),
                                    min_value=20,
                                    max_value=500,
                                    value=max(20, min(500, round(uploaded.size / 1024))),
                                    step=10,
                                    key=f"{key_prefix}_photo_target_size_{index}",
                                    help=t("Compress the processed photo before saving the order."),
                                )
                            )
                        prepared_upload = build_single_photo_document(
                            uploaded,
                            size_name,
                            config_by_name[size_name],
                            finish=finish,
                            output_format=output_format,
                            target_size_kb=target_size_kb or None,
                        )[0]
                    else:
                        control_cols = st.columns(2)
                        convert_to_pdf = control_cols[0].checkbox(
                            t("Convert image to PDF"),
                            key=f"{key_prefix}_convert_pdf_{index}",
                            help=t("If this proof is an image, store it as a PDF while creating the order."),
                        )
                        resize_image = False
                        if not convert_to_pdf:
                            resize_image = control_cols[1].checkbox(
                                t("Resize / compress image"),
                                key=f"{key_prefix}_resize_image_{index}",
                                help=t("Keep this off to store the original image size."),
                            )
                        if not convert_to_pdf and resize_image:
                            target_size_kb = int(
                                st.slider(
                                    t("Target size (KB)"),
                                    min_value=20,
                                    max_value=500,
                                    value=max(20, min(500, round(uploaded.size / 1024))),
                                    step=10,
                                    key=f"{key_prefix}_target_size_{index}",
                                    help=t("Compress the uploaded image before saving the order."),
                                )
                            )
                        prepared_upload = prepare_uploaded_document(uploaded, convert_to_pdf, target_size_kb or None)
                else:
                    prepared_upload = uploaded
                uploads.append(prepared_upload)
                labels.append(item)
                attached_name = getattr(prepared_upload, "name", uploaded.name)
                if convert_to_pdf and attached_name.lower().endswith(".pdf"):
                    st.caption(f"{t('Attached')}: {uploaded.name} -> {attached_name}")
                elif target_size_kb and attached_name.lower().endswith(".jpg"):
                    st.caption(f"{t('Attached')}: {uploaded.name} -> {attached_name} | {t('target')} {target_size_kb} KB")
                else:
                    st.caption(f"{t('Attached')}: {attached_name}")
            else:
                st.caption(t("No file attached") if optional else t("No file attached yet"))
            st.markdown("</div>", unsafe_allow_html=True)

    return uploads, labels


def render_other_documents_uploader(key_prefix: str, title: str = "Other Documents", t=lambda text: text) -> tuple[list, list[str]]:
    st.markdown(f"### {title}")
    st.caption(t("Upload any extra files that do not fit into the listed requirement boxes. These files will be added to the same order."))

    captured_other = None
    other_camera_state_key = f"{key_prefix}_other_camera_enabled"
    st.markdown("<div class='required-upload-actions'>", unsafe_allow_html=True)
    raw_uploads = st.file_uploader(
        t("Upload other documents"),
        key=f"{key_prefix}_other_docs",
        accept_multiple_files=True,
        type=None,
        label_visibility="collapsed",
    )
    other_camera_open = _camera_enabled(other_camera_state_key)
    st.markdown("</div>", unsafe_allow_html=True)
    if other_camera_open:
        captured_other = render_live_camera(
            t("Take photo for other document"),
            key=f"{key_prefix}_other_camera",
            t=t,
        )
    camera_upload = render_browser_camera_capture(captured_other, "other_document_camera.jpg", f"{key_prefix}_other_camera_crop", t=t)
    all_uploads = list(raw_uploads or [])
    if camera_upload is not None:
        all_uploads.append(camera_upload)

    uploads = []
    labels = []
    for index, uploaded in enumerate(all_uploads, start=1):
        with st.container(border=True):
            row = st.columns([1.2, 1])
            with row[0]:
                st.markdown(f"**{uploaded.name}**")
                label = st.text_input(
                    f"{t('Label for extra file')} #{index}",
                    value="",
                    placeholder=t("Other document, receipt, reference proof..."),
                    key=f"{key_prefix}_other_label_{index}_{uploaded.name}",
                )
            with row[1]:
                convert_to_pdf = False
                target_size_kb = 0
                if _is_image_upload(uploaded):
                    uploaded = render_image_crop_option(
                        uploaded,
                        f"{key_prefix}_other_{index}_{Path(uploaded.name).stem}",
                        t("Crop image"),
                        t=t,
                    )
                    convert_to_pdf = st.checkbox(
                        t("Convert image to PDF"),
                        key=f"{key_prefix}_other_convert_pdf_{index}",
                        help=t("If this extra file is an image, store it as a PDF while creating the order."),
                    )
                    resize_image = False
                    if not convert_to_pdf:
                        resize_image = st.checkbox(
                            t("Resize / compress image"),
                            key=f"{key_prefix}_other_resize_image_{index}",
                            help=t("Keep this off to store the original image size."),
                        )
                    if not convert_to_pdf and resize_image:
                        target_size_kb = int(
                            st.slider(
                                t("Target size (KB)"),
                                min_value=20,
                                max_value=500,
                                value=max(20, min(500, round(uploaded.size / 1024))),
                                step=10,
                                key=f"{key_prefix}_other_target_size_{index}",
                                help=t("Compress the uploaded image before saving the order."),
                            )
                        )

                prepared_upload = prepare_uploaded_document(uploaded, convert_to_pdf, target_size_kb or None)
                uploads.append(prepared_upload)
                labels.append(label.strip() or Path(uploaded.name).stem)
                attached_name = getattr(prepared_upload, "name", uploaded.name)
                if convert_to_pdf and attached_name.lower().endswith(".pdf"):
                    st.caption(f"{t('Prepared')}: {uploaded.name} -> {attached_name}")
                elif target_size_kb and attached_name.lower().endswith(".jpg"):
                    st.caption(f"{t('Prepared')}: {uploaded.name} -> {attached_name} | {t('target')} {target_size_kb} KB")
                else:
                    st.caption(f"{t('Prepared')}: {attached_name}")

    return uploads, labels


def render_custom_inputs(input_specs: list[dict], key_prefix: str, t=lambda text: text) -> dict:
    if not input_specs:
        return {}

    st.markdown(f"### {t('Service Details')}")
    st.caption(t("Only the inputs configured for this service are shown here."))

    values = {}
    for index, spec in enumerate(input_specs, start=1):
        label = spec.get("label", f"Field {index}")
        field_type = str(spec.get("type", "text")).strip().lower() or "text"
        placeholder = spec.get("placeholder", "")
        required = bool(spec.get("required", False))
        key = f"{key_prefix}_input_{index}_{label}"
        help_text = t("Required field") if required else None

        if field_type == "number":
            values[label] = st.number_input(
                label,
                min_value=float(spec.get("min", 0.0)),
                value=float(spec.get("default", spec.get("min", 0.0))),
                step=float(spec.get("step", 1.0)),
                help=help_text,
                key=key,
            )
        elif field_type == "textarea":
            values[label] = st.text_area(
                label,
                value=str(spec.get("default", "")),
                placeholder=placeholder,
                help=help_text,
                key=key,
            )
        elif field_type == "date":
            values[label] = st.date_input(
                label,
                value=spec.get("default", date.today()),
                help=help_text,
                key=key,
            )
        elif field_type == "select":
            options = spec.get("options", []) or ["Yes", "No"]
            default = spec.get("default", options[0])
            default_index = options.index(default) if default in options else 0
            values[label] = st.selectbox(
                label,
                options=options,
                index=default_index,
                help=help_text,
                key=key,
            )
        else:
            values[label] = st.text_input(
                label,
                value=str(spec.get("default", "")),
                placeholder=placeholder,
                help=help_text,
                key=key,
            )

    return values


def validate_custom_inputs(input_specs: list[dict], values: dict) -> str:
    for spec in input_specs or []:
        label = spec.get("label", "")
        if not label or not spec.get("required"):
            continue
        value = values.get(label)
        if value is None:
            return f"Please enter {label.lower()}."
        if isinstance(value, str) and not value.strip():
            return f"Please enter {label.lower()}."
    return ""


def summarize_custom_inputs(values: dict) -> list[str]:
    lines = []
    for label, value in (values or {}).items():
        if value in ("", None):
            continue
        if hasattr(value, "isoformat"):
            rendered = value.isoformat()
        else:
            rendered = str(value)
        lines.append(f"{label}: {rendered}")
    return lines
