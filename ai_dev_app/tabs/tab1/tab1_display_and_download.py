import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def display_market_report(material_data):
    if not material_data:
        st.warning("⚠️ No data available.")
        return

    df = pd.DataFrame(material_data)

    # 🟩 Extract and select category
    categories = df["Category"].dropna().unique().tolist()
    if "selected_category" not in st.session_state:
        st.session_state.selected_category = categories[0]
    selected_category = st.session_state.selected_category

    # ✅ Styled horizontal category buttons
    st.markdown("""
        <style>
        div.stButton > button {
            margin: 0.3rem;
            padding: 8px 20px;
            border-radius: 6px;
            font-weight: 600;
            border: none;
        }
        </style>
    """, unsafe_allow_html=True)

    cat_cols = st.columns(len(categories))
    for i, cat in enumerate(categories):
        bg = "#005F56" if cat == selected_category else "#e8e8e8"
        fg = "white" if cat == selected_category else "black"
        with cat_cols[i]:
            if st.button(f"{cat}", key=f"cat_{cat}"):
                st.session_state.selected_category = cat
                selected_category = cat

    df_filtered = df[df["Category"] == selected_category]

    if df_filtered.empty:
        st.info("No data for this category.")
        return

    # ✅ Summary Price Cards
    min_price = df_filtered["Minimum Price (SAR)"].min()
    max_price = df_filtered["Maximum Price (SAR)"].max()
    avg_price = df_filtered["Current Average Price (SAR)"].mean()
    median_price = df_filtered["Current Average Price (SAR)"].median()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔻 Min Price", f"{min_price:.2f} SAR")
    c2.metric("🔺 Max Price", f"{max_price:.2f} SAR")
    c3.metric("📊 Avg Price", f"{avg_price:.2f} SAR")
    c4.metric("📈 Median", f"{median_price:.2f} SAR")

    # ✅ Price Bar Chart
    st.markdown("### 📊 Price Chart")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df_filtered["Product Name"], df_filtered["Current Average Price (SAR)"], color='teal')
    ax.set_title(f"{selected_category} - Average Prices", fontsize=14)
    ax.set_ylabel("Price (SAR)")
    ax.set_xticklabels(df_filtered["Product Name"], rotation=45, ha="right")
    st.pyplot(fig)

    # ✅ Detailed View
    st.markdown("### 🧾 Product Breakdown")
    for _, row in df_filtered.iterrows():
        with st.expander(f"📦 {row['Product Name']}"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Min", f"{row['Minimum Price (SAR)']:.2f} SAR")
            c2.metric("Max", f"{row['Maximum Price (SAR)']:.2f} SAR")
            c3.metric("Avg", f"{row['Current Average Price (SAR)']:.2f} SAR")
            st.markdown(f"**Unit:** {row['Unit']}")
