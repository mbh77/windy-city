from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from fastapi import Depends

from database import get_db

import models

router = APIRouter(prefix="/api", tags=["search"])

@router.get("/search")
def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    from datetime import datetime
    from sqlalchemy import or_

    keyword = f"%{q}%"

    now = datetime.now()

    # 이벤트 검색: title, description, instructor_name, location_name
    # 반복 이벤트는 항상 포함 (진행중인 정기 이벤트)
    events = db.query(models.Event).filter(
        or_(
            models.Event.is_recurring == True,
            models.Event.end_date >= now,
            (models.Event.end_date == None) & (models.Event.start_date >= now),
        ),
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
            "start_date": e.start_date.isoformat() if e.start_date else None,
            "end_date": e.end_date.isoformat() if e.end_date else None,
            "event_type": e.event_type,
            "dance_genres": genres,
            "difficulty": e.difficulty,
            "price": e.price,
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
        })

    return results    