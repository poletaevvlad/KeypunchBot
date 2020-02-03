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
from pathlib import Path
from typing import Callable
from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler, \
    MessageHandler, Filters

from .i18n import TranslationManager, Language
from .utils import lazy_property

LOGGER = Logger(__name__)


def on_error(update: Update, context):
    LOGGER.warning('Update "%s" caused error "%s"', update, context.error)


class MessageContext:
    def __init__(self, update: Update, context: CallbackContext,
                 translation_manager: TranslationManager):
        self.update = update
        self.context = context
        self._translation_manager = translation_manager

    @lazy_property
    def lang(self) -> Language:
        language = self.update.message.from_user.language_code
        if language is None:
            return self._translation_manager.default_lang
        return self._translation_manager.get(language)

    def answer(self, text: str):
        bot = self.update.message.bot
        bot.send_message(
            chat_id=self.update.message.chat_id,
            text=text,
            disable_web_page_preview=True,
            parse_mode="html"
        )


MessageCallback = Callable[[MessageContext], None]


class ChatBot(ABC):
    def __init__(self, api_key: str):
        self._updater = Updater(api_key, use_context=True)
        self._dispatcher = self._updater.dispatcher
        self._dispatcher.add_error_handler(on_error)

        lang_path = Path(__file__).parents[0] / "data" / "i18n"
        self._lang_manager = TranslationManager.load(lang_path, default="en")

        self.initialize()

        self._dispatcher.add_handler(MessageHandler(
            Filters.text,
            self._create_handler(self.text)
        ))

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def text(self, ctx: MessageContext):
        pass

    def _create_handler(self, callback: MessageCallback):
        def handler(update: Update, context: CallbackContext):
            message_context = MessageContext(
                update=update,
                context=context,
                translation_manager=self._lang_manager
            )
            callback(message_context)
        return handler

    def on_command(self, command: str, callback: MessageCallback):
        handler = self._create_handler(callback)
        self._dispatcher.add_handler(CommandHandler(command, handler))

    def start_polling(self):
        self._updater.start_polling()
        self._updater.idle()