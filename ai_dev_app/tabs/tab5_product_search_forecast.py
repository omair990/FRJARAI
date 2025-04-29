import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
from ai_dev_app.helpers.openai_helpers import generate_forecast_from_openai, get_real_product_price_from_openai
from ai_dev_app.helpers.frjar_helpers import search_frjar_api

def tab5_product_search_forecast():
    st.header("🔎 Product Search and Forecast")

    with st.form("search_form"):
        product_name = st.text_input("Enter Product Name", placeholder="e.g., Cement")
        country = st.text_input("Country", placeholder="e.g., Saudi Arabia", value="Saudi Arabia")
        past_years = st.number_input("Past Years", min_value=1, max_value=10, value=3)
        future_years = st.number_input("Future Years", min_value=1, max_value=10, value=3)
        submitted = st.form_submit_button("Get Forecast")

    if submitted:
        current_price = get_real_product_price_from_openai(product_name)

        st.success(f"**Current Price Found:** {current_price} SAR")

        frjar_results = search_frjar_api(product_name)
        if frjar_results:
            st.subheader("📦 FRJAR Products Found")
            st.dataframe(pd.DataFrame(frjar_results))

        forecast = generate_forecast_from_openai(product_name, country, past_years, future_years)

        if forecast:
            st.subheader("📅 Past Prices")
            st.table(forecast.get("past_prices", {}))

            st.subheader("🔮 Future Prices")
            st.table(forecast.get("future_prices", {}))

            export_df = pd.DataFrame({
                "Year": list(forecast.get('past_prices', {}).keys()) + list(forecast.get('future_prices', {}).keys()),
                "Price (SAR)": list(forecast.get('past_prices', {}).values()) + list(forecast.get('future_prices', {}).values())
            })

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                export_df.to_excel(writer, index=False)
            buffer.seek(0)

            st.download_button("📥 Download Forecast as Excel", buffer, "forecast.xlsx", "application/vnd.ms-excel")

            if forecast.get('past_prices') or forecast.get('future_prices'):
                plt.figure(figsize=(10, 5))
                plt.plot(list(map(int, forecast.get('past_prices', {}).keys())), list(forecast.get('past_prices', {}).values()), marker='o', label="Past")
                plt.plot(list(map(int, forecast.get('future_prices', {}).keys())), list(forecast.get('future_prices', {}).values()), marker='o', linestyle='--', label="Future")
                plt.title(f"Forecast: {product_name}")
                plt.legend()
                st.pyplot(plt)
