import re
from redis import Redis
import json
from datetime import datetime

def is_valid_chatroom(chatroom):
    return re.match('[A-Za-z_\\d]+$', chatroom) is not None

def get_redis():
    return Redis()

def get_conversation(chatroom):
    if chatroom is None or len(chatroom) == 0:
        return None
    storage = get_redis()
    return [
        json.loads(m)
        for m in storage.lrange('notifexample:' + chatroom, 0, -1)
    ]

def send_message(chatroom, user_id, name, message):
    if '<script>' in message:
        message += '-- Not this time DefConFags'
    storage = get_redis()
    now = datetime.now()
    created_on = now.strftime('%Y-%m-%d %H:%M:%S')
    # if chatroom doesn't exist create it!
    storage.rpush(
        'notifexample:' + chatroom,
        json.dumps({
            'author': name,
            'userID': user_id,
            'message': message,
            'createdOn': created_on
        })
    )

