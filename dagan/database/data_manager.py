import threading

from dagan.database.db_manager import DBManager


class DataManager(DBManager):
    restaurants = None
    menus = None
    subscriptions = None
    subscriptions_lock = threading.Lock()  # Lock for multithread access to subscriptions information

    @classmethod
    def initialize(cls):
        DBManager.initialize()
        cls.restaurants = DBManager.read_restaurants()  # Basic restaurant info
        cls.menus = DBManager.read_menus()  # Basic manus info
        cls.subscriptions = DBManager.read_subscriptions()  # Actual subscriptions

    @classmethod
    def check_subscription(cls, chat_id, res_id, menu_id):
        """
        Checks if a user (chat) is subscribed to this menu
        :param chat_id: Id of chat
        :param res_id: Id of restaurant
        :param menu_id: If of menu
        :return:
        """
        with cls.subscriptions_lock:
            return cls.subscriptions and chat_id in cls.subscriptions.keys() \
                   and res_id in cls.subscriptions[chat_id].keys() and menu_id in cls.subscriptions[chat_id][res_id]

    @classmethod
    def get_subscription_by_chat_id(cls, chat_id):
        """
        Returns all subscriptions of a user (chat)
        :param chat_id: Id of chat
        :return: List of [restaurant, menu]
        """
        your_subs = []
        with cls.subscriptions_lock:
            if chat_id in cls.subscriptions.keys():
                for res_id in cls.subscriptions[chat_id]:
                    for menu_id in cls.subscriptions[chat_id][res_id]:
                        your_subs.append([res_id, menu_id])
        return your_subs

    @classmethod
    def subscribe(cls, chat_id, res_id, menu_id):
        """
        Saves a subscription into the dictionary and stores it into the database

        :param chat_id: Id of chat
        :param res_id: Id of restaurant
        :param menu_id: If of menu
        """
        with cls.subscriptions_lock:
            if chat_id not in cls.subscriptions.keys():
                cls.subscriptions[chat_id] = {}
            if res_id not in cls.subscriptions[chat_id].keys():
                cls.subscriptions[chat_id][res_id] = []
            if menu_id not in cls.subscriptions[chat_id][res_id]:
                DBManager.subscribe(chat_id, res_id, menu_id)
                cls.subscriptions[chat_id][res_id].append(menu_id)

    @classmethod
    def unsubscribe(cls, chat_id, res_id, menu_id):
        """
        Removes a subscription from internal dictionary and erase ir of the database

        :param chat_id: Id of chat
        :param res_id: Id of restaurant
        :param menu_id: If of menu
        """
        with cls.subscriptions_lock:
            if cls.subscriptions and chat_id in cls.subscriptions.keys() \
                    and res_id in cls.subscriptions[chat_id].keys() and menu_id in cls.subscriptions[chat_id][res_id]:
                DBManager.unsubscribe(chat_id, res_id, menu_id)
                cls.subscriptions[chat_id][res_id].remove(menu_id)
