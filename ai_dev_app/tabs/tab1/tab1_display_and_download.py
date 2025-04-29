import streamlit as st
import pandas as pd

def display_market_report(material_data):
    st.header("🏗️ Saudi Construction Materials Market Report")

    if not material_data:
        st.info("ℹ️ No data to display. Please load the products first.")
        return

    # ✅ Main Summary Table (Only Price Details)
    df_material = pd.DataFrame(material_data)

    st.subheader("📋 Products Price Overview")
    st.dataframe(
        df_material[[
            "Product Name",
            "Unit",
            "Minimum Price (SAR)",
            "Maximum Price (SAR)",
            "Current Average Price (SAR)"
        ]],
        use_container_width=True
    )

    # ✅ Individual Product Simple View
    st.subheader("🔎 Detailed View per Product")

    for material in material_data:
        product_name = material.get("Product Name")
        unit = material.get("Unit", "Unit")
        min_price = material.get("Minimum Price (SAR)", 0)
        max_price = material.get("Maximum Price (SAR)", 0)
        avg_price = material.get("Current Average Price (SAR)", 0)

        with st.expander(f"📦 {product_name}"):
            st.markdown(f"**Unit:** {unit}")
            st.markdown(f"**Minimum Price (SAR):** {min_price}")
            st.markdown(f"**Maximum Price (SAR):** {max_price}")
            st.markdown(f"**Current Average Price (SAR):** {avg_price}")
