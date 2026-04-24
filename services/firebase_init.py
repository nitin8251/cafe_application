import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage


def get_firebase_app():
    if not firebase_admin._apps:
        firebase_config = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(
            cred,
            {"storageBucket": firebase_config["storage_bucket"]}
        )
    return firebase_admin.get_app()


def get_firestore():
    get_firebase_app()
    return firestore.client()


def get_bucket():
    get_firebase_app()
    return storage.bucket()