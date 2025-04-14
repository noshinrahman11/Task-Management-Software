import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

# # Check if running in test mode
# IS_TESTING = os.getenv('TESTING', 'False') == 'True'

# # Define the SQLite database URL, testing uses memory
# if IS_TESTING: 
#     url = "sqlite:///:memory:"  
# else:

# Get the absolute path to the database file
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'database.db'))
url = f'sqlite:///{db_path}'

# print(f"Using database at: {db_path}")

# url = 'sqlite:///' + os.path.join(os.path.dirname(__file__), './database.db')

# Create the database engine
engine = create_engine(url)

# Create a scoped session for database operations
db_sessions = scoped_session(sessionmaker(bind=engine))

# Define the declarative base for models
Base = declarative_base()
Base.query = db_sessions.query_property()

# Initialize the database (create tables)
def init_db():
    import TaskManagement.models as models  # Import models to register them with SQLAlchemy
    Base.metadata.create_all(bind=engine)

# # Clean up the database (used for testing)
# def drop_db():
#     Base.metadata.drop_all(bind=engine)

