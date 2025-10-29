import streamlit as st
import imaplib
import email
import logging
from email.header import decode_header
from summarizer import summarize_email
from utils import extract_email_content
from gmail_connect_ui import gmail_connect_ui
from fetch_settings_ui import fetch_settings_ui
from display_emails_ui import display_emails_ui

# --- LOGGING CONFIG ---
logging.basicConfig(
    filename="email_app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(funcName)s | %(message)s"
)
# Stream to console too
logging.getLogger().addHandler(logging.StreamHandler())

# --- PAGE CONFIG ---
st.set_page_config(page_title="📧 Email Assistant", layout="wide")
st.title("📧 Email Assistant — Smart Summaries")
st.caption("✨ Modular AI-powered Gmail summarizer with LLM insights.")

# --- STATE INIT ---
st.session_state.setdefault("connected", False)
st.session_state.setdefault("fetch_ready", False)
st.session_state.setdefault("emails_data", None)

# --- STEP 1: GMAIL LOGIN ---
logging.info("Starting Gmail login UI...")
connected, email_user, app_password = gmail_connect_ui()

if connected:
    logging.info(f"✅ Gmail connection established for user: {email_user}")
    st.session_state.connected = True
else:
    logging.info("User not connected yet or login failed.")

# --- STEP 2: FETCH SETTINGS ---
if st.session_state.connected:
    logging.info("Rendering fetch settings UI...")
    fetch, start_date, end_date, email_limit, unread_only = fetch_settings_ui()

    # Use persistent flag to trigger fetching
    if fetch:
        logging.info(
            f"Fetch triggered manually: unread_only={unread_only}, limit={email_limit}, "
            f"start_date={start_date}, end_date={end_date}"
        )
        st.session_state.fetch_triggered = True
        st.session_state.fetch_params = {
            "start_date": start_date,
            "end_date": end_date,
            "email_limit": email_limit,
            "unread_only": unread_only,
        }

# --- STEP 3: FETCH & SUMMARIZE ---
if st.session_state.get("fetch_triggered", False):
    params = st.session_state.get("fetch_params", {})
    start_date = params.get("start_date")
    end_date = params.get("end_date")
    email_limit = params.get("email_limit", 3)
    unread_only = params.get("unread_only", True)

    with st.spinner("📬 Fetching and summarizing emails..."):
        try:
            logging.info("Connecting to Gmail IMAP...")
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(email_user, app_password)
            mail.select("inbox")
            logging.info("IMAP connection successful. Fetching emails...")

            criteria = '(UNSEEN)' if unread_only else 'ALL'
            _, msgs = mail.search(None, criteria)
            mail_ids = msgs[0].split()[-email_limit:]
            logging.info(f"Found {len(mail_ids)} emails to process.")

            emails_data = []
            for i, num in enumerate(reversed(mail_ids), 1):
                logging.info(f"Fetching email {i}/{len(mail_ids)} (ID: {num.decode()})")
                _, data = mail.fetch(num, "(RFC822)")

                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject_header = msg.get("Subject")
                        try:
                            subject, enc = decode_header(subject_header or "")[0]
                            if isinstance(subject, bytes):
                                subject = subject.decode(enc or "utf-8", errors="ignore")
                        except Exception as e:
                            logging.warning(f"Subject decode error: {e}")
                            subject = "(Decode Error)"
                        from_ = msg.get("From") or "(Unknown Sender)"
                        date_ = msg.get("Date") or "(Unknown Date)"
                        logging.info(f"📨 From: {from_} | Subject: {subject}")

                        clean_text = extract_email_content(msg)
                        logging.info(f"Extracted content length: {len(clean_text)}")

                        analysis = summarize_email(clean_text)

                        emails_data.append({
                            "from": from_,
                            "subject": subject or "(No Subject)",
                            "date": date_,
                            "body": clean_text or "(No content)",
                            "summary": analysis.get("summary"),
                            "actions": analysis.get("actions", []),
                            "tone": analysis.get("tone", "neutral"),
                            "priority": analysis.get("priority", "🟢 Normal"),
                            "category": analysis.get("category", "info"),
                        })

            mail.logout()
            st.session_state.emails_data = emails_data
            logging.info(f"✅ Successfully summarized {len(emails_data)} emails.")
            # st.success(f"✅ Summarized {len(emails_data)} emails")

        except Exception as e:
            logging.exception("❌ Error during email fetch/summarization.")
            st.error(f"⚠️ Error fetching emails: {e}")

        finally:
            # Reset fetch trigger after processing
            st.session_state.fetch_triggered = False


# --- STEP 4: DISPLAY RESULTS ---
if st.session_state.get("emails_data"):
    logging.info("Displaying summarized emails in UI.")
    display_emails_ui(st.session_state.emails_data)
