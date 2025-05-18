import streamlit as st
import matplotlib.pyplot as plt
from HomeScreen.components.suppliers import render_suppliers_tabs
from HomeScreen.components.pricing import render_price_cards, draw_price_chart

def render_title():
    st.markdown("""
    <h1 style='font-size: 44px; font-weight: 900; color: #fff;'>
    🏗️ Saudi Building Materials <span style='color:#f55a4e;'>FRJAR AI Pricing</span>
    </h1>
    """, unsafe_allow_html=True)

def draw_product_section(category, get_price_fn):
    products = category.get("products", [])
    if not products:
        st.warning("No products found.")
        return

    left, right = st.columns([1, 2])

    with left:
        st.markdown("#### 📦 **Select Product**")
        product_names = [p["name"] for p in products]
        selected_name = st.radio("Choose one product", product_names)
        selected_product = next((p for p in products if p["name"] == selected_name), None)

        st.markdown("#### 🌍 **Select City**")
        selected_city = st.selectbox(
            "Choose a city",
            options=["National Average", "Riyadh", "Jeddah", "Makkah", "Dammam", "Medina"],
            key=f"city_selector_{category['name']}"
        )

    if not selected_product:
        return

    # --- Calculate city-specific prices ---
    base_min = selected_product.get("min_price", 0)
    base_max = selected_product.get("max_price", 0)
    city_margins = selected_product.get("city_margins", {})

    margin = city_margins.get(selected_city, {}) if selected_city != "National Average" else {}
    min_margin = margin.get("min_margin_percent", 0)
    max_margin = margin.get("max_margin_percent", 0)

    min_price = base_min + (base_min * min_margin / 100)
    max_price = base_max + (base_max * max_margin / 100)
    avg_price = (min_price + max_price) / 2

    # --- Get AI price with city ---
    price_data = get_price_fn(selected_product, city=selected_city)
    today_price = price_data.get("today_price")

    with right:
        render_price_cards(
            min_price,
            max_price,
            avg_price,
            today_price,
            selected_product.get("unit", "—"),
            city=selected_city  # ✅ <-- now passed
        )
        draw_price_chart(today_price, avg_price)

    with left:
        render_suppliers_tabs(selected_product, selected_city)
