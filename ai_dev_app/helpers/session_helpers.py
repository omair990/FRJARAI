import json
from ai_dev_app.constants.app_constants import AppConstants
import streamlit as st
import os

def save_session():
    data = {
        "uploaded_file_name": st.session_state.get("uploaded_file_name", ""),
        "uploaded_full_df": st.session_state.get("uploaded_full_df", None).to_json() if st.session_state.get("uploaded_full_df") is not None else None,
        "full_material_data": st.session_state.get("full_material_data", []),
        "supplier_data": st.session_state.get("supplier_data", []),
        "loaded_products": st.session_state.get("loaded_products", [])
    }
    with open(AppConstants.SESSION_BACKUP_FILE, "w") as f:
        json.dump(data, f)
    st.success("✅ Session saved successfully!")

def load_session():
    if os.path.exists(AppConstants.SESSION_BACKUP_FILE):
        with open(AppConstants.SESSION_BACKUP_FILE, "r") as f:
            data = json.load(f)
            if data.get("uploaded_full_df"):
                import pandas as pd
                st.session_state.uploaded_full_df = pd.read_json(data["uploaded_full_df"])
            st.session_state.uploaded_file_name = data.get("uploaded_file_name", "")
            st.session_state.full_material_data = data.get("full_material_data", [])
            st.session_state.supplier_data = data.get("supplier_data", [])
            st.session_state.loaded_products = data.get("loaded_products", [])
        st.success("✅ Session restored successfully!")
    else:
        st.error("⚠️ No backup found to load.")
