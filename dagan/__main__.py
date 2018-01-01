import logging
import logging.config
import sys

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from dagan.dagan_bot import DaganBot
from dagan.data import private_parameters
from dagan.database.data_manager import DataManager
from dagan.resources import resource_path


def main():
    # Configure log
    logging.config.fileConfig(resource_path('log_config.ini'))

    # Override default exception handler
    sys.excepthook = lambda exctype, value, traceback: logging.getLogger(__name__).exception(value)

    # Initialize Data Manager
    DataManager.initialize()

    # Create the Updater and pass it bot's token.
    updater = Updater(private_parameters.BOT_TOKEN)

    # Create my instance
    dagan = DaganBot(updater.bot)

    # Add handler: Commands, Buttons and Error
    """
    start - Consulta de menús
    info - Información de restaurantes
    subscriptions - Consultar suscripciones activas
    help - Ayuda
    """
    updater.dispatcher.add_handler(CommandHandler('start', dagan.start_cmd))
    updater.dispatcher.add_handler(CommandHandler('info', dagan.info_cmd))
    updater.dispatcher.add_handler(CommandHandler('subscriptions', dagan.subscriptions_cmd))
    updater.dispatcher.add_handler(CommandHandler('help', dagan.help_cmd))

    updater.dispatcher.add_handler(CallbackQueryHandler(dagan.button))
    updater.dispatcher.add_error_handler(dagan.error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
