# app/models/meeting.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.user import Base

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # владелец — пользователь системы
    filename = Column(String, nullable=False)                           # имя файла (без пути)
    status = Column(String, default="pending")                          # pending | processing | done | failed
    result_json = Column(Text, nullable=True)                           # JSON-строка с транскриптом, диаризацией, суммаризацией
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связь с пользователем (опционально, для удобства)
    owner = relationship("User", back_populates="meetings")