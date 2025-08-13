import os
import json
import re
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# OpenAI-compatible client for Groq API
client = openai.OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# Predefined theme keywords
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

# Reverse keyword map
KEYWORD_TO_THEME = {w: theme for theme, words in THEME_KEYWORDS.items() for w in words}

# Cleaning function for special characters
def clean_text_encoding(text: str) -> str:
    replacements = {
        "\u2018": "'", "\u2019": "'",  # single quotes
        "\u201c": '"', "\u201d": '"',  # double quotes
        "&#39;": "'", "&quot;": '"'
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text

# Keyword scoring
def keyword_theme_score(text: str):
    txt = text.lower()
    scores = {t: 0 for t in THEME_KEYWORDS}
    for theme, words in THEME_KEYWORDS.items():
        for w in words:
            if re.search(r'\b' + re.escape(w) + r'\b', txt):
                scores[theme] += 1
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_theme, best_score = sorted_scores[0]
    return best_theme, best_score, scores

# Normalize theme name
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

# Extract JSON from text
def extract_json_from_text(text: str):
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r'(\{.*\})', text, re.DOTALL)
        if m:
            js = m.group(1)
            try:
                return json.loads(js)
            except Exception:
                pass
    return None

# Main analyzer
def analyze_feedback(feedback_text: str) -> dict:
    few_shot = """
Return only a pure JSON object. Example outputs:

Input: "I waited 30 minutes to get a response from the support team. Totally unacceptable!"
Output:
{"themes":"Support","sentiment":"Negative","highlights":"Long agent response time"}

Input: "The website checkout process was confusing and made me almost abandon my cart."
Output:
{"themes":"Checkout","sentiment":"Negative","highlights":"Confusing checkout flow"}

Input: "Great product — the battery life on this device lasts two days!"
Output:
{"themes":"Product","sentiment":"Positive","highlights":"Excellent battery life"}
"""

    prompt = f"""
You are a Customer Feedback Analyzer. Analyze the feedback and return ONLY a JSON object with keys:
- themes (single short label like Support, Pricing, Product, Checkout, UX, Delivery, Returns, Performance, etc.)
- sentiment (Positive, Negative, Neutral)
- highlights (short phrase describing the key point)

Do not include any extra text. If uncertain, use "N/A" values.

{few_shot}

Feedback: "{feedback_text}"
"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.15,
            max_tokens=256
        )

        raw_output = clean_text_encoding(response.choices[0].message.content.strip())
        print("Raw model output:", raw_output)

        data = extract_json_from_text(raw_output) or {}
        llm_theme = data.get("themes", "") or data.get("theme", "")
        llm_sentiment = data.get("sentiment", "")
        llm_highlights = data.get("highlights", "") or data.get("highlight", "")
        normalized_llm_theme = normalize_theme_name(llm_theme)

    except Exception as e:
        print("LLM call/parsing error:", e)
        normalized_llm_theme = ""
        llm_sentiment = ""
        llm_highlights = ""
        data = {}

    best_theme_kw, score, all_scores = keyword_theme_score(feedback_text)
    llm_theme_lower = (normalized_llm_theme or "").lower()
    best_theme_lower = best_theme_kw.lower()

    chosen_theme = normalized_llm_theme or ""
    if score >= 1 and (not llm_theme_lower or llm_theme_lower != best_theme_lower):
        chosen_theme = best_theme_lower.capitalize()

    output = {
        "input": feedback_text,  # original untouched input
        "themes": chosen_theme or "N/A",
        "sentiment": llm_sentiment or "N/A",
        "highlights": llm_highlights or "N/A",
        "_debug": {
            "llm_raw": raw_output if 'raw_output' in locals() else "",
            "llm_theme": llm_theme,
            "normalized_llm_theme": normalized_llm_theme,
            "keyword_best": best_theme_kw,
            "keyword_score": score,
            "keyword_scores": all_scores
        }
    }

    return output
