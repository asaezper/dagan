from dagan.bot_base.telegram_bot import TelegramBot
from dagan.upv.info_manager import InfoManager


class MenuBot(TelegramBot):
    def __init__(self, bot):
        super(MenuBot, self).__init__(bot)
        InfoManager.initialize()

    @staticmethod
    def reload():
        InfoManager.reload()

    @staticmethod
    def menu_to_show():
        pass