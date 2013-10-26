import re
from redis import Redis
import json
from datetime import datetime
from queue import send_notification

__all__ = ['is_valid_chatroom', 'get_and_register_in_conversation',
           'send_message']

def is_valid_chatroom(chatroom):
    return re.match('[A-Za-z_\\d]+$', chatroom) is not None

def get_redis():
    return Redis()

def get_and_register_in_conversation(chatroom, user_id):
    if chatroom is None or len(chatroom) == 0:
        return None
    storage = get_redis()
    storage.sadd('notifexample:convmembers:' + chatroom, user_id)
    return [
        json.loads(m)
        for m in storage.lrange('notifexample:conv:' + chatroom, 0, -1)
    ]

def send_message(chatroom, user_id, name, message, config):
    if '<script>' in message:
        message += '-- Not this time DefConFags'
    storage = get_redis()
    now = datetime.now()
    created_on = now.strftime('%Y-%m-%d %H:%M:%S')
    # if chatroom doesn't exist create it!
    message = {
        'author': name,
        'userID': user_id,
        'message': message,
        'createdOn': created_on
    }
    members = storage.smembers('notifexample:convmembers:' + chatroom)
    for member in members:
        if str(member) == str(user_id):
            continue
        send_notification(config['notification.queue.router'], message, member)
    storage.rpush('notifexample:conv:' + chatroom, json.dumps(message))

