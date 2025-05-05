import streamlit as st
import json
from ai_dev_app.helpers.openai_helpers import get_today_price_estimate_from_ai

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session handling

app.register_blueprint(chatbot_bp)

@app.route('/')
def index():
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)
