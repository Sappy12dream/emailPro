import streamlit as st
import html

def get_priority_style(priority: str):
    colors = {
        "🔴 Critical": "#ff4d4d",
        "🟠 Important": "#ffa64d",
        "🟢 Normal": "#5cd65c",
    }
    return colors.get(priority, "#cccccc")

def get_category_icon(category: str):
    icons = {
        "action_required": "⚡",
        "info": "ℹ️",
        "event": "📅",
        "spam": "🚫",
        "newsletter": "📰",
    }
    return icons.get(category, "📧")

def display_emails_ui(emails_data):
    if not emails_data:
        st.info("📭 No emails found in the selected range.")
        return

    st.markdown("## ✉️ Smart Email Summaries")
    st.success(f"✅ Summarized {len(emails_data)} emails")

    with st.expander("🔍 Filter Emails", expanded=False):
        all_senders = sorted({e.get("from", "Unknown") for e in emails_data})
        all_categories = sorted({e.get("category", "info") for e in emails_data})
        selected_sender = st.selectbox("Filter by sender", ["All"] + all_senders)
        selected_priority = st.selectbox("Filter by priority", ["All", "🔴 Critical", "🟠 Important", "🟢 Normal"])
        selected_category = st.selectbox("Filter by category", ["All"] + all_categories)

    for e in emails_data:
        sender = html.escape(e.get("from", "(Unknown Sender)"))
        subject = html.escape(e.get("subject", "(No Subject)"))
        summary = html.escape(e.get("summary", "(No summary available)"))
        full_body = html.escape(e.get("body", "(No content)"))
        date = html.escape(e.get("date", "(Unknown Date)"))
        tone = e.get("tone", "neutral").capitalize()
        priority = e.get("priority", "🟢 Normal")
        category = e.get("category", "info")
        actions = e.get("actions", [])

        if (selected_sender != "All" and sender != selected_sender) or \
           (selected_priority != "All" and priority != selected_priority) or \
           (selected_category != "All" and category != selected_category):
            continue

        color = get_priority_style(priority)
        cat_icon = get_category_icon(category)

        st.markdown(
            f"""
            <div style='background-color:#1e1e1e;border-radius:12px;padding:16px;margin-bottom:14px;
                        box-shadow:0 2px 8px rgba(0,0,0,0.3);'>
                <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <h4 style='margin:0;color:#fff;'>{cat_icon} {subject}</h4>
                    <span style='background-color:{color};padding:4px 10px;border-radius:8px;
                                color:#000;font-weight:600;'>{priority}</span>
                </div>
                <p style='color:#ccc;margin:6px 0 2px 0;'>From: <b>{sender}</b></p>
                <p style='color:#aaa;margin:0;'>Date: {date}</p>
                <hr style='border:0.5px solid #333;margin:8px 0;' />
                <p style='color:#ddd;'>{summary}</p>
                <p style='color:#bbb;margin-top:8px;'>🗣️ Tone: <b>{tone}</b></p>
                <p style='color:#bbb;'>🏷️ Category: <b>{category}</b></p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Show actions if present
        if actions:
            st.markdown("#### ✅ Suggested Actions")
            for i, action in enumerate(actions, start=1):
                st.checkbox(f"{i}. {action}", key=f"{subject}_{i}")

        with st.expander("📖 View Full Email"):
            st.write(full_body)
