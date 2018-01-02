# -*- coding: utf-8 -*-

import os
import yaml
import json
from telegram import Update
import signal

from .keypunchbot import KeypunchBot
from .encoding import Encoder
from .chatdata import MongoDataManager

token = os.environ["WEBHOOK_TOKEN"]

with open("keypunch_bot/keycodes.yaml") as keycodes:
    encoder = Encoder(yaml.load(keycodes))
with open("keypunch_bot/messages.yaml") as messages_strings:
    messages = yaml.load(messages_strings)

data_manager = MongoDataManager(server=os.environ["MONGO_SERVER"],
                                database=os.environ["MONGO_DATABASE"],
                                user=os.environ["MONGO_USER"],
                                password=os.environ["MONGO_PASSWORD"])
bot = KeypunchBot(os.environ["API_KEY"], encoder, messages, data_manager)
try:
    bot.start_webhook("https://keypunch-bot.herokuapp.com/" + token)
except:
    pass
bot.start_dispatch_thread()


def send_responce(start_response, status, text=None, content_type="text/plain",
                  headers=dict()):
    if text is None:
        text = status
    data = bytes(text, "utf-8")
    response_headers = [
        ('Content-Type', content_type),
        ('Content-Length', str(len(data)))
    ]
    response_headers.extend(headers.items())

    start_response(status, response_headers)
    return iter([data])


def application(environ, start_response):
    url = environ["PATH_INFO"]
    if url == "/":
        return send_responce(start_response, "301 Moved Permanently",
                             headers={"Location": "https://t.me/keypunch_bot"})
    elif url == "/" + token:
        if environ["REQUEST_METHOD"] != "POST":
            return send_responce(start_response, "405 Method Not Allowed",
                                 headers={"Allow": "POST"})
        else:
            try:
                content_length = int(environ.get("CONTENT_LENGTH", "0"))
            except ValueError:
                content_length = 0
            post_input = environ["wsgi.input"].read(content_length)
            update = Update.de_json(json.loads(post_input), bot)
            bot.handle_update(update)
            return send_responce(start_response, "200 OK", "")
    else:
        return send_responce(start_response, "404 Not Found")


def before_terminate(signum, frame):
    bot.remove_webhook()

signal.signal(signal.SIGINT, before_terminate)
