import streamlit as st
import imaplib
from datetime import date

st.set_page_config(page_title="📧 Email Assistant — MVP")

st.title("📧 Email Assistant — MVP")
st.write("Connect your Gmail account to start fetching emails.")

# --- Gmail Credentials Form ---
with st.form("gmail_form"):
    st.subheader("🔐 Gmail IMAP Credentials")
    
    email = st.text_input("Gmail Address", placeholder="you@gmail.com")
    app_password = st.text_input("App Password", type="password", placeholder="16-character app password")
    
    submitted = st.form_submit_button("Connect")

# --- Validate IMAP Connection ---
def validate_gmail_connection(email, app_password):
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email, app_password)
        mail.logout()
        return True, "✅ Connection successful!"
    except imaplib.IMAP4.error as e:
        return False, f"❌ Login failed: {str(e)}"
    except Exception as e:
        return False, f"⚠️ Error: {str(e)}"

# --- State variables ---
if "connected" not in st.session_state:
    st.session_state.connected = False

# --- Handle Submission ---
if submitted:
    if not email or not app_password:
        st.error("Please enter both email and app password.")
    else:
        with st.spinner("Connecting to Gmail..."):
            success, message = validate_gmail_connection(email, app_password)
        if success:
            st.session_state.connected = True
            st.success(message)
        else:
            st.session_state.connected = False
            st.error(message)

# --- Step 2: Show NEXT button if connected ---
if st.session_state.connected:
    st.markdown("---")
    st.info("Connection verified! You can now fetch emails.")
    next_clicked = st.button("➡️ Next: Choose Fetch Settings")

    if next_clicked:
        st.session_state.show_fetch_options = True

# --- Step 3: Fetch Options ---
if st.session_state.get("show_fetch_options", False):
    st.markdown("### 📅 Fetch Email Settings")
    start_date = st.date_input("Start Date", value=date.today())
    end_date = st.date_input("End Date", value=date.today())
    email_limit = st.number_input("Number of emails to fetch", min_value=1, max_value=100, value=10)
    unread_only = st.checkbox("Fetch unread emails only", value=True)

    st.success(f"Ready to fetch {email_limit} emails from {start_date} to {end_date}.")
