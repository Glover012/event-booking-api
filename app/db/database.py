from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from ..core import settings


engine = create_engine(
    url=settings.database_url,
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
