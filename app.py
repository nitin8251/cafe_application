import streamlit as st
from firebase_admin import firestore

from services.firebase_init import get_firebase_app


st.set_page_config(page_title="ANJLEE DIGITAL SERVICES", page_icon="print", layout="centered")
st.title("Firebase Test")

try:
    app = get_firebase_app()
except RuntimeError as exc:
    st.warning(str(exc))
    st.info("Add a [firebase] section in .streamlit/secrets.toml or Streamlit Cloud app secrets.")
    st.stop()

project_id = app.project_id or "unknown-project"
st.write(f"Connected project: {project_id}")

db = firestore.client(app=app)

if st.button("Test Firestore"):
    db.collection("test").add({"status": "working"})
    st.success("Firebase connected successfully")
