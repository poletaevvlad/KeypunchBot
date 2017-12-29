from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import yaml
import io
from pprint import pprint

from encoding import Encoder
from formatting import PILFormatter

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

encoder = None
formatter = None 


def start(bot, update):
    update.message.reply_text('Welcome!')


def text_command(bot, update, args, chat_data):
    if len(args) > 1:
        update.message.reply_text("To many arguments")
    chat_data["cmd"] = args


def generate(bot, update):
    if update.edited_message is None:
        message = update.message
    else:
        message = update.edited_message
    
    for card in encoder.encode(message.text):
        stream = io.BytesIO()
        formatter.format(card, None, stream)
        stream.seek(0)
        bot.send_photo(message.chat_id, photo=stream)
        stream.close()


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    global encoder, formatter
    with open("config.yaml") as file:
        config = yaml.load(file)

    with open("keycodes.yaml") as file:
        encoder = Encoder(yaml.load(file))
    formatter = PILFormatter()

    updater = Updater(config["api_key"])

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("text", text_command, pass_args=True, pass_chat_data=True))
    dp.add_handler(MessageHandler(Filters.text, generate, edited_updates=True))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()