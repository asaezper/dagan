import logging
import sys

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from dagan.dagan_bot import DaganBot
from dagan.internal_data import upv_parameters

logger = logging.getLogger(__name__)


def my_except_hook(exctype, value, traceback):
    logging.getLogger(__name__).exception(value)


def main():
    sys.excepthook = my_except_hook

    # Create the Updater and pass it your bot's token.
    updater = Updater(upv_parameters.BOT_TOKEN)

    # Create my instance
    dagan = DaganBot(updater.bot)

    # Add handler
    updater.dispatcher.add_handler(CommandHandler('start', dagan.start))

    updater.dispatcher.add_handler(CommandHandler('help', dagan.help))

    updater.dispatcher.add_handler(CommandHandler('iyo', dagan.eegg))
    updater.dispatcher.add_handler(CommandHandler('illo', dagan.eegg))

    updater.dispatcher.add_handler(CallbackQueryHandler(dagan.button))
    updater.dispatcher.add_error_handler(dagan.error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
