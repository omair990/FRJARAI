from flask import Blueprint, request, jsonify, session
from chatbot import ai_engine

chatbot_bp = Blueprint('chatbot_bp', __name__)

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')

    if not user_input.strip():
        return jsonify({"response": "Please enter a message."})

    # Keep chat history (optional, keeps last 10)
    if 'chat_history' not in session:
        session['chat_history'] = []

    if len(session['chat_history']) > 10:
        session['chat_history'] = session['chat_history'][-10:]

    session['chat_history'].append({"role": "user", "content": user_input})

    # Get reply from AI engine
    reply = ai_engine.ask_ai(user_input)

    session['chat_history'].append({"role": "assistant", "content": reply})

    return jsonify({"response": reply})
