import streamlit as st
import imaplib
import email
from email.header import decode_header
from datetime import date
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
import os

# --- CONFIG ---
st.set_page_config(page_title="📧 Email Assistant", layout="wide")
st.title("📧 Email Assistant — Smart Summaries")
st.caption("✨ AI-powered daily email insights and summaries.")

# --- ENV SETUP ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- HELPERS ---

def validate_gmail_connection(email_user, app_password):
    """Validate IMAP login credentials."""
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_user, app_password)
        mail.logout()
        return True, "✅ Connection successful!"
    except imaplib.IMAP4.error as e:
        return False, f"❌ Login failed: {str(e)}"
    except Exception as e:
        return False, f"⚠️ Error: {str(e)}"

def extract_email_content(msg):
    """Extracts clean text from both plain and HTML email parts."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdisp = str(part.get("Content-Disposition"))
            if "attachment" in cdisp:
                continue
            if ctype == "text/plain":
                body += part.get_payload(decode=True).decode(errors="ignore")
            elif ctype == "text/html" and not body:
                html = part.get_payload(decode=True).decode(errors="ignore")
                soup = BeautifulSoup(html, "html.parser")
                body = soup.get_text()
    else:
        ctype = msg.get_content_type()
        if ctype == "text/plain":
            body = msg.get_payload(decode=True).decode(errors="ignore")
        elif ctype == "text/html":
            html = msg.get_payload(decode=True).decode(errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            body = soup.get_text()
    return " ".join(body.split()).strip()

def summarize_email(content):
    """Use LLM to summarize and extract insights."""
    prompt = f"""
    You are an AI email assistant.
    Analyze the following email and provide:
    - 1–2 sentence summary
    - Key action items (if any)
    - Tone (formal/informal/urgent/neutral)
    - Priority: 🔴 Critical / 🟠 Important / 🟢 Normal
    Email content:
    {content}
    """
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            temperature=0.4,
        )
        return response.output_text.strip()
    except Exception as e:
        return f"(AI summarization failed: {e})"

# --- SESSION ---
if "connected" not in st.session_state:
    st.session_state.connected = False
if "fetch_ready" not in st.session_state:
    st.session_state.fetch_ready = False

# --- UI: Gmail Connection ---
st.markdown("### 🔐 Connect Gmail")
with st.form("gmail_form"):
    email_user = st.text_input("Gmail Address", placeholder="you@gmail.com")
    app_password = st.text_input("App Password", type="password", placeholder="16-character app password")
    connect = st.form_submit_button("🔗 Connect")

if connect:
    if not email_user or not app_password:
        st.error("Please enter both email and app password.")
    else:
        with st.spinner("Connecting to Gmail..."):
            ok, msg = validate_gmail_connection(email_user, app_password)
        if ok:
            st.session_state.connected = True
            st.success(msg)
        else:
            st.session_state.connected = False
            st.error(msg)

# --- UI: Fetch Settings ---
if st.session_state.connected:
    st.markdown("### ⚙️ Fetch Settings")
    with st.expander("Set Filters"):
        start_date = st.date_input("Start Date", value=date.today())
        end_date = st.date_input("End Date", value=date.today())
        email_limit = st.slider("Number of emails", 1, 10, 3)
        unread_only = st.checkbox("Unread only", value=True)
    if st.button("📥 Fetch & Summarize Emails"):
        st.session_state.fetch_ready = True

# --- FETCH & SUMMARIZE ---
if st.session_state.fetch_ready:
    with st.spinner("Fetching and summarizing emails..."):
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(email_user, app_password)
            mail.select("inbox")

            criteria = '(UNSEEN)' if unread_only else 'ALL'
            _, msgs = mail.search(None, criteria)
            mail_ids = msgs[0].split()[-email_limit:]

            emails_data = []
            for num in reversed(mail_ids):
                _, data = mail.fetch(num, "(RFC822)")
                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, enc = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(enc or "utf-8", errors="ignore")
                        from_ = msg.get("From")
                        clean_text = extract_email_content(msg)
                        summary = summarize_email(clean_text)
                        emails_data.append({
                            "from": from_,
                            "subject": subject,
                            "summary": summary,
                        })

            mail.logout()
            st.success(f"✅ Summarized {len(emails_data)} emails")

            # Display nicely
            for e in emails_data:
                with st.container():
                    st.markdown(f"### 📬 {e['subject']}")
                    st.caption(f"**From:** {e['from']}")
                    st.write(e["summary"])
                    st.divider()

        except Exception as e:
            st.error(f"⚠️ Error fetching emails: {str(e)}")
