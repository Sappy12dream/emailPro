from bs4 import BeautifulSoup
import imaplib

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
    try:
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition") or "")

                # skip attachments
                if "attachment" in content_disposition:
                    continue

                payload = part.get_payload(decode=True)
                if payload:
                    try:
                        text = payload.decode(errors="ignore")
                    except Exception:
                        text = str(payload)

                    if content_type == "text/plain":
                        body += text
                    elif content_type == "text/html" and not body.strip():
                        # Only use HTML if plain text missing
                        soup = BeautifulSoup(text, "html.parser")
                        body += soup.get_text(separator=" ", strip=True)
        else:
            content_type = msg.get_content_type()
            payload = msg.get_payload(decode=True)
            if payload:
                try:
                    text = payload.decode(errors="ignore")
                except Exception:
                    text = str(payload)

                if content_type == "text/plain":
                    body = text
                elif content_type == "text/html":
                    soup = BeautifulSoup(text, "html.parser")
                    body = soup.get_text(separator=" ", strip=True)
    except Exception as e:
        body = f"(Could not extract content: {e})"

    clean_text = " ".join(body.split()).strip()
    return clean_text or "(No content found)"


def safe_decode_header(header_value):
    """Safely decode email headers like Subject or From."""
    from email.header import decode_header
    if not header_value:
        return "(No Subject)"
    try:
        decoded, enc = decode_header(header_value)[0]
        if isinstance(decoded, bytes):
            return decoded.decode(enc or "utf-8", errors="ignore")
        return decoded
    except Exception:
        return str(header_value)
