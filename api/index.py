"""
Vercel Python Serverless 진입점.

Vercel은 api/index.py 를 Python serverless 함수로 실행합니다.
backend/ 패키지를 sys.path에 추가해 FastAPI app을 가져옵니다.
"""
import os
import sys

# backend/ 디렉토리를 Python path에 추가 (app 패키지 임포트)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app  # noqa: E402, F401 — Vercel이 이 모듈의 `app`을 ASGI 핸들러로 사용
