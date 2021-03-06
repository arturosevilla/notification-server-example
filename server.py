#!/usr/bin/env python

import re
from session import RedisSessionInterface
from flask import Flask, render_template, request, session, url_for, \
                  redirect, jsonify
from uuid import uuid4
from chat import get_and_register_in_conversation, send_message as do_chat, \
                 is_valid_chatroom
from config import get_config

app = Flask(__name__)
config = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    chatroom = request.form.get('chatroom', '').strip()
    if len(username) == 0:
        return redirect(url_for('index'))
    session['repoze.who.tkt'] = {
        'user.id': str(uuid4()),
        'name': username
    }
    return redirect(url_for('chat', chatroom=(chatroom or 'intercomunidades')))

@app.route('/user/logout')
def logout():
    session.pop('user', None)
    app.session_interface.logout(app, request)
    return redirect(url_for('index'))

@app.route('/chat/<chatroom>')
def chat(chatroom=None):
    user = session.get('repoze.who.tkt', {})
    user_id = user.get('user.id')
    if not is_valid_chatroom(chatroom) or user_id is None:
        return redirect(url_for('index'))
    log = get_and_register_in_conversation(chatroom, user_id)
    if log is None:
        return redirect(url_for('index'))
    name = session['repoze.who.tkt']['name']
    return render_template(
        'chat.html',
        messages=log,
        chatroom=(chatroom or 'intercomunidades'),
        user_name=name
    )

@app.route('/chat/<chatroom>/message', methods=['POST'])
def send_message(chatroom=None):
    message = request.json.get('message', '').strip()
    user = session.get('repoze.who.tkt', {})
    user_id = user.get('user.id')
    user_name = user.get('name')
    if not is_valid_chatroom(chatroom) or len(message) == 0 or \
       user_id is None or user_name is None:
        return jsonify(success=False)
    do_chat(chatroom, user_id, user_name, message, config)
    return jsonify(success=True)

def is_valid_username(username):
    return re.match('[A-Za-z_\\d]+$', username) is not None
if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print('Required configuration file!')
        sys.exit(1)
    config = get_config(sys.argv[1])
    if config is None:
        print('File not found or incorrect format for INI file')
        sys.exit(1)
        
    app.session_cookie_name = config['cookie_name']
    app.session_interface = RedisSessionInterface(
        secret=config['beaker.session.secret']
    )
    app.run(debug=config['debug'])

