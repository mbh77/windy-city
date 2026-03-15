import uuid
import os
from io import BytesIO
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from PIL import Image
from auth import get_current_user
import models

router = APIRouter(prefix="/api/upload", tags=["upload"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 원본 최대 10MB (PNG 변환 전)
MAX_FINAL_SIZE = 3 * 1024 * 1024    # 최종 파일 최대 3MB


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
):
    # 파일 타입 검증
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="JPG, PNG, WEBP만 업로드 가능합니다")

    # 파일 읽기 + 원본 크기 검증
    data = await file.read()
    if len(data) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기는 10MB 이하만 가능합니다")

    # 저장 디렉토리 생성
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # PNG → JPG 변환
    is_png = file.content_type == "image/png"
    if is_png:
        img = Image.open(BytesIO(data))
        # 투명 배경을 흰색으로 변환
        if img.mode in ("RGBA", "P"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.convert("RGBA").split()[3])
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # 품질을 조절하며 3MB 이하로 저장
        quality = 90
        while quality >= 50:
            buf = BytesIO()
            img.save(buf, format="JPEG", quality=quality)
            if buf.tell() <= MAX_FINAL_SIZE:
                break
            quality -= 10

        data = buf.getvalue()
        ext = "jpg"
    else:
        # JPG/WEBP: 3MB 초과 시 거부
        if len(data) > MAX_FINAL_SIZE:
            raise HTTPException(status_code=400, detail="JPG/WEBP 파일은 3MB 이하만 가능합니다")
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"

    # 고유 파일명 생성 + 저장
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(data)

    return {"url": f"/uploads/{filename}"}
