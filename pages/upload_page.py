import streamlit as st
from services.upload_service import upload_file_to_firebase


def render_upload_page():
    st.title("Upload your files")

    with st.form("upload_form", clear_on_submit=True):
        customer_name = st.text_input("Your name")
        uploaded_files = st.file_uploader("Choose file(s)", accept_multiple_files=True)
        submitted = st.form_submit_button("Submit Files", use_container_width=True)

        if submitted:
            if not customer_name.strip():
                st.error("Please enter your name.")
                return
            if not uploaded_files:
                st.error("Please choose at least one file.")
                return

            for uploaded_file in uploaded_files:
                upload_id, doc = upload_file_to_firebase(customer_name, uploaded_file)
            st.success(f"Uploaded {len(uploaded_files)} file(s) successfully.")