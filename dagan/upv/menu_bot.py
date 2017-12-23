import datetime

import requests

from dagan.bot_base.telegram_bot import TelegramBot
from dagan.upv.data.upv_parameters import UPV_TOKEN_URL, UPV_TOKEN_TIMEOUT, UPV_TOKEN_HEADERS, UPV_TOKEN_TYPE, UPV_PSW, \
    UPV_USER, UPV_INFO_DATE_PARAM, UPV_INFO_URL, UPV_INFO_CAMPUS_PARAM, UPV_INFO_CAMPUS_DEFAULT, UPV_INFO_BAR_DEFAULT, \
    UPV_INFO_BAR_PARAM, UPV_INFO_TIMEOUT, UPV_INFO_HEADER_AUTH, UPV_UUID, UPV_INFO_DATE_FORMAT
from dagan.upv.info import Info
from dagan.upv.token import Token


class MenuBot(TelegramBot):
    """
    Menu Bot: A Telegram Bot that woks with data from restaurants of UPV campus
    """

    def __init__(self, bot):
        super(MenuBot, self).__init__(bot)
        self.token = Token()  # UPV Token
        self.info = Info()  # Restaurants information

    def reload(self):
        """
        Reload (if it is needed) the token of UPV APi and the information of restaurants
        """
        self.reload_token()
        self.reload_info()

    def reload_token(self):
        """
        Check if token is valid. If not, request it and save it
        """
        if not self.token.is_active():
            token = requests.post(UPV_TOKEN_URL, timeout=UPV_TOKEN_TIMEOUT, headers=UPV_TOKEN_HEADERS,
                                  data=UPV_TOKEN_TYPE, auth=(UPV_USER, UPV_PSW))
            self.token.load(token.text)
            self.token.save()

    def reload_info(self):
        """
        Check if restaurants info is still valid. If not, request it and save ir
        :return:
        """
        if not self.info.is_active():
            list_com = requests.get(
                UPV_INFO_URL + '?' + UPV_INFO_DATE_PARAM + '=' + self.current_date() + '&' + UPV_INFO_CAMPUS_PARAM + '=' +
                UPV_INFO_CAMPUS_DEFAULT + '&' + UPV_INFO_BAR_PARAM + '=' + UPV_INFO_BAR_DEFAULT,
                timeout=UPV_INFO_TIMEOUT,
                headers={UPV_INFO_HEADER_AUTH: self.token.token_type + " " + self.token.access_token + ':' + UPV_UUID})
            self.info.load(list_com.text)

    @staticmethod
    def current_date():
        """
        Return current date in a format valid for UPV's API
        :return: current date in a format valid for UPV's API
        """
        return datetime.date.today().strftime(UPV_INFO_DATE_FORMAT)