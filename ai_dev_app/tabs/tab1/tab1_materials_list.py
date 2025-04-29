import streamlit as st
from ai_dev_app.tabs.tab1.tab1_upload_and_pagination import upload_and_paginate
from ai_dev_app.tabs.tab1.tab1_market_fetching import fetch_market_data
from ai_dev_app.tabs.tab1.tab1_display_and_download import display_market_report

def tab1_materials_list(default_product_list):
    st.header("🏗️ Building Materials Market Report (AI Verified)")

    final_product_list, products_per_page = upload_and_paginate(default_product_list)

    if not final_product_list:
        st.info("ℹ️ No products found. Please upload or select products.")
        return

    # ✅ Load Market Report
    if st.button("🔍 Load Market Report"):
        fetch_market_data(final_product_list, products_per_page)

    # ✅ Display Market Report
    if "full_material_data" in st.session_state and st.session_state.full_material_data:
        display_market_report(st.session_state.full_material_data)
