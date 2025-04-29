import re
import json
import time
import os
import datetime
import requests
from openai import OpenAI
from ai_dev_app.constants.app_constants import AppConstants

client = OpenAI(api_key=AppConstants.OPENAI_API_KEY)

# ✅ Fallback AI Handlers
def ask_openai(prompt):
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

def ask_groq(prompt):
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
        if r.status_code == 200:
            json_data = r.json()
            return json_data["choices"][0]["message"]["content"]
        else:
            print(f"❌ Groq API error {r.status_code}: {r.text}")
    except Exception as e:
        print(f"❌ Groq parsing error: {e}")
    return None

def ask_deepseek(prompt):
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
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        else:
            print(f"❌ DeepSeek API error {r.status_code}: {r.text}")
    except Exception as e:
        print(f"❌ DeepSeek error: {e}")
    return None

# ✅ Smart fallback order
def ask_ai(prompt):
    for ai_func in [ask_openai, ask_deepseek, ask_groq]:
        try:
            reply = ai_func(prompt)
            if reply:
                return reply
        except Exception as e:
            print(f"⚠️ {ai_func.__name__} failed: {e}")
    return None

# ✅ Fetch unit + price
def get_verified_unit_and_price_for_product(product_name):
    prompt = f"""
You are a Saudi Arabia construction material pricing expert.

Analyze the product: "{product_name}"

Return STRICT JSON format:

{{
  "unit": "Ton, Piece, 50kg Bag, Square Meter, Cubic Meter, etc.",
  "price_sar": 123.45
}}
"""
    reply = ask_ai(prompt)
    if not reply:
        return None

    match = re.search(r'\{.*\}', reply, re.DOTALL)
    if not match:
        return None

    try:
        data = json.loads(match.group(0))
        unit = data.get("unit", "").strip()
        price = float(data.get("price_sar", 0))
        if not unit or price <= 0:
            return None
        return {"unit": unit, "price_sar": price}
    except Exception as e:
        print(f"❌ JSON parse failed: {e}")
        return None

# ✅ Batch fetch
def get_batch_units_and_prices(product_list):
    prompt = "You are a Saudi Arabia construction expert. Analyze the following products:\n\n"
    for product in product_list:
        prompt += f"- {product}\n"
    prompt += """
Reply STRICT JSON like:

{
  "Cement 50kg": { "unit": "50kg Bag", "price_sar": 13.45 },
  "Steel Rebar": { "unit": "Ton", "price_sar": 2550.00 }
}
"""
    reply = ask_ai(prompt)
    if reply:
        match = re.search(r'\{.*\}', reply, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception as e:
                print(f"❌ Batch JSON parse failed: {e}")
    return {}

# ✅ Forecasting
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

# ✅ Basic fallback price estimation
def get_real_product_price_from_openai(product_name):
    prompt = f"""
Estimate a realistic retail price (SAR) for "{product_name}" in Saudi Arabia. Only return number like: 123.45
"""
    try:
        reply = ask_ai(prompt)
        price = re.findall(r'\d+\.\d+', reply)
        return float(price[0]) if price else None
    except Exception:
        return None
