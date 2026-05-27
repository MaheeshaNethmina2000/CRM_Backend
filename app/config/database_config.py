from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config.config import (
    POSTGRES_DB_NAME,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USERNAME,
    SQL_LOG,
)

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_recycle=3600,
    pool_size=100,
    pool_pre_ping=True,
    pool_timeout=60,
    max_overflow=150,
    echo=(SQL_LOG == "True"),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_database)]


class DatabaseConfig:

    @classmethod
    def get_database_session(cls):
        return SessionLocal()
