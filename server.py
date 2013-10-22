from session import RedisSessionInterface
from flask import Flask, render_template, request, session

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    return

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/chat/message', methods=['POST'])
def send_message():
    return

if __name__ == '__main__':
    app.session_interface = RedisSessionInterface()
    app.run(debug=True)

