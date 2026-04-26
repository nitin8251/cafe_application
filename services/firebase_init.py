import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore


def get_firebase_app():
    if not firebase_admin._apps:
        if "firebase" not in st.secrets:
            raise RuntimeError("Firebase secrets are not configured for this app yet.")

        firebase_config = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
    return firebase_admin.get_app()


def get_firestore():
    get_firebase_app()
    return firestore.client()
