import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Default fallback to sqlite:///./slmforge.db
DATABASE_URL = os.getenv("SLMFORGE_DB_URL", "sqlite:///./slmforge.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
