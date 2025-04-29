import streamlit as st
import pandas as pd

@st.cache_data
def read_uploaded_file(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_excel(uploaded_file)

def upload_and_paginate(default_product_list):
    uploaded_file = st.file_uploader("Upload Excel or CSV File (Optional)", type=["csv", "xlsx"])

    if uploaded_file and (st.session_state.get("uploaded_file_name") != uploaded_file.name):
        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.uploaded_full_df = read_uploaded_file(uploaded_file)

    if st.session_state.get("uploaded_full_df") is not None:
        columns = st.session_state.uploaded_full_df.columns.tolist()
        selected_column = st.selectbox("Select Product Column", columns, key="selected_column")
        selected_products = st.session_state.uploaded_full_df[selected_column].dropna().tolist()
    else:
        selected_products = []

    final_product_list = selected_products if selected_products else default_product_list

    products_per_page = 10
    if "page" not in st.session_state:
        st.session_state.page = 0
    if "loaded_products" not in st.session_state:
        st.session_state.loaded_products = []
    if "full_material_data" not in st.session_state:
        st.session_state.full_material_data = []
    if "supplier_data" not in st.session_state:
        st.session_state.supplier_data = []

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous Page") and st.session_state.page > 0:
            st.session_state.page -= 1
            st.session_state.loaded_products = []
    with col3:
        if st.button("Next Page ➡️") and st.session_state.page < (len(final_product_list) - 1) // products_per_page:
            st.session_state.page += 1
            st.session_state.loaded_products = []

    return final_product_list, products_per_page
