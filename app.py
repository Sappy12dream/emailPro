import streamlit as st
import imaplib
import email
from email.header import decode_header
from datetime import date
from bs4 import BeautifulSoup

st.set_page_config(page_title="📧 Email Assistant — MVP")

st.title("📧 Email Assistant — MVP")
st.write("Connect your Gmail account to start fetching emails.")

# --- Gmail Credentials Form ---
with st.form("gmail_form"):
    st.subheader("🔐 Gmail IMAP Credentials")
    
    email_user = st.text_input("Gmail Address", placeholder="you@gmail.com")
    app_password = st.text_input("App Password", type="password", placeholder="16-character app password")
    
    submitted = st.form_submit_button("Connect")

# --- Validate IMAP Connection ---
def validate_gmail_connection(email_user, app_password):
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_user, app_password)
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
    if not email_user or not app_password:
        st.error("Please enter both email and app password.")
    else:
        with st.spinner("Connecting to Gmail..."):
            success, message = validate_gmail_connection(email_user, app_password)
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
    email_limit = st.number_input("Number of emails to fetch", min_value=1, max_value=50, value=5)
    unread_only = st.checkbox("Fetch unread emails only", value=True)

    fetch_clicked = st.button("📥 Fetch & Summarize Emails")

    if fetch_clicked:
        with st.spinner("Fetching emails..."):
            try:
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(email_user, app_password)
                mail.select("inbox")

                criteria = '(UNSEEN)' if unread_only else 'ALL'
                status, messages = mail.search(None, criteria)
                mail_ids = messages[0].split()
                mail_ids = mail_ids[-email_limit:]  # latest N emails

                emails_data = []

                for num in reversed(mail_ids):
                    res, msg = mail.fetch(num, "(RFC822)")
                    for response_part in msg:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            subject, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding or "utf-8", errors="ignore")
                            from_ = msg.get("From")
                            # Extract body
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    ctype = part.get_content_type()
                                    cdisp = str(part.get("Content-Disposition"))
                                    if ctype == "text/plain" and "attachment" not in cdisp:
                                        body = part.get_payload(decode=True).decode(errors="ignore")
                                        break
                            else:
                                body = msg.get_payload(decode=True).decode(errors="ignore")

                            soup = BeautifulSoup(body, "html.parser")
                            clean_text = soup.get_text().strip().replace("\n", " ")[:200]

                            # Mock summary (LLM will come later)
                            summary = f"Summary: This email from {from_} is about '{subject[:50]}'."
                            emails_data.append({
                                "from": from_,
                                "subject": subject,
                                "snippet": clean_text,
                                "summary": summary
                            })
                mail.logout()
                st.success(f"✅ Fetched {len(emails_data)} emails.")
                
                for e in emails_data:
                    with st.expander(f"📨 {e['subject']}"):
                        st.write(f"**From:** {e['from']}")
                        st.write(f"**Summary:** {e['summary']}")
                        st.caption(e['snippet'])
            except Exception as e:
                st.error(f"⚠️ Error fetching emails: {str(e)}")
