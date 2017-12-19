import datetime
import logging
import sqlite3
import threading

from dagan.database.report_modes import ReportMode
from dagan.resources import resource_path


class DBManager:
    DBFILE = 'dagan.db'
    conn = sqlite3.connect(resource_path(DBFILE), check_same_thread=False)
    lock = threading.Lock()

    @classmethod
    def read_bars(cls):
        with cls.lock:
            c = cls.conn.cursor()
            bars = {}
            for row in c.execute("SELECT * from bar"):
                bar_id = int(row[0])
                name = str(row[1])
                if bar_id not in bars.keys():
                    bars[bar_id] = name
            return bars

    @classmethod
    def read_manus(cls):
        with cls.lock:
            c = cls.conn.cursor()
            menus = {}
            for row in c.execute("SELECT * from menu"):
                bar_id = int(row[0])
                menu_id = int(row[1])
                name = str(row[2])
                if bar_id not in menus.keys():
                    menus[bar_id] = {}
                if menu_id not in menus[bar_id].keys():
                    menus[bar_id][menu_id] = name
            return menus

    @classmethod
    def read_subscriptions(cls):
        with cls.lock:
            c = cls.conn.cursor()
            subscriptions = {}
            for row in c.execute("SELECT * from subscription"):
                chat_id = int(row[0])
                bar_id = int(row[1])
                menu_id = int(row[2])
                if chat_id not in subscriptions.keys():
                    subscriptions[chat_id] = {}
                if bar_id not in subscriptions[chat_id].keys():
                    subscriptions[chat_id][bar_id] = []
                if menu_id not in subscriptions[chat_id][bar_id]:
                    subscriptions[chat_id][bar_id].append(menu_id)
            return subscriptions

    @classmethod
    def subscribe(cls, chat_id, bar_id, menu_id):
        with cls.lock:
            c = cls.conn.cursor()
            c.execute("INSERT INTO subscription VALUES (?, ?, ?)", (chat_id, bar_id, menu_id))
            cls.conn.commit()

    @classmethod
    def remove_subscription(cls, chat_id, bar_id, menu_id):
        with cls.lock:
            c = cls.conn.cursor()
            c.execute(
                "DELETE FROM subscription WHERE chat_id == '" + str(chat_id) + "' and bar_id == '" + str(bar_id) +
                "' and menu_id == '" + str(menu_id) + "'")
            cls.conn.commit()

    @classmethod
    def read_reports(cls):
        with cls.lock:
            c = cls.conn.cursor()
            reports = {}
            for row in c.execute("SELECT chat_id, bar_id, menu_id from menu_report " +
                                 "where date(datetime(report_date)) = date('now') group by chat_id, bar_id, menu_id;"):
                chat_id = int(row[0])
                bar_id = int(row[1])
                menu_id = int(row[2])
                if chat_id not in reports.keys():
                    reports[chat_id] = {}
                if bar_id not in reports[chat_id].keys():
                    reports[chat_id][bar_id] = []
                if menu_id not in reports[chat_id][bar_id]:
                    reports[chat_id][bar_id].append(menu_id)
            return reports

    @classmethod
    def report_menu(cls, chat_id, bar_id, menu_id, report_date=None, mode=ReportMode.MANUAL):
        with cls.lock:
            try:
                if report_date is None:
                    report_date = datetime.datetime.now()
                c = cls.conn.cursor()
                c.execute("INSERT INTO menu_report VALUES (?, ?, ?, ?, ?)",
                          (chat_id, bar_id, menu_id, report_date, mode.value))
                cls.conn.commit()
            except Exception as err:
                cls.conn.rollback()
                logging.getLogger(__name__).exception(err)


class DBReader:
    bars = DBManager.read_bars()
    menus = DBManager.read_manus()

    subscriptions = DBManager.read_subscriptions()

    subscriptions_lock = threading.Lock()

    @classmethod
    def check_subscription(cls, chat_id, bar_id, menu_id):
        with cls.subscriptions_lock:
            return cls.subscriptions and chat_id in cls.subscriptions.keys() \
                   and bar_id in cls.subscriptions[chat_id].keys() and menu_id in cls.subscriptions[chat_id][bar_id]

    @classmethod
    def add_subscription(cls, chat_id, bar_id, menu_id):
        with cls.subscriptions_lock:
            if chat_id not in cls.subscriptions.keys():
                cls.subscriptions[chat_id] = {}
            if bar_id not in cls.subscriptions[chat_id].keys():
                cls.subscriptions[chat_id][bar_id] = []
            if menu_id not in cls.subscriptions[chat_id][bar_id]:
                DBManager.subscribe(chat_id, bar_id, menu_id)
                cls.subscriptions[chat_id][bar_id].append(menu_id)

    @classmethod
    def remove_subscription(cls, chat_id, bar_id, menu_id):
        with cls.subscriptions_lock:
            if cls.subscriptions and chat_id in cls.subscriptions.keys() \
                    and bar_id in cls.subscriptions[chat_id].keys() and menu_id in cls.subscriptions[chat_id][bar_id]:
                DBManager.remove_subscription(chat_id, bar_id, menu_id)
                cls.subscriptions[chat_id][bar_id].remove(menu_id)
