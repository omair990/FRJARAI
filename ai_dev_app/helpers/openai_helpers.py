import re
import json
import time
import requests
import random
import os
import pickle
import numpy as np
from datetime import datetime, timedelta, date
from openai import OpenAI
from ai_dev_app.constants.app_constants import AppConstants
from utils.feature_extractor import extract_features

client = OpenAI(api_key=AppConstants.OPENAI_API_KEY)
_ai_price_cache = {}

FALLBACK_MODEL_PATH = "models/ai_price_model.pkl"
if os.path.exists(FALLBACK_MODEL_PATH):
    with open(FALLBACK_MODEL_PATH, "rb") as f:
        print("Local Model")
        _local_model = pickle.load(f)
else:
    _local_model = None

PRICE_HISTORY_FILE = "assets/price_history.json"
if os.path.exists(PRICE_HISTORY_FILE):
    with open(PRICE_HISTORY_FILE, "r") as f:
        _daily_price_history = json.load(f)
else:
    _daily_price_history = {}

TRAINING_FILE = "assets/cloud_ai_training.json"
if os.path.exists(TRAINING_FILE):
    with open(TRAINING_FILE, "r") as f:
        try:
            _training_data = json.load(f)
            if not isinstance(_training_data, list):
                _training_data = []
        except json.JSONDecodeError:
            print(f"⚠️ Error decoding JSON from {TRAINING_FILE}. Initializing empty training data.")
            _training_data = []
else:
    _training_data = []

def ask_openai(prompt):
    print("O Model")
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
    print("G Model")
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        headers = {"Content-Type": "application/json"}
        params = {"key": AppConstants.GEMINI_API_KEY}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        r = requests.post(url, headers=headers, params=params, json=data)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"⚠️ Gemini error: {e}")
        return None

def ask_deepseek(prompt):
    print("D Model")
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
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"⚠️ DeepSeek error: {e}")
        return None

def ask_groq(prompt):
    print("Gr Model")

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
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"⚠️ Groq error: {e}")
        return None

def ask_ai(prompt):
    ai_models = [ask_gemini, ask_groq]  # List of AI functions to try
    for ai_func in ai_models:
        try:
            reply = ai_func(prompt)
            if reply:
                return reply.strip()
        except Exception as e:
            print(f"⚠️ {ai_func.__name__} failed: {e}")
    return None

