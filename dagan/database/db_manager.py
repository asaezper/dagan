import datetime
import logging
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from dagan.data import public_parameters
from dagan.database.db_enums import ReportMode
from dagan.database.entities import Restaurant, Subscription, Menu, Chat, MenuReport


class DBManager:
    @classmethod
    def initialize(cls):
        session_factory = sessionmaker(bind=create_engine('sqlite:///' + public_parameters.DB_FILE))
        cls.Session = scoped_session(session_factory)
        cls.lock = threading.Lock()  # Lock for access to the DB

    @classmethod
    def read_restaurants(cls):
        """
        Read all restaurants info from database
        :return: Dict of res_id: name
        """
        with cls.lock:
            restaurants = {}
            for item in cls.Session().query(Restaurant).all():
                restaurants[item.res_id] = item
            return restaurants

    @classmethod
    def read_subscriptions(cls):
        """
        Read all subscriptions info
        :return: Dictionary of chat_id: {res_id: [menu__id]}
        """
        with cls.lock:
            subscriptions = {}
            for item in cls.Session().query(Subscription).all():
                if item.chat_id not in subscriptions.keys():
                    subscriptions[item.chat_id] = {}
                if item.res_id not in subscriptions[item.chat_id].keys():
                    subscriptions[item.chat_id][item.res_id] = []
                if item.menu_id not in subscriptions[item.chat_id][item.res_id]:
                    subscriptions[item.chat_id][item.res_id].append(item.menu_id)
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
            session = cls.Session()
            try:
                if report_date is None:
                    report_date = datetime.datetime.now()
                mr = MenuReport()
                mr.menu = session.query(Menu).filter(Menu.res_id == res_id).filter(Menu.menu_id == menu_id).all()[0]
                mr.chat = session.query(Chat).filter(Chat.chat_id == chat_id).all()[0]
                mr.report_date = report_date
                mr.mode = mode
                session.add(mr)
                session.commit()
            except Exception as err:
                session.rollback()
                logging.getLogger(__name__).exception(err)
