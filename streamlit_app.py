import json
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Saudi Construction Market", layout="wide")

# ✅ Enhanced CSS for full-width tabs + styled product card
st.markdown("""
<style>
/* Body padding */
.block-container {
    padding-top: 2.5rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Full-width tab container with padding and rounded background */
div[data-baseweb="tab-list"] {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 10px;
    padding: 1rem;
    background-color: #0000;
    border-radius: 10px;
    border: 1px solid #d0e0dd;
}

/* Inactive tabs: light background, dark text */
div[data-baseweb="tab"] button {
    width: 100%;
    font-size: 16px !important;
    font-weight: 700 !important;
    padding: 12px !important;
    border-radius: 8px !important;
    background-color: #ffffff !important;
    color: #065f55 !important;
    border: 2px solid #d5e7e4 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    transition: all 0.2s ease;
}

/* Selected tab looks like green block with white text */
div[data-baseweb="tab"] button[aria-selected="true"] {
    background-color: #275e56 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
    padding: 16px 24px !important;
    border: none !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    text-align: center;
}

/* Product radio styling */
section[data-testid="stRadio"] {
    background: #fdfdfd;
    border: 1px solid #ddd;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    margin-top: 1rem;
}
section[data-testid="stRadio"] label {
    font-size: 17px !important;
    font-weight: 600;
    padding: 8px 4px;
    color: #222;
}
</style>
""", unsafe_allow_html=True)

# ✅ Load data
with open("assets/final_materials_with_forecast.json", "r") as f:
    raw_data = json.load(f)

categories = raw_data["materials"]

st.markdown("### 🏗️ Saudi Building Materials Pricing (2013–2025)")

# ✅ Horizontal Tabs (Category)
tab_objs = st.tabs([cat["name"] for cat in categories])

for tab, category in zip(tab_objs, categories):
    with tab:
        products = category.get("products", [])
        if not products:
            st.warning("No products found for this category.")
            continue

        left, right = st.columns([1, 2])

        with left:
            st.markdown("#### 📦 **Select Product**")
            product_names = [p["name"] for p in products]
            selected_product_name = st.radio(
                "Choose one product only", product_names, key=category["name"]
            )
            selected_product = next((p for p in products if p["name"] == selected_product_name), None)

        if selected_product:
            with right:
                avg = selected_product["average"]
                median = selected_product["median"]
                min_price = selected_product["min_price"]
                max_price = selected_product["max_price"]

                def get_color(val, ref):
                    return "green" if val > ref else "red" if val < ref else "gray"

                # --- Styled value blocks
                st.markdown("""
                <style>
                .stat-block {
                    border-radius: 10px;
                    padding: 1rem;
                    text-align: center;
                    font-size: 18px;
                    font-weight: bold;
                    height: 100px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
                }
                .stat-label {
                    font-size: 14px;
                    font-weight: 600;
                    margin-top: 6px;
                    display: block;
                }
                .green { background: #e0f8f1; color: #007e5b; border: 2px solid #9fe1cd; }
                .red { background: #fdeceb; color: #c9302c; border: 2px solid #f5b9b8; }
                .gray { background: #f3f3f3; color: #333; border: 2px solid #ccc; }
                </style>
                """, unsafe_allow_html=True)

                col1, col2, col3, col4, col5 = st.columns(5)
                col1.markdown(f"<div class='stat-block {get_color(min_price, avg)}'>{min_price:.2f} SAR<span class='stat-label'>Min Price</span></div>", unsafe_allow_html=True)
                col2.markdown(f"<div class='stat-block {get_color(max_price, avg)}'>{max_price:.2f} SAR<span class='stat-label'>Max Price</span></div>", unsafe_allow_html=True)
                col3.markdown(f"<div class='stat-block gray'>{selected_product.get('unit', category.get('unit', '—'))}<span class='stat-label'>Unit</span></div>", unsafe_allow_html=True)
                col4.markdown(f"<div class='stat-block {get_color(median, avg)}'>{median:.2f} SAR<span class='stat-label'>Median</span></div>", unsafe_allow_html=True)
                col5.markdown(f"<div class='stat-block gray'>{avg:.2f} SAR<span class='stat-label'>Average</span></div>", unsafe_allow_html=True)

                # --- Graph
                st.markdown("#### 📈 Forecasted Price Trend (2013–2025)")
                fig, ax = plt.subplots(figsize=(5.5, 2.7))
                years = list(range(2013, 2026))
                trend = [avg * (1 + 0.01 * (i % 8 - 4)) for i in range(len(years))]

                ax.plot(years, trend, marker='o', label=selected_product["name"])
                ax.set_xlabel("Year")
                ax.set_ylabel("Price (SAR)")
                ax.set_title(f"{selected_product['name']} Price Forecast")
                ax.legend()
                st.pyplot(fig)
