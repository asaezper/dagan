import datetime

import requests

from dagan.internal_data import upv_parameters
from dagan.objects.information import Information
from dagan.objects.upv_token import UPVToken


class MenuBaseBot:
    def __init__(self, bot):
        self.bot = bot
        self.token = UPVToken()
        self.info = Information()

    def update_info(self):
        self.load_upv_token()
        self.reload_info()

    def load_upv_token(self):
        if not self.token.is_active():
            token_com = requests.post(upv_parameters.UPV_TOKEN_URL, timeout=upv_parameters.UPV_TOKEN_TIMEOUT,
                                      headers=upv_parameters.UPV_TOKEN_HEADERS,
                                      data=upv_parameters.UPV_TOKEN_TYPE,
                                      auth=(upv_parameters.UPV_USER, upv_parameters.UPV_PSW))
            self.token.load(token_com.text)
            self.token.save()

    def reload_info(self):
        if not self.info.is_active():
            list_com = requests.get(
                upv_parameters.UPV_INFO_URL + '?' + upv_parameters.UPV_INFO_DATE_PARAM + '=' + self.get_date() + '&'
                + upv_parameters.UPV_INFO_CAMPUS_PARAM + '=' + upv_parameters.UPV_INFO_CAMPUS_DEFAULT + '&' +
                upv_parameters.UPV_INFO_BAR_PARAM + '=' + upv_parameters.UPV_INFO_BAR_DEFAULT,
                timeout=upv_parameters.UPV_INFO_TIMEOUT,
                headers={upv_parameters.UPV_INFO_HEADER_AUTH: self.token.token_type + " " +
                                                              self.token.access_token + ':' +
                                                              upv_parameters.UPV_UUID})
            self.info.load(list_com.text)

    @staticmethod
    def get_date():
        return datetime.date.today().strftime(upv_parameters.UPV_INFO_DATE_FORMAT)