def get_today_price_estimate_from_ai(product):
    now = datetime.utcnow()
    today_key = date.today().isoformat()

    product_name = product.get("name", "unknown")
    min_price = product.get("min_price")
    max_price = product.get("max_price")
    average = product.get("average")
    median = product.get("median", average)

    cache_key = f"{product_name.strip().lower()}"

    # Step 1: Memory cache
    if cache_key in _ai_price_cache:
        cached_time, cached_data = _ai_price_cache[cache_key]
        if now - cached_time < timedelta(hours=6):
            return cached_data

    # Step 2: File history
    if product_name in _daily_price_history and today_key in _daily_price_history[product_name]:
        cached_data = _daily_price_history[product_name][today_key]
        _ai_price_cache[cache_key] = (now, cached_data)
        return cached_data

    # Step 3: AI Call
    today = now.strftime("%A, %d %B %Y")
    random_hint = round(random.uniform(-1.5, 1.5), 2)

    prompt = f"""
    You are a senior construction pricing analyst in Saudi Arabia.

    📅 Date: {today}
    📦 Product: "{product_name}"

    📊 12-Year Summary:
    - Min Price: {min_price} SAR
    - Max Price: {max_price} SAR
    - Median: {median} SAR
    - Average: {average} SAR

    📌 Market Context:
    - Price must be > min_price and < max_price
    - Price must not equal average
    - Slight fluctuation: ~{random_hint} SAR allowed

    🎯 Rules:
    - Today's price must be BETWEEN min and max
    - Use all stats (median, average, volatility, etc.)
    - If average ≈ median → stable market
    - If average ≫ median → skewed by outliers
    - Add daily fluctuation of ~{random_hint} SAR
    - Reflect Saudi construction market realities

    Return JSON only:
    {{ "today_price_sar": 123.45 }}
    """

    reply = ask_ai(prompt)
    if reply:
        try:
            # Ensure that the AI response is in JSON format
            match = re.search(r'\{.*\}', reply, re.DOTALL)
            print(f" AI Full data : {match.group(0)}" if match else "❌ No valid match found")

            if match:
                ai_data = json.loads(match.group(0))
                raw_price = float(ai_data.get("today_price_sar", 0.0))
                final_price = adjust_today_price(raw_price, min_price, max_price, average)

                # ✅ Save for local model training
                save_training_example(product, final_price)

                result = build_price_summary(product, final_price, "AI")
                _ai_price_cache[cache_key] = (now, result)
                _daily_price_history.setdefault(product_name, {})[today_key] = result

                with open(PRICE_HISTORY_FILE, "w") as f:
                    json.dump(_daily_price_history, f, indent=2)

                return result

        except Exception as e:
            print(f"❌ AI parse failed: {e}")

    # Step 4: Local model fallback
    if _local_model:
        try:
            features = extract_features(product)
            print(f" AI Features : {features}")
            if len(features) != 31:
                print(f"⚠️ Feature mismatch: expected 31, got {len(features)}. Skipping local model.")
            else:
                prediction = _local_model.predict(np.array([features]))[0]

                base_price = (0.25 * min_price) + (0.25 * median) + (0.4 * average) + (0.1 * max_price)
                adjusted = (prediction + base_price) / 2
                fluctuation = random.uniform(-0.02, 0.02)
                raw_price = adjusted * (1 + fluctuation)

                final_price = adjust_today_price(raw_price, min_price, max_price, average)
                result = build_price_summary(product, final_price, "LocalModel")

                _ai_price_cache[cache_key] = (now, result)
                _daily_price_history.setdefault(product_name, {})[today_key] = result

                with open(PRICE_HISTORY_FILE, "w") as f:
                    json.dump(_daily_price_history, f, indent=2)

                return result
        except Exception as e:
            print(f"⚠️ Local model fallback failed: {e}")

    # Step 5: Fallback to average
    fallback_price = average or median or (min_price + max_price) / 2
    final_price = adjust_today_price(fallback_price, min_price, max_price, average)
    result = build_price_summary(product, final_price, "Fallback")

    _ai_price_cache[cache_key] = (now, result)
    _daily_price_history.setdefault(product_name, {})[today_key] = result

    with open(PRICE_HISTORY_FILE, "w") as f:
        json.dump(_daily_price_history, f, indent=2)

    return result

def adjust_today_price(price, min_price, max_price, average):
    epsilon = 0.01
    max_limit = max_price - epsilon
    min_limit = min_price + epsilon
    avg_limit = average + epsilon if price <= average else average - epsilon

    # Apply bounds and fix overlaps
    corrected_price = max(price, min_limit)
    corrected_price = min(corrected_price, max_limit)

    # Ensure not equal to average
    if abs(corrected_price - average) < epsilon:
        corrected_price += epsilon if corrected_price < max_limit else -epsilon

    return round(corrected_price, 2)

def build_price_summary(product, today_price, model_source):
    min_price = product.get("min_price")
    max_price = product.get("max_price")
    average = product.get("average")

    features = extract_features(product)

    def get_feature(index, default=0.0, cast=float):
        try:
            return cast(features[index])
        except (IndexError, TypeError, ValueError):
            return default

    return {
        "today_price": float(today_price),
        "min_price": float(min_price),
        "max_price": float(max_price),
        "average_price": float(average),
        "volatility": get_feature(8),
        "symmetry_index": get_feature(9),
        "monthly_volatility": get_feature(10),
        "source_score": get_feature(11),
        "supplier_counts": {
            "wholesale": get_feature(12, 0, int),
            "second_layer": get_feature(13, 0, int),
            "retail": get_feature(14, 0, int)
        },
        "model_source": model_source
    }

def save_training_example(product, ai_price):
    record = {
        "name": product.get("name"),
        "min_price": product.get("min_price"),
        "max_price": product.get("max_price"),
        "average": product.get("average"),
        "median": product.get("median", product.get("average")),
        "unit": product.get("unit", ""),
        "ai_price": float(ai_price)
    }

    global _training_data  # Ensure we're modifying the global variable
    _training_data.append(record)

    with open(TRAINING_FILE, "w") as f:
        json.dump(_training_data, f, indent=2)