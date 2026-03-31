import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta

from database import get_db
import models
import schemas
import auth as auth_utils

from models import EventComment
from schemas import EventCommentCreate, EventCommentOut

# 요일 매핑 (Python weekday: 0=월 ~ 6=일)
DAY_TO_WEEKDAY = {
    'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3,
    'fri': 4, 'sat': 5, 'sun': 6,
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _delete_media_file(url: str):
    """미디어 URL에 해당하는 실제 파일 삭제"""
    if url and url.startswith("/uploads/"):
        filepath = os.path.join(BASE_DIR, url.lstrip("/"))
        if os.path.exists(filepath):
            os.remove(filepath)

router = APIRouter(prefix="/api/events", tags=["events"])


def _get_dance_genres(event: models.Event) -> list:
    """강습·행사의 춤 종류 목록 반환"""
    return [dg.dance_genre for dg in event.dance_genres]


def _set_dance_genres(db: Session, event: models.Event, genres: list):
    """강습·행사의 춤 종류 설정 (기존 삭제 후 재생성)"""
    event.dance_genres.clear()
    for genre in genres:
        event.dance_genres.append(models.EventDanceGenre(dance_genre=genre))


def _get_media(db: Session, entity_id: int) -> list:
    """강습·행사의 미디어 목록 반환"""
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


def _recurring_in_range(event, date_from: date, date_to: date) -> bool:
    """반복 강습·행사가 날짜 범위 내에 해당 요일이 있는지 확인"""
    rule = event.recurrence_rule
    if not rule or not rule.get('days'):
        return True  # 규칙 없으면 일단 포함

    days = rule.get('days', [])
    target_weekdays = {DAY_TO_WEEKDAY[d] for d in days if d in DAY_TO_WEEKDAY}
    if not target_weekdays:
        return True

    # 범위 내 날짜를 순회하며 반복 요일이 있는지 확인
    current = date_from
    while current <= date_to:
        if current.weekday() in target_weekdays:
            return True
        current += timedelta(days=1)
    return False


@router.get("/", response_model=List[schemas.EventResponse])
def get_events(
    date_from: Optional[date] = Query(None, description="시작일 필터"),
    date_to: Optional[date] = Query(None, description="종료일 필터"),
    event_type: Optional[models.EventType] = Query(None, description="강습·행사 유형 필터"),
    dance_genre: Optional[models.DanceGenre] = Query(None, description="춤 종류 필터"),
    venue_id: Optional[int] = Query(None, description="장소 필터"),
    difficulty: Optional[models.DifficultyLevel] = Query(None, description="난이도 필터"),
    db: Session = Depends(get_db)
):
    """강습·행사 목록 조회 (로그인 불필요)"""
    query = db.query(models.Event)

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

    all_events = query.order_by(models.Event.event_date).all()
    results = []

    for e in all_events:
        if e.is_recurring:
            # 반복 이벤트: 시작일~종료일 범위가 필터 범위와 겹치는지 확인
            if date_to and e.event_date and e.event_date > date_to:
                continue
            if date_from and e.event_end_date and e.event_end_date < date_from:
                continue
            if date_from and date_to and not _recurring_in_range(e, date_from, date_to):
                continue
            results.append(_event_to_response(db, e))
        else:
            # 비반복 이벤트: 기존 날짜 필터
            if date_from and e.event_date < date_from:
                continue
            if date_to and e.event_date > date_to:
                continue
            results.append(_event_to_response(db, e))

    return results


@router.get("/list")
def list_events(
    q: str = Query("", description="검색어"),
    event_type: Optional[models.EventType] = Query(None),
    dance_genre: Optional[models.DanceGenre] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """강습·행사 목록 (페이징, 검색)"""
    query = db.query(models.Event)

    if event_type:
        query = query.filter(models.Event.event_type == event_type)
    if dance_genre:
        query = query.join(models.EventDanceGenre).filter(
            models.EventDanceGenre.dance_genre == dance_genre
        )
    if q:
        keyword = f"%{q}%"
        query = query.filter(
            (models.Event.title.like(keyword)) |
            (models.Event.description.like(keyword)) |
            (models.Event.location_name.like(keyword)) |
            (models.Event.instructor_name.like(keyword))
        )

    total = query.count()
    events = query.order_by(models.Event.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "events": [
            {**_event_to_response(db, e).model_dump(), "comment_count": len(e.comments)}
            for e in events
        ],
    }


@router.post("/", response_model=schemas.EventResponse, status_code=201)
def create_event(
    event_data: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """강습·행사 등록 (로그인 필요)"""
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
def get_event(event_id: int, no_count: bool = False, db: Session = Depends(get_db)):
    """강습·행사 상세 조회"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="강습·행사를 찾을 수 없습니다")
    
    # GET /{id} 엔드포인트에서 이벤트 조회 후

    if not no_count:
        event.view_count = (event.view_count or 0) + 1
        db.commit()

    return _event_to_response(db, event)

@router.put("/{event_id}", response_model=schemas.EventResponse)
def update_event(
    event_id: int,
    event_data: schemas.EventUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """강습·행사 수정 (본인만 가능)"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="강습·행사를 찾을 수 없습니다")
    if event.organizer_id != current_user.id and not current_user.is_admin:
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
    """강습·행사 삭제 (본인만 가능)"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="강습·행사를 찾을 수 없습니다")
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
    """강습·행사에 미디어 추가 (본인만 가능)"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="강습·행사를 찾을 수 없습니다")
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
    """강습·행사 미디어 삭제 (본인만 가능)"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="강습·행사를 찾을 수 없습니다")
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

# ── 댓글 ──────────────────────────────────────────────

# 댓글 목록
@router.get("/{event_id}/comments", response_model=list[EventCommentOut])
def get_event_comments(event_id: int, db: Session = Depends(get_db)):
    comments = db.query(EventComment).filter(EventComment.event_id == event_id)\
        .order_by(EventComment.created_at.asc()).all()
    return [
        EventCommentOut(
            id=c.id, event_id=c.event_id, author_id=c.author_id,
            author_nickname=c.author.nickname if c.author else "",
            content=c.content, created_at=c.created_at, updated_at=c.updated_at,
        ) for c in comments
    ]

# 댓글 작성
@router.post("/{event_id}/comments", response_model=EventCommentOut)
def create_event_comment(event_id: int, body: EventCommentCreate,
                         db: Session = Depends(get_db),
                         user: models.User = Depends(auth_utils.get_current_user)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(404, "이벤트를 찾을 수 없습니다")
    comment = EventComment(event_id=event_id, author_id=user.id, content=body.content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return EventCommentOut(
        id=comment.id, event_id=comment.event_id, author_id=comment.author_id,
        author_nickname=user.nickname, content=comment.content,
        created_at=comment.created_at, updated_at=comment.updated_at,
    )

# 댓글 수정
@router.put("/{event_id}/comments/{comment_id}", response_model=EventCommentOut)
def update_event_comment(event_id: int, comment_id: int, body: EventCommentCreate,
                         db: Session = Depends(get_db),
                         user: models.User = Depends(auth_utils.get_current_user)):
    comment = db.query(EventComment).filter(
        EventComment.id == comment_id, EventComment.event_id == event_id
    ).first()
    if not comment:
        raise HTTPException(404)
    if comment.author_id != user.id and not user.is_admin:
        raise HTTPException(403)
    comment.content = body.content
    comment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(comment)
    return EventCommentOut(
        id=comment.id, event_id=comment.event_id, author_id=comment.author_id,
        author_nickname=comment.author.nickname, content=comment.content,
        created_at=comment.created_at, updated_at=comment.updated_at,
    )

# 댓글 삭제
@router.delete("/{event_id}/comments/{comment_id}")
def delete_event_comment(event_id: int, comment_id: int,
                         db: Session = Depends(get_db),
                         user: models.User = Depends(auth_utils.get_current_user)):
    comment = db.query(EventComment).filter(
        EventComment.id == comment_id, EventComment.event_id == event_id
    ).first()
    if not comment:
        raise HTTPException(404)
    if comment.author_id != user.id and not user.is_admin:
        raise HTTPException(403)
    db.delete(comment)
    db.commit()
    return {"ok": True}
