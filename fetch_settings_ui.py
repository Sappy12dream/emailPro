import streamlit as st
from datetime import date

def fetch_settings_ui():
    """Displays filters for fetching emails and returns user selections."""
    st.markdown("### ⚙️ Fetch Settings")
    with st.expander("Set Filters"):
        start_date = st.date_input("Start Date", value=date.today())
        end_date = st.date_input("End Date", value=date.today())
        email_limit = st.slider("Number of emails", 1, 10, 3)
        unread_only = st.checkbox("Unread only", value=True)
    fetch = st.button("📥 Fetch & Summarize Emails")
    return fetch, start_date, end_date, email_limit, unread_only
