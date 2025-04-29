import os
from ai_dev_app.constants.app_constants import AppConstants
from openai import OpenAI

client = OpenAI(api_key=AppConstants.OPENAI_API_KEY)

def translate_to_english(product_name):
#     """Translate Arabic product name to English using OpenAI without cache."""
#     if not product_name:
#         return product_name
#
#     prompt = f"""
# You are a professional Arabic to English translator.
#
# Translate the following Saudi construction material product name into natural English:
#
# Product: {product_name}
#
# Only return the translated English product name, no extra explanation.
# """
#
#     try:
#         response = client.chat.completions.create(
#             model=AppConstants.OPENAI_MODEL,
#             messages=[{"role": "user", "content": prompt}]
#         )
#         reply = response.choices[0].message.content.strip()
#         return reply
#     except Exception as e:
#         print(f"⚠️ Translation Error: {e}")
        return product_name  # fallback to original if translation fails

# ✅ You can also keep simulate_forecast() inside fallback_helpers
def simulate_forecast(base_price, past_years=3, future_years=3):
    from datetime import datetime
    current_year = datetime.now().year
    past_prices = {}
    future_prices = {}

    for i in range(past_years, 0, -1):
        year = current_year - i
        past_prices[str(year)] = round(base_price * (1 - (i * 0.01)), 2)

    for i in range(1, future_years + 1):
        year = current_year + i
        future_prices[str(year)] = round(base_price * (1 + (i * 0.015)), 2)

    return {
        "past_prices": past_prices,
        "future_prices": future_prices
    }
