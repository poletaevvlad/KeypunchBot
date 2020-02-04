# -*- coding: utf-8 -*-
#
# Copyright 2017, 2018, 2020 Vladislav Poletaev
#
# This file is part of KeyunchBot.
#
# KeyunchBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# KeypunchBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with KeypunchBot. If not, see <http://www.gnu.org/licenses/>.

import os
import base64
import signal
import tornado.ioloop
from tornado.web import RequestHandler, Application
from tornado.httpserver import HTTPServer
from telegram import Update
from .bot import ChatBot


class WebHookHandler(RequestHandler):
    def initialize(self, bot: ChatBot):
        # pylint: disable=attribute-defined-outside-init
        self.bot = bot

    def post(self):
        update = Update.de_json(self.request.body)
        self.bot.handle_update(update)


class RedirectHandler(RequestHandler):
    def get(self):
        self.set_status(307)
        self.set_header("Location", "https://t.me/keypunch_bot")


def generate_token() -> str:
    return base64.urlsafe_b64encode(os.urandom(48)).decode("ascii")


def start_webhook_server(bot: ChatBot, url: str, port: int):
    token = generate_token()
    if not url.endswith("/"):
        url += "/"
    bot.start_webhook(url + token)

    application = Application([
        ("/", RedirectHandler),
        (f"/{token}", WebHookHandler, dict(bot=bot))
    ])
    http_server = HTTPServer(application)

    def before_terminate(*_args):
        bot.remove_webhook()
        ioloop = tornado.ioloop.IOLoop.current()
        ioloop.add_callback_from_signal(ioloop.stop)

    signal.signal(signal.SIGINT, before_terminate)

    http_server.listen(port)
    tornado.ioloop.IOLoop.current().start()
