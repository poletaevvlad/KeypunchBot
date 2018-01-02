# -*- coding: utf-8 -*-

from telegram import Bot
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CallbackQueryHandler
from telegram.ext import Dispatcher
from telegram.ext import Updater
from telegram.utils.request import Request

import logging
import yaml
from io import BytesIO
from threading import Thread
from queue import Queue
from functools import wraps

from .encoding import Encoder
from .formatting import Format
from .parsers import parse_boolean


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
    html_escape_chars = [("&", "&amp;"), (">", "&gt;"), ("<", "&lt;")]
    __slots__ = ["bot", "dispatcher", "encoder", "messages", "logger",
                 "data_manager"]

    def __init__(self, token, encoder, messages, data_manager, workers=4,
                 logger=None):
        self.bot = Bot(token, request=Request(con_pool_size=workers + 4))

        self.dispatcher = Dispatcher(self.bot, Queue(), workers=workers)
        self.add_command_handler("start", self.start_command)
        self.add_command_handler("characters", self.characters_command)
        self.add_command_handler("стасик", self.stasik)
        self.add_command_handler("showtext", self.showtext_command,
                                 pass_args=True)
        for format_name in Format.formats:
            self.add_command_handler(format_name, self.generate,
                                     allow_edited=True)
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.generate,
                                                   edited_updates=True))
        self.add_command_handler("cancel", self.cancel_command)
        self.add_command_handler("help", self.help_command)
        self.add_command_handler("about", self.about_command)
        self.add_command_handler("about", self.about_command)
        self.dispatcher.add_handler(MessageHandler([Filters.command],
                                                   self.unknown_command))
        self.dispatcher.add_handler(CallbackQueryHandler(self.inlinequery))
        self.dispatcher.add_error_handler(self.error)
        self.encoder = encoder
        self.messages = messages
        self.logger = logger
        self.data_manager = data_manager

    def add_command_handler(self, name, callback, **kwargs):
        self.dispatcher.add_handler(CommandHandler(name, callback, **kwargs))

    def start_command(self, bot, update):
        update.message.reply_text('Welcome!')

    def get_text_format(self, text):
        if text.startswith("/"):
            format_end = text.find(" ")
            if format_end >= 0:
                format_name = text[1: format_end]
                text = text[format_end + 1:]
            else:
                format_name = text[1:]
                text = ""
            text_format = Format.get_by_name(format_name)
            if text_format is not None:
                return text_format, text
        return Format.default, text

    def send_result(self, bot, chat_id, message_format, stream, index):
        if message_format.send_image:
            bot.send_photo(chat_id, photo=stream)
        else:
            if index == -1:
                filename = message_format.make_filename("punchcards")
            elif index == -2:
                filename = message_format.make_filename("punchcard")
            else:
                index_str = str(index + 1)
                name = "punchcard" + index_str
                filename = message_format.make_filename(name)
            bot.send_document(chat_id, document=stream, filename=filename)

    def escape_chars(self, text):
        for original, replacement in KeypunchBot.html_escape_chars:
            text = text.replace(original, replacement)
        return text

    def handle_format_request(self, bot, chat_data, text, message_format):
        filtered, valid_chars = self.encoder.filter_string(text)
        cards_num = self.encoder.num_cards(filtered)
        if cards_num > 10:
            bot.sendMessage(chat_data.id, self.messages["too_many_cards"]
                                              .format(cards_num))
        elif valid_chars < len(text) / 2:
            bot.sendMessage(chat_data.id, self.messages["mostly_unsupported"])
        else:
            if valid_chars < len(text):
                bot.sendMessage(chat_data.id,
                                self.messages["partially_unsupported"]
                                .format(self.escape_chars(filtered)),
                                parse_mode="HTML")

            cards_text = self.encoder.split_by_card(filtered)
            for i, card_text in enumerate(cards_text):
                char_codes = self.encoder.encode(card_text)

                if i == 0 or not message_format.join_cards:
                    stream = BytesIO()
                message_format.renderer.format(char_codes, stream,
                                               message_format,
                                               chat_data.show_text)
                if i == cards_num - 1 or not message_format.join_cards:
                    stream.seek(0)
                    index = i
                    if message_format.join_cards:
                        index = -2 if i == 0 else -1
                    self.send_result(bot, chat_data.id, message_format, stream,
                                     index)
                    stream.close()

    @requires_chat_data
    def generate(self, bot, update, chat_data):
        if update.edited_message is None:
            message = update.message
        else:
            message = update.edited_message

        text_format, text = self.get_text_format(message.text)
        if chat_data.format is not None and text_format.is_default():
            text_format = Format.get_by_name(chat_data.format)
        if len(text) > 0:
            self.handle_format_request(bot, chat_data, text, text_format)
            if chat_data.format is not None:
                chat_data.format = None
                self.data_manager.put(chat_data)
        else:
            if chat_data.format != text_format.name:
                chat_data.format = text_format.name
                self.data_manager.put(chat_data)
            message = (self.messages["empty_format_request"]
                           .format(text_format.name_readable))
            bot.sendMessage(chat_data.id, message)

    @requires_chat_data
    def cancel_command(self, bot, update, chat_data):
        if chat_data.format is None:
            bot.sendMessage(chat_data.id, self.messages["no_cancel"])
        else:
            bot.sendMessage(chat_data.id, self.messages["cancel_confirm"])
            chat_data.format = None
            self.data_manager.put(chat_data)

    def showtext_respond(self, new_val, chat_data):
        if new_val is None:
            return self.messages["showtext_invalid"]
        elif new_val and chat_data.show_text:
            return self.messages["showtext_already_on"]
        elif not new_val and not chat_data.show_text:
            return self.messages["showtext_already_off"]
        elif new_val:
            chat_data.show_text = True
            self.data_manager.put(chat_data)
            return self.messages["showtext_set_on"]
        else:
            chat_data.show_text = False
            self.data_manager.put(chat_data)
            return self.messages["showtext_set_off"]

    @requires_chat_data
    def showtext_command(self, bot, update, args, chat_data):
        reply = None
        reply_markup = None
        if len(args) > 1:
            reply = self.messages["too_many_arguments"].format("show_text")
        elif len(args) == 0:
            if chat_data.show_text:
                reply = self.messages["showtext_currently_on"]
            else:
                reply = self.messages["showtext_currently_off"]

            buttons = list()
            buttons.append(InlineKeyboardButton("Enable",
                                                callback_data="showtext on"))
            buttons.append(InlineKeyboardButton("Disable",
                                                callback_data="showtext off"))
            reply_markup = InlineKeyboardMarkup([buttons], resize_keybord=True,
                                                selective=True)
        else:
            arg = parse_boolean(args[0])
            reply = self.showtext_respond(arg, chat_data)
        if reply is not None:
            bot.sendMessage(chat_data.id, reply, reply_markup=reply_markup)

    def characters_command(self, bot, update):
        bot.sendMessage(update.message.chat_id,
                        self.messages["supported_chars"], parse_mode="HTML")

    def error(self, bot, update, error):
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        self.logger.warning('Update "%s" caused error "%s"', update, error)

    @requires_chat_data
    def inlinequery(self, bot, update, chat_data):
        query = update.callback_query
        bot.answerCallbackQuery(query.id)
        if query.data and len(query.data) > 0:
            data = str(query.data).split(" ")
            if data[0] == "showtext" and len(data) == 2:
                new_val = parse_boolean(data[1])
                reply = self.showtext_respond(new_val, chat_data)
                if reply is not None:
                    bot.sendMessage(chat_data.id, reply)

    def stasik(self, bot, update):
        bot.sendMessage(update.effective_chat.id, "❤")

    def help_command(self, bot, update):
        bot.sendMessage(update.effective_chat.id, self.messages["help"],
                        parse_mode="HTML")

    def about_command(self, bot, update):
        bot.sendMessage(update.effective_chat.id, self.messages["about"],
                        parse_mode="Markdown", disable_web_page_preview=True)

    def unknown_command(self, bot, update):
        bot.sendMessage(update.effective_chat.id,
                        self.messages["unknown_command"])

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
    with open("config.yaml") as file:
        config = yaml.load(file)

    with open("keycodes.yaml") as file:
        encoder = Encoder(yaml.load(file))

    with open("messages.yaml") as file:
        messages = yaml.load(file)

    keypunch = KeypunchBot(config["api_key"], encoder, messages)
    keypunch.run_polling()

    # token = config["token"]
    # updater.start_webhook(listen="0.0.0.0", port="80", url_path=token)
    # updater.bot.set_webhook("https://keypunch-bot.appspot.com/"+token)
    # updater.idle()


if __name__ == "__main__":
    main()
