import streamlit as st
import pandas as pd

def tab3_manual_entry():
    st.header("📝 Manual Daily Price Entry")

    if "manual_data" not in st.session_state:
        st.session_state.manual_data = []

    with st.form("manual_entry_form"):
        entry_date = st.date_input("Date")
        material_name = st.text_input("Material Name", placeholder="e.g., Cement")
        price = st.number_input("Price (SAR)", min_value=0.0, step=0.01)
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Submit")

    if submitted:
        st.session_state.manual_data.append({
            "Date": entry_date,
            "Material": material_name,
            "Price (SAR)": price,
            "Notes": notes
        })
        st.success(f"✅ Submitted: {material_name} ({price:.2f} SAR)")

    if st.session_state.manual_data:
        df = pd.DataFrame(st.session_state.manual_data)
        st.dataframe(df, use_container_width=True)
