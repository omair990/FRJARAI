import time
import concurrent.futures
import streamlit as st

from ai_dev_app.helpers.openai_helpers import get_verified_unit_and_price_for_product

MAX_RETRIES = 5

def fetch_single_product_data(row):
    product_name = ""
    try:
        product_name = row.get("Product Name", "").strip()
        category = row.get("Category", "").strip()

        if not product_name:
            return None

        query = f"{product_name} - {category}" if category else product_name

        retry = 0
        verified_info = None

        while retry < MAX_RETRIES:
            verified_info = get_verified_unit_and_price_for_product(query)
            if verified_info:
                break
            retry += 1
            time.sleep(1)

        if not verified_info:
            return None

        unit = verified_info.get("unit", "N/A")
        base_price = verified_info.get("price_sar", 0)

        avg_price = base_price
        min_price = round(base_price * 0.97, 2)
        max_price = round(base_price * 1.03, 2)

        return {
            "Product Name": product_name,
            "Category": category,
            "Unit": unit,
            "Minimum Price (SAR)": min_price,
            "Maximum Price (SAR)": max_price,
            "Current Average Price (SAR)": avg_price
        }

    except Exception as e:
        st.error(f"⚠️ Failed to fetch product: {product_name or 'Unknown'}\nError: {str(e)}")
        return None

def fetch_all_products_parallel(product_rows):
    material_data = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    total = len(product_rows)
    completed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(fetch_single_product_data, row): row
            for row in product_rows
        }

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
