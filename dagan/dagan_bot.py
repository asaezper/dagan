import datetime
import logging
import threading

import pkg_resources
from telegram import InlineKeyboardButton

from dagan.base_bot import MenuBaseBot
from dagan.database.db_manager import DBReader, DBManager
from dagan.database.report_modes import ReportMode
from dagan.internal_data import labels, dagan_parameters
from dagan.messages import edit_msg, reply_msg, remove_msg, send_msg
from dagan.objects.information import Bar, Menu


class DaganBot(MenuBaseBot):
    def __init__(self, bot):
        super(DaganBot, self).__init__(bot)
        self.subscriptions_thread = threading.Thread(target=self.check_subs)
        self.subscriptions_thread.start()

    """ Subscription handlers """

    def check_subs(self):
        stopped = threading.Event()
        while not stopped.wait(dagan_parameters.THREAD_TIMER_SECONDS):
            # Check time
            weekday = datetime.datetime.today().weekday()
            hour = datetime.datetime.today().hour + (datetime.datetime.today().minute / 60)
            if weekday in dagan_parameters.SUBS_WEEKDAY_LIST and \
                    dagan_parameters.SUBS_HOUR_INTERVAL[0] <= hour < dagan_parameters.SUBS_HOUR_INTERVAL[1]:
                self.update_info()
                with DBReader.subscriptions_lock:
                    subs = dict(DBReader.subscriptions)
                reports = DBManager.read_reports()
                for chat_id in subs.keys():
                    for bar_id in subs[chat_id].keys():
                        for menu_id in subs[chat_id][bar_id]:
                            if chat_id not in reports.keys() \
                                    or bar_id not in reports[chat_id].keys() \
                                    or menu_id not in reports[chat_id][bar_id]:
                                try:
                                    self.send_menu_info_by_new(chat_id, bar_id, menu_id, chain=True)
                                except Exception as err:
                                    logging.getLogger(__name__).exception(err)

    """ Command Handlers """

    def start(self, bot, update):
        try:
            self.update_info()
            self.send_start_menu(update)
        except Exception as err:
            logging.getLogger(__name__).exception(err)

    def help(self, bot, update):
        update.message.reply_text(labels.HELP + pkg_resources.require("dagan")[0].version, parse_mode=labels.MODE)

    def error(self, bot, update, error):
        logging.getLogger(__name__).warning('Update "%s" caused error "%s"', update, error)

    def eegg(self, bot, update):
        update.message.reply_text(labels.EEGG, parse_mode=labels.MODE)

    """ Callback Query Handler """

    def button(self, bot, update):
        try:
            query = update.callback_query
            my_req_id = query.data
            if my_req_id == dagan_parameters.CBDATA_CANCEL:
                # Cancel request
                remove_msg(query)
            if my_req_id.startswith(dagan_parameters.CBDATA_REQ):
                # Request
                my_req_id = my_req_id.split(dagan_parameters.CBDATA_REQ, 1)[-1]
                if my_req_id.startswith(dagan_parameters.CBDATA_BAR):
                    # Request bar info
                    bar_id = int(my_req_id.replace(dagan_parameters.CBDATA_BAR, '', 1))
                    self.send_bar_info(query, bar_id, chain=True)
                elif my_req_id.startswith(dagan_parameters.CBDATA_MENU):
                    # Request menu info
                    my_req_id = my_req_id.replace(dagan_parameters.CBDATA_MENU, '', 1)
                    menu_id, bar_id = my_req_id.split(dagan_parameters.CBDATA_BAR)
                    bar_id, menu_id = int(bar_id), int(menu_id)
                    self.send_menu_info_by_edit(query, bar_id, menu_id, chain=True)
            elif my_req_id.startswith(dagan_parameters.CBDATA_SUBS):
                # Subscription
                my_req_id = my_req_id.split(dagan_parameters.CBDATA_SUBS, 1)[-1]
                menu_id, bar_id = my_req_id.replace(dagan_parameters.CBDATA_MENU, '', 1).split(
                    dagan_parameters.CBDATA_BAR)
                bar_id, menu_id = int(bar_id), int(menu_id)
                DBReader.add_subscription(update.effective_chat.id, bar_id, menu_id)
                self.send_menu_info_by_edit(query, bar_id, menu_id, chain=True)
            elif my_req_id.startswith(dagan_parameters.CBDATA_REM):
                # Subscription
                my_req_id = my_req_id.split(dagan_parameters.CBDATA_REM, 1)[-1]
                menu_id, bar_id = my_req_id.replace(dagan_parameters.CBDATA_MENU, '', 1).split(
                    dagan_parameters.CBDATA_BAR)
                bar_id, menu_id = int(bar_id), int(menu_id)
                DBReader.remove_subscription(update.effective_chat.id, bar_id, menu_id)
                self.send_menu_info_by_edit(query, bar_id, menu_id, chain=True)
            elif my_req_id == dagan_parameters.CBDATA_START:
                self.start(bot, query)
        except Exception as err:
            logging.getLogger(__name__).exception(err)

    """ Data Senders """

    def send_start_menu(self, update):
        if not self.info.bars:
            reply_msg(update, labels.NO_INFO)
        else:
            keyboard = [
                InlineKeyboardButton(bar.name, callback_data=dagan_parameters.CBDATA_REQ + Bar.generate_bar_cb(bar.id))
                for bar in self.info.bars.values()]
            reply_msg(update, labels.CHOOSE_BAR, keyboard)

    def send_bar_info(self, query, my_req_id, chain):
        if my_req_id in self.info.bars.keys():
            if self.info.bars[my_req_id].menus.__len__() == 1:
                self.send_menu_info_by_edit(query, my_req_id, 0, chain)
            elif self.info.bars[my_req_id].menus.__len__() > 1:
                keyboard = [InlineKeyboardButton(menu.name,
                                                 callback_data=dagan_parameters.CBDATA_REQ + Menu.generate_menu_cb(
                                                     my_req_id, self.info.bars[my_req_id].menus.index(menu)))
                            for menu in self.info.bars[my_req_id].menus]
                edit_msg(self.bot, query, labels.CHOOSE_MENU, keyboard, cols=1)
            else:
                edit_msg(self.bot, query, labels.NO_INFO)
        else:
            edit_msg(self.bot, query, labels.NO_INFO)

    def send_menu_info_by_edit(self, query, bar_id, menu_id, chain):
        ok, chain_keyboard = self._generate_menu_info(query.message.chat_id, bar_id, menu_id, chain)
        if ok:
            edit_msg(self.bot, query, self.info.bars[bar_id].show_info(menu_id), chain_keyboard, with_cancel=False)
            DBManager.report_menu(query.message.chat_id, bar_id, menu_id, mode=ReportMode.MANUAL)
        else:
            edit_msg(self.bot, query, labels.NO_INFO, chain_keyboard, with_cancel=False)

    def send_menu_info_by_new(self, chat_id, bar_id, menu_id, chain):
        ok, chain_keyboard = self._generate_menu_info(chat_id, bar_id, menu_id, chain)
        if ok:
            send_msg(self.bot, chat_id, self.info.bars[bar_id].show_info(menu_id), chain_keyboard, with_cancel=False)
            DBManager.report_menu(chat_id, bar_id, menu_id, mode=ReportMode.AUTO)
        else:
            send_msg(self.bot, chat_id, labels.NO_INFO, chain_keyboard, with_cancel=False)

    def _generate_menu_info(self, chat_id, bar_id, menu_id, chain):
        chain_keyboard = []
        if chain:
            chain_keyboard.append(InlineKeyboardButton(labels.AGAIN_BTN, callback_data=dagan_parameters.CBDATA_START))
        chain_keyboard.append(self.generate_sub_rem_btn(chat_id, bar_id, menu_id))
        if bar_id in self.info.bars.keys() and self.info.bars[bar_id].menus.__len__() > menu_id:
            return True, chain_keyboard
        else:
            return False, chain_keyboard

    """ Auxiliary methods for Data Senders """

    def generate_sub_rem_btn(self, chat_id, bar_id, menu_id):
        if DBReader.check_subscription(chat_id, bar_id, menu_id):
            return self._generate_unsub_btn(bar_id, menu_id)
        else:
            return self._generate_sub_btn(bar_id, menu_id)

    def _generate_sub_btn(self, bar_id, menu_id):
        return InlineKeyboardButton(labels.SUB_BTN,
                                    callback_data=dagan_parameters.CBDATA_SUBS + Menu.generate_menu_cb(bar_id, menu_id))

    def _generate_unsub_btn(self, bar_id, menu_id):
        return InlineKeyboardButton(labels.REM_BTN,
                                    callback_data=dagan_parameters.CBDATA_REM + Menu.generate_menu_cb(bar_id, menu_id))

    # updater.dispatcher.add_handler(CommandHandler('subs', dagan.subs))
    # def subs(bot, update):
    #     info = ''
    #     if update.message.chat_id in subscriptions.keys():
    #         for bar_id in subscriptions[update.message.chat_id].keys():
    #             for menu_id in subscriptions[update.message.chat_id][bar_id]:
    #                 info += self.info.bars[bar_id].generate_menu_name(int(menu_id))
    #     if not info:
    #         info = labels.NO_SUBS
    #     reply_msg(update, info)
