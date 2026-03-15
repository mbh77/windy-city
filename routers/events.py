import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
import models
import schemas
import auth as auth_utils

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _delete_media_file(url: str):
    """미디어 URL에 해당하는 실제 파일 삭제"""
    if url and url.startswith("/uploads/"):
        filepath = os.path.join(BASE_DIR, url.lstrip("/"))
        if os.path.exists(filepath):
            os.remove(filepath)

router = APIRouter(prefix="/api/events", tags=["events"])


def _get_dance_genres(event: models.Event) -> list:
    """이벤트의 춤 종류 목록 반환"""
    return [dg.dance_genre for dg in event.dance_genres]


def _set_dance_genres(db: Session, event: models.Event, genres: list):
    """이벤트의 춤 종류 설정 (기존 삭제 후 재생성)"""
    event.dance_genres.clear()
    for genre in genres:
        event.dance_genres.append(models.EventDanceGenre(dance_genre=genre))


def _get_media(db: Session, entity_id: int) -> list:
    """이벤트의 미디어 목록 반환"""
    return db.query(models.Media).filter(
        models.Media.entity_type == "event",
        models.Media.entity_id == entity_id
    ).order_by(models.Media.sort_order).all()


def _event_to_response(db: Session, event: models.Event) -> schemas.EventResponse:
    """Event 모델을 EventResponse로 변환"""
    return schemas.EventResponse(
        **{c.name: getattr(event, c.name) for c in event.__table__.columns},
        dance_genres=_get_dance_genres(event),
        organizer_nickname=event.organizer.nickname if event.organizer else None,
        media=[schemas.MediaResponse.model_validate(m) for m in _get_media(db, event.id)],
    )


@router.get("/", response_model=List[schemas.EventResponse])
def get_events(
    date_from: Optional[datetime] = Query(None, description="시작일 필터"),
    date_to: Optional[datetime] = Query(None, description="종료일 필터"),
    event_type: Optional[models.EventType] = Query(None, description="이벤트 유형 필터"),
    dance_genre: Optional[models.DanceGenre] = Query(None, description="춤 종류 필터"),
    venue_id: Optional[int] = Query(None, description="장소 필터"),
    difficulty: Optional[models.DifficultyLevel] = Query(None, description="난이도 필터"),
    db: Session = Depends(get_db)
):
    """이벤트 목록 조회 (로그인 불필요)"""
    query = db.query(models.Event)

    if date_from:
        query = query.filter(models.Event.start_date >= date_from)
    if date_to:
        query = query.filter(models.Event.start_date <= date_to)
    if event_type:
        query = query.filter(models.Event.event_type == event_type)
    if dance_genre:
        query = query.join(models.EventDanceGenre).filter(
            models.EventDanceGenre.dance_genre == dance_genre
        )
    if venue_id:
        query = query.filter(models.Event.venue_id == venue_id)
    if difficulty:
        query = query.filter(models.Event.difficulty == difficulty)

    events = query.order_by(models.Event.start_date).all()
    return [_event_to_response(db, e) for e in events]


@router.post("/", response_model=schemas.EventResponse, status_code=201)
def create_event(
    event_data: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """이벤트 등록 (로그인 필요)"""
    data = event_data.model_dump(exclude={"dance_genres"})
    event = models.Event(**data, organizer_id=current_user.id)
    db.add(event)
    db.flush()

    # 춤 종류 저장
    _set_dance_genres(db, event, event_data.dance_genres)

    db.commit()
    db.refresh(event)
    return _event_to_response(db, event)


@router.get("/{event_id}", response_model=schemas.EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """이벤트 상세 조회"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="이벤트를 찾을 수 없습니다")
    return _event_to_response(db, event)


@router.put("/{event_id}", response_model=schemas.EventResponse)
def update_event(
    event_id: int,
    event_data: schemas.EventUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """이벤트 수정 (본인만 가능)"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="이벤트를 찾을 수 없습니다")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다")

    # 변경된 필드만 업데이트 (dance_genres 제외)
    update_data = event_data.model_dump(exclude_unset=True, exclude={"dance_genres"})
    for field, value in update_data.items():
        setattr(event, field, value)

    # 춤 종류가 포함된 경우 업데이트
    if event_data.dance_genres is not None:
        _set_dance_genres(db, event, event_data.dance_genres)

    db.commit()
    db.refresh(event)
    return _event_to_response(db, event)


@router.delete("/{event_id}", status_code=204)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """이벤트 삭제 (본인만 가능)"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="이벤트를 찾을 수 없습니다")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다")

    # 관련 미디어 파일 + 레코드 삭제
    media_list = db.query(models.Media).filter(
        models.Media.entity_type == "event",
        models.Media.entity_id == event_id
    ).all()
    for m in media_list:
        _delete_media_file(m.url)
        db.delete(m)

    db.delete(event)
    db.commit()


# ── 이벤트 미디어 API ────────────────────────────────────────

@router.post("/{event_id}/media", response_model=schemas.MediaResponse, status_code=201)
def add_event_media(
    event_id: int,
    media_data: schemas.MediaCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """이벤트에 미디어 추가 (본인만 가능)"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="이벤트를 찾을 수 없습니다")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="미디어 추가 권한이 없습니다")

    media = models.Media(
        entity_type="event",
        entity_id=event_id,
        **media_data.model_dump()
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


@router.delete("/{event_id}/media/{media_id}", status_code=204)
def delete_event_media(
    event_id: int,
    media_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """이벤트 미디어 삭제 (본인만 가능)"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="이벤트를 찾을 수 없습니다")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="미디어 삭제 권한이 없습니다")

    media = db.query(models.Media).filter(
        models.Media.id == media_id,
        models.Media.entity_type == "event",
        models.Media.entity_id == event_id
    ).first()
    if not media:
        raise HTTPException(status_code=404, detail="미디어를 찾을 수 없습니다")

    _delete_media_file(media.url)
    db.delete(media)
    db.commit()
