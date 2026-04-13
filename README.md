# AI 영수증 지출 관리 시스템

> 영수증 한 장으로 시작하는 스마트 가계부 — 촬영만 하면 AI가 알아서 기록하고 분석한다.

영수증 이미지(JPG/PNG) 또는 PDF를 업로드하면 **Upstage Vision LLM**이 자동 OCR 분석하고,  
지출 항목을 SQLite에 저장·시각화하는 웹 애플리케이션입니다.

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| 프론트엔드 | React 18, Vite 5, TailwindCSS 3, Recharts 2, Axios 1.6 |
| 백엔드 | Python 3.11+, FastAPI 0.110+, LangChain 1.2+, langchain-upstage 0.7+ |
| 데이터베이스 | SQLite (내장) |
| AI/OCR | Upstage Vision LLM (Document Parse) |

---

## 프로젝트 구조

```
claude_upstage_ocr/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 앱 진입점
│   │   ├── database.py      # SQLAlchemy 설정
│   │   ├── models/          # ORM 모델
│   │   ├── schemas/         # Pydantic 스키마
│   │   ├── routers/         # API 라우터
│   │   └── services/        # 비즈니스 로직 (OCR 등)
│   ├── uploads/             # 업로드된 영수증 이미지
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios API 모듈
│   │   ├── components/      # 공통 + 도메인 컴포넌트
│   │   ├── pages/           # 5개 화면 페이지
│   │   └── hooks/           # 커스텀 훅
│   ├── package.json
│   └── vite.config.js
├── images/                  # OCR 테스트 샘플 영수증
├── PRD_AI_영수증_지출관리.md
└── 개요서_AI_영수증_지출관리.md
```

---

## 빠른 시작

### 사전 요구사항

- Python 3.11+
- Node.js 18+
- Upstage API Key ([콘솔](https://console.upstage.ai)에서 발급)

### 백엔드 실행

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/Scripts/activate   # Windows
source venv/bin/activate        # macOS/Linux

pip install -r backend/requirements.txt

# 환경변수 설정
cp .env.example backend/.env
# backend/.env에 UPSTAGE_API_KEY 입력

# 개발 서버 실행 (http://localhost:8000)
uvicorn app.main:app --reload --app-dir backend

# API 문서: http://localhost:8000/docs
```

### 프론트엔드 실행

```bash
cd frontend
npm install

# 환경변수 설정
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local

npm run dev   # http://localhost:5173
```

---

## 환경변수

### backend/.env

```env
UPSTAGE_API_KEY=your_upstage_api_key_here
DATABASE_URL=sqlite:///./receipt.db
```

### frontend/.env.local

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## API 문서

서버 실행 후 http://localhost:8000/docs 에서 Swagger UI로 전체 API를 확인할 수 있습니다.

| Method | URL | 설명 |
|--------|-----|------|
| `POST` | `/api/receipts/upload` | 영수증 업로드 및 OCR 분석 |
| `GET` | `/api/receipts` | 지출 내역 목록 조회 |
| `GET` | `/api/receipts/{id}` | 지출 상세 조회 |
| `PUT` | `/api/receipts/{id}` | 지출 수정 |
| `DELETE` | `/api/receipts/{id}` | 지출 삭제 |
| `GET` | `/api/stats/summary` | 통계 데이터 조회 |
| `GET` | `/api/categories` | 카테고리 목록 |

---

## 브랜치 전략

| 브랜치 | 역할 |
|--------|------|
| `main` | Vercel 자동 배포 트리거 |
| `develop` | 기능 통합 및 테스트 |
| `feature/*` | 기능 단위 개발 |
| `hotfix/*` | 운영 긴급 수정 |

---

## 라이선스

MIT
