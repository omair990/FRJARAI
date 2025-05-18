import sys
import os

# Add the root project folder (one level up from HomeScreen) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



import streamlit as st
from ai_dev_app.helpers.openai_helpers import get_today_price_estimate_from_ai
from HomeScreen.components.styles import apply_custom_css
from HomeScreen.components.ui import render_title, draw_product_section

st.set_page_config(page_title="Saudi Construction Market", layout="wide")

# Apply CSS & Title
apply_custom_css()
render_title()

# Load and Display
from HomeScreen.utils.data_loader import load_materials
categories = load_materials("assets/final_materials_with_forecast.json")
tabs = st.tabs([cat["name"] for cat in categories])

for tab, category in zip(tabs, categories):
    with tab:
        draw_product_section(category, get_today_price_estimate_from_ai)
