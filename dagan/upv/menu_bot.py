from dagan.bot_base.telegram_bot import TelegramBot
from dagan.data import public_parameters, labels
from dagan.upv.info_manager import InfoManager


class MenuBot(TelegramBot):
    def __init__(self, bot):
        super(MenuBot, self).__init__(bot)
        InfoManager.initialize()

    @staticmethod
    def reload():
        InfoManager.reload()

    @staticmethod
    def generate_restaurant_cb(res_id):
        """
        Generate callback data from a restaurant

        :param res_id: Restaurant id
        :return: Callback data
        """
        return public_parameters.CBDATA_RESTAURANT + str(res_id)

    @staticmethod
    def generate_menu_cb(res_id, menu_id):
        """
        Generate callback data from a menu

        :param res_id: Restaurant id
        :param menu_id: Menu id
        :return: Callback data
        """
        return public_parameters.CBDATA_MENU + str(menu_id) + public_parameters.CBDATA_RESTAURANT + str(res_id)

    @staticmethod
    def menu_name_to_show(res_id, menu_id):
        res = InfoManager.restaurants[res_id]
        menu = res.menus[menu_id]

        return public_parameters.BOLD_START + res.name + public_parameters.RESTAURANT_MENU_SEPARATOR + \
               menu.name + public_parameters.BOLD_END + public_parameters.NEW_LINE

    @staticmethod
    def menu_today_to_show(res_id, menu_id):
        res = InfoManager.restaurants[res_id]
        menu = res.menus[menu_id]

        text = public_parameters.BOLD_START + res.name + public_parameters.RESTAURANT_MENU_SEPARATOR
        text += menu.name + public_parameters.BOLD_END + public_parameters.NEW_LINE
        if menu.today_menu.price:
            text += labels.PRICE + menu.today_menu.price
        text += public_parameters.NEW_LINE
        if menu.today_menu.first:
            text += public_parameters.NEW_LINE + public_parameters.BOLD_START + labels.FIRST + \
                    public_parameters.BOLD_END + public_parameters.NEW_LINE
            text += menu.today_menu.first + public_parameters.NEW_LINE
        if menu.today_menu.second:
            text += public_parameters.NEW_LINE + public_parameters.BOLD_START + labels.SECOND + \
                    public_parameters.BOLD_END + public_parameters.NEW_LINE
            text += menu.today_menu.second + public_parameters.NEW_LINE
        if menu.today_menu.others:
            text += public_parameters.NEW_LINE + public_parameters.BOLD_START + \
                    labels.OTHERS + public_parameters.BOLD_END + public_parameters.NEW_LINE
            text += menu.today_menu.others + public_parameters.NEW_LINE
        if menu.today_menu.observations:
            text += public_parameters.NEW_LINE + public_parameters.BOLD_START + \
                    labels.OBSERVATIONS + public_parameters.BOLD_END + public_parameters.NEW_LINE
            text += menu.today_menu.observations + public_parameters.NEW_LINE
        return text.strip()
