import json
import streamlit as st
import matplotlib.pyplot as plt
from ai_dev_app.helpers.openai_helpers import get_today_price_estimate_from_ai

st.set_page_config(page_title="Saudi Construction Market", layout="wide")

# --- Custom CSS for Big Scrollable Tabs ---
st.markdown("""
<style>
/* Prevent font size shrinking when many tabs exist */
div[data-baseweb="tab-list"] {
    overflow-x: auto !important;
    white-space: nowrap !important;
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 2rem !important;
    padding: 1.5rem 2rem !important;
    background-color: #111 !important;
    border-radius: 16px !important;
    border: 1px solid #444 !important;
    scroll-behavior: smooth;
}

/* Remove scrollbar background */
div[data-baseweb="tab-list"]::-webkit-scrollbar {
    height: 6px;
}
div[data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
    background: #555;
    border-radius: 10px;
}

/* Tab button fixed size */
div[data-baseweb="tab"] button {
    font-size: 32px !important;
    font-weight: 900 !important;
    padding: 24px 36px !important;
    color: #ffffff !important;
    background: transparent !important;
    border: none !important;
    white-space: nowrap !important;
    min-width: max-content !important;
    line-height: 1.4 !important;
}

/* Active tab style */
div[data-baseweb="tab"] button[aria-selected="true"] {
    color: #f55a4e !important;
}

/* Underline for active tab */
div[data-baseweb="tab"] button[aria-selected="true"]::after {
    content: "";
    position: absolute;
    bottom: -6px;
    left: 0;
    width: 100%;
    height: 4px;
    background-color: #f55a4e;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("""
<h1 style='font-size: 44px; font-weight: 900; color: #fff;'>
🏗️ Saudi Building Materials <span style='color:#f55a4e;'>FRJAR AI Pricing</span>
</h1>
""", unsafe_allow_html=True)

# --- Load data ---
with open("assets/final_materials_with_forecast.json", "r") as f:
    raw_data = json.load(f)
categories = raw_data["materials"]

# --- Create Tabs ---
tabs = st.tabs([cat["name"] for cat in categories])

for tab, category in zip(tabs, categories):
    with tab:
        products = category.get("products", [])
        if not products:
            st.warning("No products found.")
            continue

        left, right = st.columns([1, 2])

        with left:
            st.markdown("#### 📦 **Select Product**")
            product_names = [p["name"] for p in products]
            selected_name = st.radio("Choose one product", product_names, key=category["name"])
            selected_product = next((p for p in products if p["name"] == selected_name), None)

        if selected_product:
            with right:
                avg = selected_product["average"]
                min_price = selected_product["min_price"]
                max_price = selected_product["max_price"]
                unit = selected_product.get("unit", category.get("unit", "—"))
                name = selected_product["name"]

                today_price = get_today_price_estimate_from_ai(
                    product_name=name,
                    unit=unit,
                    min_price=min_price,
                    max_price=max_price,
                    median=avg,
                    average=avg
                )

                def get_color(val, ref):
                    return "green" if val > ref else "red" if val < ref else "gray"

                st.markdown("""
                <style>
                .stat-block {
                    border-radius: 10px;
                    padding: 1rem;
                    text-align: center;
                    font-size: 20px;
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
                col3.markdown(f"<div class='stat-block gray'>{avg:.2f} SAR<span class='stat-label'>Average</span></div>", unsafe_allow_html=True)

                if today_price:
                    col4.markdown(f"<div class='stat-block green'>{today_price:.2f} SAR<span class='stat-label'>AI Price Today</span></div>", unsafe_allow_html=True)
                else:
                    col4.markdown("<div class='stat-block red'>—<span class='stat-label'>AI Price Today</span></div>", unsafe_allow_html=True)

                col5.markdown(f"<div class='stat-block gray'>{unit}<span class='stat-label'>Unit</span></div>", unsafe_allow_html=True)

                # --- Draw chart ---
                def draw_price_comparison_chart(today_price, average_price):
                    today_price = today_price or 0.0
                    average_price = average_price or 0.0
                    labels = ["Average Price", "AI Today Price"]
                    values = [average_price, today_price]
                    colors = ["#a9c5bc", "#275e56"]
                    diff = today_price - average_price
                    percent = (diff / average_price) * 100 if average_price else 0
                    color = "#007e5b" if diff > 0 else "#c9302c" if diff < 0 else "#666"

                    st.markdown("### 📊 Price Comparison Chart")
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
                    plt.close(fig)  # ✅ Fix memory leak


                draw_price_comparison_chart(today_price, avg)
