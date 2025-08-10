import os
from dotenv import load_dotenv
import openai
import json

# Load .env values
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

client = openai.OpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1"
)

def analyze_feedback(feedback_text: str) -> dict:
    prompt = f"""
You are a Customer Feedback Analyzer Agent.

Analyze the following customer feedback and return a JSON with:
- themes: the core topic of feedback (e.g., support, pricing, product)
- sentiment: Positive, Negative, or Neutral
- highlights: any specific unusual or noteworthy issue

Feedback: \"{feedback_text}\"

Respond ONLY in pure JSON format with keys:
{{
  "themes": "...",
  "sentiment": "...",
  "highlights": "..."
}}
"""

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    raw_output = response.choices[0].message.content.strip()
    print("Raw model output:", raw_output)

    try:
        data = json.loads(raw_output)

        # Ensure correct keys exist
        return {
            "themes": data.get("themes", ""),
            "sentiment": data.get("sentiment", ""),
            "highlights": data.get("highlights", "")
        }
    except Exception:
        return {
            "themes": "",
            "sentiment": "",
            "highlights": ""
        }
