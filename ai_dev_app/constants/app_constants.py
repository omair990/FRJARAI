import os
import streamlit as st

class AppConstants:
    # Default products if no file uploaded
    DEFAULT_PRODUCTS = [
        "Cement", "Bricks", "Steel", "Tiles", "Concrete", "Paint", "Wood", "Pipes", "Doors", "Windows"
    ]

    # Supplier API URL
    SUPPLIER_SEARCH_URL = "https://frjar-customer-api-225f2577339d.herokuapp.com/api/customer/product/searchSuggestionByName"

    # Default country for AI analysis and forecast
    COUNTRY_NAME = "Saudi Arabia"

    # Forecast years
    PAST_YEARS = 3
    FUTURE_YEARS = 3

    # OpenAI settings
    OPENAI_MODEL = "gpt-4o"
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

    # Gemini (Google AI) settings
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    GEMINI_MODEL = "gemini-2.0-flash"

    # Groq settings
    GROQ_MODEL = "llama3-70b-8192"
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

    # DeepSeek settings
    DEEPSEEK_MODEL = "deepseek-chat"
    DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]

    # Session backup
    SESSION_BACKUP_FILE = "cache/session_backup.json"
