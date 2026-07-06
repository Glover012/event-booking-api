from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from ..core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    url=settings.DATABASE_URL,
    )

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
