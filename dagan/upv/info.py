import json
import time

from dagan.data.labels import PRICE, FIRST, SECOND, OTHERS, OBSERVATIONS
from dagan.data.public_parameters import INFO_EXP_TIME, RESTAURANT_REPLACE, CBDATA_RESTAURANT, CBDATA_MENU, NEW_LINE, \
    CLEAN_TEXT_REPLACE, BOLD_START, BOLD_END, PRICE_REPLACE, RESTAURANT_MENU_SEPARATOR, ALL_INFO_REPLACE


def clean_text(text):
    """
    Recives a text and prepares it to be sent by the bot
    :param text: Plain text
    :return: Corrected text
    """
    for org, dst in CLEAN_TEXT_REPLACE:
        text = text.replace(org, dst)
    while text.endswith(NEW_LINE):
        text = text[0:-len(NEW_LINE)]
    return text.strip()


class Info:
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
        self.expiration_time = time.time() + INFO_EXP_TIME  # With each load we reset the expiration counter
        # Clean input info
        for org, dst in ALL_INFO_REPLACE:
            text = text.replace(org, dst)
        for item in json.loads(text):
            # Text is a list of dictionarys, and each dictionary contains info from the menu of a restaurant
            # (and all restaurant's information)
            restaurant_instance = Restaurant(item)
            if restaurant_instance.id not in self.restaurants.keys():
                self.restaurants[restaurant_instance.id] = restaurant_instance
            self.restaurants[restaurant_instance.id].add_menu(item)

    def is_active(self):
        """
        Checks if this information is still valid
        :return: True if this instance references valid information
        """
        return time.time() < self.expiration_time


class Restaurant:
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
        self.menus.append(Menu(my_dict))

    def show_info(self, menu_index):
        """
        Build a text to be sent with the whole information of a menu
        :param menu_index: Index of menu to inform about
        :return: String to send
        """
        info = BOLD_START + self.name + RESTAURANT_MENU_SEPARATOR
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
        return BOLD_START + restaurant_name + RESTAURANT_MENU_SEPARATOR + menu_name + BOLD_END + NEW_LINE

    @staticmethod
    def clean_name(text):
        """
        Prepare a restaurant's name to be sent
        :param text: Text with restaurant's name
        :return: Formatted text
        """
        for org, dst in RESTAURANT_REPLACE:
            text = text.replace(org, dst)
        return text.strip()

    @staticmethod
    def generate_restaurant_cb(res_id):
        """
        Generate callback data from a restaurant

        :param res_id: Restaurant id
        :return: Callback data
        """
        return CBDATA_RESTAURANT + str(res_id)


class Menu:
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
        self.name = clean_text(my_dict[Menu.NAME])
        self.first = clean_text(my_dict[Menu.FIRST])
        self.second = clean_text(my_dict[Menu.SECOND])
        self.others = clean_text(my_dict[Menu.OTHERS])
        self.observations = clean_text(my_dict[Menu.OBSERVATIONS])
        self.price = self.clean_price(clean_text(my_dict[Menu.PRICE]))

    def show_info(self):
        """
        Build a string to be sent
        :return: String to send
        """
        text = self.name + BOLD_END + NEW_LINE
        if self.price:
            text += PRICE + self.price
        text += NEW_LINE
        if self.first:
            text += NEW_LINE + BOLD_START + FIRST + BOLD_END + NEW_LINE
            text += self.first + NEW_LINE
        if self.second:
            text += NEW_LINE + BOLD_START + SECOND + BOLD_END + NEW_LINE
            text += self.second + NEW_LINE
        if self.others:
            text += NEW_LINE + BOLD_START + OTHERS + BOLD_END + NEW_LINE
            text += self.others + NEW_LINE
        if self.observations:
            text += NEW_LINE + BOLD_START + OBSERVATIONS + BOLD_END + NEW_LINE
            text += self.observations + NEW_LINE
        return text.strip()

    @staticmethod
    def clean_price(price):
        """
        Prepare a price info to be sent
        :param price: Text with price info
        :return: Formatted text
        """
        for org, dst in PRICE_REPLACE:
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
        return CBDATA_MENU + str(menu_id) + CBDATA_RESTAURANT + str(res_id)
