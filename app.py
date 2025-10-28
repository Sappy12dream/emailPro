import streamlit as st
import imaplib
import email
from email.header import decode_header
from datetime import date
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
import os

# --- Load environment variables ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="📧 Email Assistant — LLM Enhanced")

st.title("📧 Email Assistant — Smart Summaries")
st.write("Now powered by LLM insights! Connect Gmail and get summaries + action items.")

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

# --- Session state ---
if "connected" not in st.session_state:
    st.session_state.connected = False

# --- Handle connection ---
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

# --- Next step ---
if st.session_state.connected:
    st.markdown("---")
    st.info("Connection verified! Choose your fetch settings.")
    next_clicked = st.button("➡️ Next: Choose Fetch Settings")

    if next_clicked:
        st.session_state.show_fetch_options = True
def extract_email_content(msg):
    """Extracts clean text content from both plain and HTML email parts."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if "attachment" in content_disposition:
                continue  # Skip attachments

            # Prefer plain text, fallback to HTML
            if content_type == "text/plain":
                body += part.get_payload(decode=True).decode(errors="ignore")
            elif content_type == "text/html" and not body:
                html = part.get_payload(decode=True).decode(errors="ignore")
                soup = BeautifulSoup(html, "html.parser")
                body = soup.get_text()
    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            body = msg.get_payload(decode=True).decode(errors="ignore")
        elif content_type == "text/html":
            html = msg.get_payload(decode=True).decode(errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            body = soup.get_text()

    body = " ".join(body.split())  # Clean whitespace
    return body.strip()

# --- Fetch Settings ---
if st.session_state.get("show_fetch_options", False):
    st.markdown("### 📅 Fetch Email Settings")
    start_date = st.date_input("Start Date", value=date.today())
    end_date = st.date_input("End Date", value=date.today())
    email_limit = st.number_input("Number of emails to fetch", min_value=1, max_value=10, value=3)
    unread_only = st.checkbox("Fetch unread emails only", value=True)

    fetch_clicked = st.button("📥 Fetch & Summarize with AI")

    if fetch_clicked:
        with st.spinner("Fetching and summarizing emails..."):
            try:
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(email_user, app_password)
                mail.select("inbox")

                criteria = '(UNSEEN)' if unread_only else 'ALL'
                status, messages = mail.search(None, criteria)
                mail_ids = messages[0].split()
                mail_ids = mail_ids[-email_limit:]  # latest emails

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
                            clean_text = extract_email_content(msg)


                            # --- AI Summarization ---
                            prompt = f"""
                            You are an AI email assistant.
                            Analyze the following email content and provide:
                            - A short summary (2 sentences)
                            - Any action items (if mentioned)
                            - The tone (formal/informal/urgent/neutral)
                            - Priority: 🔴 Critical / 🟠 Important / 🟢 Normal
                            Email content:
                            {clean_text}
                            """

                            try:
                                response = client.responses.create(
                                    model="gpt-4.1-mini",
                                    input=prompt,
                                    temperature=0.4,
                                )
                                summary_text = response.output_text.strip()
                            except Exception as e:
                                summary_text = f"(AI summarization failed: {e})"

                            emails_data.append({
                                "from": from_,
                                "subject": subject,
                                "summary": summary_text[:1500]
                            })

                mail.logout()
                st.success(f"✅ Fetched and summarized {len(emails_data)} emails.")

                for e in emails_data:
                    with st.expander(f"📨 {e['subject']}"):
                        st.write(f"**From:** {e['from']}")
                        st.markdown(e["summary"])

            except Exception as e:
                st.error(f"⚠️ Error fetching emails: {str(e)}")
