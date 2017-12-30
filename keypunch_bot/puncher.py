# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import Filters, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import yaml
from io import BytesIO
from pprint import pprint

from encoding import Encoder
from formatting import Format
from chatdata import requires_chat_data
from parsers import parse_boolean

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


encoder = None
messages = None


def start(bot, update):
    update.message.reply_text('Welcome!')


def get_text_format(text):
    if text.startswith("/"):
        format_end = text.find(" ")
        if format_end >= 0:
            format_name = text[1: format_end]
            text_format = Format.get_by_name(format_name)
            if text_format != None:
                return text_format, text[format_end + 1:]
    return Format.default, text


def send_result(bot, chat_id, message_format, stream, index):
    if message_format.send_image:
        bot.send_photo(chat_id, photo=stream)
    else:
        if index == -1:
            filename = message_format.make_filename("punchcards")
        elif index == -2:
            filename = message_format.make_filename("punchcard")
        else:
            filename = message_format.make_filename("punchcard" + str(index + 1))
        bot.send_document(chat_id, document=stream, filename=filename)


def handle_format_request(bot, chat_data, text, message_format):
    filtered, valid_chars = encoder.filter_string(text)
    cards_num = encoder.num_cards(filtered)
    if cards_num > 10:
         bot.sendMessage(message.chat_id, messages["too_many_cards"]
            .format(cards_num))
    elif valid_chars < len(text) / 2:
        bot.sendMessage(message.chat_id, messages["mostly_unsupported"])
    else:
        if valid_chars < len(text):
            bot.sendMessage(message.chat_id, messages["partially_unsupported"]
                .format(filtered), parse_mode="HTML")
        
        for i, card_text in enumerate(encoder.split_by_card(filtered)):
            char_codes = encoder.encode(card_text)

            if i == 0 or not message_format.join_cards:
                stream = BytesIO()
            message_format.renderer.format(char_codes, stream, message_format)
            if i == cards_num - 1 or not message_format.join_cards:
                stream.seek(0)
                send_result(bot, chat_data.id, message_format, stream, 
                    (-2 if i == 0 else -1) if message_format.join_cards else i)
                stream.close()


@requires_chat_data
def generate(bot, update, chat_data):
    if update.edited_message is None:
        message = update.message
    else:
        message = update.edited_message

    text_format, text = get_text_format(message.text)
    handle_format_request(bot, chat_data, text, text_format)
    

def showtext_respond(new_val, chat_data):
    if new_val is None:
        return messages["showtext_invalid"]
    elif new_val and chat_data.show_text:
        return messages["showtext_already_on"]
    elif not new_val and not chat_data.show_text:
        return messages["showtext_already_off"]
    elif new_val:
        chat_data.show_text = True
        return messages["showtext_set_on"]
    else:
        chat_data.show_text = False
        return messages["showtext_set_off"]


@requires_chat_data
def showtext_command(bot, update, args, chat_data=None):
    reply = None
    reply_markup = None
    if len(args) > 1:
        reply = messages["too_many_arguments"].format("show_text")
    elif len(args) == 0:
        if chat_data.show_text:
            reply = messages["showtext_currently_on"]
        else:
            reply = messages["showtext_currently_off"]
        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("Enable", callback_data="showtext on"),
            InlineKeyboardButton("Disable", callback_data="showtext off")]], 
            resize_keybord=True, one_time_keyboard=True, selective=True)
    else:
        arg = parse_boolean(args[0])
        reply = showtext_respond(arg, chat_data)
    if reply is not None:
        bot.sendMessage(chat_data.id, reply, reply_markup=reply_markup)


def characters_command(bot, update):
    bot.sendMessage(update.message.chat_id, messages["supported_chars"], 
                    parse_mode="HTML")


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


@requires_chat_data
def inlinequery(bot, update, chat_data):
    query = update.callback_query
    bot.answerCallbackQuery(query.id)
    if query.data and len(query.data) > 0:
        data = str(query.data).split(" ")
        if data[0] == "showtext" and len(data) == 2:
            new_val = parse_boolean(data[1])
            reply = showtext_respond(new_val, chat_data)
            if reply is not None:
                bot.sendMessage(chat_data.id, reply)


def stasik(bot, update):
    bot.sendMessage(update.effective_chat.id, "❤")


def main():
    global encoder, formatter, messages
    with open("config.yaml") as file:
        config = yaml.load(file)

    with open("keycodes.yaml") as file:
        encoder = Encoder(yaml.load(file))

    with open("messages.yaml") as file:
        messages = yaml.load(file)

    updater = Updater(config["api_key"])

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("characters", characters_command))
    dp.add_handler(CommandHandler("стасик", stasik))
    dp.add_handler(CommandHandler("showtext", showtext_command, pass_args=True))
    for format_name in Format.formats:
        dp.add_handler(CommandHandler(format_name, generate, allow_edited=True))
    dp.add_handler(MessageHandler(Filters.text, generate, edited_updates=True))
    dp.add_handler(CallbackQueryHandler(inlinequery))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()