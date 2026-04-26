import streamlit as st

from components.service_form import (
    render_camera_capture,
    render_custom_inputs,
    render_document_uploader,
    render_other_documents_uploader,
    summarize_custom_inputs,
    validate_custom_inputs,
)
from components.ui import render_page_intro
from components.upload_sections import (
    DEFAULT_COLOR_MODE,
    PRINT_STYLE_OPTIONS,
    apply_upload_page_styles,
    build_file_overrides,
    render_jpg_to_pdf_fields,
    render_photo_service_fields,
    render_service_guidance_panel,
)
from services.catalog import get_service_catalog, get_service_groups
from services.upload_helpers import (
    estimate_upload_total,
    filter_service_names,
    multiplier_price,
    service_suggestions,
    service_variant_options,
    slab_price,
)
from services.upload_service import submit_uploads


NOTES_SERVICE_GROUPS = {"desk", "scan", "utility", "rental"}
LANGUAGE_OPTIONS = {"en": "English", "hi": "हिन्दी", "mr": "मराठी"}
UPLOAD_TRANSLATIONS = {
    "Create Service Order": {"hi": "सेवा ऑर्डर बनाएं", "mr": "सेवा ऑर्डर तयार करा"},
    "Search the required service, check the document checklist, and create one clean order batch. Only the fields needed for the chosen service are shown.": {
        "hi": "ज़रूरी सेवा खोजें, दस्तावेज़ सूची देखें और एक साफ़ ऑर्डर बैच बनाएं। केवल चुनी गई सेवा के लिए आवश्यक फ़ील्ड दिखेंगी।",
        "mr": "आवश्यक सेवा शोधा, कागदपत्रांची यादी तपासा आणि एक स्वच्छ ऑर्डर बॅच तयार करा. निवडलेल्या सेवेसाठी लागणारीच फील्ड्स दिसतील।",
    },
    "Customer Desk": {"hi": "ग्राहक डेस्क", "mr": "ग्राहक डेस्क"},
    "Language": {"hi": "भाषा", "mr": "भाषा"},
    "All services": {"hi": "सभी सेवाएं", "mr": "सर्व सेवा"},
    "Service category": {"hi": "सेवा श्रेणी", "mr": "सेवा विभाग"},
    "Search service": {"hi": "सेवा खोजें", "mr": "सेवा शोधा"},
    "Search Aadhaar, PAN, photo, rental...": {"hi": "आधार, पैन, फोटो, रेंटल खोजें...", "mr": "आधार, पॅन, फोटो, रेंटल शोधा..."},
    "No services matched that search. Try a different keyword.": {"hi": "इस खोज से कोई सेवा नहीं मिली। दूसरा शब्द आज़माएं।", "mr": "या शोधाशी जुळणारी सेवा सापडली नाही. दुसरा शब्द वापरून पहा."},
    "Quick picks": {"hi": "त्वरित विकल्प", "mr": "जलद पर्याय"},
    "Service": {"hi": "सेवा", "mr": "सेवा"},
    "Service option": {"hi": "सेवा विकल्प", "mr": "सेवा पर्याय"},
    "Customer name": {"hi": "ग्राहक का नाम", "mr": "ग्राहकाचे नाव"},
    "Enter customer name": {"hi": "ग्राहक का नाम लिखें", "mr": "ग्राहकाचे नाव लिहा"},
    "Phone number": {"hi": "फोन नंबर", "mr": "फोन नंबर"},
    "Enter customer phone number": {"hi": "ग्राहक का फोन नंबर लिखें", "mr": "ग्राहकाचा फोन नंबर लिहा"},
    "Phone number is required for every order.": {"hi": "हर ऑर्डर के लिए फोन नंबर आवश्यक है।", "mr": "प्रत्येक ऑर्डरसाठी फोन नंबर आवश्यक आहे."},
    "Required Document Uploads": {"hi": "ज़रूरी दस्तावेज़ अपलोड", "mr": "आवश्यक कागदपत्र अपलोड"},
    "Upload the exact documents this service needs.": {"hi": "इस सेवा के लिए आवश्यक सही दस्तावेज़ अपलोड करें।", "mr": "या सेवेसाठी लागणारी नेमकी कागदपत्रे अपलोड करा."},
    "Upload the matching document beside each checklist item wherever it is available.": {"hi": "जहाँ संभव हो, हर सूची आइटम के सामने संबंधित दस्तावेज़ अपलोड करें।", "mr": "जिथे शक्य असेल तिथे प्रत्येक यादी आयटमसमोर संबंधित कागदपत्र अपलोड करा."},
    "Optional Document Upload": {"hi": "वैकल्पिक दस्तावेज़ अपलोड", "mr": "ऐच्छिक कागदपत्र अपलोड"},
    "Only upload the extra supporting document if the customer wants to attach it now.": {"hi": "केवल तभी अतिरिक्त दस्तावेज़ अपलोड करें जब ग्राहक अभी जोड़ना चाहता हो।", "mr": "ग्राहकाला आत्ता जोडायचे असल्यासच अतिरिक्त कागदपत्र अपलोड करा."},
    "Choose file(s)": {"hi": "फ़ाइल चुनें", "mr": "फाइल निवडा"},
    "Attach supporting file(s) if available": {"hi": "यदि उपलब्ध हों तो सहायक फ़ाइलें जोड़ें", "mr": "उपलब्ध असल्यास सहाय्यक फाइल्स जोडा"},
    "Service rate": {"hi": "सेवा शुल्क", "mr": "सेवा दर"},
    "Use this when the desk needs to override the listed rate for this job.": {"hi": "जब इस काम के लिए सूचीबद्ध दर बदलनी हो तब इसका उपयोग करें।", "mr": "या कामासाठी सूचीतील दर बदलायचा असल्यास हे वापरा."},
    "Notes": {"hi": "नोट्स", "mr": "नोंदी"},
    "Add application details, page notes, payment notes, or pickup instructions.": {"hi": "आवेदन विवरण, पेज नोट्स, भुगतान नोट्स या पिकअप निर्देश जोड़ें।", "mr": "अर्ज तपशील, पेज नोट्स, पेमेंट नोट्स किंवा पिकअप सूचना जोडा."},
    "Estimated bill": {"hi": "अनुमानित बिल", "mr": "अंदाजित बिल"},
    "This is a desk service. A file is optional, so you can create the order even without attachments.": {"hi": "यह डेस्क सेवा है। फ़ाइल वैकल्पिक है, इसलिए बिना अटैचमेंट भी ऑर्डर बना सकते हैं।", "mr": "ही डेस्क सेवा आहे. फाइल ऐच्छिक आहे, त्यामुळे अटॅचमेंट नसतानाही ऑर्डर तयार करू शकता."},
    "Option": {"hi": "विकल्प", "mr": "पर्याय"},
    "Bill amount": {"hi": "बिल राशि", "mr": "बिल रक्कम"},
    "Print style": {"hi": "प्रिंट स्टाइल", "mr": "प्रिंट स्टाइल"},
    "Mode": {"hi": "मोड", "mr": "मोड"},
    "Create order": {"hi": "ऑर्डर बनाएं", "mr": "ऑर्डर तयार करा"},
    "Please enter the customer name.": {"hi": "कृपया ग्राहक का नाम लिखें।", "mr": "कृपया ग्राहकाचे नाव लिहा."},
    "Please enter the phone number.": {"hi": "कृपया फोन नंबर लिखें।", "mr": "कृपया फोन नंबर लिहा."},
    "Please upload at least one supporting file for this service.": {"hi": "इस सेवा के लिए कम से कम एक फ़ाइल अपलोड करें।", "mr": "या सेवेसाठी किमान एक फाइल अपलोड करा."},
    "Please upload at least one portrait photo.": {"hi": "कृपया कम से कम एक फोटो अपलोड करें।", "mr": "कृपया किमान एक फोटो अपलोड करा."},
    "Order created. Pickup code": {"hi": "ऑर्डर बन गया। पिकअप कोड", "mr": "ऑर्डर तयार झाला. पिकअप कोड"},
    "item(s) queued for": {"hi": "आइटम कतार में जोड़े गए", "mr": "आयटम रांगेत जोडले गेले"},
    "file(s) stored successfully in local Streamlit storage.": {"hi": "फ़ाइलें स्थानीय स्ट्रीमलिट स्टोरेज में सुरक्षित हो गईं।", "mr": "फाइल्स स्थानिक स्ट्रीमलिट स्टोरेजमध्ये जतन झाल्या."},
    "This service was saved as a counter request without file storage.": {"hi": "यह सेवा बिना फ़ाइल स्टोरेज के काउंटर अनुरोध के रूप में सहेजी गई।", "mr": "ही सेवा फाइल स्टोरेजशिवाय काउंटर विनंती म्हणून जतन झाली."},
    "Repeat customer detected. Added to priority follow-up.": {"hi": "दोबारा आने वाले ग्राहक का पता चला। प्राथमिक फॉलो-अप में जोड़ा गया।", "mr": "पुन्हा येणारा ग्राहक ओळखला. प्राधान्य फॉलो-अपमध्ये जोडला."},
    "Amount": {"hi": "राशि", "mr": "रक्कम"},
    "Units": {"hi": "इकाइयाँ", "mr": "युनिट्स"},
}


