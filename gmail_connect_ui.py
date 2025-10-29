import streamlit as st
from utils import validate_gmail_connection
import logging

def gmail_connect_ui():
    """UI block for Gmail connection with persistent state."""
    st.markdown("### 🔐 Connect Gmail")

    # Load from session state if available
    email_user = st.session_state.get("email_user", "")
    app_password = st.session_state.get("app_password", "")

    with st.form("gmail_form"):
        email_user = st.text_input("Gmail Address", value=email_user, placeholder="you@gmail.com")
        app_password = st.text_input("App Password", value=app_password, type="password", placeholder="16-character app password")
        connect = st.form_submit_button("🔗 Connect")

    if connect:
        if not email_user or not app_password:
            st.error("Please enter both email and app password.")
            logging.warning("User tried to connect without credentials.")
            return False, None, None

        with st.spinner("Connecting to Gmail..."):
            ok, msg = validate_gmail_connection(email_user, app_password)
        if ok:
            st.session_state.email_user = email_user
            st.session_state.app_password = app_password
            st.success(msg)
            logging.info(f"✅ Gmail connection successful for {email_user}")
            return True, email_user, app_password
        else:
            st.error(msg)
            logging.error(f"❌ Gmail connection failed for {email_user}: {msg}")
            return False, None, None

    # If already connected before, persist state
    if "email_user" in st.session_state and "app_password" in st.session_state:
        logging.info(f"🔁 Reusing previous Gmail connection for {st.session_state.email_user}")
        return True, st.session_state.email_user, st.session_state.app_password

    return False, None, None
