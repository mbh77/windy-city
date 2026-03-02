from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
import models
import schemas
import auth as auth_utils

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("/", response_model=List[schemas.EventResponse])
def get_events(
    date_from: Optional[datetime] = Query(None, description="시작일 필터"),
    date_to: Optional[datetime] = Query(None, description="종료일 필터"),
    event_type: Optional[models.EventType] = Query(None, description="이벤트 유형 필터"),
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

    events = query.order_by(models.Event.start_date).all()

    # organizer_nickname 추가
    result = []
    for event in events:
        event_dict = {
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "location_name": event.location_name,
            "address": event.address,
            "latitude": event.latitude,
            "longitude": event.longitude,
            "start_date": event.start_date,
            "end_date": event.end_date,
            "event_type": event.event_type,
            "organizer_id": event.organizer_id,
            "organizer_nickname": event.organizer.nickname if event.organizer else None,
            "created_at": event.created_at,
        }
        result.append(schemas.EventResponse(**event_dict))
    return result


@router.post("/", response_model=schemas.EventResponse, status_code=201)
def create_event(
    event_data: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """이벤트 등록 (로그인 필요)"""
    event = models.Event(
        **event_data.model_dump(),
        organizer_id=current_user.id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return schemas.EventResponse(
        **{c.name: getattr(event, c.name) for c in event.__table__.columns},
        organizer_nickname=current_user.nickname,
    )


@router.get("/{event_id}", response_model=schemas.EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """이벤트 상세 조회"""
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="이벤트를 찾을 수 없습니다")

    return schemas.EventResponse(
        **{c.name: getattr(event, c.name) for c in event.__table__.columns},
        organizer_nickname=event.organizer.nickname if event.organizer else None,
    )


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

    # 변경된 필드만 업데이트
    for field, value in event_data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return schemas.EventResponse(
        **{c.name: getattr(event, c.name) for c in event.__table__.columns},
        organizer_nickname=current_user.nickname,
    )


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

    db.delete(event)
    db.commit()
