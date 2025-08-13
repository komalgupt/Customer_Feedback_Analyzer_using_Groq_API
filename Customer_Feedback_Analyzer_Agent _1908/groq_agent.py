import os
import json
import re
from dotenv import load_dotenv
import openai

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = openai.OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# A simple keyword map for fallback / normalization
THEME_KEYWORDS = {
    "checkout": ["checkout", "cart", "payment", "payment gateway", "card", "billing", "billing page"],
    "support": ["support", "customer service", "agent", "response", "ticket", "helpdesk"],
    "pricing": ["price", "cost", "expensive", "cheap", "pricing", "subscription", "fee"],
    "product": ["product", "feature", "quality", "item", "spec", "functionality", "bug"],
    "performance": ["slow", "lag", "load time", "performance", "timeout"],
    "ux": ["ui", "user interface", "navigation", "confusing", "difficult to use", "experience", "flow", "process"],
    "delivery": ["delivery", "shipment", "tracking", "courier", "late", "arrival"],
    "returns": ["return", "refund", "exchange", "return policy"],
    # you can add more as needed or integrate with your own PAST companeis data through RAG...
}

# reverse map to normalized theme name
KEYWORD_TO_THEME = {}
for theme, words in THEME_KEYWORDS.items():
    for w in words:
        KEYWORD_TO_THEME[w] = theme

def keyword_theme_score(text: str):
    """
    Count keyword occurrences per theme and return best theme + scores dict.
    """
    txt = text.lower()
    scores = {t: 0 for t in THEME_KEYWORDS}
    for theme, words in THEME_KEYWORDS.items():
        for w in words:
            # simple word match; use word boundaries for short words
            if re.search(r'\b' + re.escape(w) + r'\b', txt):
                scores[theme] += 1
    # return sorted list
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_theme, best_score = sorted_scores[0]
    return best_theme, best_score, scores

def normalize_theme_name(raw_theme: str) -> str:
    """
    Normalize model-provided theme strings into our canonical theme labels.
    """
    if not raw_theme:
        return ""
    s = raw_theme.strip().lower()
    # direct mapping attempts
    for canonical in THEME_KEYWORDS.keys():
        if canonical in s:
            return canonical.capitalize()
    # if model returned something like "checkout process" or "checkout"
    for kw in KEYWORD_TO_THEME:
        if kw in s:
            return KEYWORD_TO_THEME[kw].capitalize()
    # fallback: title-case the provided string
    return raw_theme.strip().title()

def extract_json_from_text(text: str):
    """
    Try to find the first {...} JSON substring in text and parse it.
    """
    try:
        # try direct parse first
        return json.loads(text)
    except Exception:
        # try to find {...} block
        m = re.search(r'(\{.*\})', text, re.DOTALL)
        if m:
            js = m.group(1)
            try:
                return json.loads(js)
            except Exception:
                pass
    return None

def analyze_feedback(feedback_text: str) -> dict:
    """
    1) Ask the LLM for a structured JSON output (few-shot + schema).
    2) Parse it and normalize keys.
    3) Use keyword scoring as fallback/override when LLM seems inconsistent.
    """
    # Few-shot examples to guide theme selection
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
            model="llama3-70b-8192",  # use your supported model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.15,
            max_tokens=256
        )

        raw_output = response.choices[0].message.content.strip()
        # Debug print so you can see LLM raw output in logs
        print("Raw model output:", raw_output)

        data = extract_json_from_text(raw_output) or {}
        # Ensure default keys
        llm_theme = data.get("themes", "") or data.get("theme", "")
        llm_sentiment = data.get("sentiment", "")
        llm_highlights = data.get("highlights", "") or data.get("highlight", "")

        # Normalize LLM theme
        normalized_llm_theme = normalize_theme_name(llm_theme)

    except Exception as e:
        print("LLM call/parsing error:", e)
        normalized_llm_theme = ""
        llm_sentiment = ""
        llm_highlights = ""
        data = {}

    # Keyword fallback / validation
    best_theme_kw, score, all_scores = keyword_theme_score(feedback_text)
    # Decide threshold: if keyword score >=1 and LLM theme doesn't match, prefer keywords
    # Compare lowercased names
    llm_theme_lower = (normalized_llm_theme or "").lower()
    best_theme_lower = best_theme_kw.lower()

    chosen_theme = normalized_llm_theme or ""
    # If keywords strongly indicate a different theme, override
    if score >= 1:
        # map keyword theme to display name
        kw_theme_display = best_theme_lower.capitalize()
        # if LLM is empty or differs and keyword evidence exists, override
        if not llm_theme_lower or (llm_theme_lower != best_theme_lower):
            chosen_theme = kw_theme_display

    # Final output structure (consistent keys for frontend)
    output = {
        "themes": chosen_theme or "N/A",
        "sentiment": (llm_sentiment or "N/A"),
        "highlights": (llm_highlights or "N/A")
    }

    # Optionally include diagnostic info for debugging (remove or hide in production)
    output["_debug"] = {
        "llm_raw": raw_output if 'raw_output' in locals() else "",
        "llm_theme": llm_theme,
        "normalized_llm_theme": normalized_llm_theme,
        "keyword_best": best_theme_kw,
        "keyword_score": score,
        "keyword_scores": all_scores
    }

    return output
