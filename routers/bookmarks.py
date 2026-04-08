from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from database import get_db
import models
import schemas
import auth as auth_utils

router = APIRouter(prefix="/api/bookmarks", tags=["bookmarks"])


@router.post("/{entity_type}/{entity_id}", status_code=201)
def add_bookmark(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    """북마크 추가"""
    if entity_type not in ("event", "venue"):
        raise HTTPException(status_code=400, detail="잘못된 타입입니다")

    # 이미 북마크했는지 확인
    existing = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id,
        models.Bookmark.entity_type == entity_type,
        models.Bookmark.entity_id == entity_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 북마크한 항목입니다")

    bookmark = models.Bookmark(
        user_id=current_user.id,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


@router.delete("/{entity_type}/{entity_id}")
def remove_bookmark(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    """북마크 삭제"""
    bookmark = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id,
        models.Bookmark.entity_type == entity_type,
        models.Bookmark.entity_id == entity_id,
    ).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="북마크를 찾을 수 없습니다")

    db.delete(bookmark)
    db.commit()
    return {"message": "북마크가 삭제되었습니다"}


@router.get("/me", response_model=list[schemas.BookmarkResponse])
def get_my_bookmarks(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    """내 북마크 목록 조회"""
    bookmarks = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id,
    ).order_by(models.Bookmark.created_at.desc()).all()
    return bookmarks


@router.get("/me/details")
def get_my_bookmarks_details(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    entity_type: str = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    """내 북마크 상세 목록 (이벤트/장소 정보 포함, 페이징)"""
    query = db.query(models.Bookmark).filter(
        models.Bookmark.user_id == current_user.id,
    )
    if entity_type in ("event", "venue"):
        query = query.filter(models.Bookmark.entity_type == entity_type)

    total = query.count()
    bookmarks = query.order_by(models.Bookmark.created_at.desc()) \
        .offset((page - 1) * limit).limit(limit).all()

    items = []
    for bm in bookmarks:
        item = {
            "bookmark_id": bm.id,
            "entity_type": bm.entity_type,
            "entity_id": bm.entity_id,
            "bookmarked_at": bm.created_at,
        }
        if bm.entity_type == "event":
            event = db.query(models.Event).options(
                joinedload(models.Event.dance_genres),
                joinedload(models.Event.organizer),
            ).filter(models.Event.id == bm.entity_id).first()
            if event:
                item["title"] = event.title
                item["location_name"] = event.location_name
                item["event_date"] = str(event.event_date) if event.event_date else None
                item["start_time"] = str(event.start_time)[:5] if event.start_time else None
                item["event_type"] = event.event_type.value if event.event_type else None
                item["dance_genres"] = [g.dance_genre.value for g in event.dance_genres]
                item["organizer_nickname"] = event.organizer.nickname if event.organizer else ""
                item["view_count"] = event.view_count or 0
            else:
                item["title"] = "(삭제된 행사)"
        elif bm.entity_type == "venue":
            venue = db.query(models.Venue).options(
                joinedload(models.Venue.dance_genres),
                joinedload(models.Venue.owner),
            ).filter(models.Venue.id == bm.entity_id).first()
            if venue:
                item["name"] = venue.name
                item["address"] = venue.address
                item["venue_type"] = venue.venue_type.value if venue.venue_type else None
                item["dance_genres"] = [g.dance_genre.value for g in venue.dance_genres]
                item["owner_nickname"] = venue.owner.nickname if venue.owner else ""
                item["view_count"] = venue.view_count or 0
            else:
                item["name"] = "(삭제된 장소)"
        items.append(item)

    return {"items": items, "total": total, "page": page, "limit": limit}
