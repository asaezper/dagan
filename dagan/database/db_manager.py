import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from dagan.data import public_parameters
from dagan.database.entities import Restaurant, Chat, MenuReport, SearchReport, ReportMode


class DBManager:
    chats = None
    menu_reports = None
    search_reports = None

    @classmethod
    def initialize(cls):
        session_factory = sessionmaker(bind=create_engine(public_parameters.DB_URL))
        cls.Session = scoped_session(session_factory)
        cls.lock = threading.Lock()  # Lock for access to the DB

        cls.chats = cls.read_chats()
        cls.menu_reports = cls.read_menu_reports()
        cls.search_reports = cls.read_search_reports()

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
            return cls.Session().query(Chat).all()

    @classmethod
    def read_menu_reports(cls):
        with cls.lock:
            return cls.Session().query(MenuReport).all()

    @classmethod
    def read_search_reports(cls):
        with cls.lock:
            return cls.Session().query(SearchReport).all()

    @classmethod
    def subscribe(cls, chat_id, res_id, menu_id):
        # TODO
        pass

    @classmethod
    def unsubscribe(cls, chat_id, res_id, menu_id):
        # TODO
        pass

    @classmethod
    def report_menu(cls, chat_id, res_id, menu_id, report_date=None, mode=ReportMode.MANUAL):
        # TODO
        pass
