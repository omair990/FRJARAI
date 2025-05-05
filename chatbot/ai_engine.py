from chatbot.prompt_builder import build_frjar_prompt
from ai_dev_app.helpers import openai_helpers
import json

# Optional: If you want to load the knowledge base here
with open('assets/final_materials_with_forecast.json', 'r') as f:
    material_data = json.load(f)

def ask_local_model(user_input):
    # Example logic to simulate local model (replace with real code!)
    keywords = ["cement", "steel", "sand"]
    if any(word in user_input.lower() for word in keywords):
        return None  # Simulate no match
    return None

def ask_ai(user_input):
    # First: Try local model
    local_reply = ask_local_model(user_input)
    if local_reply:
        return local_reply

    # Second: Build the prompt for OpenAI / Groq / etc.
    prompt = build_frjar_prompt(user_input)
    reply = openai_helpers.ask_ai(prompt)

    if not reply:
        reply = "⚠️ FRJAR Assistant: Sorry, I couldn't find the information you requested."

    return reply
