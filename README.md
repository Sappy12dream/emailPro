# 📧 Email Assistant — Smart Summaries with AI

A Streamlit-based intelligent email assistant that connects to your Gmail inbox, fetches emails, and uses AI to summarize them — highlighting key insights, tone, actions, and priorities.

✨ **Built for productivity. Read less, act faster.**

---

## 🚀 Features

### 🧠 Smart Summaries
- Extracts key insights from each email using LLM summarization
- Highlights important actions, tone, and priority levels
- Categorizes emails automatically for better organization

### ⚙️ Configurable Fetch Settings
- Filter by date range and read/unread status
- Limit the number of emails fetched
- Customizable search criteria

### 🔐 Secure Gmail Connection
- Uses App Passwords for authentication (IMAP)
- Your credentials are never stored
- Session-based security

### 🖥️ Clean Streamlit UI
- Step-by-step guided interface:
  1. Connect to Gmail
  2. Choose filters
  3. Fetch & summarize
  4. View insights instantly
- Intuitive design with responsive layout

---

## 🧩 Tech Stack

| Component | Description |
|-----------|-------------|
| **Frontend/UI** | Streamlit |
| **Backend Logic** | Python 3.x |
| **Email Fetching** | IMAP via `imaplib` |
| **Parsing** | Python `email` library |
| **Summarization** | Custom LLM-based summarizer |
| **Logging** | `logging` module for debugging |

---

## 📂 Project Structure
```
📧 email-assistant/
├── app.py                     # Main Streamlit app
├── summarizer.py              # AI summarization logic
├── utils.py                   # Helper utilities (cleaning, parsing, etc.)
├── gmail_connect_ui.py        # Gmail login UI
├── fetch_settings_ui.py       # Fetch filter settings
├── display_emails_ui.py       # UI to show summarized emails
├── requirements.txt           # Dependencies
├── email_app.log              # (Generated) App logs
└── README.md                  # You're here!
```

---

## 🧠 How It Works

1. **Login** — Connect using your Gmail credentials (App Password)
2. **Filter** — Choose your fetch range, unread filter, and count
3. **Fetch** — The app retrieves emails via IMAP
4. **Summarize** — Each email's content is analyzed and summarized using AI
5. **Display** — Summaries with actions, tone, and priority appear beautifully in Streamlit

---

## 🧰 Setup & Run Locally

### 1️⃣ Clone the repo
```bash
git clone https://github.com/yourusername/email-assistant.git
cd email-assistant
```

### 2️⃣ Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # (macOS/Linux)
venv\Scripts\activate      # (Windows)
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set up environment variables (optional)

Create a `.env` file for API keys if using external LLM services:
```bash
OPENAI_API_KEY=your_api_key_here
# or other LLM provider credentials
```

### 5️⃣ Run the app
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 🔑 Gmail Setup

1. **Enable IMAP** in your Gmail settings:
   - Go to Settings → See all settings → Forwarding and POP/IMAP
   - Enable IMAP access

2. **Create an App Password**:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Navigate to Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"

3. **Use the App Password** (not your Gmail login password) in the app

⚠️ **Important:** Your credentials are only used in-session and are not stored anywhere.

---

## 💡 Example Output
```
⚡ Reminder: SDE2- UI at Increff
🟢 Normal Priority

From: Voila - your professional assistant <voila@alerts.cutshort.io>
Date: Oct 27, 2025

📋 Summary:
Ariba Khan invited Sapna Khatik to apply for the SDE II - UI role at Increff.
The email encourages Sapna to respond or track the application via links.

💬 Tone: Neutral
📁 Category: action_required

✅ Suggested Actions:
- Apply for the role
- Review similar job alerts
```

---

## 🧪 For Developers

You can easily extend the functionality:

- **`summarizer.py`** → Replace or upgrade the LLM summarization model
- **`display_emails_ui.py`** → Add pagination, filters, or search functionality
- **`utils.py`** → Enhance content extraction or cleaning logic

### 🔮 Future Ideas:
- ✅ Add OAuth-based Gmail login
- 📊 Export summaries to CSV/PDF
- 🧾 Smart daily digest email summaries
- 🧠 Multi-account or team dashboard view
- 🔍 Advanced search and filtering options
- 📱 Mobile-responsive design improvements
- 🤖 Integration with other email providers (Outlook, Yahoo)

---

## 🧑‍💻 Contributing

Pull requests are welcome! If you'd like to add features or fix bugs:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Submit a PR with clear description

---

## 🛡️ License

MIT License © 2025 — Developed by Sapna Singh Khatik

---

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the logs in `email_app.log`
- Review Gmail IMAP settings

---

**⭐ If you find this project helpful, please consider giving it a star!**
