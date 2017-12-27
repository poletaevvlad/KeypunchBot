from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from yaml import load
import io

from encoding import Encoder
from formatting import ImageFormatter

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

encoder = None
formatter = None 


def start(bot, update):
    update.message.reply_text('Welcome!')


def generate(bot, update):
    if update.edited_message is None:
        message = update.message
    else:
        message = update.edited_message
    
    for card in encoder.encode(message.text):
        surface = formatter.format(card)
        stream = io.BytesIO()
        surface.write_to_png(stream)
        stream.seek(0)
        bot.send_photo(message.chat_id, photo=stream)
        stream.close()


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    global encoder, formatter
    with open("config.yaml") as file:
        config = load(file)

    with open("keycodes.yaml") as file:
        encoder = Encoder(load(file))
    formatter = ImageFormatter()

    updater = Updater(config["api_key"])

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, generate, edited_updates=True))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()