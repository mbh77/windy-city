from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from database import engine
import models
from routers import auth, events, venues, search, upload, feedback, admin, posts

# DB 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Windy City", description="살사 댄스 강습·행사 지도 서비스")

# CORS 설정 (개발 중 모든 origin 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(venues.router)
app.include_router(search.router)
app.include_router(upload.router)
app.include_router(feedback.router)
app.include_router(admin.router)
app.include_router(posts.router)

# 업로드 이미지 서빙 (빌드와 분리)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 정적 파일 서빙 (프론트엔드)
app.mount("/static-files", StaticFiles(directory="static"), name="static")

# SPA fallback: 정적 파일이 있으면 반환, 없으면 index.html 반환
@app.get("/{full_path:path}")
async def spa_fallback(request: Request, full_path: str):
    file_path = os.path.join("static", full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse("static/index.html")
