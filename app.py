from uuid import uuid4

import streamlit as st

from components.ui import apply_global_styles, render_shell_banner, render_workspace_nav
from pages.dashboard_page import render_dashboard_page
from pages.manager_page import render_manager_page
from pages.rates_page import render_rates_page
from pages.status_page import render_status_page
from pages.upload_page import render_upload_page
from services.firebase_init import get_firebase_app


APP_TITLE = "ANJLEE DIGITAL SERVICES"
WORKSPACE_CAPTIONS = {
    "Upload": "Create new customer orders, guided document requests, and counter-ready upload batches.",
    "Track Status": "Check pickup codes quickly without exposing the full operations desk.",
    "Manager": "Operate the live queue, completed work, print actions, and retention tasks.",
    "Rates": "Manage pricing, service builder fields, and photo size presets from one place.",
    "Dashboard": "Review revenue, queue pressure, service mix, and repeat-customer movement.",
}


def get_current_identity() -> dict:
    user_info = st.user.to_dict() if hasattr(st.user, "to_dict") else {}
    is_logged_in = bool(user_info.get("is_logged_in"))

    if is_logged_in:
        email = (user_info.get("email") or "").strip().lower()
        display_name = user_info.get("name") or user_info.get("given_name") or (email.split("@")[0] if email else "Customer")
        return {
            "identity_mode": "google",
            "is_logged_in": True,
            "email": email,
            "display_name": display_name,
            "user_id": f"user_{email or uuid4().hex}",
        }

    if "guest_id" not in st.session_state:
        st.session_state.guest_id = f"guest_{uuid4().hex[:10]}"

    guest_name = st.session_state.get("guest_name", "Guest Customer")
    return {
        "identity_mode": "guest",
        "is_logged_in": False,
        "email": "",
        "display_name": guest_name,
        "user_id": st.session_state.guest_id,
    }


def get_manager_settings() -> dict:
    if "manager" not in st.secrets:
        return {"allowed_emails": [], "pin": str(st.secrets.get("manager_pin", "")).strip()}

    manager_config = dict(st.secrets["manager"])
    allowed_emails = manager_config.get("allowed_emails", [])
    if isinstance(allowed_emails, str):
        allowed_emails = [allowed_emails]
    manager_config["allowed_emails"] = [email.strip().lower() for email in allowed_emails]
    manager_config["pin"] = str(manager_config.get("pin") or st.secrets.get("manager_pin", "")).strip()
    return manager_config


def render_auth_panel(identity: dict, manager_settings: dict) -> tuple[bool, dict]:
    with st.sidebar:
        st.title(APP_TITLE)
        st.caption("Fast counter workspace for services, print orders, delivery tracking, and reporting.")

        if identity["is_logged_in"]:
            st.success(f"Signed in as {identity['display_name']}")
            if identity["email"]:
                st.caption(identity["email"])
            if st.button("Logout", use_container_width=True):
                st.logout()
        else:
            st.info(f"Guest mode active: {identity['user_id']}")
            if st.button("Continue with Google", use_container_width=True):
                try:
                    st.login("google")
                except Exception:
                    st.warning("Google login is not configured yet. You can continue as guest.")

        st.divider()
        st.markdown(
            """
            <div class="sidebar-panel">
                <div class="sidebar-panel-title">Manager Access</div>
                <div class="sidebar-panel-caption">
                    Unlock operations, rates, and reporting with an allowed Google account or the manager PIN.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        manager_email_ok = bool(identity["email"]) and identity["email"] in manager_settings["allowed_emails"]
        manager_override = st.session_state.get("manager_override", False)
        pin_value = manager_settings["pin"]

        if not manager_email_ok:
            entered_pin = st.text_input("Manager PIN", type="password", key="manager_pin", placeholder="Enter manager PIN")
            if st.button("Unlock Manager", use_container_width=True):
                entered_pin = str(entered_pin).strip()
                if not pin_value:
                    st.session_state.manager_override = False
                    st.error("Manager PIN is not configured in Streamlit secrets. Add [manager] pin = \"your-pin\".")
                elif not entered_pin:
                    st.session_state.manager_override = False
                    st.error("Please enter the manager PIN.")
                elif entered_pin == pin_value:
                    st.session_state.manager_override = True
                    manager_override = True
                    st.success("Manager unlocked.")
                else:
                    st.session_state.manager_override = False
                    manager_override = False
                    st.error("Incorrect manager PIN.")

        is_manager = manager_email_ok or manager_override
        if is_manager:
            st.success("Manager mode enabled")
        else:
            st.caption("Manager pages require an allowed Google account or the manager PIN.")

        manager_identity = {
            "name": identity["display_name"],
            "email": identity["email"],
            "is_manager": is_manager,
        }

    return is_manager, manager_identity


st.set_page_config(page_title=APP_TITLE, page_icon="🖨️", layout="wide")
apply_global_styles()

try:
    get_firebase_app()
except RuntimeError as exc:
    st.warning(str(exc))
    st.info("Add Firebase and optional manager settings to .streamlit/secrets.toml before running the full app.")
    st.stop()

identity = get_current_identity()
manager_settings = get_manager_settings()
is_manager, manager_identity = render_auth_panel(identity, manager_settings)

render_shell_banner(APP_TITLE, identity, is_manager)

page = render_workspace_nav(
    ["Upload", "Track Status", "Manager", "Rates", "Dashboard"],
    default=st.session_state.get("active_workspace", "Upload"),
    captions=WORKSPACE_CAPTIONS,
)
st.session_state.active_workspace = page

if page == "Upload":
    render_upload_page(identity)
elif page == "Track Status":
    render_status_page(identity)
elif page == "Manager":
    render_manager_page(identity, manager_identity, is_manager)
elif page == "Rates":
    render_rates_page(is_manager)
else:
    render_dashboard_page(identity, is_manager)
