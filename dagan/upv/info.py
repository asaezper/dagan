import json
import time

from dagan.data import labels, public_parameters


def clean_text(text):
    """
    Recives a text and prepares it to be sent by the bot
    :param text: Plain text
    :return: Corrected text
    """
    for org, dst in public_parameters.CLEAN_TEXT_REPLACE:
        text = text.replace(org, dst)
    while text.endswith(public_parameters.NEW_LINE):
        text = text[0:-len(public_parameters.NEW_LINE)]
    return text.strip()


class TodayInfo:
    """
    Class to store all restaurants and menus information for the UPV campus
    """

    def __init__(self):
        self.restaurants = {}
        self.expiration_time = time.time()

    def load(self, text):
        """
        Parse info from UPV's API
        :param text: Text (a json list of dictionaries)
        """
        self.restaurants = {}  # Dictrionary with id (int): restaurant (Restaurant)
        self.expiration_time = time.time() + public_parameters.INFO_EXP_TIME  # With each load we reset the expiration counter
        # Clean input info
        for org, dst in public_parameters.ALL_INFO_REPLACE:
            text = text.replace(org, dst)
        for item in json.loads(text):
            # Text is a list of dictionarys, and each dictionary contains info from the menu of a restaurant
            # (and all restaurant's information)
            restaurant_instance = TodayRestaurant(item)
            if restaurant_instance.id not in self.restaurants.keys():
                self.restaurants[restaurant_instance.id] = restaurant_instance
            self.restaurants[restaurant_instance.id].add_menu(item)

    def is_active(self):
        """
        Checks if this information is still valid
        :return: True if this instance references valid information
        """
        return time.time() < self.expiration_time


class TodayRestaurant:
    """
    Information of a restaurant
    """
    ID = 'ID_BAR'
    NAME = 'NOMBRE_BAR'

    def __init__(self, my_dict):
        """
        Parse restaurants's info
        :param my_dict: Dictionary with information of a restaurant
        """
        self.id = int(clean_text(my_dict[self.ID]))
        self.name = self.clean_name(clean_text(my_dict[self.NAME]))
        self.menus = []

    def add_menu(self, my_dict):
        """
        Add a menu
        :param my_dict: Information of a menu
        """
        self.menus.append(TodayMenu(my_dict))

    def show_info(self, menu_index):
        """
        Build a text to be sent with the whole information of a menu
        :param menu_index: Index of menu to inform about
        :return: String to send
        """
        info = public_parameters.BOLD_START + self.name + public_parameters.RESTAURANT_MENU_SEPARATOR
        info += self.menus[menu_index].show_info()
        return info

    def show_menu_name(self, menu_index):
        """
        Build a text to be sent with only the name of the menu
        :param menu_index: Index of menu to inform about
        :return: String to send
        """
        return self.generate_menu_name(self.name, self.menus[menu_index].name)

    @staticmethod
    def generate_menu_name(restaurant_name, menu_name):
        """
        Static method to build a text with only names of restaurant and menu
        :param restaurant_name: Restaurant's name
        :param menu_name: Menu's name
        :return:
        """
        return public_parameters.BOLD_START + restaurant_name + public_parameters.RESTAURANT_MENU_SEPARATOR + \
               menu_name + public_parameters.BOLD_END + public_parameters.NEW_LINE

    @staticmethod
    def clean_name(text):
        """
        Prepare a restaurant's name to be sent
        :param text: Text with restaurant's name
        :return: Formatted text
        """
        for org, dst in public_parameters.RESTAURANT_REPLACE:
            text = text.replace(org, dst)
        return text.strip()

    @staticmethod
    def generate_restaurant_cb(res_id):
        """
        Generate callback data from a restaurant

        :param res_id: Restaurant id
        :return: Callback data
        """
        return public_parameters.CBDATA_RESTAURANT + str(res_id)


class TodayMenu:
    """
    Information of a menu
    """
    NAME = 'MENU'
    FIRST = 'PLATO1'
    SECOND = 'PLATO2'
    OTHERS = 'OTROS'
    OBSERVATIONS = 'OBSERVACIONES'
    PRICE = 'PRECIO'

    def __init__(self, my_dict):
        """
        Parse the info (inside a dictionary)
        :param my_dict: Dict with menu info
        """
        self.name = clean_text(my_dict[TodayMenu.NAME])
        self.first = clean_text(my_dict[TodayMenu.FIRST])
        self.second = clean_text(my_dict[TodayMenu.SECOND])
        self.others = clean_text(my_dict[TodayMenu.OTHERS])
        self.observations = clean_text(my_dict[TodayMenu.OBSERVATIONS])
        self.price = self.clean_price(clean_text(my_dict[TodayMenu.PRICE]))

    def show_info(self):
        """
        Build a string to be sent
        :return: String to send
        """
        text = self.name + public_parameters.BOLD_END + public_parameters.NEW_LINE
        if self.price:
            text += labels.PRICE + self.price
        text += public_parameters.NEW_LINE
        if self.first:
            text += public_parameters.NEW_LINE + public_parameters.BOLD_START + labels.FIRST + \
                    public_parameters.BOLD_END + public_parameters.NEW_LINE
            text += self.first + public_parameters.NEW_LINE
        if self.second:
            text += public_parameters.NEW_LINE + public_parameters.BOLD_START + labels.SECOND + \
                    public_parameters.BOLD_END + public_parameters.NEW_LINE
            text += self.second + public_parameters.NEW_LINE
        if self.others:
            text += public_parameters.NEW_LINE + public_parameters.BOLD_START + \
                    labels.OTHERS + public_parameters.BOLD_END + public_parameters.NEW_LINE
            text += self.others + public_parameters.NEW_LINE
        if self.observations:
            text += public_parameters.NEW_LINE + public_parameters.BOLD_START + \
                    labels.OBSERVATIONS + public_parameters.BOLD_END + public_parameters.NEW_LINE
            text += self.observations + public_parameters.NEW_LINE
        return text.strip()

    @staticmethod
    def clean_price(price):
        """
        Prepare a price info to be sent
        :param price: Text with price info
        :return: Formatted text
        """
        for org, dst in public_parameters.PRICE_REPLACE:
            price = price.replace(org, dst)
        return price.strip()

    @staticmethod
    def generate_menu_cb(res_id, menu_id):
        """
        Generate callback data from a menu

        :param res_id: Restaurant id
        :param menu_id: Menu id
        :return: Callback data
        """
        return public_parameters.CBDATA_MENU + str(menu_id) + public_parameters.CBDATA_RESTAURANT + str(res_id)
