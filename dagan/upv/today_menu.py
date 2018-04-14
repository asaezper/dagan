from dagan.data import public_parameters
from dagan.database.entities import Menu


class TodayMenu:
    """
    Information of a menu
    """
    RES_ID = 'ID_BAR'
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
        self.res_id = int(self.clean_text(my_dict[self.RES_ID]))
        self.name = self.clean_text(my_dict[self.NAME])
        self.codename = Menu.generate_codename(self.name)
        self.first = self.clean_text(my_dict[self.FIRST])
        self.second = self.clean_text(my_dict[self.SECOND])
        self.others = self.clean_text(my_dict[self.OTHERS])
        self.observations = self.clean_text(my_dict[self.OBSERVATIONS])
        self.price = self.clean_price(self.clean_text(my_dict[self.PRICE]))

    @staticmethod
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
