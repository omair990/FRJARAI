import re
import json
import time
import requests
import random
import os
from datetime import datetime, timedelta, date
from openai import OpenAI
from ai_dev_app.constants.app_constants import AppConstants

client = OpenAI(api_key=AppConstants.OPENAI_API_KEY)
_ai_price_cache = {}

# Load daily price history
PRICE_HISTORY_FILE = "assets/price_history.json"
if os.path.exists(PRICE_HISTORY_FILE):
    with open(PRICE_HISTORY_FILE, "r") as f:
        _daily_price_history = json.load(f)
else:
    _daily_price_history = {}

# === Individual AI Providers ===

def ask_openai(prompt):
    print("ASK OPEN AI")
    try:
        response = client.chat.completions.create(
            model=AppConstants.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ OpenAI error: {e}")
        return None

def ask_gemini(prompt, model="gemini-2.0-flash"):
    print("Gemni Call")
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        headers = {"Content-Type": "application/json"}
        params = {"key": AppConstants.GEMINI_API_KEY}
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        r = requests.post(url, headers=headers, params=params, json=data)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"⚠️ Gemini error: {e}")
        return None

def ask_deepseek(prompt):
    print("ASK Deep Seek")
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {AppConstants.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": AppConstants.DEEPSEEK_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 300
        }
        r = requests.post(url, headers=headers, json=data)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"⚠️ DeepSeek error: {e}")
        return None

def ask_groq(prompt):
    print("Groq Call")
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {AppConstants.GROQ_API_KEY}"}
        data = {
            "model": AppConstants.GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 300
        }
        r = requests.post(url, headers=headers, json=data)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"⚠️ Groq error: {e}")
        return None

# === Unified AI Wrapper ===

def ask_ai(prompt):
    for ai_func in [ask_gemini, ask_openai, ask_deepseek, ask_groq]:

        try:
            reply = ai_func(prompt)
            if reply:
                return reply
        except Exception as e:
            print(f"⚠️ {ai_func.__name__} failed: {e}")
    return None

# === Core Business Logic ===


def get_today_price_estimate_from_ai(product_name, unit, min_price, max_price, median, average):
    now = datetime.utcnow()
    today_key = date.today().isoformat()
    cache_key = f"{today_key}:{product_name}"

    # ✅ Check memory cache with timestamp
    cached_entry = _ai_price_cache.get(cache_key)
    if cached_entry:
        cached_time, cached_price = cached_entry
        if now - cached_time < timedelta(hours=6):
            return cached_price

    # ✅ Check saved history
    if product_name in _daily_price_history and today_key in _daily_price_history[product_name]:
        cached_price = _daily_price_history[product_name][today_key]
        _ai_price_cache[cache_key] = (now, cached_price)
        return cached_price

    # === Prompt AI ===
    today = now.strftime("%A, %d %B %Y")
    random_hint = round(random.uniform(-1.5, 1.5), 2)

    prompt = f"""
You are a senior market analyst for Saudi construction materials.

Today is: {today}  
Add a slight market shift factor of ~{random_hint} SAR for daily variation.

🔹 Product: "{product_name}"  
🔹 Unit: {unit}

📊 12-Year Price Summary:
- Min: {min_price} SAR  
- Max: {max_price} SAR  
- Median: {median} SAR  
- Average: {average} SAR  

📦 Market context:
- Stable trends, up to ±10% seasonal fluctuation.
- Median ≈ Average → balanced market.
- Median ≪ Average → outliers present.
- Use judgment to produce today's most realistic price.

Return this JSON format only:
{{ "today_price_sar": 123.45 }}
"""
    reply = ask_ai(prompt)
    if not reply:
        return None

    match = re.search(r'\{.*\}', reply, re.DOTALL)
    if not match:
        return None

    try:
        data = json.loads(match.group(0))
        price = float(data.get("today_price_sar", 0))
        final_price = round(price, 2) if price > 0 else None

        # ✅ Save to memory with timestamp
        _ai_price_cache[cache_key] = (now, final_price)

        # ✅ Save to daily price history (persistent)
        if product_name not in _daily_price_history:
            _daily_price_history[product_name] = {}
        _daily_price_history[product_name][today_key] = final_price

        with open(PRICE_HISTORY_FILE, "w") as f:
            json.dump(_daily_price_history, f, indent=2)

        return final_price
    except Exception as e:
        print(f"❌ AI price parse failed: {e}")
        return None


def generate_forecast_from_openai(product_name, country, past_years, future_years):
    current_year = datetime.datetime.now().year
    prompt = f"""
You are an expert in Saudi Arabia's construction material pricing.

Estimate:
- Past {past_years} years prices
- Future {future_years} years prices
- Assume stable market with max ±10% change.

Respond STRICT JSON:

{{
  "past_prices": {{
    "{current_year-3}": 140.00,
    "{current_year-2}": 145.00,
    "{current_year-1}": 150.00
  }},
  "future_prices": {{
    "{current_year+1}": 155.00,
    "{current_year+2}": 160.00,
    "{current_year+3}": 165.00
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
    return {"past_prices": {}, "future_prices": {}}

def get_real_product_price_from_openai(product_name):
    prompt = f"Estimate a realistic retail price (SAR) for \"{product_name}\" in Saudi Arabia. Only return a number like: 123.45"
    try:
        reply = ask_ai(prompt)
        price = re.findall(r'\d+\.\d+', reply)
        return float(price[0]) if price else None
    except Exception:
        return None
