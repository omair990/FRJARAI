import json
import streamlit as st
import matplotlib.pyplot as plt
from datetime import date
from ai_dev_app.helpers.openai_helpers import get_today_price_summary_from_ai, _daily_price_history

st.set_page_config(page_title="Saudi Construction Market", layout="wide")

# --- DAILY CACHE RESET ---
today_key = date.today().isoformat()
if _daily_price_history.get("date") != today_key:
    _daily_price_history.clear()
    _daily_price_history["date"] = today_key

# --- Custom CSS ---
st.markdown("""
<style>
div[data-baseweb="tab-list"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    white-space: nowrap !important;
    gap: 2rem !important;
    padding: 1.2rem 1rem !important;
    border: 1px solid #444 !important;
    border-radius: 16px !important;
    background-color: #111 !important;
    scroll-behavior: smooth;
}
div[data-baseweb="tab-list"]::-webkit-scrollbar { height: 6px; }
div[data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
    background: #555;
    border-radius: 10px;
}
div[data-baseweb="tab"] button {
    font-size: 30px !important;
    font-weight: 800 !important;
    padding: 20px 30px !important;
    min-width: max-content !important;
    color: #fff !important;
    background: transparent !important;
    border: none !important;
    position: relative;
}
div[data-baseweb="tab"] button[aria-selected="true"] {
    color: #f55a4e !important;
}
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

st.markdown("""
<h1 style='font-size: 44px; font-weight: 900; color: #fff;'>
🏗️ Saudi Building Materials <span style='color:#f55a4e;'>FRJAR AI Pricing</span>
</h1>
""", unsafe_allow_html=True)

# --- Load data ---
with open("assets/final_materials_with_forecast.json", "r") as f:
    raw_data = json.load(f)
categories = raw_data["materials"]

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
            selected_name = st.radio("Choose one product", product_names, key=f"{category['name']}_{tabs.index(tab)}")
            selected_product = next((p for p in products if p["name"] == selected_name), None)

        if selected_product:
            with right:
                avg = selected_product["average"]
                min_price = selected_product["min_price"]
                max_price = selected_product["max_price"]
                unit = selected_product.get("unit", category.get("unit", "—"))
                name = selected_product["name"]

                cache_key = f"{name}::{unit}"
                summary = _daily_price_history.get(cache_key)

                # ---- If not cached → calculate ----
                if not summary:
                    summary = get_today_price_summary_from_ai(
                        product_name=name,
                        unit=unit,
                        min_price=min_price,
                        max_price=max_price,
                        median=avg,
                        average=avg
                    )
                    # Save result to cache
                    if isinstance(summary, dict):
                        _daily_price_history[cache_key] = summary
                        _daily_price_history["date"] = today_key
                        with open("assets/price_history.json", "w") as f:
                            json.dump(_daily_price_history, f, indent=2)

                if isinstance(summary, dict):
                    today_price = summary.get("today_price")
                    ai_min = summary.get("min_price")
                    ai_max = summary.get("max_price")
                    ai_avg = summary.get("average_price")
                else:
                    today_price = None
                    ai_min = ai_max = ai_avg = None

                # --- Your colors and layout ---
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
                    col4.markdown(f"<div class='stat-block green'>{today_price:.2f} SAR<span class='stat-label'>AI Price Today (Idea)</span></div>", unsafe_allow_html=True)
                else:
                    col4.markdown("<div class='stat-block red'>—<span class='stat-label'>AI Price Today</span></div>", unsafe_allow_html=True)

                col5.markdown(f"<div class='stat-block gray'>{unit}<span class='stat-label'>Unit</span></div>", unsafe_allow_html=True)

                if ai_min and ai_max and ai_avg:
                    st.markdown(
                        f"""<div style="background:#222;padding:10px;border-radius:8px;color:#ccc;">
                        🔎 <strong>AI Price Range Idea</strong>: Min: {ai_min:.2f} SAR | Max: {ai_max:.2f} SAR | Avg: {ai_avg:.2f} SAR
                        </div>""",
                        unsafe_allow_html=True
                    )

                # --- Chart ---
                def draw_price_comparison_chart(today_price, average_price):
                    today_price = today_price or 0.0
                    average_price = average_price or 0.0
                    labels = ["Average Price", "AI Today Price"]
                    values = [average_price, today_price]
                    colors = ["#a9c5bc", "#275e56"]
                    diff = today_price - average_price
                    percent = (diff / average_price) * 100 if average_price else 0

                    show_percent = abs(percent) >= 0.05 and abs(diff) >= 0.5

                    st.markdown("### 📊 Price Comparison Chart")
                    fig, ax = plt.subplots(figsize=(5.8, 4))
                    bars = ax.bar(labels, values, color=colors, width=0.5)

                    max_val = max(values) or 1
                    for bar in bars:
                        yval = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width() / 2, yval + max_val * 0.02,
                                f"{yval:.2f} SAR", ha='center', va='bottom', fontsize=11, fontweight='bold')

                    if show_percent:
                        color = "#007e5b" if diff > 0 else "#c9302c"
                        ax.text(1, max_val + max_val * 0.08,
                                f"{abs(percent):.1f}%", color=color,
                                fontsize=12, ha='center', fontweight='bold')

                    ax.set_ylim(0, max_val + max_val * 0.15)
                    ax.set_title("AI Price vs Average", fontsize=13, weight='bold')
                    ax.set_ylabel("SAR")
                    ax.spines[['top', 'right']].set_visible(False)
                    ax.grid(axis='y', linestyle='--', alpha=0.3)
                    st.pyplot(fig)
                    plt.close(fig)

                draw_price_comparison_chart(today_price, avg)

                # --- Suppliers tabs ---
                with left:
                    st.markdown("### 🏢 Available Wholesale Suppliers")

                    suppliers = selected_product.get("suppliers", [])
                    second_layer = selected_product.get("second_layer_wholesale_suppliers", [])

                    supplier_tabs = st.tabs(
                        ["🔹 Main Wholesale Suppliers", "🔸 Bulk / Secondary Wholesale Suppliers"]
                    )

                    with supplier_tabs[0]:
                        if suppliers:
                            for supplier in suppliers:
                                s_name = supplier.get("name", "—")
                                s_location = supplier.get("location", "—")
                                website = supplier.get("website", None)

                                st.markdown(f"""
                                <div style="border:1px solid #555; border-radius:10px; padding:10px; margin-bottom:8px; background-color:#222;">
                                    <strong style="font-size:16px; color:#f55a4e;">{s_name}</strong><br>
                                    <span style="color:#ccc;">📍 {s_location}</span><br>
                                    {"🌐 <a href='" + website + "' target='_blank' style='color:#4db8ff;'>Visit Website</a>" if website else ""}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No main wholesale suppliers listed.")

                    with supplier_tabs[1]:
                        if second_layer:
                            for wholesaler in second_layer:
                                name = wholesaler.get("name", "—")
                                location = wholesaler.get("location", "—")
                                description = wholesaler.get("description", "—")
                                website = wholesaler.get("website", None)
                                email = wholesaler.get("email", "—")
                                sales_email = wholesaler.get("sales_email", None)
                                phone = wholesaler.get("phone", "—")
                                landline = wholesaler.get("landline", "—")
                                toll_free = wholesaler.get("toll_free", None)

                                st.markdown(f"""
                                <div style="border:2px solid #444; border-radius:10px; padding:12px; margin-bottom:10px; background-color:#222;">
                                    <strong style="font-size:17px; color:#4db8ff;">{name}</strong><br>
                                    <span style="color:#ccc;">📍 {location}</span><br>
                                    <em style="color:#aaa;">{description}</em><br><br>
                                    {"🌐 <a href='" + website + "' target='_blank' style='color:#4db8ff;'>Visit Website</a><br>" if website else ""}
                                    <br><p>📧 <strong>Email:</strong> {email}</p>
                                    {f"<p>📧 <strong>Sales Email:</strong> {sales_email}</p>" if sales_email else ""}
                                    <p>📞 <strong>Phone:</strong> {phone}</p>
                                    {f"<p>☎ <strong>Landline:</strong> {landline}</p>" if landline else ""}
                                    {f"<p>📞 <strong>Toll Free:</strong> {toll_free}</p>" if toll_free else ""}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No secondary wholesale suppliers listed.")
