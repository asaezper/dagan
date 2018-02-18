import datetime
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from dagan.data import public_parameters
from dagan.database.entities import Restaurant, Chat, MenuReport, ReportMode, Subscription


class DBManager:
    Session = None
    lock = threading.Lock()  # Lock for access to the DB
    chats = None
    menu_reports = None
    search_reports = None

    @classmethod
    def initialize(cls):
        session_factory = sessionmaker(bind=create_engine(public_parameters.DB_URL))
        cls.Session = scoped_session(session_factory)

        cls.chats = cls.read_chats()
        cls.menu_reports = cls.read_menu_reports()

    @classmethod
    def read_restaurants(cls):
        with cls.lock:
            restaurants = {}
            for item in cls.Session().query(Restaurant).all():
                restaurants[item.res_id] = item
            return restaurants

    @classmethod
    def read_chats(cls):
        with cls.lock:
            chats = []
            for item in cls.Session().query(Chat).all():
                chats[item.chat_id] = item
            return chats

    @classmethod
    def read_menu_reports(cls):
        menu_report = {}  # {chat_id: {res_id: {list_of_menu_ids}}
        with cls.lock:
            result_list = cls.Session().query(MenuReport).filter(
                MenuReport.report_date >= datetime.date.today().strftime('%Y-%m-%d')).all()
            for item in result_list:
                if item.chat_id not in menu_report.keys():
                    menu_report[item.chat_id] = {}
                if item.res_id not in menu_report[item.chat_id].keys():
                    menu_report[item.chat_id][item.res_id] = []
                if item.menu_id not in menu_report[item.chat_id][item.res_id]:
                    menu_report[item.chat_id][item.res_id].append(item.menu_id)
            return menu_report

    @classmethod
    def subscribe(cls, chat_id, res_id, menu_id):
        sub = Subscription()
        sub.res_id = res_id
        sub.menu_id = menu_id
        sub.chat_id = chat_id
        with cls.lock and cls.Session() as session:
            cls.chats[chat_id].subscriptions.append(sub)
            session.add(cls.chats[chat_id])
            session.commit()

    @classmethod
    def unsubscribe(cls, chat_id, res_id, menu_id):
        with cls.lock and cls.Session() as session:
            for sub in cls.chats[chat_id].subscriptions:
                if sub.res_id == res_id and sub.menu_id == menu_id:
                    cls.chats[chat_id].subscriptions.remove(sub)
                    break
            session.add(cls.chats[chat_id])
            session.commit()

    @classmethod
    def report_menu(cls, chat_id, res_id, menu_id, report_date=None, mode=ReportMode.MANUAL):
        with cls.lock and cls.Session() as session:
            mr = MenuReport()
            mr.res_id = res_id
            mr.menu_id = menu_id
            mr.chat_id = chat_id
            mr.report_date = datetime.datetime.now()
            mr.mode = mode
            session.add(mr)
            session.commit()
