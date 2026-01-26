from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Default to local SQLite for simplicity in this phase
DB_URL = os.getenv('DATABASE_URL', 'sqlite:///data/supply_chain.db')

class DBConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
            cls._instance.engine = create_engine(DB_URL)
            cls._instance.Session = sessionmaker(bind=cls._instance.engine)
        return cls._instance

    def get_session(self):
        return self.Session()
    
    def get_engine(self):
        return self.engine

def get_db():
    """Generator for dependency injection (FastAPI style if needed)"""
    db = DBConnection().get_session()
    try:
        yield db
    finally:
        db.close()
