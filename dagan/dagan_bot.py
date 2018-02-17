import datetime
import logging
import threading

import pkg_resources
from telegram import InlineKeyboardButton

from dagan.data import public_parameters, labels
from dagan.upv.menu_bot import MenuBot
from dagan.upv.old_info import TodayRestaurant, TodayMenu


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

    def start_cmd(self, bot, update):
        """
        Command Handler for start
        Send a keypad to select available restaurants

        :param bot: API's bot instance
        :param update: API's update instance
        """
        try:
            self.report_busy(update.message.chat_id)
            self.reload()  # Update info
            self.send_start_keypad(update.message.chat_id)  # Send the keypad
        except Exception as err:
            logging.getLogger(__name__).exception(err)

    def info_cmd(self, bot, update):
        """
        Command Handler for info
        Send a keypad to select all restaurants

        :param bot: API's bot instance
        :param update: API's update instance
        """
        try:
            self.report_busy(update.message.chat_id)
            self.send_info_keypad(update.message.chat_id)
        except Exception as err:
            logging.getLogger(__name__).exception(err)

    def subscriptions_cmd(self, bot, update):
        """
        Command Handler for subscriptions
        Send a message with the name of the menus you're subscribed

        :param bot: API's bot instance
        :param update: API's update instance
        """
        try:
            self.report_busy(update.message.chat_id)
            self.reload()  # Update info
            info = ''
            for item in DataManager.get_subscription_by_chat_id(update.message.chat_id):
                info += TodayRestaurant.generate_menu_name(item.menu.restaurant.name, item.menu.name)
            if not info:
                info = labels.NO_SUBS
            self.send_msg(update.message.chat_id, info)
        except Exception as err:
            logging.getLogger(__name__).exception(err)

    def help_cmd(self, bot, update):
        """
        Command Handler for help
        Send a message with some information about the bot

        :param bot: API's bot instance
        :param update: API's update instance
        """
        self.send_msg(update.message.chat_id, labels.HELP + pkg_resources.require("dagan")[0].version)

    def error(self, bot, update, error):
        """
        Error handler

        :param bot: API's bot instance
        :param update: API's update instance
        :param error: Telegram API error
        """
        logging.getLogger(__name__).warning('Update "%s" caused error "%s"', update, error)

    """ Callback Query Handler """

    def button(self, bot, update):
        """
        Button handler

        :param bot: API's bot instance
        :param update: API's update instance
        """
        try:
            self.reload()  # Update info
            prev_update = update.callback_query  # Get previous update
            cb_info = prev_update.data  # Get callback info
            if cb_info == public_parameters.CBDATA_CANCEL:
                """ Cancel request """
                self.remove_msg(*self.get_ids_in_update(prev_update))

            elif cb_info == public_parameters.CBDATA_START_CMD:
                """ Start command """
                self.start_cmd(bot, prev_update)

            elif cb_info == public_parameters.CBDATA_INFO_CMD:
                """ Info command """
                self.info_cmd(bot, prev_update)

            elif cb_info.startswith(public_parameters.CBDATA_REP_REQ):
                """ Report request """
                cb_info = cb_info.split(public_parameters.CBDATA_REP_REQ, 1)[-1]  # Get information below REQUEST code

                if cb_info.startswith(public_parameters.CBDATA_RESTAURANT):
                    """ Request restaurant info """
                    res_id = int(cb_info.replace(public_parameters.CBDATA_RESTAURANT, '', 1))
                    # Info below restaurant Callback code is the restaurant id
                    self.send_restaurant_report(*self.get_ids_in_update(prev_update), res_id)

                elif cb_info.startswith(public_parameters.CBDATA_MENU):
                    """ Request menu info """
                    res_id, menu_id, prev_cb = self.get_res_menu_id_in_request(cb_info)
                    self.send_menu_report(*self.get_ids_in_update(prev_update), res_id, menu_id)

            elif cb_info.startswith(public_parameters.CBDATA_INFO_REQ):
                """ Info request """
                cb_info = cb_info.split(public_parameters.CBDATA_INFO_REQ, 1)[-1]  # Get information below REQUEST code
                res_id = int(cb_info.replace(public_parameters.CBDATA_RESTAURANT, '', 1))
                self.send_info_restaurant(*self.get_ids_in_update(prev_update), res_id)

            elif cb_info.startswith(public_parameters.CBDATA_SUBS_REQ):
                """ Subscription """
                cb_info = cb_info.replace(public_parameters.CBDATA_SUBS_REQ, '', 1)
                res_id, menu_id, prev_cb = self.get_res_menu_id_in_request(cb_info)
                DataManager.subscribe(update.effective_chat.id, res_id, menu_id)
                if prev_cb == public_parameters.CBDATA_MENU:
                    self.send_menu_report(*self.get_ids_in_update(prev_update), res_id, menu_id)
                elif prev_cb == public_parameters.CBDATA_INFO_REQ:
                    self.send_info_restaurant(*self.get_ids_in_update(prev_update), res_id)

            elif cb_info.startswith(public_parameters.CBDATA_UNSUBS_REQ):
                """ Unsubscription request """
                cb_info = cb_info.replace(public_parameters.CBDATA_UNSUBS_REQ, '', 1)
                res_id, menu_id, prev_cb = self.get_res_menu_id_in_request(cb_info)
                DataManager.unsubscribe(update.effective_chat.id, res_id, menu_id)
                if prev_cb == public_parameters.CBDATA_MENU:
                    self.send_menu_report(*self.get_ids_in_update(prev_update), res_id, menu_id)
                elif prev_cb == public_parameters.CBDATA_INFO_REQ:
                    self.send_info_restaurant(*self.get_ids_in_update(prev_update), res_id)

        except Exception as err:
            logging.getLogger(__name__).exception(err)

    """ Data Senders """

    def send_start_keypad(self, chat_id):
        """
        Send a keypad with all menus available

        :param chat_id: If of char to write
        """
        if not self.today_info.restaurants:
            self.send_msg(chat_id, labels.NO_INFO)
        else:
            keyboard = [
                InlineKeyboardButton(restaurant.name,
                                     callback_data=public_parameters.CBDATA_REP_REQ + TodayRestaurant.generate_restaurant_cb(
                                         restaurant.id))
                for restaurant in self.today_info.restaurants.values()]
            self.send_msg(chat_id, labels.CHOOSE_RESTAURANT, keyboard)

    def send_restaurant_report(self, chat_id, msg_id, res_id):
        """
        Send a keypad with all menus available for this restaurant if there are more than one.
        Otherwise, it sends the info for the unique menu

        :param chat_id: Id of chat
        :param msg_id: Id of previous message
        :param res_id: Id of the restaurant
        """
        if res_id in self.today_info.restaurants.keys():
            if len(self.today_info.restaurants[res_id].menus) == 0:  # No menu for this restaurant
                self.edit_msg(chat_id, msg_id, labels.NO_INFO)
            elif len(self.today_info.restaurants[
                         res_id].menus) == 1:  # Just one menu for this restaurant - The bot sends its info
                self.send_menu_report(chat_id, msg_id, res_id, 0)
            else:  # More than one menu. The Bot sends a new keypad of menus
                keyboard = [InlineKeyboardButton(menu.name,
                                                 callback_data=public_parameters.CBDATA_REP_REQ + TodayMenu.generate_menu_cb(
                                                     res_id,
                                                     menu_id))
                            for menu_id, menu in enumerate(self.today_info.restaurants[res_id].menus)]
                self.edit_msg(chat_id, msg_id, labels.CHOOSE_MENU, keyboard, cols=1)
        else:  # Restaurant not present in dictionary of current available info
            self.edit_msg(chat_id, msg_id.message_id, labels.NO_INFO)

    def send_menu_report(self, chat_id, msg_id, res_id, menu_id):
        """
        Send the info of the requested menu

        :param chat_id: Id of chat
        :param msg_id: Id of previous message
        :param res_id: Id of the restaurant
        :param menu_id: Id of the menu
        """
        keypad = [InlineKeyboardButton(labels.AGAIN_BTN, callback_data=public_parameters.CBDATA_START_CMD),
                  self.generate_sub_rem_btn(chat_id, res_id, menu_id, public_parameters.CBDATA_MENU)]

        if res_id in self.today_info.restaurants.keys() and len(self.today_info.restaurants[res_id].menus) > menu_id:
            info = self.today_info.restaurants[res_id].show_info(menu_id)
            if msg_id is None:
                # It is a subscription message
                self.send_msg(chat_id, info, keypad, with_cancel=False)
                DataManager.report_menu(chat_id, res_id, menu_id, mode=ReportMode.AUTO)
            else:
                # It is a regular message
                self.edit_msg(chat_id, msg_id, info, keypad, with_cancel=False)
                DataManager.report_menu(chat_id, res_id, menu_id, mode=ReportMode.MANUAL)
        elif msg_id is not None:
            self.edit_msg(chat_id, msg_id, labels.NO_INFO, keypad, with_cancel=False)

    def send_info_keypad(self, chat_id):
        """
        Send a keypad with all menus available

        :param chat_id: If of char to write
        """
        keyboard = [
            InlineKeyboardButton(info.name,
                                 callback_data=public_parameters.CBDATA_INFO_REQ + TodayRestaurant.generate_restaurant_cb(
                                     res_id)) for res_id, info in DataManager.restaurants.items()]
        self.send_msg(chat_id, labels.CHOOSE_RESTAURANT, keyboard)

    def send_info_restaurant(self, chat_id, msg_id, res_id):
        """
        Send information for a restaurant

        :param chat_id: Id of chat
        :param msg_id: Id of previous message
        :param res_id: Id of the restaurant
        """
        res = DataManager.restaurants[res_id]
        name = public_parameters.BOLD_START + res.name + public_parameters.BOLD_END
        # Title
        self.edit_msg(chat_id, msg_id, name)
        # Location
        if res.latitude and res.longitude:
            self.send_location(chat_id, res.latitude, res.longitude)
        # Phone
        if res.phone:
            self.send_contact(chat_id, phone=res.phone, name=res.name)
        # Menus / Subs
        keypad = [self.generate_sub_rem_btn(chat_id, res_id, menu.menu_id, public_parameters.CBDATA_INFO_REQ, menu.name)
                  for menu in res.menus]
        keypad.append(InlineKeyboardButton(labels.INFO_BTN, callback_data=public_parameters.CBDATA_INFO_CMD))

        self.send_msg(chat_id, labels.SUBS_MENUS, keypad, with_cancel=False)

    """ Subscription handlers """

    def check_subs(self):
        """
        Method executed by the subscription checker thread.
        Send the info a subscribed menu if there are no previous messages for this user and menu today.
        It only works at parametrized days and hours
        """
        stopped = threading.Event()
        while not stopped.wait(public_parameters.THREAD_TIMER_SECONDS):
            # Execute below code each THREAD_TIMER_SECONDS seconds
            # Check time
            try:
                logging.getLogger(__name__).info('Checking subscriptions...')
                weekday = datetime.datetime.today().weekday()
                hour = datetime.datetime.today().hour + (datetime.datetime.today().minute / 60)
                if weekday in public_parameters.SUBS_WEEKDAY_LIST and \
                        public_parameters.SUBS_HOUR_INTERVAL[0] <= hour < public_parameters.SUBS_HOUR_INTERVAL[
                    1]:  # Valid day and hout
                    self.reload()  # Reload info
                    with DataManager.subscriptions_lock:
                        subs = dict(DataManager.subscriptions)  # Copy subscriptions to avoid conflict
                    reports = DataManager.read_reports()  # Get actual reports
                    logging.getLogger(__name__).info('Subscriptions: ' + str(subs))
                    logging.getLogger(__name__).info('Reports: ' + str(reports))  # FIXME Remove
                    for chat_id in subs.keys():  # For each chat - restaurant - menu
                        for res_id in subs[chat_id].keys():
                            for menu_id in subs[chat_id][res_id]:
                                if chat_id not in reports.keys() \
                                        or res_id not in reports[chat_id].keys() \
                                        or menu_id not in reports[chat_id][res_id]:  # No previous report
                                    try:
                                        self.report_busy(chat_id)
                                        self.send_menu_report(chat_id, None, res_id, menu_id)
                                    except Exception as err:
                                        logging.getLogger(__name__).exception(err)
                logging.getLogger(__name__).info('Checking subscriptions... Done')
            except Exception as err:
                logging.getLogger(__name__).exception(err)

    """ Auxiliary methods """

    @staticmethod
    def get_res_menu_id_in_request(cb_info):
        """
        Get restaurant and menu ids stored in a callback data
        :param cb_info: Text to process
        :return: res_id, menu_id, prev_cb
        """
        cb_info = cb_info.replace(public_parameters.CBDATA_MENU, '', 1)  # Remove initial code
        menu_id, res_id = cb_info.split(public_parameters.CBDATA_RESTAURANT)
        prev_cb = None
        tmp_list = res_id.split(public_parameters.CBDATA_PREVIOUS_TYPE)
        if len(tmp_list) == 2:
            res_id = tmp_list[0]
            prev_cb = tmp_list[1]
        # Menu - Restaurant ids are separated with public_parameters.CBDATA_RESTAURANT
        return int(res_id), int(menu_id), prev_cb

    @staticmethod
    def generate_sub_rem_btn(chat_id, res_id, menu_id, prev_msg_type, name=None):
        """
        Returns a subscription button. Its value depends of subscription status for this chat and menu

        :param chat_id: Id of chat
        :param res_id: Id of restaurant
        :param menu_id: Id of menu
        :param prev_msg_type: Callback data of the type of message that calls the [un]subscription
        :param name: Extra text button
        :return: The subscription button
        """
        if DataManager.check_subscription(chat_id, res_id, menu_id):
            msg = labels.REM_BTN
            if name is not None:
                msg = name + labels.SUBS_SEPARATOR + msg
            return InlineKeyboardButton(msg,
                                        callback_data=public_parameters.CBDATA_UNSUBS_REQ + TodayMenu.generate_menu_cb(
                                            res_id, menu_id) + public_parameters.CBDATA_PREVIOUS_TYPE + prev_msg_type)
        else:
            msg = labels.SUB_BTN
            if name is not None:
                msg = name + labels.SUBS_SEPARATOR + msg
            return InlineKeyboardButton(msg,
                                        callback_data=public_parameters.CBDATA_SUBS_REQ +
                                                      TodayMenu.generate_menu_cb(res_id, menu_id) +
                                                      public_parameters.CBDATA_PREVIOUS_TYPE + prev_msg_type)

    @staticmethod
    def get_ids_in_update(update):
        """
        Get chat_id and message_id of a update
        :param update: Update
        :return: chat_id and message_id of the update
        """
        return update.message.chat_id, update.message.message_id
