import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ai_dev_app.constants.app_constants import AppConstants
from ai_dev_app.services.market_service import fetch_all_products_parallel

# Sample categories
CATEGORIES = [
    "Aluminum", "Black Block", "Cables", "Cement", "Concrete",
    "Gypsum", "Marble Tiles", "Reinforcing Iron", "Sand", "Wires", "Wood"
]

def category_selector():
    st.markdown("## 🏠 Construction Products")
    selected_category = st.selectbox("Select a Category", CATEGORIES, index=0)
    return selected_category

def render_price_boxes(data):
    if not data:
        st.warning("No product data available.")
        return

    min_price = min(item['Minimum Price (SAR)'] for item in data)
    max_price = max(item['Maximum Price (SAR)'] for item in data)
    avg_price = round(sum(item['Current Average Price (SAR)'] for item in data) / len(data), 2)
    median_price = round(pd.DataFrame(data)['Current Average Price (SAR)'].median(), 2)
    unit = data[0].get("Unit", "N/A")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Min Price", f"{min_price:.2f}")
    col2.metric("Max Price", f"{max_price:.2f}")
    col3.metric("Unit", unit)
    col4.metric("Median", f"{median_price:.2f}")
    col5.metric("Average", f"{avg_price:.2f}")

def render_price_chart(data):
    df = pd.DataFrame(data)
    fig = go.Figure()
    for i, row in df.iterrows():
        fig.add_trace(go.Scatter(
            x=[2022, 2023, 2024],
            y=[row['Current Average Price (SAR)'] * 0.95, row['Current Average Price (SAR)'], row['Current Average Price (SAR)'] * 1.05],
            mode='lines+markers',
            name=row['Product Name']
        ))

    fig.update_layout(title="3-Year AI Forecast", xaxis_title="Year", yaxis_title="Price (SAR)")
    st.plotly_chart(fig, use_container_width=True)

def tab1_materials_list(default_product_list):
    st.set_page_config(layout="wide")
    st.title("🏗 Saudi Building Material Dashboard")

    selected_category = category_selector()

    # Simulate filtered product list
    product_list = [{"Product Name": name, "Category": selected_category} for name in default_product_list if selected_category.lower() in name.lower()]

    if not product_list:
        st.info("No products match the selected category.")
        return

    if st.button("🔍 Load Market Report"):
        with st.spinner("Fetching Market Data..."):
            material_data = fetch_all_products_parallel(product_list)
            if material_data:
                st.session_state.full_material_data = material_data

    if "full_material_data" in st.session_state and st.session_state.full_material_data:
        st.markdown("### 💹 Price Summary")
        render_price_boxes(st.session_state.full_material_data)

        st.markdown("### 📊 Historical Chart View")
        render_price_chart(st.session_state.full_material_data)

        st.markdown("### 📋 Detailed Table")
        st.dataframe(pd.DataFrame(st.session_state.full_material_data), use_container_width=True)
