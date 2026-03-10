from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List, Dict, Any
from models import EventType, DanceGenre, VenueType, DifficultyLevel


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


class VerifyEmail(BaseModel):
    email: EmailStr
    code: str


class ResendCode(BaseModel):
    email: EmailStr


# ── 미디어 스키마 ──────────────────────────────────────────────

class MediaCreate(BaseModel):
    media_type: str  # "image" 또는 "video"
    url: str
    thumbnail_url: Optional[str] = None
    sort_order: int = 0


class MediaResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    media_type: str
    url: str
    thumbnail_url: Optional[str]
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── 장소 스키마 ──────────────────────────────────────────────

class VenueCreate(BaseModel):
    venue_type: VenueType
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: float
    longitude: float
    phone: Optional[str] = None
    website: Optional[str] = None
    sns_links: Optional[Dict[str, str]] = None
    business_hours: Optional[Dict[str, Any]] = None
    dance_genres: List[DanceGenre] = []

    # 공통 시설
    floor_type: Optional[str] = None
    capacity: Optional[int] = None
    has_parking: bool = False
    parking_info: Optional[str] = None

    # 클럽 전용
    cover_charge: Optional[str] = None
    has_bar: bool = False

    # 연습실 전용
    rental_fee: Optional[str] = None
    has_mirror: bool = False
    has_sound_system: bool = False
    area_sqm: Optional[float] = None

    # 학원 전용
    has_trial_class: bool = False
    trial_class_fee: Optional[str] = None

    extra_info: Optional[Dict[str, Any]] = None


class VenueUpdate(BaseModel):
    venue_type: Optional[VenueType] = None
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    sns_links: Optional[Dict[str, str]] = None
    business_hours: Optional[Dict[str, Any]] = None
    dance_genres: Optional[List[DanceGenre]] = None

    floor_type: Optional[str] = None
    capacity: Optional[int] = None
    has_parking: Optional[bool] = None
    parking_info: Optional[str] = None

    cover_charge: Optional[str] = None
    has_bar: Optional[bool] = None

    rental_fee: Optional[str] = None
    has_mirror: Optional[bool] = None
    has_sound_system: Optional[bool] = None
    area_sqm: Optional[float] = None

    has_trial_class: Optional[bool] = None
    trial_class_fee: Optional[str] = None

    extra_info: Optional[Dict[str, Any]] = None


class VenueResponse(BaseModel):
    id: int
    venue_type: VenueType
    name: str
    description: Optional[str]
    address: Optional[str]
    latitude: float
    longitude: float
    phone: Optional[str]
    website: Optional[str]
    sns_links: Optional[Dict[str, str]]
    business_hours: Optional[Dict[str, Any]]
    dance_genres: List[DanceGenre] = []

    floor_type: Optional[str]
    capacity: Optional[int]
    has_parking: bool
    parking_info: Optional[str]

    cover_charge: Optional[str]
    has_bar: bool

    rental_fee: Optional[str]
    has_mirror: bool
    has_sound_system: bool
    area_sqm: Optional[float]

    has_trial_class: bool
    trial_class_fee: Optional[str]

    extra_info: Optional[Dict[str, Any]]

    owner_id: int
    owner_nickname: Optional[str] = None
    media: List[MediaResponse] = []
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


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

    # 장소 연결
    venue_id: Optional[int] = None

    # 가격 정보
    price: Optional[str] = None
    early_bird_price: Optional[str] = None

    # 워크샵/수업
    difficulty: Optional[DifficultyLevel] = None
    instructor_name: Optional[str] = None
    max_participants: Optional[int] = None
    requires_partner: bool = False

    # 소셜 파티
    dj_name: Optional[str] = None
    has_pre_lesson: bool = False
    dress_code: Optional[str] = None

    # 반복 이벤트
    is_recurring: bool = False
    recurrence_rule: Optional[Dict[str, Any]] = None

    extra_info: Optional[Dict[str, Any]] = None


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

    venue_id: Optional[int] = None
    price: Optional[str] = None
    early_bird_price: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    instructor_name: Optional[str] = None
    max_participants: Optional[int] = None
    requires_partner: Optional[bool] = None
    dj_name: Optional[str] = None
    has_pre_lesson: Optional[bool] = None
    dress_code: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[Dict[str, Any]] = None
    extra_info: Optional[Dict[str, Any]] = None


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

    venue_id: Optional[int]
    price: Optional[str]
    early_bird_price: Optional[str]
    difficulty: Optional[DifficultyLevel]
    instructor_name: Optional[str]
    max_participants: Optional[int]
    requires_partner: bool
    dj_name: Optional[str]
    has_pre_lesson: bool
    dress_code: Optional[str]
    is_recurring: bool
    recurrence_rule: Optional[Dict[str, Any]]
    extra_info: Optional[Dict[str, Any]]

    organizer_id: int
    organizer_nickname: Optional[str] = None
    media: List[MediaResponse] = []
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
