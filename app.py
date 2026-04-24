import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
st.write(st.secrets["firebase"]["project_id"])
st.write(st.secrets["firebase"]["client_email"])
st.title("Firebase Test")

if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

if st.button("Test Firestore"):
    db.collection("test").add({"status": "working"})
    st.success("🔥 Connected successfully")

# import streamlit as st
# import firebase_admin
# from firebase_admin import credentials, firestore

# if not firebase_admin._apps:
#     cred = credentials.Certificate(dict(st.secrets["firebase"]))
#     firebase_admin.initialize_app(cred)

# db = firestore.client()

# st.title("Firebase test")

# if st.button("Test Firestore"):
#     db.collection("test").add({"status": "working"})
#     st.success("Firestore connected")

# # import streamlit as st
# # from pages.upload_page import render_upload_page
# # from pages.manager_page import render_manager_page
# # from pages.dashboard_page import render_dashboard_page

# # st.set_page_config(page_title="ANJLEE DIGITAL SERVICES", page_icon="🖨️", layout="centered")

# # page = st.segmented_control("Menu", ["Upload", "Manager", "Dashboard"], default="Upload")

# # if page == "Upload":
# #     render_upload_page()
# # elif page == "Manager":
# #     render_manager_page()
# # else:
# #     render_dashboard_page()