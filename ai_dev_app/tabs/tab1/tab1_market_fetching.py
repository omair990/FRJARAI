import streamlit as st
from ai_dev_app.services.market_service import fetch_all_products_parallel

def fetch_market_data(product_list, products_per_page):
    start_idx = st.session_state.page * products_per_page
    end_idx = start_idx + products_per_page
    current_products = product_list[start_idx:end_idx]

    if not current_products:
        st.warning("⚠️ No products selected to fetch.")
        return

    if "full_material_data" not in st.session_state:
        st.session_state.full_material_data = []

    with st.spinner("🔄 Fetching Market Data..."):
        material_data = fetch_all_products_parallel(current_products)

    if material_data:
        st.session_state.full_material_data.extend(material_data)
        st.success(f"✅ Loaded {len(material_data)} products.")
    else:
        st.warning("⚠️ No data fetched. Check API limits or fallback models.")
