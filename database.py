# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from asyncpgsa import create_pool

from config import settings

DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL)
pool = create_pool(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_pool():
    return pool
