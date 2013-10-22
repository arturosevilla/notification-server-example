from session import RedisSessionInterface
from flask import Flask, render_template, request, session, url_for, \
                  redirect, jsonify
from uuid import uuid4
from chat import get_conversation, send_message as do_chat, is_valid_chatroom

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    chatroom = request.form.get('chatroom', '').strip()
    if len(username) == 0:
        return redirect(url_for('index'))
    session['user'] = {
        'user.id': str(uuid4()),
        'name': username
    }
    return redirect(url_for('chat', chatroom=(chatroom or 'intercomunidades')))

@app.route('/user/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/chat/<chatroom>')
def chat(chatroom=None):
    if not is_valid_chatroom(chatroom) or session.get('user') is None:
        return redirect(url_for('index'))
    log = get_conversation(chatroom)
    if log is None:
        return redirect(url_for('index'))
    return render_template('chat.html', messages=log, chatroom=(chatroom or 'intercomunidades'))

@app.route('/chat/<chatroom>/message', methods=['POST'])
def send_message(chatroom=None):
    message = request.json.get('message', '').strip()
    user = session.get('user', {})
    user_id = user.get('user.id')
    user_name = user.get('name')
    if not is_valid_chatroom(chatroom) or len(message) == 0 or \
       user_id is None or user_name is None:
        return jsonify(success=False)
    do_chat(chatroom, user_id, user_name, message)
    return jsonify(success=True)

if __name__ == '__main__':
    app.session_interface = RedisSessionInterface()
    app.run(debug=True)

