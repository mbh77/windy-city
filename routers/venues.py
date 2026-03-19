import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

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

router = APIRouter(prefix="/api/venues", tags=["venues"])


def _get_dance_genres(venue: models.Venue) -> list:
    """장소의 춤 종류 목록 반환"""
    return [dg.dance_genre for dg in venue.dance_genres]


def _set_dance_genres(db: Session, venue: models.Venue, genres: list):
    """장소의 춤 종류 설정 (기존 삭제 후 재생성)"""
    venue.dance_genres.clear()
    for genre in genres:
        venue.dance_genres.append(models.VenueDanceGenre(dance_genre=genre))


def _get_media(db: Session, entity_type: str, entity_id: int) -> list:
    """엔티티의 미디어 목록 반환"""
    return db.query(models.Media).filter(
        models.Media.entity_type == entity_type,
        models.Media.entity_id == entity_id
    ).order_by(models.Media.sort_order).all()


def _venue_to_response(db: Session, venue: models.Venue) -> schemas.VenueResponse:
    """Venue 모델을 VenueResponse로 변환"""
    return schemas.VenueResponse(
        **{c.name: getattr(venue, c.name) for c in venue.__table__.columns},
        dance_genres=_get_dance_genres(venue),
        owner_nickname=venue.owner.nickname if venue.owner else None,
        media=[schemas.MediaResponse.model_validate(m) for m in _get_media(db, "venue", venue.id)],
    )


@router.get("/", response_model=List[schemas.VenueResponse])
def get_venues(
    venue_type: Optional[models.VenueType] = Query(None, description="장소 유형 필터"),
    dance_genre: Optional[models.DanceGenre] = Query(None, description="춤 종류 필터"),
    db: Session = Depends(get_db)
):
    """장소 목록 조회 (로그인 불필요)"""
    query = db.query(models.Venue)

    if venue_type:
        query = query.filter(models.Venue.venue_type == venue_type)
    if dance_genre:
        query = query.join(models.VenueDanceGenre).filter(
            models.VenueDanceGenre.dance_genre == dance_genre
        )

    venues = query.order_by(models.Venue.created_at.desc()).all()
    return [_venue_to_response(db, v) for v in venues]


@router.post("/", response_model=schemas.VenueResponse, status_code=201)
def create_venue(
    venue_data: schemas.VenueCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """장소 등록 (로그인 필요)"""
    data = venue_data.model_dump(exclude={"dance_genres"})
    venue = models.Venue(**data, owner_id=current_user.id)
    db.add(venue)
    db.flush()

    # 춤 종류 저장
    _set_dance_genres(db, venue, venue_data.dance_genres)

    db.commit()
    db.refresh(venue)
    return _venue_to_response(db, venue)


@router.get("/{venue_id}", response_model=schemas.VenueResponse)
def get_venue(venue_id: int, db: Session = Depends(get_db)):
    """장소 상세 조회"""
    venue = db.query(models.Venue).filter(models.Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="장소를 찾을 수 없습니다")
    return _venue_to_response(db, venue)


@router.put("/{venue_id}", response_model=schemas.VenueResponse)
def update_venue(
    venue_id: int,
    venue_data: schemas.VenueUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """장소 수정 (본인만 가능)"""
    venue = db.query(models.Venue).filter(models.Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="장소를 찾을 수 없습니다")
    if venue.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다")

    # 변경된 필드만 업데이트 (dance_genres 제외)
    update_data = venue_data.model_dump(exclude_unset=True, exclude={"dance_genres"})
    for field, value in update_data.items():
        setattr(venue, field, value)

    # 춤 종류가 포함된 경우 업데이트
    if venue_data.dance_genres is not None:
        _set_dance_genres(db, venue, venue_data.dance_genres)

    db.commit()
    db.refresh(venue)
    return _venue_to_response(db, venue)


@router.delete("/{venue_id}", status_code=204)
def delete_venue(
    venue_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """장소 삭제 (본인만 가능)"""
    venue = db.query(models.Venue).filter(models.Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="장소를 찾을 수 없습니다")
    if venue.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다")

    # 관련 미디어 파일 + 레코드 삭제
    media_list = db.query(models.Media).filter(
        models.Media.entity_type == "venue",
        models.Media.entity_id == venue_id
    ).all()
    for m in media_list:
        _delete_media_file(m.url)
        db.delete(m)

    db.delete(venue)
    db.commit()


# ── 장소 미디어 API ──────────────────────────────────────────

@router.post("/{venue_id}/media", response_model=schemas.MediaResponse, status_code=201)
def add_venue_media(
    venue_id: int,
    media_data: schemas.MediaCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """장소에 미디어 추가 (본인만 가능)"""
    venue = db.query(models.Venue).filter(models.Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="장소를 찾을 수 없습니다")
    if venue.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="미디어 추가 권한이 없습니다")

    media = models.Media(
        entity_type="venue",
        entity_id=venue_id,
        **media_data.model_dump()
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


@router.delete("/{venue_id}/media/{media_id}", status_code=204)
def delete_venue_media(
    venue_id: int,
    media_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    """장소 미디어 삭제 (본인만 가능)"""
    venue = db.query(models.Venue).filter(models.Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="장소를 찾을 수 없습니다")
    if venue.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="미디어 삭제 권한이 없습니다")

    media = db.query(models.Media).filter(
        models.Media.id == media_id,
        models.Media.entity_type == "venue",
        models.Media.entity_id == venue_id
    ).first()
    if not media:
        raise HTTPException(status_code=404, detail="미디어를 찾을 수 없습니다")

    _delete_media_file(media.url)
    db.delete(media)
    db.commit()
