import streamlit as st
from ai_dev_app.services.market_service import fetch_all_products_parallel
from ai_dev_app.helpers.smart_cleaner import smart_clean_building_data  # ✅ new import

def fetch_market_data(product_list, products_per_page):
    start_idx = st.session_state.page * products_per_page
    end_idx = start_idx + products_per_page
    current_products = product_list[start_idx:end_idx]

    if not current_products:
        st.warning("⚠️ No products selected to fetch.")
        return

    # ✅ Auto-format list of strings to expected dict format
    if isinstance(current_products[0], str):
        current_products = [{"Product Name": name, "Category": ""} for name in current_products]

    if "full_material_data" not in st.session_state:
        st.session_state.full_material_data = []

    with st.spinner("🔄 Fetching Market Data..."):
        raw_data = fetch_all_products_parallel(current_products)

    if raw_data:
        # ✅ Apply smart cleanup
        cleaned_data = smart_clean_building_data(raw_data)

        st.session_state.full_material_data.extend(cleaned_data.to_dict(orient="records"))
        st.success(f"✅ Loaded and cleaned {len(cleaned_data)} products.")
    else:
        st.warning("⚠️ No data fetched. Check API limits or fallback models.")
