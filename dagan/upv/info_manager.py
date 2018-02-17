import datetime
import json
import logging
import time

import requests

from dagan.data import public_parameters
from dagan.database.db_manager import DBManager
from dagan.upv.data import upv_parameters
from dagan.upv.today_menu import TodayMenu
from dagan.upv.token import Token


class InfoManager(DBManager):
    restaurants = None
    token = Token()
    expiration_time = time.time()

    @classmethod
    def initialize(cls):
        DBManager.initialize()
        cls.reload()

    @classmethod
    def reload(cls):
        """
        Reload (if it is needed) the token of UPV APi and the information of restaurants
        """
        cls.reload_token()
        cls.reload_info()

    @classmethod
    def reload_token(cls):
        """
        Check if token is valid. If not, request it and save it
        """
        if not cls.token.is_active():
            cls.token.load(cls.request_token())
            cls.token.save()

    @staticmethod
    def request_token():
        text = ''
        try:
            text = requests.post(upv_parameters.UPV_TOKEN_URL, timeout=upv_parameters.UPV_TOKEN_TIMEOUT,
                                 headers=upv_parameters.UPV_TOKEN_HEADERS, data=upv_parameters.UPV_TOKEN_TYPE,
                                 auth=(upv_parameters.UPV_USER, upv_parameters.UPV_PSW)).text
        except Exception as err:
            logging.getLogger(__name__).exception(err)
        return text

    @classmethod
    def reload_info(cls):
        """
        Check if restaurants info is still valid. If not, request it and save ir
        :return:
        """
        if not cls.is_active():
            cls.restaurants = cls.read_restaurants()
            text = cls.request_info()
            for item in json.loads(text):
                # Text is a list of dictionaries, and each dictionary contains info from the menu of a restaurant
                # (and all restaurant's information)
                tm = TodayMenu(item)
                if tm.res_id in cls.restaurants.keys():
                    found = False
                    for menu in cls.restaurants[tm.res_id].menus.values():
                        if menu.codename == tm.codename:
                            menu.today_menu = tm
                            found = True
                            break
                    if not found:
                        logging.getLogger(__name__).warning('Menu not matched!! ' + str(item))
                else:
                    logging.getLogger(__name__).warning('Restaurant Id not found!! ' + str(item))

    @classmethod
    def request_info(cls):
        text = ''
        try:
            text = requests.get(
                upv_parameters.UPV_INFO_URL + '?' + upv_parameters.UPV_INFO_DATE_PARAM + '=' + cls.current_date() + '&' + upv_parameters.UPV_INFO_CAMPUS_PARAM + '=' + upv_parameters.UPV_INFO_CAMPUS_DEFAULT + '&' + upv_parameters.UPV_INFO_BAR_PARAM + '=' + upv_parameters.UPV_INFO_BAR_DEFAULT,
                timeout=upv_parameters.UPV_INFO_TIMEOUT, headers={
                    upv_parameters.UPV_INFO_HEADER_AUTH: cls.token.token_type + " " + cls.token.access_token + ':' + upv_parameters.UPV_UUID}).text
            for org, dst in public_parameters.ALL_INFO_REPLACE:
                text = text.replace(org, dst)
            cls.expiration_time = time.time() + public_parameters.INFO_EXP_TIME  # With each load we reset the expiration counter
        except Exception as err:
            logging.getLogger(__name__).exception(err)
        return text

    @classmethod
    def is_active(cls):
        """
        Checks if this information is still valid
        :return: True if this instance references valid information
        """
        return time.time() < cls.expiration_time

    @staticmethod
    def current_date():
        """
        Return current date in a format valid for UPV's API
        :return: current date in a format valid for UPV's API
        """
        return datetime.date.today().strftime(upv_parameters.UPV_INFO_DATE_FORMAT)
