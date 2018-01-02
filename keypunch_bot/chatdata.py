# -*- coding: utf-8 -*-

from functools import wraps

data = dict()


class ChatData:
    def __init__(self, id):
        self.id = id
        self.show_text = True
        self.format = None


def get_chat_data(chat_id):
    if chat_id not in data:
        chat_data = ChatData(chat_id)
        data[chat_id] = chat_data
    else:
        chat_data = data[chat_id]
    return chat_data


def requires_chat_data(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        chat_id = args[2].effective_chat.id
        func(*args, **kwargs, chat_data=get_chat_data(chat_id))
    return wrapper
