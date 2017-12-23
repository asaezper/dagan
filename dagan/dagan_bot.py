import datetime
import logging
import threading

import pkg_resources
from telegram import InlineKeyboardButton

from dagan.data.labels import NO_SUBS, HELP, NO_INFO, CHOOSE_MENU, AGAIN_BTN, SUB_BTN, REM_BTN, \
    CHOOSE_RESTAURANT
from dagan.data.public_parameters import THREAD_TIMER_SECONDS, SUBS_WEEKDAY_LIST, SUBS_HOUR_INTERVAL, MODE, \
    CBDATA_CANCEL, CBDATA_REQUEST, CBDATA_RESTAURANT, CBDATA_MENU, CBDATA_SUBSCRIBE, CBDATA_UNSUBSCRIBE, CBDATA_START
from dagan.database.db_manager import DBReader, DBManager
from dagan.database.report_modes import ReportMode
from dagan.upv.info import Restaurant, Menu
from dagan.upv.menu_bot import MenuBot


class DaganBot(MenuBot):
    """
    Dagan Bot: A UPV Menus Telegram bot that communicates with users with commands and buttons
    """

    def __init__(self, bot):
        super(DaganBot, self).__init__(bot)
        # Start subscriptions thread
        self.subscriptions_thread = threading.Thread(target=self.check_subs)
        self.subscriptions_thread.start()

    """ Command Handlers """

    def start(self, bot, update):
        try:
            self.reload()
            self.send_start_menu(update)
        except Exception as err:
            logging.getLogger(__name__).exception(err)

    def subs(self, bot, update):
        try:
            info = ''
            for res_id, menu_id in DBReader.get_subscription_by_chat_id(update.message.chat_id):
                try:
                    info += self.info.restaurants[res_id].show_menu_name(int(menu_id))
                except:
                    info += Restaurant.generate_menu_name(DBReader.restaurants[res_id], DBReader.menus[res_id][menu_id])
            if not info:
                info = NO_SUBS
            self.send_msg(update.message.chat_id, info)
        except Exception as err:
            logging.getLogger(__name__).exception(err)

    def help(self, bot, update):
        # FIXME
        update.message.reply_text(HELP + pkg_resources.require("dagan")[0].version, parse_mode=MODE)

    def error(self, bot, update, error):
        logging.getLogger(__name__).warning('Update "%s" caused error "%s"', update, error)

    """ Subscription handlers """

    def check_subs(self):
        stopped = threading.Event()
        while not stopped.wait(THREAD_TIMER_SECONDS):
            # Check time
            try:
                weekday = datetime.datetime.today().weekday()
                hour = datetime.datetime.today().hour + (datetime.datetime.today().minute / 60)
                if weekday in SUBS_WEEKDAY_LIST and \
                        SUBS_HOUR_INTERVAL[0] <= hour < SUBS_HOUR_INTERVAL[1]:
                    self.reload()
                    with DBReader.subscriptions_lock:
                        subs = dict(DBReader.subscriptions)
                    reports = DBManager.read_reports()
                    for chat_id in subs.keys():
                        for res_id in subs[chat_id].keys():
                            for menu_id in subs[chat_id][res_id]:
                                if chat_id not in reports.keys() \
                                        or res_id not in reports[chat_id].keys() \
                                        or menu_id not in reports[chat_id][res_id]:
                                    try:
                                        self.send_menu_info_by_new(chat_id, res_id, menu_id, chain=True)
                                    except Exception as err:
                                        logging.getLogger(__name__).exception(err)
            except Exception as err:
                logging.getLogger(__name__).exception(err)

    """ Callback Query Handler """

    def button(self, bot, update):
        try:
            query = update.callback_query
            my_req_id = query.data
            if my_req_id == CBDATA_CANCEL:
                # Cancel request
                self.remove_msg(query.message.chat_id, query.message.message_id)
            if my_req_id.startswith(CBDATA_REQUEST):
                # Request
                my_req_id = my_req_id.split(CBDATA_REQUEST, 1)[-1]
                if my_req_id.startswith(CBDATA_RESTAURANT):
                    # Request restaurant info
                    res_id = int(my_req_id.replace(CBDATA_RESTAURANT, '', 1))
                    self.send_restaurant_info(query, res_id, chain=True)
                elif my_req_id.startswith(CBDATA_MENU):
                    # Request menu info
                    my_req_id = my_req_id.replace(CBDATA_MENU, '', 1)
                    menu_id, res_id = my_req_id.split(CBDATA_RESTAURANT)
                    res_id, menu_id = int(res_id), int(menu_id)
                    self.send_menu_info_by_edit(query, res_id, menu_id, chain=True)
            elif my_req_id.startswith(CBDATA_SUBSCRIBE):
                # Subscription
                my_req_id = my_req_id.split(CBDATA_SUBSCRIBE, 1)[-1]
                menu_id, res_id = my_req_id.replace(CBDATA_MENU, '', 1).split(
                    CBDATA_RESTAURANT)
                res_id, menu_id = int(res_id), int(menu_id)
                DBReader.add_subscription(update.effective_chat.id, res_id, menu_id)
                self.send_menu_info_by_edit(query, res_id, menu_id, chain=True)
            elif my_req_id.startswith(CBDATA_UNSUBSCRIBE):
                # Subscription
                my_req_id = my_req_id.split(CBDATA_UNSUBSCRIBE, 1)[-1]
                menu_id, res_id = my_req_id.replace(CBDATA_MENU, '', 1).split(
                    CBDATA_RESTAURANT)
                res_id, menu_id = int(res_id), int(menu_id)
                DBReader.remove_subscription(update.effective_chat.id, res_id, menu_id)
                self.send_menu_info_by_edit(query, res_id, menu_id, chain=True)
            elif my_req_id == CBDATA_START:
                self.start(bot, query)
        except Exception as err:
            logging.getLogger(__name__).exception(err)

    """ Data Senders """

    def send_start_menu(self, update):
        if not self.info.restaurants:
            self.send_msg(update.message.chat_id, NO_INFO)
        else:
            keyboard = [
                InlineKeyboardButton(restaurant.name,
                                     callback_data=CBDATA_REQUEST + Restaurant.generate_restaurant_cb(restaurant.id))
                for restaurant in self.info.restaurants.values()]
            self.send_msg(update.message.chat_id, CHOOSE_RESTAURANT, keyboard)

    def send_restaurant_info(self, query, my_req_id, chain):
        if my_req_id in self.info.restaurants.keys():
            if self.info.restaurants[my_req_id].menus.__len__() == 1:
                self.send_menu_info_by_edit(query, my_req_id, 0, chain)
            elif self.info.restaurants[my_req_id].menus.__len__() > 1:
                keyboard = [InlineKeyboardButton(menu.name,
                                                 callback_data=CBDATA_REQUEST + Menu.generate_menu_cb(
                                                     my_req_id, self.info.restaurants[my_req_id].menus.index(menu)))
                            for menu in self.info.restaurants[my_req_id].menus]
                self.edit_msg(query.message.chat_id, query.message.message_id, CHOOSE_MENU, keyboard, cols=1)
            else:
                self.edit_msg(query.message.chat_id, query.message.message_id, NO_INFO)
        else:
            self.edit_msg(query.message.chat_id, query.message.message_id, NO_INFO)

    def send_menu_info_by_edit(self, query, res_id, menu_id, chain):
        ok, chain_keyboard = self._generate_menu_info(query.message.chat_id, res_id, menu_id, chain)
        if ok:
            self.edit_msg(query.message.chat_id, query.message.message_id,
                          self.info.restaurants[res_id].show_info(menu_id),
                          chain_keyboard, with_cancel=False)
            DBManager.report_menu(query.message.chat_id, res_id, menu_id, mode=ReportMode.MANUAL)
        else:
            self.edit_msg(query.message.chat_id, query.message.message_id, NO_INFO, chain_keyboard,
                          with_cancel=False)

    def send_menu_info_by_new(self, chat_id, res_id, menu_id, chain):
        ok, chain_keyboard = self._generate_menu_info(chat_id, res_id, menu_id, chain)
        if ok:
            self.send_msg(chat_id, self.info.restaurants[res_id].show_info(menu_id), chain_keyboard, with_cancel=False)
            DBManager.report_menu(chat_id, res_id, menu_id, mode=ReportMode.AUTO)

    def _generate_menu_info(self, chat_id, res_id, menu_id, chain):
        chain_keyboard = []
        if chain:
            chain_keyboard.append(InlineKeyboardButton(AGAIN_BTN, callback_data=CBDATA_START))
        chain_keyboard.append(self.generate_sub_rem_btn(chat_id, res_id, menu_id))
        if res_id in self.info.restaurants.keys() and self.info.restaurants[res_id].menus.__len__() > menu_id:
            return True, chain_keyboard
        else:
            return False, chain_keyboard

    """ Auxiliary methods for Data Senders """

    def generate_sub_rem_btn(self, chat_id, res_id, menu_id):
        if DBReader.check_subscription(chat_id, res_id, menu_id):
            return self._generate_unsub_btn(res_id, menu_id)
        else:
            return self._generate_sub_btn(res_id, menu_id)

    def _generate_sub_btn(self, res_id, menu_id):
        return InlineKeyboardButton(SUB_BTN,
                                    callback_data=CBDATA_SUBSCRIBE + Menu.generate_menu_cb(res_id,
                                                                                           menu_id))

    def _generate_unsub_btn(self, res_id, menu_id):
        return InlineKeyboardButton(REM_BTN,
                                    callback_data=CBDATA_UNSUBSCRIBE + Menu.generate_menu_cb(res_id,
                                                                                             menu_id))
