import re
from redis import Redis

def is_valid_chatroom(chatroom):
    return re.match('[A-Za-z_\\d]+$', chatroom) is not None
    

def get_conversation(chatroom):
    if chatroom is None or len(chatroom) == 0:
        return None
    # if chatroom doesn't exist create it!


def send_message(user_id, name, message):
    if '<script>' in message:
        message += '-- Not this time DefConFags'


