from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from email_utils import send_email
import os

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

class FeedbackRequest(BaseModel):
    name: str = ""
    email: str = ""
    message: str

@router.post("/")
def submit_feedback(req: FeedbackRequest):
    if not req.message.strip():
        raise HTTPException(400, "내용을 입력해주세요")
    
    admin_email = os.getenv("ADMIN_EMAIL")
    if not admin_email:
        raise HTTPException(500, "관리자 이메일이 설정되지 않았습니다")
    
    subject = f"[바람난 도시] 제보/제안: {req.name or '익명'}"
    body = f"보낸 사람: {req.name or '익명'}\n이메일: {req.email or '없음'}\n\n{req.message}"
    
    send_email(admin_email, subject, body)
    return {"message": "제보가 전송되었습니다"}