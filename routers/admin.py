from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_admin
import models

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/users")
def list_users(
    q: str = Query("", description="검색어"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(models.User)
    if q:
        keyword = f"%{q}%"
        query = query.filter(
            (models.User.email.like(keyword)) |
            (models.User.nickname.like(keyword))
        )
    total = query.count()
    users = query.order_by(models.User.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "nickname": u.nickname,
                "is_organizer": u.is_organizer,
                "is_admin": u.is_admin,
                "is_verified": u.is_verified,
                "created_at": u.created_at,
            }
            for u in users
        ],
    }

@router.put("/users/{user_id}")
def update_user_role(
    user_id: int,
    role: dict,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "사용자를 찾을 수 없습니다")
    if "is_organizer" in role:
        user.is_organizer = role["is_organizer"]
    db.commit()
    return {"message": "권한이 변경되었습니다"}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(404, "사용자를 찾을 수 없습니다")
    if user.is_admin:
        raise HTTPException(400, "관리자 계정은 삭제할 수 없습니다")
    if user.email == 'ghost@windycity.internal':
        raise HTTPException(400, "시스템 계정은 삭제할 수 없습니다")

    # 게시물(이벤트/장소) 존재 여부 확인
    event_count = db.query(models.Event).filter(models.Event.organizer_id == user_id).count()
    venue_count = db.query(models.Venue).filter(models.Venue.owner_id == user_id).count()
    if event_count > 0 or venue_count > 0:
        raise HTTPException(400, f"등록한 이벤트({event_count}건) 또는 장소({venue_count}건)가 있어 삭제할 수 없습니다")

    db.delete(user)
    db.commit()
    return {"message": "계정이 삭제되었습니다"}

@router.get("/events")
def list_events(
    q: str = Query("", description="검색어"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(models.Event)
    if q:
        keyword = f"%{q}%"
        query = query.filter(
            (models.Event.title.like(keyword)) |
            (models.Event.location_name.like(keyword))
        )
    total = query.count()
    events = query.order_by(models.Event.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "location_name": e.location_name,
                "event_type": e.event_type,
                "start_date": e.start_date,
                "organizer_nickname": e.organizer.nickname if e.organizer else None,
                "created_at": e.created_at,
            }
            for e in events
        ],
    }


@router.delete("/events/{event_id}")
def admin_delete_event(
    event_id: int,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(404, "이벤트를 찾을 수 없습니다")
    # 미디어 삭제
    media_list = db.query(models.Media).filter(
        models.Media.entity_type == "event", models.Media.entity_id == event_id
    ).all()
    for m in media_list:
        import os
        if m.url and m.url.startswith("/uploads/"):
            filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), m.url.lstrip("/"))
            if os.path.exists(filepath):
                os.remove(filepath)
        db.delete(m)
    # 장르 삭제
    db.query(models.EventDanceGenre).filter(models.EventDanceGenre.event_id == event_id).delete()
    db.delete(event)
    db.commit()
    return {"message": "이벤트가 삭제되었습니다"}


@router.get("/venues")
def list_venues(
    q: str = Query("", description="검색어"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(models.Venue)
    if q:
        keyword = f"%{q}%"
        query = query.filter(
            (models.Venue.name.like(keyword)) |
            (models.Venue.address.like(keyword))
        )
    total = query.count()
    venues = query.order_by(models.Venue.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "venues": [
            {
                "id": v.id,
                "name": v.name,
                "venue_type": v.venue_type,
                "address": v.address,
                "owner_nickname": v.owner.nickname if v.owner else None,
                "created_at": v.created_at,
            }
            for v in venues
        ],
    }


@router.delete("/venues/{venue_id}")
def admin_delete_venue(
    venue_id: int,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    venue = db.query(models.Venue).filter(models.Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(404, "장소를 찾을 수 없습니다")
    media_list = db.query(models.Media).filter(
        models.Media.entity_type == "venue", models.Media.entity_id == venue_id
    ).all()
    for m in media_list:
        import os
        if m.url and m.url.startswith("/uploads/"):
            filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), m.url.lstrip("/"))
            if os.path.exists(filepath):
                os.remove(filepath)
        db.delete(m)
    db.query(models.VenueDanceGenre).filter(models.VenueDanceGenre.venue_id == venue_id).delete()
    db.delete(venue)
    db.commit()
    return {"message": "장소가 삭제되었습니다"}
