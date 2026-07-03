from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from ..core.config import settings


engine = create_engine(
    url=settings.DATABASE_URL,
    )

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    )

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
