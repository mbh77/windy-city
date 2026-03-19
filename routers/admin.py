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

    # 게시물(이벤트/장소) 존재 여부 확인
    event_count = db.query(models.Event).filter(models.Event.organizer_id == user_id).count()
    venue_count = db.query(models.Venue).filter(models.Venue.owner_id == user_id).count()
    if event_count > 0 or venue_count > 0:
        raise HTTPException(400, f"등록한 이벤트({event_count}건) 또는 장소({venue_count}건)가 있어 삭제할 수 없습니다")

    db.delete(user)
    db.commit()
    return {"message": "계정이 삭제되었습니다"}