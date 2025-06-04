from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base  

DATABASE_URL = "sqlite:///journal.db" 

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def create_db_and_tables():
    """Creates all tables defined in models.py if they don't exist."""
    Base.metadata.create_all(engine)
    print(f"Database and tables created at {DATABASE_URL}")

def get_session():
    """Returns a new session."""
    return Session()