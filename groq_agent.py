import os
import json
import re
from dotenv import load_dotenv
import openai

# Load .env and API key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = openai.OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# -------------------- THEME KEYWORDS --------------------
THEME_KEYWORDS = {
    "checkout": ["checkout", "cart", "payment", "payment gateway", "card", "billing", "billing page"],
    "support": ["support", "customer service", "agent", "response", "ticket", "helpdesk"],
    "pricing": ["price", "cost", "expensive", "cheap", "pricing", "subscription", "fee"],
    "product": ["product", "feature", "quality", "item", "spec", "functionality", "bug"],
    "performance": ["slow", "lag", "load time", "performance", "timeout"],
    "ux": ["ui", "user interface", "navigation", "confusing", "difficult to use", "experience", "flow", "process"],
    "delivery": ["delivery", "shipment", "tracking", "courier", "late", "arrival"],
    "returns": ["return", "refund", "exchange", "return policy"],
}

KEYWORD_TO_THEME = {w: t for t, words in THEME_KEYWORDS.items() for w in words}

# -------------------- UTILS --------------------
def clean_text(text: str) -> str:
    """Fix encoding issues & remove problematic control chars."""
    text = text.encode("utf-8", "ignore").decode("utf-8")
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    return text.strip()

def keyword_theme_score(text: str):
    txt = text.lower()
    scores = {t: 0 for t in THEME_KEYWORDS}
    for theme, words in THEME_KEYWORDS.items():
        for w in words:
            if re.search(r'\b' + re.escape(w) + r'\b', txt):
                scores[theme] += 1
    best_theme, best_score = max(scores.items(), key=lambda x: x[1])
    return best_theme, best_score, scores

def normalize_theme_name(raw_theme: str) -> str:
    if not raw_theme:
        return ""
    s = raw_theme.strip().lower()
    for canonical in THEME_KEYWORDS.keys():
        if canonical in s:
            return canonical.capitalize()
    for kw in KEYWORD_TO_THEME:
        if kw in s:
            return KEYWORD_TO_THEME[kw].capitalize()
    return raw_theme.strip().title()

def extract_json_from_text(text: str):
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r'(\{.*\})', text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
    return None

# -------------------- MAIN ANALYSIS --------------------
def analyze_feedback(feedback_text: str) -> dict:
    feedback_text = clean_text(feedback_text)

    prompt = f"""
Analyze the feedback and return ONLY a JSON object:
- themes: one label (Support, Pricing, Product, Checkout, UX, Delivery, Returns, Performance)
- sentiment: Positive, Negative, or Neutral
- highlights: short phrase about key point

Feedback: "{feedback_text}"
"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.15,
            max_tokens=256
        )
        raw_output = response.choices[0].message.content.strip()
        print("Raw model output:", raw_output)

        data = extract_json_from_text(raw_output) or {}
        llm_theme = data.get("themes", "") or data.get("theme", "")
        llm_sentiment = data.get("sentiment", "")
        llm_highlights = data.get("highlights", "") or data.get("highlight", "")
        normalized_llm_theme = normalize_theme_name(llm_theme)

    except Exception as e:
        print("LLM call/parsing error:", e)
        normalized_llm_theme = llm_sentiment = llm_highlights = ""
        data = {}

    # Keyword fallback
    best_theme_kw, score, all_scores = keyword_theme_score(feedback_text)
    chosen_theme = normalized_llm_theme or ""
    if score >= 1 and (not chosen_theme or chosen_theme.lower() != best_theme_kw.lower()):
        chosen_theme = best_theme_kw.capitalize()

    # Final structured output
    return {
        "input": feedback_text,  # original cleaned input
        "themes": chosen_theme or "N/A",
        "sentiment": llm_sentiment or "N/A",
        "highlights": llm_highlights or "N/A",
        "_debug": {
            "llm_theme": llm_theme,
            "normalized_llm_theme": normalized_llm_theme,
            "keyword_best": best_theme_kw,
            "keyword_score": score,
            "keyword_scores": all_scores
        }
    }
