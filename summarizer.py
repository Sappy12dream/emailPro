# summarizer.py
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_email(email_text: str) -> str:
    """Safely summarize an email using the LLM, with fallbacks."""
    if not email_text or not isinstance(email_text, str):
        return "(No email content to summarize)"

    try:
        prompt = f"""
        You are an intelligent email assistant.
        Summarize the following email briefly and clearly:
        - Give a 2–3 sentence summary
        - Extract action items if any
        - Identify tone (formal/informal/neutral/urgent)
        - Assign priority 🔴 Critical / 🟠 Important / 🟢 Normal
        Email content:
        {email_text}
        """

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            temperature=0.4,
        )

        summary = getattr(response, "output_text", None)
        if not summary or not isinstance(summary, str):
            summary = "(AI summary unavailable)"
        return summary.strip()

    except Exception as e:
        return f"(AI summarization failed: {e})"
