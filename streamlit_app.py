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
@@ -31,67 +31,66 @@
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
            selected_name = st.radio("Choose one product", product_names, key=f"{category['name']}_{tabs.index(tab)}")

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

                    # ---- NEW: thresholds ----
                    epsilon_percent = 0.05  # below 0.05% difference, don't display
                    epsilon_value = 0.5  # below 0.5 SAR difference, don't display

                    # Decide whether to show the percentage
                    if (
                            average_price >= 0.001 and today_price >= 0.001 and
                            abs(percent) >= epsilon_percent and abs(diff) >= epsilon_value
                    ):
                        percent_display = f"{abs(percent):.1f}%"
                        color = "#007e5b" if diff > 0 else "#c9302c" if diff < 0 else "#666"
                        show_percent = True
                    else:
                        percent_display = ""
                        show_percent = False
                    # ----------------------------

                    st.markdown("### 📊 Price Comparison Chart")
                    fig, ax = plt.subplots(figsize=(5.8, 4))
                    bars = ax.bar(labels, values, color=colors, width=0.5)

                    max_val = max(values) or 1  # Avoid zero max_val

                    for bar in bars:
                        yval = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width() / 2, yval + max_val * 0.02,
                                f"{yval:.2f} SAR", ha='center', va='bottom',
                                fontsize=11, fontweight='bold')

                    if show_percent:
                        ax.text(1, max_val + max_val * 0.08,
                                percent_display, color=color,
                                fontsize=12, ha='center', fontweight='bold')

                    ax.set_ylim(0, max_val + max_val * 0.15)
                    ax.set_title("AI Price vs Average", fontsize=13, weight='bold')
                    ax.set_ylabel("SAR")
                    ax.spines[['top', 'right']].set_visible(False)
                    ax.grid(axis='y', linestyle='--', alpha=0.3)

                    st.pyplot(fig)
                    plt.close(fig)


                draw_price_comparison_chart(today_price, avg)
                with left:
                    st.markdown("### 🏢 Available Suppliers")

                    # Read all three supplier categories from the selected product
                    suppliers = selected_product.get("suppliers", [])
                    second_layer = selected_product.get("second_layer_wholesale_suppliers", [])
                    retail_suppliers = selected_product.get("retail_suppliers", [])

                    # Calculate totals
                    all_wholesale = suppliers + second_layer
                    wholesale_count = len(all_wholesale)
                    retail_count = len(retail_suppliers)

                    # Create tabs with counts
                    supplier_tabs = st.tabs([
                        f"🏢 Wholesale Suppliers ({wholesale_count})",
                        f"🛒 Retail Suppliers ({retail_count})"
                    ])


                    # Function to check valid phone
                    def is_valid_phone(phone):
                        return phone and phone.strip() != "+966 12 123 4567"


                    # --- WHOLESALE SUPPLIERS TAB ---
                    with supplier_tabs[0]:
                        if all_wholesale:
                            for supplier in all_wholesale:
                                name = supplier.get("name", "—")
                                location = supplier.get("location", "—")
                                description = supplier.get("description", "")
                                website = supplier.get("website", None)
                                email = supplier.get("email", None)
                                sales_email = supplier.get("sales_email", None)
                                phone = supplier.get("phone", None)
                                landline = ""
                                toll_free = ""

                                contact_html = ""
                                if email:
                                    contact_html += f"<p>📧 <strong>Email:</strong> <a href='mailto:{email}' style='color:#4db8ff;'>{email}</a></p>"
                                if sales_email:
                                    contact_html += f"<p>📧 <strong>Sales Email:</strong> <a href='mailto:{sales_email}' style='color:#4db8ff;'>{sales_email}</a></p>"
                                if is_valid_phone(phone):
                                    contact_html += f"<p>📞 <strong>Phone:</strong> <a href='tel:{phone}' style='color:#4db8ff;'>{phone}</a></p>"
                                if is_valid_phone(landline):
                                    contact_html += f"<p>☎ <strong>Landline:</strong> <a href='tel:{landline}' style='color:#4db8ff;'>{landline}</a></p>"
                                if is_valid_phone(toll_free):
                                    contact_html += f"<p>📞 <strong>Toll Free:</strong> <a href='tel:{toll_free}' style='color:#4db8ff;'>{toll_free}</a></p>"
                                if not any([email, sales_email, is_valid_phone(phone), is_valid_phone(landline),
                                            is_valid_phone(toll_free)]):
                                    contact_html = "<p style='color:#888;'>No contact information available.</p>"

                                st.markdown(f"""
                                    <div style="border:2px solid #444; border-radius:10px; padding:12px; margin-bottom:10px; background-color:#222;">
                                        <strong style="font-size:17px; color:#4db8ff;">{name}</strong><br>
                                        <span style="color:#ccc;">📍 {location}</span><br>
                                        <em style="color:#aaa;">{description}</em><br><br>
                                        {"🌐 <a href='" + website + "' target='_blank' style='color:#4db8ff;'>Visit Website</a><br>" if website else ""}
                                        {contact_html}
                                    </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No wholesale suppliers listed.")

                    # --- RETAIL SUPPLIERS TAB ---
                    with supplier_tabs[1]:
                        if retail_suppliers:
                            for supplier in retail_suppliers:
                                name = supplier.get("name", "—")
                                location = supplier.get("location", "—")
                                description = supplier.get("description", "")
                                website = supplier.get("website", None)
                                email = supplier.get("email", None)
                                phone = supplier.get("phone", None)

                                contact_html = ""
                                if email:
                                    contact_html += f"<p>📧 <strong>Email:</strong> <a href='mailto:{email}' style='color:#4db8ff;'>{email}</a></p>"
                                if is_valid_phone(phone):
                                    contact_html += f"<p>📞 <strong>Phone:</strong> <a href='tel:{phone}' style='color:#4db8ff;'>{phone}</a></p>"
                                if not any([email, is_valid_phone(phone)]):
                                    contact_html = "<p style='color:#888;'>No contact information available.</p>"

                                st.markdown(f"""
                                    <div style="border:2px solid #444; border-radius:10px; padding:12px; margin-bottom:10px; background-color:#222;">
                                        <strong style="font-size:17px; color:#ffcc00;">{name}</strong><br>
                                        <span style="color:#ccc;">📍 {location}</span><br>
                                        <em style="color:#aaa;">{description}</em><br><br>
                                        {"🌐 <a href='" + website + "' target='_blank' style='color:#4db8ff;'>Visit Website</a><br>" if website else ""}
                                        {contact_html}
                                    </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No retail suppliers listed.")

