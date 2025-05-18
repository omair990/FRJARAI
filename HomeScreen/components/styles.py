import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
    /* Make the tab bar scrollable instead of wrapping */
    div[data-baseweb="tab-list"] {
        display: flex !important;
        flex-wrap: nowrap !important;   /* 🛑 Prevent wrapping */
        overflow-x: auto !important;    /* ✅ Enable scrolling */
        white-space: nowrap !important;
        gap: 2rem !important;
        padding: 1.2rem 1rem !important;
        border: 1px solid #444 !important;
        border-radius: 16px !important;
        background-color: #111 !important;
        scroll-behavior: smooth;
    }

    /* Scrollbar styling */
    div[data-baseweb="tab-list"]::-webkit-scrollbar {
        height: 6px;
    }
    div[data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
        background: #555;
        border-radius: 10px;
    }

    /* Tab buttons (normal and selected) */
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

    /* Selected tab styling */
    div[data-baseweb="tab"] button[aria-selected="true"] {
        color: #f55a4e !important;
    }

    /* Red underline under selected tab */
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

