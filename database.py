import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

url = 'sqlite:///' + os.path.join(os.path.dirname(__file__), './database.db')

engine = create_engine(url)

db_sessions = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_sessions.query_property()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)