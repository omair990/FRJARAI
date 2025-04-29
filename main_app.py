import streamlit as st

from ai_dev_app.constants.app_constants import AppConstants
from ai_dev_app.helpers.session_helpers import save_session, load_session

from ai_dev_app.tabs.tab1.tab1_materials_list import tab1_materials_list
from ai_dev_app.tabs.tab2_ai_price_analysis import tab2_ai_price_analysis
from ai_dev_app.tabs.tab3_manual_entry import tab3_manual_entry
from ai_dev_app.tabs.tab4_price_factors import tab4_price_factors
from ai_dev_app.tabs.tab5_product_search_forecast import tab5_product_search_forecast


def main():
    st.set_page_config(page_title="Saudi Building Market Dashboard", layout="wide")

    # Sidebar options
    st.sidebar.header("⚙️ Session Options")
    if st.sidebar.button("💾 Save Session"):
        save_session()

    if st.sidebar.button("♻️ Load Session"):
        load_session()

    # Top-level tabs
    tabs = st.tabs([
        "🏗 Materials List",
        "🧠 AI Price Analysis",
        "📝 Manual Entry",
        "📈 Price Factors",
        "🔎 Product Search & Forecast"
    ])

    # Load default products from constants
    default_product_list = AppConstants.DEFAULT_PRODUCTS

    with tabs[0]:
        tab1_materials_list(default_product_list)

    with tabs[1]:
        tab2_ai_price_analysis()

    with tabs[2]:
        tab3_manual_entry()

    with tabs[3]:
        tab4_price_factors()

    with tabs[4]:
        tab5_product_search_forecast()


if __name__ == "__main__":
    main()
