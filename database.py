import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

# Define the SQLite database URL
url = 'sqlite:///' + os.path.join(os.path.dirname(__file__), './database.db')

# Create the database engine
engine = create_engine(url)

# Create a scoped session for database operations
db_sessions = scoped_session(sessionmaker(bind=engine))

# Define the declarative base for models
Base = declarative_base()
Base.query = db_sessions.query_property()

# Initialize the database (create tables)
def init_db():
    import models  # Import models to register them with SQLAlchemy
    Base.metadata.create_all(bind=engine)