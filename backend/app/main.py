import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import categories, receipts, stats

load_dotenv()

# uploads 디렉토리 결정
# - Vercel: 파일시스템 읽기 전용 → /tmp/uploads 사용
# - 로컬:   UPLOAD_DIR 환경변수 또는 backend/uploads/ 기본값
if os.getenv("VERCEL"):
    UPLOAD_DIR = "/tmp/uploads"
else:
    UPLOAD_DIR = os.getenv(
        "UPLOAD_DIR",
        os.path.join(os.path.dirname(__file__), "..", "uploads"),
    )

# StaticFiles 마운트 전에 디렉토리를 미리 생성 (import 시점에 실행)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# CORS 허용 오리진
# 환경변수 CORS_ORIGINS: 쉼표로 구분된 URL 목록
# 예) CORS_ORIGINS=https://my-app.vercel.app,https://my-app-git-main.vercel.app
_env_origins = os.getenv("CORS_ORIGINS", "")
ALLOWED_ORIGINS = (
    [o.strip() for o in _env_origins.split(",") if o.strip()]
    if _env_origins
    else [
        "http://localhost:5173",  # Vite 개발 서버
        "http://localhost:4173",  # Vite preview
    ]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 DB 테이블 생성
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AI 영수증 지출 관리 API",
    description="Upstage Vision LLM 기반 영수증 OCR 및 지출 관리 시스템",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 업로드 파일 정적 서빙 (/uploads/{filename})
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 라우터 등록
app.include_router(receipts.router)
app.include_router(stats.router)
app.include_router(categories.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "message": "AI 영수증 지출 관리 API가 정상 동작 중입니다."}
