import json
import streamlit as st
import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta



from ai_dev_app.helpers.openai_helpers import get_today_price_estimate_from_ai

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

st.markdown("### 🏗️ Saudi Building Materials FRJAR AI Pricing")

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
                min_price = selected_product["min_price"]
                max_price = selected_product["max_price"]
                unit = selected_product.get('unit', category.get('unit', '—'))
                name = selected_product["name"]


                def get_color(val, ref):
                    return "green" if val > ref else "red" if val < ref else "gray"


                # ✅ Get AI-estimated daily price
                today_price = get_today_price_estimate_from_ai(
                    product_name=name,
                    unit=unit,
                    min_price=min_price,
                    max_price=max_price,
                    median=avg,  # removed median, using average instead
                    average=avg
                )

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
                col1.markdown(
                    f"<div class='stat-block {get_color(min_price, avg)}'>{min_price:.2f} SAR<span class='stat-label'>Min Price</span></div>",
                    unsafe_allow_html=True)
                col2.markdown(
                    f"<div class='stat-block {get_color(max_price, avg)}'>{max_price:.2f} SAR<span class='stat-label'>Max Price</span></div>",
                    unsafe_allow_html=True)
                col3.markdown(
                    f"<div class='stat-block gray'>{avg:.2f} SAR<span class='stat-label'>Average</span></div>",
                    unsafe_allow_html=True)
                if today_price:
                    col4.markdown(
                        f"<div class='stat-block green'>{today_price:.2f} SAR<span class='stat-label'>AI Price Today</span></div>",
                        unsafe_allow_html=True
                    )
                else:
                    col4.markdown(
                        "<div class='stat-block red'>—<span class='stat-label'>AI Price Today</span></div>",
                        unsafe_allow_html=True
                    )

                col5.markdown(f"<div class='stat-block gray'>{unit}<span class='stat-label'>Unit</span></div>",
                              unsafe_allow_html=True)


                def draw_price_comparison_chart(today_price: float, average_price: float):
                    import matplotlib.pyplot as plt
                    import streamlit as st

                    # ✅ Fallback to 0 if None
                    today_price = today_price or 0.0
                    average_price = average_price or 0.0

                    labels = ["Average Price", "AI Today Price"]
                    values = [average_price, today_price]
                    colors = ["#a9c5bc", "#275e56"]

                    diff = today_price - average_price
                    percent = (diff / average_price) * 100 if average_price else 0
                    color = "#007e5b" if diff > 0 else "#c9302c" if diff < 0 else "#666"

                    st.markdown("### 📊 Price Comparison Chart")

                    with st.container():
                        fig, ax = plt.subplots(figsize=(5.8, 4))
                        bars = ax.bar(labels, values, color=colors, width=0.5)

                        max_val = max(values)

                        for bar in bars:
                            yval = bar.get_height()
                            ax.text(bar.get_x() + bar.get_width() / 2, yval + max_val * 0.02,
                                    f"{yval:.2f} SAR", ha='center', va='bottom', fontsize=11, fontweight='bold')

                        ax.text(1, max_val + max_val * 0.08,
                                f"{abs(percent):.1f}%", color=color,
                                fontsize=12, ha='center', fontweight='bold')

                        ax.set_ylim(0, max_val + max_val * 0.15)
                        ax.set_title("AI Price vs Average", fontsize=13, weight='bold')
                        ax.set_ylabel("SAR")
                        ax.spines[['top', 'right']].set_visible(False)
                        ax.grid(axis='y', linestyle='--', alpha=0.3)

                        st.pyplot(fig)


                draw_price_comparison_chart(today_price, avg)

