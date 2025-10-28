# display_emails_ui.py
import streamlit as st

def display_emails_ui(emails_data):
    """Display summarized emails in Streamlit."""
    if not emails_data:
        st.info("No emails found in the selected range.")
        return

    st.success(f"✅ Summarized {len(emails_data)} emails")
    for e in emails_data:
        subject = e.get("subject") or "(No Subject)"
        sender = e.get("from") or "(Unknown Sender)"
        summary = e.get("summary") or "(No summary available)"

        # Ensure summary is a string to avoid 'NoneType' issues
        if not isinstance(summary, str):
            summary = str(summary)

        with st.container():
            st.markdown(f"### 📬 {subject}")
            st.caption(f"**From:** {sender}")
            st.write(summary)
            st.divider()
