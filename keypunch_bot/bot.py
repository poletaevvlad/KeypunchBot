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

from logging import Logger
from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import Updater

LOGGER = Logger(__name__)


def on_error(update: Update, context):
    LOGGER.warning('Update "%s" caused error "%s"', update, context.error)


class ChatBot(ABC):
    def __init__(self, api_key: str):
        self.updater = Updater(api_key, use_context=True)
        dispatcher = self.updater.dispatcher
        dispatcher.add_error_handler(on_error)

        self.initialize()

    @abstractmethod
    def initialize(self):
        pass

    def start_polling(self):
        self.updater.start_polling()
        self.updater.idle()
