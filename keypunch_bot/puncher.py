from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from yaml import load
import io

from encoding import Encoder
from formatting import ImageFormatter

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

encoder = Encoder("codes")
formatter = ImageFormatter()


def start(bot, update):
    update.message.reply_text('Welcome!')


def generate(bot, update):
    if update.edited_message is None:
        message = update.message
    else:
        message = update.edited_message
    
    text = message.text
    codes = encoder.encode(text)
    surface = formatter.format(codes)
    writer = io.BytesIO()
    surface.write_to_png(writer)
    writer.seek(0)
    bot.send_photo(message.chat_id, photo=writer)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    with open("config.yaml") as file:
        config = load(file)

    updater = Updater(config["api_key"])

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, generate, edited_updates=True))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()