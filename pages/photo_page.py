import base64

import streamlit as st

from services.catalog import get_photo_size_options
from services.photo_layout import build_photo_sheet
from services.upload_service import submit_uploads


def render_photo_page(identity: dict) -> None:
    st.subheader("Photo Print Studio")
    st.caption("Create passport sheets and other photo-size layouts automatically, ready for cutting after print.")

    if not identity["is_logged_in"]:
        guest_name = st.text_input(
            "Guest name",
            value=st.session_state.get("guest_name", ""),
            placeholder="Enter a name or nickname",
            key="photo_guest_name",
        )
        if guest_name.strip():
            st.session_state.guest_name = guest_name.strip()
            identity["display_name"] = guest_name.strip()

    photo_options = get_photo_size_options()
    label_by_name = {name: label for name, label, _ in photo_options}
    config_by_name = {name: config for name, _, config in photo_options}

    size_name = st.selectbox(
        "Photo size preset",
        options=[name for name, _, _ in photo_options],
        format_func=lambda name: label_by_name[name],
    )
    size_config = config_by_name[size_name]

    info_cols = st.columns([1, 1, 2])
    info_cols[0].metric("Rate", f"Rs. {size_config['unit_price']:.2f}")
    info_cols[1].metric("Cut Size", f"{size_config['width_mm']} x {size_config['height_mm']} mm")
    info_cols[2].caption(size_config.get("description", ""))

    customer_name = st.text_input(
        "Customer name",
        value=identity["display_name"] if identity["display_name"] != "Guest Customer" else "",
        placeholder="Enter customer name",
        key="photo_customer_name",
    )
    uploaded_files = st.file_uploader(
        "Upload portrait photo(s)",
        accept_multiple_files=True,
        type=["jpg", "jpeg", "png", "webp"],
        key="photo_files",
    )

    form_cols = st.columns(2)
    photo_count = form_cols[0].number_input("Number of photos", min_value=1, max_value=200, value=8)
    finish = form_cols[1].selectbox(
        "Background / finish",
        ["Original", "White background", "Blue background", "Matte finish", "Glossy finish"],
    )
    customer_phone = st.text_input("Phone number", placeholder="Enter customer phone number", key="photo_customer_phone")
    notes = st.text_area("Extra notes", placeholder="Passport office, visa type, crop note, duplicate set...")

    if uploaded_files:
        try:
            preview_upload, preview_bytes, layout = build_photo_sheet(
                uploaded_files[0],
                size_name,
                size_config,
                int(photo_count),
                finish,
            )
            encoded = base64.b64encode(preview_bytes).decode("utf-8")
            st.markdown("#### Printable Sheet Preview")
            preview_cols = st.columns([2, 1])
            with preview_cols[0]:
                st.markdown(
                    f'<img src="data:image/jpeg;base64,{encoded}" '
                    f'style="width:100%;border:1px solid #ddd;border-radius:16px;background:white;" />',
                    unsafe_allow_html=True,
                )
            with preview_cols[1]:
                st.write(f"Sheet file: `{preview_upload.name}`")
                st.write(f"Copies on one sheet: **{layout['copies_rendered']}**")
                st.write(f"Grid: **{layout['columns']} x {layout['rows']}**")
                if int(photo_count) > layout["capacity"]:
                    st.warning(
                        f"One A4 sheet fits {layout['capacity']} copies. "
                        "Extra copies are trimmed to sheet capacity in the generated preview."
                    )
        except Exception as exc:
            st.error(f"Could not build the photo sheet preview: {exc}")

    if st.button("Create photo order", use_container_width=True, type="primary"):
        if not customer_name.strip():
            st.error("Please enter the customer name.")
            return
        if not uploaded_files:
            st.error("Please upload at least one photo file.")
            return

        try:
            generated = [
                build_photo_sheet(uploaded_file, size_name, size_config, int(photo_count), finish)
                for uploaded_file in uploaded_files
            ]
        except Exception as exc:
            st.error(f"Unable to generate photo sheet(s): {exc}")
            return

        generated_uploads = [item[0] for item in generated]

        service_request = {
            "service_name": f"Photo Print - {size_name}",
            "copies": int(photo_count),
            "urgent": False,
            "notes": f"Size: {size_name} | Finish: {finish} | {notes.strip()}".strip(),
            "unit_price": float(size_config["unit_price"]),
            "service_group": "photo",
            "service_meta": {
                "photo_size_name": size_name,
                "photo_width_mm": float(size_config["width_mm"]),
                "photo_height_mm": float(size_config["height_mm"]),
                "photo_finish": finish,
                "sheet_capacity": generated[0][2]["capacity"] if generated else 0,
                "copies_rendered": generated[0][2]["copies_rendered"] if generated else 0,
            },
        }
        if not customer_phone.strip():
            st.error("Please enter the phone number.")
            return

        result = submit_uploads(identity, customer_name.strip(), customer_phone.strip(), generated_uploads, service_request)

        st.success(f"Photo order created. Pickup code: {result['pickup_code']}")
        st.info(
            f"{len(result['upload_ids'])} printable sheet(s) queued for {label_by_name[size_name]}. "
            f"Estimated bill: Rs. {result['estimated_total']:.2f}"
        )
        if result["stored_file_count"]:
            st.caption(f"{result['stored_file_count']} printable sheet(s) saved in local storage.")
