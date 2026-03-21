from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from auth import get_current_user, get_current_admin
import models
import schemas
from datetime import datetime

router = APIRouter(prefix="/api/posts", tags=["posts"])


# ── 게시글 CRUD ──────────────────────────────────────────────

@router.get("/")
def list_posts(
    category: str = Query("free", description="notice 또는 free"),
    q: str = Query("", description="검색어"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(models.Post).filter(models.Post.category == category)
    if q:
        keyword = f"%{q}%"
        query = query.filter(
            (models.Post.title.like(keyword)) |
            (models.Post.content.like(keyword))
        )
    total = query.count()
    posts = query.order_by(models.Post.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return {
        "total": total,
        "page": page,
        "posts": [
            {
                "id": p.id,
                "category": p.category,
                "title": p.title,
                "content": p.content,
                "author_id": p.author_id,
                "author_nickname": p.author.nickname if p.author else None,
                "comment_count": len(p.comments),
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "view_count": p.view_count,
            }
            for p in posts
        ],
    }


@router.post("/", status_code=201)
def create_post(
    req: schemas.PostCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 공지사항은 관리자만
    if req.category == "notice" and not user.is_admin:
        raise HTTPException(403, "공지사항은 관리자만 작성할 수 있습니다")

    post = models.Post(
        category=req.category,
        title=req.title,
        content=req.content,
        author_id=user.id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return {
        "id": post.id,
        "category": post.category,
        "title": post.title,
        "content": post.content,
        "author_id": post.author_id,
        "author_nickname": user.nickname,
        "comment_count": 0,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "view_count": 0,
    }


@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(404, "게시글을 찾을 수 없습니다")
        
    post.view_count = (post.view_count or 0) + 1
    db.commit()

    return {
        "id": post.id,
        "category": post.category,
        "title": post.title,
        "content": post.content,
        "author_id": post.author_id,
        "author_nickname": post.author.nickname if post.author else None,
        "comment_count": len(post.comments),
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "view_count": post.view_count,
        "comments": [
            {
                "id": c.id,
                "post_id": c.post_id,
                "author_id": c.author_id,
                "author_nickname": c.author.nickname if c.author else None,
                "content": c.content,
                "created_at": c.created_at,
            }
            for c in post.comments
        ],
    }


@router.put("/{post_id}")
def update_post(
    post_id: int,
    req: schemas.PostUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(404, "게시글을 찾을 수 없습니다")
    if post.author_id != user.id and not user.is_admin:
        raise HTTPException(403, "수정 권한이 없습니다")
    if req.title is not None:
        post.title = req.title
    if req.content is not None:
        post.content = req.content
    post.updated_at = datetime.now()
    db.commit()
    db.refresh(post)
    return {
        "id": post.id,
        "category": post.category,
        "title": post.title,
        "content": post.content,
        "author_id": post.author_id,
        "author_nickname": post.author.nickname if post.author else None,
        "comment_count": len(post.comments),
        "created_at": post.created_at,
        "updated_at": post.updated_at,
    }


@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(404, "게시글을 찾을 수 없습니다")
    if post.author_id != user.id and not user.is_admin:
        raise HTTPException(403, "삭제 권한이 없습니다")
    db.delete(post)
    db.commit()


# ── 댓글 ──────────────────────────────────────────────

@router.post("/{post_id}/comments", status_code=201)
def create_comment(
    post_id: int,
    req: schemas.CommentCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(404, "게시글을 찾을 수 없습니다")
    if not req.content.strip():
        raise HTTPException(400, "댓글 내용을 입력해주세요")

    comment = models.Comment(
        post_id=post_id,
        author_id=user.id,
        content=req.content,
        created_at=datetime.now(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "author_id": comment.author_id,
        "author_nickname": user.nickname,
        "content": comment.content,
        "created_at": comment.created_at,
    }


@router.delete("/{post_id}/comments/{comment_id}", status_code=204)
def delete_comment(
    post_id: int,
    comment_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = db.query(models.Comment).filter(
        models.Comment.id == comment_id,
        models.Comment.post_id == post_id,
    ).first()
    if not comment:
        raise HTTPException(404, "댓글을 찾을 수 없습니다")
    if comment.author_id != user.id and not user.is_admin:
        raise HTTPException(403, "삭제 권한이 없습니다")
    db.delete(comment)
    db.commit()
