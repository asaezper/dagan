import json
import time

from dagan.internal_data import labels, dagan_parameters


def clean_text(text):
    text = text.replace('#', '\r\n').replace(':s:', '').replace('  ', ' ')
    while text.endswith('\r\n'):
        text = text[0:-2]
    return text.strip()


def new_line():
    return '\r\n'


class Information:
    def __init__(self):
        self.bars = {}
        self.expiration_time = time.time()

    def load(self, text):
        self.bars = {}
        self.expiration_time = time.time() + dagan_parameters.INFO_EXP_TIME
        for item in json.loads(text.replace('\r\n', '').replace('\n', '')):
            bar_instance = Bar(item)
            if bar_instance.id not in self.bars.keys():
                self.bars[bar_instance.id] = bar_instance
            self.bars[bar_instance.id].add_menu(item)

    def is_active(self):
        return time.time() < self.expiration_time


class Bar:
    ID = 'ID_BAR'
    NAME = 'NOMBRE_BAR'

    def __init__(self, my_dict):
        self.id = int(clean_text(my_dict[self.ID]))
        self.name = self.clean_name(clean_text(my_dict[self.NAME]))
        self.menus = []

    def add_menu(self, my_dict):
        self.menus.append(Menu(my_dict))

    def show_info(self, index):
        info = '*' + self.name + '  >  '
        info += self.menus[index].show_info()
        return info

    def generate_menu_name(self, index):
        return self._gen_menu_name(self.name, self.menus[index].name)

    @staticmethod
    def _gen_menu_name(bar_name, menu_name):
        info = '*' + bar_name + '  >  '
        info += menu_name + '*' + new_line()
        return info

    @staticmethod
    def clean_name(text):
        for item in dagan_parameters.BAR_REPLACE:
            text = text.replace(item, '')
        return text.strip()

    @staticmethod
    def generate_bar_cb(bar_id):
        return dagan_parameters.CBDATA_BAR + str(bar_id)


class Menu:
    NAME = 'MENU'
    FIRST = 'PLATO1'
    SECOND = 'PLATO2'
    OTHERS = 'OTROS'
    OBSERVATIONS = 'OBSERVACIONES'
    PRICE = 'PRECIO'

    def __init__(self, my_dict):
        self.name = clean_text(my_dict[Menu.NAME])
        self.first = clean_text(my_dict[Menu.FIRST])
        self.second = clean_text(my_dict[Menu.SECOND])
        self.others = clean_text(my_dict[Menu.OTHERS])
        self.observations = clean_text(my_dict[Menu.OBSERVATIONS])
        self.price = self.clean_price(clean_text(my_dict[Menu.PRICE]))

    def show_info(self):
        text = self.name + '*' + new_line()
        if self.price:
            text += labels.PRICE + self.price
        text += new_line()
        if self.first:
            text += new_line() + '*' + labels.FIRST + '*' + new_line()
            text += self.first + new_line()
        if self.second:
            text += new_line() + '*' + labels.SECOND + '*' + new_line()
            text += self.second + new_line()
        if self.others:
            text += new_line() + '*' + labels.OTHERS + '*' + new_line()
            text += self.others + new_line()
        if self.observations:
            text += new_line() + '*' + labels.OBSERVATIONS + '*' + new_line()
            text += self.observations + new_line()
        return text

    @staticmethod
    def clean_price(price):
        return price.replace(' Euros', '€').replace(' euros', '€').replace('Euros', '€').replace('euros', '€').strip()

    @staticmethod
    def generate_menu_cb(bar_id, menu_id):
        return dagan_parameters.CBDATA_MENU + str(menu_id) + dagan_parameters.CBDATA_BAR + str(bar_id)
