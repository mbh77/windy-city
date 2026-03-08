from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from models import EventType, DanceGenre


# ── 사용자 스키마 ──────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str
    is_organizer: bool = False


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    nickname: str
    is_organizer: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── 이벤트 스키마 ──────────────────────────────────────────────

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location_name: str
    address: Optional[str] = None
    latitude: float
    longitude: float
    start_date: datetime
    end_date: Optional[datetime] = None
    event_type: EventType = EventType.social
    dance_genres: List[DanceGenre] = []


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location_name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    event_type: Optional[EventType] = None
    dance_genres: Optional[List[DanceGenre]] = None


class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    location_name: str
    address: Optional[str]
    latitude: float
    longitude: float
    start_date: datetime
    end_date: Optional[datetime]
    event_type: EventType
    dance_genres: List[DanceGenre] = []
    organizer_id: int
    organizer_nickname: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
