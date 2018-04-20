# -*- coding: utf-8 -*-

import logging
from functools import wraps
from io import BytesIO, StringIO
from queue import Queue
from threading import Thread

from telegram import Bot
from telegram.ext import CommandHandler
from telegram.ext import Dispatcher
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.utils.request import Request

import yaml

from .chatdata import InMemoryDataManager
from .encoding import split_images
from .generator import FormatsManager

logging.basicConfig(format='%(asctime)s-%(name)s-%(levelname)s - %(message)s',
                    level=logging.INFO)


def requires_chat_data(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        chat_id = args[2].effective_chat.id
        chat_data = args[0].data_manager.get(chat_id)
        func(*args, **kwargs, chat_data=chat_data)
    return wrapper


class KeypunchBot:
    default_char_table = "mtk2"

    def __init__(self, token, formats_manager, messages, data_manager,
                 workers=4, logger=None):
        self.bot = Bot(token, request=Request(con_pool_size=workers + 4))
        self.dispatcher = Dispatcher(self.bot, Queue(), workers=workers)

        def command(name, cb, **kwargs):
            self.dispatcher.add_handler(CommandHandler(name, cb, **kwargs))

        command("start", self.start_command)
        command("info", self.info_command)
        command("cancel", self.cancel_command)
        command("showtext", self.showtext_command)
        command("hidetext", self.hidetext_command)
        command("characters", self.characters_command)
        command("help", self.help_command)
        command("about", self.about_command)

        for format_name in FormatsManager.formats:
            command(format_name, self.handle_format)

        for chartable_name in formats_manager.char_tables:
            command(chartable_name, self.handle_chartable)

        self.dispatcher.add_handler(MessageHandler(Filters.text, self.run))
        self.dispatcher.add_handler(MessageHandler(Filters.command,
                                                   self.unknown_command))
        self.dispatcher.add_error_handler(self.error)
        self.formats_manager = formats_manager
        self.messages = messages
        self.logger = logger
        self.data_manager = data_manager

    def add_command_handler(self, name, callback, **kwargs):
        self.dispatcher.add_handler(CommandHandler(name, callback, **kwargs))

    @requires_chat_data
    def info_command(self, bot, update, chat_data):
        self.reply(bot, update, "id = {}, show_text = {}, format={}".
                   format(chat_data.id, chat_data.show_text,
                          chat_data.format))

    def reply(self, bot, update, message, filename=None):
        if isinstance(message, BytesIO):
            message.seek(0)
            if filename is None:
                bot.send_photo(update.message.chat_id, photo=message)
            else:
                bot.send_document(update.message.chat_id, document=message,
                                  filename=filename)
        elif isinstance(message, StringIO):
            message.seek(0)
            if filename is None:
                bot.sendMessage(update.message.chat_id, message.read())
            else:
                document = BytesIO(bytes(message.read(), encoding="utf-8"))
                bot.send_document(update.message.chat_id, document=document,
                                  filename=filename)
        else:
            bot.sendMessage(update.message.chat_id, message,
                            disable_web_page_preview=True, parse_mode="html")

    def start_command(self, bot, update):
        self.reply(bot, update, self.messages["welcome"])

    def _get_type_repr(self, type):
        if type == "punchcard":
            return self.messages["punched_cards"]
        else:
            return self.messages["punched_tape"]

    def generate(self, bot, update, text, format="png",
                 chartable=default_char_table, show_text=True, as_file=False):
        formatter = self.formats_manager.get(chartable, format)
        count = formatter.chartable.count_chars(text, formatter.per_image)
        if count.images > formatter.max_images:
            name, t = self.formats_manager.get_info(chartable)
            if format != "text":
                self.reply(bot, update, self.messages["too_many_images"].
                           format(count.images, formatter.max_images))
            else:
                self.reply(bot, update, self.messages["too_many_text"].
                           format(self._get_type_repr(t),
                                  formatter.max_images * formatter.per_image))
            return
        if count.supported < len(text) / 2:
            self.reply(bot, update, self.messages["mostly_unsupported"])
            return
        elif count.supported < len(text):
            self.reply(bot, update, self.messages["partially_unsupported"])
        buffer = formatter.create_buffer()
        encoded = formatter.chartable.encode(text)
        if count.images == 1:
            encoded = [encoded]
        else:
            encoded = split_images(encoded, formatter.per_image)
        for i, codes in enumerate(encoded):
            formatter.renderer.render(codes, format, show_text, buffer)
            if not formatter.reuse_buffer:
                filename = formatter.make_filename(i, count.images) if as_file\
                    else None
                self.reply(bot, update, buffer, filename=filename)
                buffer = formatter.create_buffer()
        if formatter.reuse_buffer:
            filename = formatter.make_filename(i, count.images) if as_file\
                else None
            self.reply(bot, update, buffer, filename=filename)

    @requires_chat_data
    def run(self, bot, update, chat_data):
        if chat_data.format is not None:
            image_format = chat_data.format
        else:
            image_format = "png"
        if chat_data.char_table is not None:
            char_table = chat_data.char_table
        else:
            char_table = self.default_char_table
        self.generate(bot, update, update.message.text, format=image_format,
                      as_file=chat_data.format is not None,
                      show_text=chat_data.show_text, chartable=char_table)
        if chat_data.format is not None:
            chat_data.format = None
            self.data_manager.put(chat_data)

    def _get_command(self, text):
        command_end = text.find(" ")
        if command_end < 0:
            command_end = len(text) + 1
        return text[1: command_end]

    @requires_chat_data
    def handle_format(self, bot, update, chat_data):
        format_name = self._get_command(update.message.text)
        text = update.message.text[len(format_name) + 1:].strip()
        if len(text) > 0:
            self.generate(bot, update, text, format=format_name, as_file=True,
                          show_text=chat_data.show_text)
        else:
            chat_data.format = format_name
            self.data_manager.put(chat_data)
            self.reply(bot, update, self.messages["empty_format_request"].
                       format(format_name))

    @requires_chat_data
    def handle_chartable(self, bot, update, chat_data):
        chartable = self._get_command(update.message.text)
        name, t = self.formats_manager.get_info(chartable)
        unchanged = chat_data.char_table is None and \
            chartable == self.default_char_table
        unchanged |= chat_data.char_table == chartable
        if unchanged:
            self.reply(bot, update, self.messages["unchanged_char_table"].
                       format(name))
        else:
            chat_data.char_table = chartable
            self.data_manager.put(chat_data)
            type_repr = self._get_type_repr(t)
            reply = self.messages["changed_char_table"].format(type_repr, name)
            self.reply(bot, update, reply)

    @requires_chat_data
    def cancel_command(self, bot, update, chat_data):
        if chat_data.format is None:
            bot.sendMessage(chat_data.id, self.messages["no_cancel"])
        else:
            bot.sendMessage(chat_data.id, self.messages["cancel_confirm"])
            chat_data.format = None
            self.data_manager.put(chat_data)

    @requires_chat_data
    def showtext_command(self, bot, update, chat_data):
        if chat_data.show_text:
            self.reply(bot, update, self.messages["showtext_already_on"])
        else:
            self.reply(bot, update, self.messages["showtext_set_on"])
            chat_data.show_text = True
            self.data_manager.put(chat_data)

    @requires_chat_data
    def hidetext_command(self, bot, update, chat_data):
        if not chat_data.show_text:
            self.reply(bot, update, self.messages["showtext_already_off"])
        else:
            self.reply(bot, update, self.messages["showtext_set_off"])
            chat_data.show_text = False
            self.data_manager.put(chat_data)

    @requires_chat_data
    def characters_command(self, bot, update, chat_data):
        char_table = chat_data.char_table
        if char_table is None:
            char_table = self.default_char_table
        name, t = self.formats_manager.get_info(char_table)
        message = self.messages["supported_chars_prefix"].format(name)
        for line in self.formats_manager.get_supported_characters(char_table):
            message += self.messages["characters_line"].format(line)
        message += self.messages["supported_chars_postfix"]
        for name, table, type in self.formats_manager.get_all():
            message += (self.messages["encoding_line"].
                        format(name, self._get_type_repr(type), table))
        self.reply(bot, update, message)

    def error(self, bot, update, error):
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        self.logger.warning('Update "%s" caused error "%s"', update, error)

    def help_command(self, bot, update):
        encodings = ""
        for name, table, type in self.formats_manager.get_all():
            encodings += (self.messages["help_encoding"].format(table, name))
        self.reply(bot, update, self.messages["help"].format(encodings))

    def about_command(self, bot, update):
        self.reply(bot, update, self.messages["about"])

    def unknown_command(self, bot, update):
        self.reply(bot, update, self.messages["unknown_command"])

    def run_polling(self):
        updater = Updater(bot=self.bot)
        updater.dispatcher = self.dispatcher
        updater.update_queue = updater.dispatcher.update_queue
        updater.start_polling()
        updater.idle()

    def start_webhook(self, url):
        self.bot.set_webhook(url=url)

    def remove_webhook(self):
        self.bot.delete_webhook()

    def start_dispatch_thread(self):
        thread = Thread(target=self.dispatcher.start, name='dispatcher')
        thread.start()

    def handle_update(self, update):
        self.dispatcher.update_queue.put(update)


def main():
    with open("keypunch_bot/config.yaml") as file:
        config = yaml.load(file)

    with open("keypunch_bot/messages.yaml") as file:
        messages = yaml.load(file)

    formats_manager = FormatsManager("keypunch_bot/keycodes.yaml")
    keypunch = KeypunchBot(config["api_key"], formats_manager, messages,
                           InMemoryDataManager())
    keypunch.run_polling()


if __name__ == "__main__":
    main()
