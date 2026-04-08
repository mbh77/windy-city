from sqlalchemy import Column, Integer, String, Text, Float, Double, Boolean, DateTime, ForeignKey, Enum, JSON, Date, Time, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base


# 춤 종류 (복수 선택 가능)
class DanceGenre(str, enum.Enum):
    salsa = "salsa"
    bachata = "bachata"
    kizomba = "kizomba"
    zouk = "zouk"
    tango = "tango"
    merengue = "merengue"
    lindy_hop = "lindy_hop"
    balboa = "balboa"
    blues = "blues"
    west_coast_swing = "west_coast_swing"
    other = "other"


# 이벤트 유형 (단일 선택)
class EventType(str, enum.Enum):
    social = "social"
    workshop = "workshop"
    festival = "festival"
    regular_class = "regular_class"
    performance = "performance"
    practice = "practice"
    other = "other"


# 장소 유형 (단일 선택)
class VenueType(str, enum.Enum):
    club = "club"
    academy = "academy"
    practice_room = "practice_room"


# 난이도 (단일 선택)
class DifficultyLevel(str, enum.Enum):
    beginner = "beginner"
    elementary = "elementary"
    pre_intermediate = "pre_intermediate"
    upper_intermediate = "upper_intermediate"
    intermediate = "intermediate"
    advanced = "advanced"
    all_level = "all_level"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint('email', 'provider', name='uq_email_provider'),
    )

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # 소셜 로그인은 비밀번호 없음
    nickname = Column(String(100), nullable=False)
    is_organizer = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    verify_code = Column(String(6))
    verify_code_expires = Column(DateTime)
    provider = Column(String(10), default="email")  # email, kakao, naver, google
    provider_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    # 관계
    events = relationship("Event", back_populates="organizer")
    venues = relationship("Venue", back_populates="owner")
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")

class Bookmark(Base):
    __tablename__ = "bookmarks"
    __table_args__ = (
        UniqueConstraint('user_id', 'entity_type', 'entity_id', name='uq_bookmark'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    entity_type = Column(String(20), nullable=False)  # 'event' or 'venue'
    entity_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

# ── 장소 (Venue) ─────────────────────────────────────────────

class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    venue_type = Column(Enum(VenueType), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)  # 리치 텍스트 HTML
    address = Column(String(500))
    address_detail = Column(String(255))
    latitude = Column(Double, nullable=False)
    longitude = Column(Double, nullable=False)
    phone = Column(String(50))
    website = Column(String(500))
    sns_links = Column(JSON)  # {"instagram": "...", "kakao": "..."}
    business_hours = Column(JSON)  # {"mon": "18:00-02:00", ...}

    # 공통 시설 정보
    floor_type = Column(String(50))  # 우드/타일/대리석
    capacity = Column(Integer)
    has_parking = Column(Boolean, default=False)
    parking_info = Column(String(255))

    # 클럽 전용
    cover_charge = Column(String(255))  # 입장료
    has_bar = Column(Boolean, default=False)

    # 연습실 전용
    rental_fee = Column(String(255))  # 대관료
    has_mirror = Column(Boolean, default=False)
    has_sound_system = Column(Boolean, default=False)
    area_sqm = Column(Float)  # 면적 (㎡)

    # 학원 전용
    has_trial_class = Column(Boolean, default=False)
    trial_class_fee = Column(String(100))

    # 확장용
    extra_info = Column(JSON)

    # 등록자
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    owner = relationship("User", back_populates="venues")
    dance_genres = relationship("VenueDanceGenre", back_populates="venue", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="venue")

    view_count = Column(Integer, default=0)
    comments = relationship("VenueComment", back_populates="venue", cascade="all, delete-orphan")


# 장소-춤종류 연결 테이블
class VenueDanceGenre(Base):
    __tablename__ = "venue_dance_genres"

    venue_id = Column(Integer, ForeignKey("venues.id", ondelete="CASCADE"), primary_key=True)
    dance_genre = Column(Enum(DanceGenre), primary_key=True)

    venue = relationship("Venue", back_populates="dance_genres")


# ── 이벤트 (Event) ───────────────────────────────────────────

# 이벤트-춤종류 연결 테이블
class EventDanceGenre(Base):
    __tablename__ = "event_dance_genres"

    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    dance_genre = Column(Enum(DanceGenre), primary_key=True)

    event = relationship("Event", back_populates="dance_genres")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)  # 리치 텍스트 HTML
    location_name = Column(String(255), nullable=False)
    address = Column(String(500))
    address_detail = Column(String(255))
    latitude = Column(Double, nullable=False)
    longitude = Column(Double, nullable=False)
    event_date = Column(Date, nullable=False)
    event_end_date = Column(Date, nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    event_type = Column(Enum(EventType), default=EventType.social)

    # 장소 연결 (선택)
    venue_id = Column(Integer, ForeignKey("venues.id"), nullable=True)

    # 가격 정보
    price = Column(String(255))
    early_bird_price = Column(String(255))

    # 워크샵/수업 관련
    difficulty = Column(Enum(DifficultyLevel), nullable=True)
    instructor_name = Column(String(255))
    max_participants = Column(Integer)
    requires_partner = Column(Boolean, default=False)

    # 소셜 파티 관련
    dj_name = Column(String(255))
    has_pre_lesson = Column(Boolean, default=False)
    dress_code = Column(String(255))

    # 반복 이벤트
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(JSON)  # {"day_of_week": "fri", "frequency": "weekly"}

    # 확장용
    extra_info = Column(JSON)

    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    organizer = relationship("User", back_populates="events")
    venue = relationship("Venue", back_populates="events")
    dance_genres = relationship("EventDanceGenre", back_populates="event", cascade="all, delete-orphan")

    view_count = Column(Integer, default=0)    
    comments = relationship("EventComment", back_populates="event", cascade="all, delete-orphan")


# ── 미디어 (이미지/영상 공용) ─────────────────────────────────

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(20), nullable=False)  # "venue" 또는 "event"
    entity_id = Column(Integer, nullable=False)
    media_type = Column(String(20), nullable=False)  # "image" 또는 "video"
    url = Column(String(1000), nullable=False)  # 이미지 경로 또는 영상 URL
    thumbnail_url = Column(String(1000))  # 썸네일 (영상용)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


# ── 게시판 (Board) ─────────────────────────────────────────────

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(Enum("notice", "free", name="post_category"), nullable=False, default="free")
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    view_count = Column(Integer, default=0, nullable=False)
    is_pinned = Column(Boolean, default=False, nullable=False)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")

class EventComment(Base):
    __tablename__ = "event_comments"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    event = relationship("Event", back_populates="comments")
    author = relationship("User")

class VenueComment(Base):
    __tablename__ = "venue_comments"

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    venue = relationship("Venue", back_populates="comments")
    author = relationship("User")
