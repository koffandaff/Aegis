"""
SQLAlchemy Database Engine Configuration

This module provides a database-agnostic interface using SQLAlchemy.
To switch databases, only change the DATABASE_URL in this file or via environment variable.

Supported databases:
- SQLite: sqlite:///./data/fsociety.db
- PostgreSQL: postgresql://user:pass@localhost/fsociety
- MySQL: mysql://user:pass@localhost/fsociety
"""
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

# Database URL - easily swappable via environment variable
# Default to SQLite for development
_raw_database_url = os.getenv("DATABASE_URL", "sqlite:///./data/fsociety.db")

# SQLAlchemy 1.4+ requires 'postgresql://' instead of 'postgres://'
# Many cloud providers (Heroku, Aiven) still use 'postgres://' in their URLs
DATABASE_URL = _raw_database_url.replace("postgres://", "postgresql://", 1) if _raw_database_url.startswith("postgres://") else _raw_database_url

# Create engine with appropriate settings based on database type
if DATABASE_URL.startswith("sqlite"):
    # SQLite-specific settings
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Required for SQLite + FastAPI
        echo=False  # Set to True for SQL debugging
    )
    
    # Enable foreign keys for SQLite (off by default)
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # PostgreSQL / MySQL settings
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI routes to get a database session.
    Automatically closes the session when done.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for use outside of FastAPI routes.
    
    Usage:
        with get_db_context() as db:
            db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize the database by creating all tables.
    Call this on application startup.
    """
    # Import models to register them with Base
    from database import models  # noqa: F401
    
    # Ensure data directory exists for SQLite
    if DATABASE_URL.startswith("sqlite"):
        os.makedirs("data", exist_ok=True)
    
    Base.metadata.create_all(bind=engine)
    print(f"[DATABASE] Initialized: {DATABASE_URL.split('://')[0].upper()}")


def drop_all_tables():
    """
    Drop all tables. Use with caution!
    """
    Base.metadata.drop_all(bind=engine)
    print("[DATABASE] All tables dropped")
