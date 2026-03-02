from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base


class EventType(str, enum.Enum):
    salsa = "salsa"
    bachata = "bachata"
    kizomba = "kizomba"
    social = "social"
    workshop = "workshop"
    congress = "congress"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nickname = Column(String, nullable=False)
    is_organizer = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계: 주최자가 등록한 이벤트들
    events = relationship("Event", back_populates="organizer")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    location_name = Column(String, nullable=False)
    address = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    event_type = Column(Enum(EventType), default=EventType.social)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계: 이벤트 주최자
    organizer = relationship("User", back_populates="events")
