import streamlit as st
from utils import validate_gmail_connection

def gmail_connect_ui():
    """Handles Gmail connection form and returns connection state + credentials."""
    st.markdown("### 🔐 Connect Gmail")
    with st.form("gmail_form"):
        email_user = st.text_input("Gmail Address", placeholder="you@gmail.com")
        app_password = st.text_input("App Password", type="password", placeholder="16-character app password")
        connect = st.form_submit_button("🔗 Connect")

    if connect:
        if not email_user or not app_password:
            st.error("Please enter both email and app password.")
            return False, None, None
        with st.spinner("Connecting to Gmail..."):
            ok, msg = validate_gmail_connection(email_user, app_password)
        if ok:
            st.success(msg)
            return True, email_user, app_password
        else:
            st.error(msg)
            return False, None, None

    return st.session_state.get("connected", False), None, None
