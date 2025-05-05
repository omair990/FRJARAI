import streamlit as st
import json
from ai_dev_app.helpers.openai_helpers import get_today_price_estimate_from_ai

st.set_page_config(page_title="FRJAR AI Assistant", layout="wide")

st.title("👷 FRJAR – Saudi Construction Assistant")

user_input = st.text_input("Ask about construction materials (e.g., cement, steel)")

if st.button("Send"):
    if user_input.strip():
        st.markdown(f"**You:** {user_input}")

        # Example AI response
        ai_reply = get_today_price_estimate_from_ai(
            product_name=user_input,
            unit="Bag",
            min_price=10,
            max_price=25,
            median=18,
            average=18
        )

        st.markdown(f"**FRJAR:** Today's estimated price is **{ai_reply:.2f} SAR**")
    else:
        st.warning("Please enter a valid message.")
