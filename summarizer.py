# summarizer.py
from openai import OpenAI
from dotenv import load_dotenv
import os, json, logging

# --- SETUP ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Optional: enable logging for debugging
logging.basicConfig(
    filename="summarizer.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# --- DEFAULT STRUCTURE ---
DEFAULT_RESULT = {
    "summary": "(No summary available)",
    "actions": [],
    "tone": "neutral",
    "priority": "🟢 Normal",
    "category": "info",
}


def summarize_email(email_text: str):
    """Analyze and summarize an email using LLM for structured, reliable insights."""

    if not email_text or not isinstance(email_text, str):
        logging.warning("Empty or invalid email_text passed to summarizer.")
        return DEFAULT_RESULT.copy()

    try:
        # --- SMART PROMPT ---
        prompt = f"""
You are an intelligent **email understanding agent**.
Your task is to read the full email and return a **valid JSON** response that captures both summary and actionable intelligence.

Follow these STRICT rules:
1. Output ONLY valid JSON — no extra text or markdown.
2. Ensure all fields are always present.
3. Use concise, human-like summaries (max 3 sentences).
4. Detect and list actionable steps clearly (e.g., "Reply to confirm", "Submit form by Monday").
5. Infer the **tone**, **priority**, and **category** logically.
6. If content includes a meeting invite or schedule, mark category as "event".
7. If promotional or automated, mark category as "newsletter" or "spam".

The required JSON structure is:
{{
  "summary": "Brief 2–3 sentence summary of the email",
  "actions": ["list of actionable tasks if any, otherwise empty list"],
  "tone": "formal / informal / neutral / urgent",
  "priority": "🔴 Critical / 🟠 Important / 🟢 Normal",
  "category": "one of: action_required / info / event / spam / newsletter"
}}

Now read and analyze the following email carefully:
-----------------------
{email_text}
-----------------------
"""

        # --- LLM CALL ---
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            temperature=0.3,
        )

        output_text = getattr(response, "output_text", None)
        logging.info(f"Raw LLM output: {output_text[:250]}...")  # truncate long logs

        # --- SAFE PARSING ---
        try:
            data = json.loads(output_text)
            if not isinstance(data, dict):
                raise ValueError("Parsed LLM output not a dict")

        except Exception as e:
            logging.warning(f"JSON parsing failed: {e}. Returning fallback JSON.")
            # Fallback: return wrapped string
            data = {"summary": output_text.strip()} if output_text else {}

        # --- ENSURE ALL KEYS EXIST ---
        final = DEFAULT_RESULT.copy()
        final.update({k: v for k, v in data.items() if k in final})

        # Type-safety cleanup
        if not isinstance(final["actions"], list):
            final["actions"] = [str(final["actions"])]

        # Normalize tone and category
        final["tone"] = str(final.get("tone", "neutral")).lower()
        final["category"] = str(final.get("category", "info")).lower()

        logging.info(f"✅ Final summary ready: {json.dumps(final, ensure_ascii=False)}")
        return final

    except Exception as e:
        logging.exception("LLM summarization failed.")
        result = DEFAULT_RESULT.copy()
        result["summary"] = f"(AI summarization failed: {e})"
        return result
