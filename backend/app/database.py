import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Vercel 환경: 파일시스템이 읽기 전용이므로 /tmp 사용
# 로컬 환경: DATABASE_URL 환경변수 또는 backend/ 디렉토리 기본값
_default_db = (
    "sqlite:////tmp/receipt.db"
    if os.getenv("VERCEL")
    else "sqlite:///./receipt.db"
)
DATABASE_URL = os.getenv("DATABASE_URL", _default_db)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 전용 설정
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI Depends용 DB 세션 의존성 주입."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
