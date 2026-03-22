from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
import models
import schemas
import auth as auth_utils
from email_utils import generate_verify_code, send_verify_email

router = APIRouter(prefix="/api/auth", tags=["auth"])

# 인증 코드 유효 시간 (분)
VERIFY_CODE_EXPIRE_MINUTES = 10

# 금지 닉네임 목록
RESERVED_NICKNAMES = ['admin', 'administrator', '관리자', '운영자', '바람난도시', 'windycity', '어드민']

# 고스트 계정 이메일 (탈퇴 시 콘텐츠 이전용)
GHOST_EMAIL = 'ghost@windycity.internal'


@router.post("/register", status_code=201)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """회원가입 → 인증 코드 이메일 발송"""
    # 금지 닉네임 확인
    if user_data.nickname.lower().strip() in RESERVED_NICKNAMES:
        raise HTTPException(status_code=400, detail="사용할 수 없는 닉네임입니다")
    # 고스트 계정 이메일 차단
    if user_data.email == GHOST_EMAIL:
        raise HTTPException(status_code=400, detail="사용할 수 없는 이메일입니다")
    # 이메일 중복 확인
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        if existing.is_verified:
            raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다")
        # 미인증 계정이면 정보 덮어쓰기 (재가입 허용)
        existing.hashed_password = auth_utils.hash_password(user_data.password)
        existing.nickname = user_data.nickname
        existing.is_organizer = True
        user = existing
    else:
        # 새 사용자 생성 (가입 시 주최자 권한 기본 부여)
        user = models.User(
            email=user_data.email,
            hashed_password=auth_utils.hash_password(user_data.password),
            nickname=user_data.nickname,
            is_organizer=True,
            is_verified=False,
        )
        db.add(user)

    # 인증 코드 생성
    code = generate_verify_code()
    user.verify_code = code
    user.verify_code_expires = datetime.utcnow() + timedelta(minutes=VERIFY_CODE_EXPIRE_MINUTES)
    db.commit()
    db.refresh(user)

    # 인증 메일 발송
    if not send_verify_email(user.email, code):
        raise HTTPException(status_code=500, detail="인증 메일 발송에 실패했습니다. 잠시 후 다시 시도해 주세요.")

    return {"message": "인증 코드가 이메일로 발송되었습니다", "email": user.email}


@router.post("/verify-email")
def verify_email(data: schemas.VerifyEmail, db: Session = Depends(get_db)):
    """이메일 인증 코드 확인"""
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="등록되지 않은 이메일입니다")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="이미 인증된 계정입니다")

    # 코드 만료 확인
    if user.verify_code_expires and user.verify_code_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="인증 코드가 만료되었습니다. 재발송해 주세요.")

    # 코드 일치 확인
    if user.verify_code != data.code:
        raise HTTPException(status_code=400, detail="인증 코드가 일치하지 않습니다")

    # 인증 완료
    user.is_verified = True
    user.verify_code = None
    user.verify_code_expires = None
    db.commit()

    # 인증 완료 후 자동 로그인 (JWT 발급)
    token = auth_utils.create_access_token(user.id)
    return {"message": "이메일 인증이 완료되었습니다", "access_token": token, "token_type": "bearer"}


@router.post("/resend-code")
def resend_code(data: schemas.ResendCode, db: Session = Depends(get_db)):
    """인증 코드 재발송"""
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="등록되지 않은 이메일입니다")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="이미 인증된 계정입니다")

    # 새 코드 생성
    code = generate_verify_code()
    user.verify_code = code
    user.verify_code_expires = datetime.utcnow() + timedelta(minutes=VERIFY_CODE_EXPIRE_MINUTES)
    db.commit()

    # 이메일 발송
    if not send_verify_email(user.email, code):
        raise HTTPException(status_code=500, detail="인증 메일 발송에 실패했습니다")

    return {"message": "인증 코드가 재발송되었습니다"}


@router.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """로그인 - JWT 토큰 발급"""
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if not user or not auth_utils.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀렸습니다")

    # 이메일 미인증 → 인증 코드 재발송
    if not user.is_verified:
        code = generate_verify_code()
        user.verify_code = code
        user.verify_code_expires = datetime.utcnow() + timedelta(minutes=VERIFY_CODE_EXPIRE_MINUTES)
        db.commit()
        send_verify_email(user.email, code)
        raise HTTPException(status_code=403, detail="이메일 인증이 완료되지 않았습니다. 인증 코드를 재발송했습니다.")

    token = auth_utils.create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth_utils.get_current_user)):
    """내 정보 조회"""
    return current_user


@router.delete("/me", status_code=200)
def delete_me(current_user: models.User = Depends(auth_utils.get_current_user), db: Session = Depends(get_db)):
    """회원 탈퇴 — 콘텐츠를 고스트 계정으로 이전 후 계정 삭제"""
    if current_user.is_admin:
        raise HTTPException(status_code=400, detail="관리자 계정은 탈퇴할 수 없습니다")

    user_id = current_user.id

    # 고스트 계정 조회
    ghost = db.query(models.User).filter(models.User.email == GHOST_EMAIL).first()
    if not ghost:
        raise HTTPException(status_code=500, detail="시스템 오류: 고스트 계정이 없습니다")

    # 작성물을 고스트 계정으로 이전
    db.query(models.Event).filter(models.Event.organizer_id == user_id).update({"organizer_id": ghost.id})
    db.query(models.Venue).filter(models.Venue.owner_id == user_id).update({"owner_id": ghost.id})
    db.query(models.Post).filter(models.Post.author_id == user_id).update({"author_id": ghost.id})
    db.query(models.Comment).filter(models.Comment.author_id == user_id).update({"author_id": ghost.id})

    # 회원 레코드 완전 삭제
    user = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(user)
    db.commit()

    return {"message": "회원 탈퇴가 완료되었습니다"}
