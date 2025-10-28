import streamlit as st
import imaplib

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

# --- Handle Submission ---
if submitted:
    if not email or not app_password:
        st.error("Please enter both email and app password.")
    else:
        with st.spinner("Connecting to Gmail..."):
            success, message = validate_gmail_connection(email, app_password)
        if success:
            st.success(message)
        else:
            st.error(message)
