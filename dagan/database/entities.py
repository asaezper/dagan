from enum import Enum

import unidecode
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, ForeignKeyConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection

from dagan.data import public_parameters

Base = declarative_base()


class ReportMode(Enum):
    """
    Modes of a menu report in database
    """
    MANUAL = 0
    AUTO = 1


class Restaurant(Base):
    __tablename__ = 'restaurant'
    res_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(Integer)
    web = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    menus = relationship("Menu", collection_class=attribute_mapped_collection('code'), back_populates="restaurant",
                         lazy='joined', cascade='all, delete-orphan')


class Menu(Base):
    __tablename__ = 'menu'
    res_id = Column(Integer, ForeignKey('restaurant.res_id'), primary_key=True)
    restaurant = relationship("Restaurant", back_populates="menus", lazy='select')
    menu_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)

    @staticmethod
    def generate_codename(name):
        return unidecode.unidecode(name.lower()).replace(' ', '')

    def __init__(self, *args, **kwargs):
        super(Menu, self).__init__(args, kwargs)
        self.codename = self.generate_codename()
        self.today_menu = None


class Chat(Base):
    __tablename__ = 'chat'
    chat_id = Column(Integer, primary_key=True)
    mute = Column(Boolean, nullable=False, default=False)
    start_hour = Column(Float, nullable=False, default=public_parameters.SUBS_HOUR_INTERVAL[0])
    end_hour = Column(Float, nullable=False, default=public_parameters.SUBS_HOUR_INTERVAL[1])
    days = Column(String, nullable=False, default=str(public_parameters.SUBS_WEEKDAY_LIST))
    subscriptions = relationship("Subscription", back_populates="chat", lazy='joined', cascade='all, delete-orphan')
    scheduled_searches = relationship("ScheduledSearch", back_populates="chat", lazy='joined',
                                      cascade='all, delete-orphan')


class Subscription(Base):
    __tablename__ = 'subscription'
    res_id = Column(Integer, primary_key=True)
    menu_id = Column(Integer, primary_key=True)
    menu = relationship("Menu", lazy='select')
    ForeignKeyConstraint([res_id, menu_id], [Menu.res_id, Menu.menu_id])
    chat_id = Column(Integer, ForeignKey('chat.chat_id'), primary_key=True)
    chat = relationship("Chat", lazy='select')


class ScheduledSearch(Base):
    __tablename__ = 'scheduled_search'
    chat_id = Column(Integer, ForeignKey('chat.chat_id'), primary_key=True)
    chat = relationship("Chat", lazy='select')
    text_to_search = Column(String, primary_key=True)


class MenuReport(Base):
    __tablename__ = 'menu_report'
    res_id = Column(Integer, primary_key=True)
    menu_id = Column(Integer, primary_key=True)
    menu = relationship("Menu", lazy='select')
    ForeignKeyConstraint([res_id, menu_id], [Menu.res_id, Menu.menu_id])
    chat_id = Column(Integer, ForeignKey('chat.chat_id'), primary_key=True)
    chat = relationship("Chat", lazy='select')
    report_date = Column(DateTime, nullable=False, primary_key=True)
    mode = Column(Enum(ReportMode), nullable=False)


class SearchReport(Base):
    __tablename__ = 'search_report'
    chat_id = Column(Integer, ForeignKey('chat.chat_id'), primary_key=True)
    chat = relationship("Chat", lazy='select')
    text_to_search = Column(String, primary_key=True)
    results = Column(Integer, nullable=False)
    search_date = Column(DateTime, nullable=False, primary_key=True)
    mode = Column(Enum(ReportMode), nullable=False)
