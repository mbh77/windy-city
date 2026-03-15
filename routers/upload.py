import uuid
import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from auth import get_current_user
import models

router = APIRouter(prefix="/api/upload", tags=["upload"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
):
    # 파일 타입 검증
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="JPG, PNG, WEBP만 업로드 가능합니다")

    # 파일 읽기 + 크기 검증
    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기는 5MB 이하만 가능합니다")

    # 저장 디렉토리 생성
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # 고유 파일명 생성
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # 파일 저장
    with open(filepath, "wb") as f:
        f.write(data)

    return {"url": f"/uploads/{filename}"}