def _slab_price(amount: float, slab_size: float, slab_rate: float) -> float:
    return slab_price(amount, slab_size, slab_rate)


def _multiplier_price(units: float, unit_rate: float) -> float:
    return multiplier_price(units, unit_rate)


def _t(language: str, text: str) -> str:
    return UPLOAD_TRANSLATIONS.get(text, {}).get(language, text)


def render_upload_page(identity: dict) -> None:
    apply_upload_page_styles()
    top_bar = st.columns([4, 1])
    with top_bar[1]:
        language = st.selectbox(
            _t("en", "Language"),
            options=list(LANGUAGE_OPTIONS.keys()),
            index=list(LANGUAGE_OPTIONS.keys()).index(st.session_state.get("upload_language", "en")),
            format_func=lambda code: LANGUAGE_OPTIONS[code],
            key="upload_language_selector",
        )
    st.session_state.upload_language = language
    t = lambda text: _t(language, text)

    render_page_intro(
        t("Create Service Order"),
        t("Search the required service, check the document checklist, and create one clean order batch. Only the fields needed for the chosen service are shown."),
        eyebrow=t("Customer Desk"),
    )

    service_catalog = get_service_catalog()
    group_labels = {"all": t("All services")} | {group: group.replace("_", " ").title() for group in get_service_groups()}
    filter_cols = st.columns([0.9, 1.2])
    selected_group = filter_cols[0].selectbox(t("Service category"), list(group_labels.keys()), format_func=lambda key: group_labels[key])
    service_search = filter_cols[1].text_input(t("Search service"), placeholder=t("Search Aadhaar, PAN, photo, rental..."))
    filtered_service_names = filter_service_names(service_catalog, selected_group, service_search)

    if not filtered_service_names:
        st.warning(t("No services matched that search. Try a different keyword."))
        return

    suggestion_names = service_suggestions(service_catalog, filtered_service_names, service_search)
    if suggestion_names:
        quick_pick = st.segmented_control(
            t("Quick picks"),
            suggestion_names,
            default=st.session_state.get("selected_service_name") if st.session_state.get("selected_service_name") in suggestion_names else suggestion_names[0],
            selection_mode="single",
        )
        if quick_pick:
            st.session_state.selected_service_name = quick_pick

    default_service = st.session_state.get("selected_service_name")
    default_index = filtered_service_names.index(default_service) if default_service in filtered_service_names else 0
    layout_cols = st.columns([1.55, 1], gap="large")

    with layout_cols[0]:
        service_name = st.selectbox(t("Service"), filtered_service_names, index=default_index)
        st.session_state.selected_service_name = service_name
        service_config = service_catalog[service_name]
        checklist = service_config.get("checklist", [])
        required_upload_labels = service_config.get("required_uploads", [])
        optional_upload_labels = service_config.get("optional_uploads", [])
        custom_input_specs = service_config.get("custom_inputs", [])
        checklist_upload_mode = bool(checklist) and not service_config.get("upload_required", True) and not optional_upload_labels and not required_upload_labels
        optional_upload_mode = bool(optional_upload_labels)

        variant_by_name = service_variant_options(service_config)
        selected_variant_name = ""
        variant_config = {}
        if variant_by_name:
            selected_variant_name = st.selectbox(t("Service option"), list(variant_by_name.keys()))
            variant_config = variant_by_name[selected_variant_name]

        customer_name = st.text_input(
            t("Customer name"),
            value=identity["display_name"] if identity["display_name"] != "Guest Customer" else "",
            placeholder=t("Enter customer name"),
        )
        customer_phone = st.text_input(
            t("Phone number"),
            value="",
            placeholder=t("Enter customer phone number"),
            help=t("Phone number is required for every order."),
        )
        if customer_name.strip() and not identity["is_logged_in"]:
            st.session_state.guest_name = customer_name.strip()
            identity["display_name"] = customer_name.strip()

        custom_input_values = render_custom_inputs(custom_input_specs, service_name, t=t)

        upload_required = bool(service_config.get("upload_required", True))
        extra_uploads = []
        extra_labels = []
        if required_upload_labels:
            uploaded_files, checklist_file_labels = render_document_uploader(
                required_upload_labels,
                f"required_{service_name}",
                t("Required Document Uploads"),
                t("Upload the exact documents this service needs."),
                t=t,
            )
            extra_uploads, extra_labels = render_other_documents_uploader(f"required_{service_name}", t=t)
        elif checklist_upload_mode:
            uploaded_files, checklist_file_labels = render_document_uploader(
                checklist,
                f"checklist_{service_name}",
                t("Required Document Uploads"),
                t("Upload the matching document beside each checklist item wherever it is available."),
                t=t,
            )
            extra_uploads, extra_labels = render_other_documents_uploader(f"checklist_{service_name}", t=t)
        elif optional_upload_mode:
            uploaded_files, checklist_file_labels = render_document_uploader(
                optional_upload_labels,
                f"optional_{service_name}",
                t("Optional Document Upload"),
                t("Only upload the extra supporting document if the customer wants to attach it now."),
                optional=True,
                t=t,
            )
            extra_uploads, extra_labels = render_other_documents_uploader(f"optional_{service_name}", t=t)
        else:
            uploader_label = t("Choose file(s)") if upload_required else t("Attach supporting file(s) if available")
            uploaded_files = st.file_uploader(uploader_label, accept_multiple_files=True, type=None)
            captured_file = None
            camera_state_key = f"generic_camera_enabled_{service_name}"
            if st.button("📷", key=f"{camera_state_key}_open", help=t("Take document photo"), type="secondary"):
                st.session_state[camera_state_key] = True
            if st.session_state.get(camera_state_key, False):
                captured_file = st.camera_input(
                    t("Take document photo"),
                    key=f"generic_camera_{service_name}",
                    help=t("Use camera if the customer does not have the file ready."),
                )
            if captured_file is not None:
                uploaded_files = list(uploaded_files or [])
                uploaded_files.append(render_camera_capture(captured_file, f"{service_name}_camera.jpg", f"generic_camera_crop_{service_name}", t=t))
            checklist_file_labels = []

        if service_name == "Passport Photo Print":
            estimated_total, service_request, submission_uploads = render_photo_service_fields(service_name, service_config, uploaded_files, t=t, language=language)
        elif service_name == "JPG to PDF":
            estimated_total, service_request, submission_uploads = render_jpg_to_pdf_fields(service_name, service_config, uploaded_files, t=t)
        else:
            unit_price = float(variant_config.get("unit_price", service_config.get("unit_price", 0.0)))
            slab_amount = 0.0
            multiplier_units = 0.0
            slab_pricing = service_config.get("slab_pricing")
            multiplier_pricing = service_config.get("multiplier_pricing")

            if slab_pricing:
                slab_amount = st.number_input(
                    slab_pricing.get("input_label", "Amount"),
                    min_value=0.0,
                    value=float(slab_pricing.get("slab_size", 1000.0)),
                    step=100.0,
                )
                unit_price = slab_price(
                    slab_amount,
                    slab_pricing.get("slab_size", 1000.0),
                    slab_pricing.get("slab_rate", unit_price),
                )
            elif multiplier_pricing:
                multiplier_units = st.number_input(
                    multiplier_pricing.get("unit_label", "Units"),
                    min_value=float(multiplier_pricing.get("min_units", 1)),
                    value=float(multiplier_pricing.get("min_units", 1)),
                    step=1.0,
                )
                unit_price = multiplier_price(multiplier_units, multiplier_pricing.get("unit_rate", unit_price))

            if service_config.get("allow_custom_rate"):
                unit_price = st.number_input(
                    t("Service rate"),
                    min_value=0.0,
                    value=float(unit_price),
                    step=5.0,
                    help=t("Use this when the desk needs to override the listed rate for this job."),
                )

            st.caption(service_config.get("description", ""))

            quantity_label = service_config.get("quantity_label", "Copies / quantity")
            color_modes = service_config.get("color_modes", [])
            color_mode_rates = {item.get("label", ""): float(item.get("unit_price", unit_price)) for item in color_modes if item.get("label")}
            color_mode_options = list(color_mode_rates.keys())
            use_quantity_multiplier = bool(upload_required or service_config.get("pricing_mode") == "per_unit")
            order_cols = st.columns(2 if upload_required else 3)
            if use_quantity_multiplier and not upload_required:
                quantity = order_cols[0].number_input(quantity_label, min_value=1, max_value=500, value=1)
            else:
                quantity = 1
            urgent = False

            print_style = ""
            if service_config.get("show_print_style") and not upload_required:
                print_style = order_cols[1 if use_quantity_multiplier and not upload_required else 0].selectbox("Print style", PRINT_STYLE_OPTIONS)

            file_overrides = build_file_overrides(
                uploaded_files,
                quantity_label,
                bool(service_config.get("show_print_style")),
                color_mode_options=color_mode_options,
                t=t,
            ) if upload_required else []
            for override in file_overrides:
                override["unit_price"] = float(color_mode_rates.get(override.get("color_mode", ""), unit_price))

            notes = ""
            if service_config.get("service_group") in NOTES_SERVICE_GROUPS or service_config.get("allow_custom_rate"):
                notes = st.text_area(
                    t("Notes"),
                    placeholder=service_config.get(
                        "notes_placeholder",
                        t("Add application details, page notes, payment notes, or pickup instructions."),
                    ),
                )

            estimated_total = estimate_upload_total(unit_price, urgent, file_overrides, int(quantity))
            st.info(f"{t('Estimated bill')}: Rs. {estimated_total:.2f}")

            if not upload_required:
                st.caption(t("This is a desk service. A file is optional, so you can create the order even without attachments."))

            detail_lines = []
            if selected_variant_name:
                detail_lines.append(f"{t('Option')}: {selected_variant_name}")
            if slab_pricing:
                detail_lines.append(f"{t('Bill amount')}: Rs. {slab_amount:.2f}")
            if multiplier_pricing:
                detail_lines.append(f"{t(multiplier_pricing.get('unit_label', 'Units'))}: {multiplier_units:.2f}")
            if print_style:
                detail_lines.append(f"{t('Print style')}: {print_style}")
            if notes.strip():
                detail_lines.append(notes.strip())
            if color_mode_options and not upload_required:
                detail_lines.append(f"{t('Mode')}: {DEFAULT_COLOR_MODE}")
            detail_lines.extend(summarize_custom_inputs(custom_input_values))

            service_request = {
                "service_name": service_name,
                "copies": int(quantity),
                "urgent": urgent,
                "notes": " | ".join(detail_lines),
                "unit_price": float(unit_price),
                "service_group": service_config["service_group"],
                "pricing_mode": service_config.get("pricing_mode", "per_unit"),
                "service_meta": {
                    "source": "upload_desk",
                    "service_variant": selected_variant_name,
                    "print_style": print_style,
                    "color_mode": DEFAULT_COLOR_MODE if color_mode_options else "",
                    "quantity_label": quantity_label,
                    "upload_required": upload_required,
                    "bill_amount": slab_amount if slab_pricing else 0.0,
                    "service_units": multiplier_units if multiplier_pricing else 0.0,
                    "custom_inputs": custom_input_values,
                },
                "file_overrides": file_overrides,
                "file_labels": checklist_file_labels + extra_labels,
            }
            submission_uploads = (uploaded_files or []) + extra_uploads

        if st.button(t("Create order"), use_container_width=True, type="primary"):
            if not customer_name.strip():
                st.error(t("Please enter the customer name."))
                return
            if not customer_phone.strip():
                st.error(t("Please enter the phone number."))
                return
            custom_input_error = validate_custom_inputs(custom_input_specs, custom_input_values)
            if custom_input_error:
                st.error(custom_input_error)
                return
            if upload_required and not uploaded_files:
                st.error(t("Please upload at least one supporting file for this service."))
                return
            if service_name == "Passport Photo Print" and not submission_uploads:
                st.error(t("Please upload at least one portrait photo."))
                return

            result = submit_uploads(identity, customer_name.strip(), customer_phone.strip(), submission_uploads, service_request)

            st.success(f"{t('Order created. Pickup code')}: {result['pickup_code']}")
            st.info(
                f"{len(result['upload_ids'])} {t('item(s) queued for')} {service_request['service_name']}. {t('Estimated bill')}: Rs. {result['estimated_total']:.2f}"
            )
            if result["stored_file_count"]:
                st.caption(f"{result['stored_file_count']} {t('file(s) stored successfully in local Streamlit storage.')}")
            else:
                st.caption(t("This service was saved as a counter request without file storage."))
            if result["customer_tier"] == "regular":
                st.toast(t("Repeat customer detected. Added to priority follow-up."), icon="⭐")

    with layout_cols[1]:
        render_service_guidance_panel(
            service_catalog,
            filtered_service_names,
            service_name,
            service_config,
            selected_variant_name,
            service_search,
            t=t,
        )
