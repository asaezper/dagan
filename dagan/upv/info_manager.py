import datetime
import json
import logging
import time

import requests

from dagan.data import public_parameters
from dagan.database.db_manager import DBManager
from dagan.database.entities import ReportMode
from dagan.upv.data import upv_parameters
from dagan.upv.today_menu import TodayMenu
from dagan.upv.token import Token
from dagan.utils.dagan_rw_lock import DaganRWLock


class InfoManager(DBManager):
    data_lock = DaganRWLock()  # Lock for access to info data (restaurants, chats, searches, ...)
    report_lock = DaganRWLock()  # Lock for access to report data (reported menus, results, ...)
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
        cls.__reload_token()
        cls.__reload_info()

    @classmethod
    def __reload_token(cls):
        """
        Check if token is valid. If not, request it and save it
        """
        if not cls.token.is_active():
            cls.token.load(cls._request_token())
            cls.token.save()

    @staticmethod
    def _request_token():
        text = ''
        try:
            text = requests.post(upv_parameters.UPV_TOKEN_URL, timeout=upv_parameters.UPV_TOKEN_TIMEOUT,
                                 headers=upv_parameters.UPV_TOKEN_HEADERS, data=upv_parameters.UPV_TOKEN_TYPE,
                                 auth=(upv_parameters.UPV_USER, upv_parameters.UPV_PSW)).text
        except Exception as err:
            logging.getLogger(__name__).exception(err)
        return text

    @classmethod
    def __reload_info(cls):
        """
        Check if restaurants info is still valid. If not, request it and save ir
        :return:
        """
        if not cls.is_active():
            with cls.data_lock.writer():
                cls.restaurants = cls.read_restaurants()
                text = cls._request_info()
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
    def _request_info(cls):
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
    def get_available_restaurants(cls):
        available_restaurants = []
        for res in cls.restaurants.values():
            for menu in res.menus.values():
                if menu.today_menu is not None:
                    available_restaurants.append(res)
                    break
        return available_restaurants

    @classmethod
    def check_subscription(cls, chat_id, res_id, menu_id):
        found = False
        if chat_id in cls.chats.keys():
            for sub in cls.chats[chat_id].subscriptions:
                if sub.res_id == res_id and sub.menu_id == menu_id:
                    found = True
                    break
        return found

    @classmethod
    def subscribe(cls, chat_id, res_id, menu_id):
        with cls.data_lock.writer():
            DBManager.subscribe(chat_id, res_id, menu_id)

    @classmethod
    def unsubscribe(cls, chat_id, res_id, menu_id):
        with cls.data_lock.writer():
            DBManager.unsubscribe(chat_id, res_id, menu_id)

    @classmethod
    def report_menu(cls, chat_id, res_id, menu_id, report_date=None, mode=ReportMode.MANUAL):
        with cls.report_lock.writer():
            DBManager.report_menu(chat_id, res_id, menu_id, report_date, mode)

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
