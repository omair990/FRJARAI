from flask import Flask, render_template
from chatbot.routes import chatbot_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session handling

app.register_blueprint(chatbot_bp)

@app.route('/')
def index():
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)
