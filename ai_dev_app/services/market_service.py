import time
import concurrent.futures
import streamlit as st

from ai_dev_app.helpers.openai_helpers import get_verified_unit_and_price_for_product
from ai_dev_app.helpers.fallback_helpers import translate_to_english

MAX_RETRIES = 5


def fetch_single_product_data(product_name):
    try:
        retry = 0
        verified_info = None

        while retry < MAX_RETRIES:
            verified_info = get_verified_unit_and_price_for_product(product_name)
            if verified_info:
                break
            retry += 1
            time.sleep(1)  # small delay between retries

        if not verified_info:
            return None

        unit = verified_info.get("unit", "N/A")
        base_price = verified_info.get("price_sar", 0)

        avg_price = base_price
        min_price = round(base_price * 0.97, 2)
        max_price = round(base_price * 1.03, 2)

        return {
            "Product Name": product_name,
            "Unit": unit,
            "Minimum Price (SAR)": min_price,
            "Maximum Price (SAR)": max_price,
            "Current Average Price (SAR)": avg_price
        }

    except Exception as e:
        st.error(f"⚠️ Failed to fetch product: {product_name}\nError: {str(e)}")
        return None


def fetch_all_products_parallel(product_list):
    material_data = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    total = len(product_list)
    completed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_single_product_data, product): product for product in product_list}

        for future in concurrent.futures.as_completed(futures):
            material = future.result()
            if material:
                material_data.append(material)

            completed += 1
            progress = completed / total
            progress_bar.progress(progress)
            status_text.text(f"🔄 Loading {completed} of {total} products...")

    progress_bar.empty()
    status_text.success("✅ Market Report Loaded Successfully!")

    return material_data
