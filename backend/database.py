"""
Database initialization and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base
import config


# Create engine
engine = create_engine(f'sqlite:///{config.DATABASE_PATH}', echo=False)

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(engine)
    print("Database initialized successfully!")


def get_session():
    """Get a new database session"""
    return Session()


def close_session():
    """Close the current session"""
    Session.remove()


if __name__ == '__main__':
    # Initialize database when run directly
    init_db()
