from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, ForeignKeyConstraint, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from dagan.data import public_parameters
from dagan.database.db_enums import ReportMode

Base = declarative_base()


class Restaurant(Base):
    __tablename__ = 'restaurant'
    res_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(Integer)
    web = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    menus = relationship("Menu", back_populates="restaurant")



class Menu(Base):
    __tablename__ = 'menu'
    res_id = Column(Integer, ForeignKey('restaurant.res_id'), primary_key=True)
    restaurant = relationship("Restaurant", back_populates="menus")
    menu_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Chat(Base):
    __tablename__ = 'chat'
    chat_id = Column(Integer, primary_key=True)
    mute = Column(Boolean, nullable=False, default=False)
    start_hour = Column(Float, nullable=False, default=public_parameters.SUBS_HOUR_INTERVAL[0])
    end_hour = Column(Float, nullable=False, default=public_parameters.SUBS_HOUR_INTERVAL[1])
    days = Column(String, nullable=False, default=str(public_parameters.SUBS_WEEKDAY_LIST))
    subscriptions = relationship("Subscription", back_populates="chat")
    scheduled_searches = relationship("ScheduledSearch", back_populates="chat")


class Subscription(Base):
    __tablename__ = 'subscription'
    res_id = Column(Integer, primary_key=True)
    menu_id = Column(Integer, primary_key=True)
    menu = relationship("Menu")
    ForeignKeyConstraint([res_id, menu_id], [Menu.res_id, Menu.menu_id])
    chat_id = Column(Integer, ForeignKey('chat.chat_id'), primary_key=True)
    chat = relationship("Chat")


class MenuReport(Base):
    __tablename__ = 'menu_report'
    res_id = Column(Integer, primary_key=True)
    menu_id = Column(Integer, primary_key=True)
    menu = relationship("Menu")
    ForeignKeyConstraint([res_id, menu_id], [Menu.res_id, Menu.menu_id])
    chat_id = Column(Integer, ForeignKey('chat.chat_id'), primary_key=True)
    chat = relationship("Chat")
    report_date = Column(DateTime, nullable=False, primary_key=True)
    mode = Column(Enum(ReportMode), nullable=False)


class SearchReport(Base):
    __tablename__ = 'search_report'
    chat_id = Column(Integer, ForeignKey('chat.chat_id'), primary_key=True)
    chat = relationship("Chat")
    text_to_search = Column(String, primary_key=True)
    results = Column(Integer, nullable=False)
    search_date = Column(DateTime, nullable=False, primary_key=True)
    mode = Column(Enum(ReportMode), nullable=False)


class ScheduledSearch(Base):
    __tablename__ = 'scheduled_search'
    chat_id = Column(Integer, ForeignKey('chat.chat_id'), primary_key=True)
    chat = relationship("Chat")
    text_to_search = Column(String, primary_key=True)
