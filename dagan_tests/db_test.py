from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from dagan.data import public_parameters
from dagan.database.entities import Restaurant, Menu, Subscription, Chat, MenuReport, ScheduledSearch, SearchReport

session_factory = sessionmaker(bind=create_engine('sqlite:///' + public_parameters.DB_FILE))
Session = scoped_session(session_factory)
Session().query(Restaurant).all()
Session().query(Menu).all()
Session().query(Chat).all()
Session().query(Subscription).all()
Session().query(MenuReport).all()
Session().query(ScheduledSearch).all()
Session().query(SearchReport).all()
