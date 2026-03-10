from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine
import models
from routers import auth, events, venues

# DB 테이블 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Windy City", description="살사 댄스 이벤트 지도 서비스")

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

# 정적 파일 서빙 (프론트엔드)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
