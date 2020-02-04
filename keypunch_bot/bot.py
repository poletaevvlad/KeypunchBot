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

import re
from io import BytesIO
from pathlib import Path
from logging import Logger
from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler, \
    MessageHandler, Filters

from .i18n import TranslationManager, Language
from .utils import lazy_property
from .persistance import Store, ChatData, Format

LOGGER = Logger(__name__)


def on_error(update: Update, context):
    LOGGER.warning('Update "%s" caused error "%s"', update, context.error)


class MessageContext:
    COMMAND_REGEX = re.compile(r"^//?[a-zA-Z0-9_]+")

    def __init__(self, update: Update, context: CallbackContext,
                 translation_manager: TranslationManager,
                 store: Store):
        self.update = update
        self.context = context
        self._translation_manager = translation_manager
        self._store = store

    @lazy_property
    def lang(self) -> Language:
        language = self.update.message.from_user.language_code
        if language is None:
            return self._translation_manager.default_lang
        return self._translation_manager.get(language)

    @property
    def chat_id(self) -> int:
        return self.update.message.chat_id

    @lazy_property
    def data(self) -> ChatData:
        return self._store.load_or_default(self.chat_id)

    @property
    def message(self):
        text = self.update.message.text.strip()
        match = MessageContext.COMMAND_REGEX.search(text)
        if match is None:
            return text
        if match[0].startswith("//"):
            return text[1:]
        return text[len(match[0]):].strip()

    # pylint: disable=redefined-builtin
    def save(self, *, format: Format = None, show_text: bool = None,
             charset: str = None):
        current = self.data
        new_data = ChatData(
            output_format=current.output_format if format is None else format,
            show_text=current.show_text if show_text is None else show_text,
            charset=current.charset if charset is None else charset
        )
        if new_data != current:
            self._store.save(self.chat_id, new_data)

    def answer(self, text: str):
        bot = self.update.message.bot
        bot.send_message(
            chat_id=self.chat_id,
            text=text,
            disable_web_page_preview=True,
            parse_mode="html"
        )

    def send_photo(self, file: BytesIO):
        bot = self.update.message.bot
        bot.send_photo(self.chat_id, photo=file)

    def send_file(self, file: BytesIO, filename: str):
        bot = self.update.message.bot
        bot.send_document(self.chat_id, document=file, filename=filename)


class ChatBot(ABC):
    def __init__(self, api_key: str, store: Store):
        self._updater = Updater(api_key, use_context=True)
        self._dispatcher = self._updater.dispatcher
        self._dispatcher.add_error_handler(on_error)
        self._store = store

        lang_path = Path(__file__).parents[0] / "data" / "i18n"
        self._lang_manager = TranslationManager.load(lang_path, default="en")

        self._dispatcher.add_handler(MessageHandler(
            Filters.text,
            self._create_handler(self.text, None)
        ))

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def text(self, ctx: MessageContext):
        pass

    def _create_handler(self, callback, argument=None):
        def handler(update: Update, context: CallbackContext):
            message_context = MessageContext(
                update=update,
                context=context,
                translation_manager=self._lang_manager,
                store=self._store
            )
            if argument is not None:
                callback(message_context, argument)
            else:
                callback(message_context)
        return handler

    def on_command(self, command: str, callback, argument=None):
        handler = self._create_handler(callback, argument)
        self._dispatcher.add_handler(CommandHandler(command, handler))

    def start_polling(self):
        self._updater.start_polling()
        self._updater.idle()
