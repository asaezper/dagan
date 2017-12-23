import datetime
import logging
import sqlite3
import threading

from dagan.data import public_parameters
from dagan.database.db_enums import ReportMode


class DBManager:
    conn = sqlite3.connect(public_parameters.DB_FILE, check_same_thread=False)  # Database connection
    lock = threading.Lock()  # Lock for access to the DB

    @classmethod
    def read_restaurants(cls):
        """
        Read all restaurants info from database
        :return: Dict of res_id: name
        """
        with cls.lock:
            c = cls.conn.cursor()
            restaurants = {}
            for row in c.execute("SELECT * from restaurant"):
                res_id = int(row[0])
                name = str(row[1])
                if res_id not in restaurants.keys():
                    restaurants[res_id] = name
            return restaurants

    @classmethod
    def read_menus(cls):
        """
        Read all menus info from database
        :return: Dictionary of res_id: {menu_id: menu_name}
        """
        with cls.lock:
            c = cls.conn.cursor()
            menus = {}
            for row in c.execute("SELECT * from menu"):
                res_id = int(row[0])
                menu_id = int(row[1])
                name = str(row[2])
                if res_id not in menus.keys():
                    menus[res_id] = {}
                if menu_id not in menus[res_id].keys():
                    menus[res_id][menu_id] = name
            return menus

    @classmethod
    def read_subscriptions(cls):
        """
        Read all subscriptions info
        :return: Dictionary of chat_id: {res_id: [menu__id]}
        """
        with cls.lock:
            c = cls.conn.cursor()
            subscriptions = {}
            for row in c.execute("SELECT * from subscription"):
                chat_id = int(row[0])
                res_id = int(row[1])
                menu_id = int(row[2])
                if chat_id not in subscriptions.keys():
                    subscriptions[chat_id] = {}
                if res_id not in subscriptions[chat_id].keys():
                    subscriptions[chat_id][res_id] = []
                if menu_id not in subscriptions[chat_id][res_id]:
                    subscriptions[chat_id][res_id].append(menu_id)
            return subscriptions

    @classmethod
    def read_reports(cls):
        """
        Read all menus reported today
        :return: Dictionary of chat_id: {res_id: [menu__id]}
        """
        with cls.lock:
            c = cls.conn.cursor()
            reports = {}
            for row in c.execute("SELECT chat_id, res_id, menu_id from menu_report " +
                                 "where date(datetime(report_date)) = date('now') group by chat_id, res_id, menu_id;"):
                chat_id = int(row[0])
                res_id = int(row[1])
                menu_id = int(row[2])
                if chat_id not in reports.keys():
                    reports[chat_id] = {}
                if res_id not in reports[chat_id].keys():
                    reports[chat_id][res_id] = []
                if menu_id not in reports[chat_id][res_id]:
                    reports[chat_id][res_id].append(menu_id)
            return reports

    @classmethod
    def subscribe(cls, chat_id, res_id, menu_id):
        """
        Stores a subscription into the database
        
        :param chat_id: Id of chat
        :param res_id: Id of restaurant
        :param menu_id: If of menu
        """
        with cls.lock:
            c = cls.conn.cursor()
            c.execute("INSERT INTO subscription VALUES (?, ?, ?)", (chat_id, res_id, menu_id))
            cls.conn.commit()

    @classmethod
    def unsubscribe(cls, chat_id, res_id, menu_id):
        """
        Removes a subscription of the database

        :param chat_id: Id of chat
        :param res_id: Id of restaurant
        :param menu_id: If of menu
        """
        with cls.lock:
            c = cls.conn.cursor()
            c.execute(
                "DELETE FROM subscription WHERE chat_id == '" + str(chat_id) + "' and res_id == '" + str(res_id) +
                "' and menu_id == '" + str(menu_id) + "'")
            cls.conn.commit()

    @classmethod
    def report_menu(cls, chat_id, res_id, menu_id, report_date=None, mode=ReportMode.MANUAL):
        """
        Save a menu report into the database

        :param chat_id: Id of chat
        :param res_id: Id of restaurant
        :param menu_id: If of menu
        :param report_date: Report date
        :param mode: Report mode
        """
        with cls.lock:
            try:
                if report_date is None:
                    report_date = datetime.datetime.now()
                c = cls.conn.cursor()
                c.execute("INSERT INTO menu_report VALUES (?, ?, ?, ?, ?)",
                          (chat_id, res_id, menu_id, report_date, mode.value))
                cls.conn.commit()
            except Exception as err:
                cls.conn.rollback()
                logging.getLogger(__name__).exception(err)
