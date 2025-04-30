import os
import json
from datetime import datetime
from ai_dev_app.constants.app_constants import AppConstants
from openai import OpenAI

client = OpenAI(api_key=AppConstants.OPENAI_API_KEY)

# --- Translation cache ---
_translation_cache = {}
TRANSLATION_FILE = "ai_dev_app/cache/translations.json"

# --- Load existing cache ---
if os.path.exists(TRANSLATION_FILE):
    try:
        with open(TRANSLATION_FILE, "r", encoding="utf-8") as f:
            _translation_cache = json.load(f)
    except Exception as e:
        print(f"⚠️ Could not load translation cache: {e}")

# --- Save to cache ---
def save_translation_cache():
    os.makedirs(os.path.dirname(TRANSLATION_FILE), exist_ok=True)
    with open(TRANSLATION_FILE, "w", encoding="utf-8") as f:
        json.dump(_translation_cache, f, ensure_ascii=False, indent=2)

# --- Translate Arabic to English using AI (cached) ---
def translate_to_english(product_name):
    if product_name in _translation_cache:
        return _translation_cache[product_name]

    prompt = f"""
You are a professional Arabic-to-English translator.

Translate this construction material product to English:
"{product_name}"

Return ONLY the translated English name, no explanation.
"""

    try:
        response = client.chat.completions.create(
            model=AppConstants.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=50
        )
        translation = response.choices[0].message.content.strip()
        _translation_cache[product_name] = translation
        save_translation_cache()
        return translation
    except Exception as e:
        print(f"⚠️ Translation failed: {e}")
        return product_name  # fallback

# --- Simulate forecast if AI fails ---
def generate_forecast_from_openai(product_name, country, past_years, future_years):
    current_year = datetime.datetime.now().year
    prompt = f"""
You are an expert in Saudi construction pricing.

Estimate:
- Past {past_years} years
- Future {future_years} years
- Based on stable market. Max ±10% variance.

Respond ONLY JSON:
{{
  "past_prices": {{
    "{current_year-3}": 100.00,
    "{current_year-2}": 110.00,
    "{current_year-1}": 115.00
  }},
  "future_prices": {{
    "{current_year+1}": 120.00,
    "{current_year+2}": 125.00,
    "{current_year+3}": 130.00
  }}
}}
"""

    for _ in range(3):
        reply = ask_ai(prompt)
        if reply:
            match = re.search(r'\{.*\}', reply, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except:
                    continue
        time.sleep(1)

    # 🔁 Fallback
    return simulate_forecast(base_price=100)  # you can pass a better base if available



def fallback_today_price(min_price, max_price, median, average):
    base = (median + average) / 2
    seasonal_fluctuation = 0.02  # ±2%
    fluctuation = base * seasonal_fluctuation
    return round(base + fluctuation, 2)
