# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    verification_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Обратная связь: пользователь → его встречи
    meetings = relationship("Meeting", back_populates="owner", cascade="all, delete-orphan")