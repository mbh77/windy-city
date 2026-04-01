from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from fastapi import Depends
from database import get_db

import models

router = APIRouter(prefix="/api", tags=["search"])

@router.get("/search")
def search(
    q: str = Query(..., min_length=1),
    date_from: str = Query(None),
    date_to: str = Query(None),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    from datetime import datetime, date
    from sqlalchemy import or_

    keyword = f"%{q}%"

    # 기간 필터: 파라미터가 있으면 해당 범위, 없으면 오늘 기준
    try:
        filter_from = date.fromisoformat(date_from) if date_from else date.today()
    except ValueError:
        filter_from = date.today()
    try:
        filter_to = date.fromisoformat(date_to) if date_to else None
    except ValueError:
        filter_to = None

    # 이벤트 검색: 기간 필터 적용
    # 반복 이벤트는 항상 포함 (진행중인 정기 이벤트)
    date_conditions = [models.Event.is_recurring == True]
    if filter_to:
        # event_date <= filter_to AND (event_end_date >= filter_from OR event_date >= filter_from)
        date_conditions.append(
            (models.Event.event_date <= filter_to) &
            or_(
                models.Event.event_end_date >= filter_from,
                (models.Event.event_end_date == None) & (models.Event.event_date >= filter_from),
            )
        )
    else:
        date_conditions.append(
            or_(
                models.Event.event_end_date >= filter_from,
                (models.Event.event_end_date == None) & (models.Event.event_date >= filter_from),
            )
        )

    events = db.query(models.Event).filter(
        or_(*date_conditions),
        (models.Event.title.like(keyword)) |
        (models.Event.description.like(keyword)) |
        (models.Event.instructor_name.like(keyword)) |
        (models.Event.location_name.like(keyword))
    ).limit(limit).all()

    # 장소 검색: name, address
    venues = db.query(models.Venue).filter(
        (models.Venue.name.like(keyword)) |
        (models.Venue.address.like(keyword))
    ).limit(limit).all()

    results = []

    def get_media(entity_type, entity_id):
        media = db.query(models.Media).filter(
            models.Media.entity_type == entity_type,
            models.Media.entity_id == entity_id,
        ).order_by(models.Media.sort_order).all()
        return [{"id": m.id, "url": m.url, "media_type": m.media_type} for m in media]

    for e in events:
        genres = [dg.dance_genre for dg in e.dance_genres]
        results.append({
            "item_type": "event",
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "location_name": e.location_name,
            "address": e.address,
            "latitude": e.latitude,
            "longitude": e.longitude,
            "event_date": e.event_date.isoformat() if e.event_date else None,
            "event_end_date": e.event_end_date.isoformat() if e.event_end_date else None,
            "start_time": e.start_time.isoformat() if e.start_time else None,
            "end_time": e.end_time.isoformat() if e.end_time else None,
            "event_type": e.event_type,
            "dance_genres": genres,
            "difficulty": e.difficulty,
            "price": e.price,
            "media": get_media("event", e.id),
        })

    for v in venues:
        genres = [dg.dance_genre for dg in v.dance_genres]
        results.append({
            "item_type": "venue",
            "id": v.id,
            "venue_type": v.venue_type,
            "name": v.name,
            "description": v.description,
            "address": v.address,
            "latitude": v.latitude,
            "longitude": v.longitude,
            "dance_genres": genres,
            "media": get_media("venue", v.id),
        })

    return results    