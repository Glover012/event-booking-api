from sqlalchemy import Column, Integer, String, ForeignKey

from ..database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    role = Column(String)

class Events(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
