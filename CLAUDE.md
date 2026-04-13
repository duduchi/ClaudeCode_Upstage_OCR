# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

**AI 영수증 지출 관리 시스템** (Receipt Intelligence & Expense Tracker)  
영수증 이미지(JPG/PNG) 또는 PDF를 업로드하면 Upstage Vision LLM이 자동 OCR 분석하고, 지출 항목을 SQLite에 저장·시각화하는 웹 애플리케이션.

- 기획 문서: `PRD_AI_영수증_지출관리.md` (기능 요구사항, API 명세, 화면 설계, 마일스톤)
- 개요서: `개요서_AI_영수증_지출관리.md` (아키텍처 흐름도, 기술 선택 근거)
- OCR 테스트 샘플: `images/` (이마트·스타벅스·CU 등 14종 실제 영수증 이미지/PDF)

---

## 기술 스택 (버전 고정, 변경 불가)

| 영역 | 기술 |
|------|------|
| 프론트엔드 | ReactJS 18+, Vite 5+, TailwindCSS 3+, Recharts 2+, Axios 1.6+ |
| 백엔드 | Python 3.11+, FastAPI 0.110+, LangChain 1.2+, langchain-upstage 0.7+ |
| 데이터베이스 | SQLite (내장, 별도 서버 없음) |
| 배포 | Vercel (프론트엔드), 백엔드 배포 환경 미확정 (로컬 기준 개발) |

---

## 개발 명령어

### 백엔드

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/Scripts/activate   # Windows
source venv/bin/activate        # macOS/Linux

pip install -r backend/requirements.txt

# 개발 서버 (http://localhost:8000)
uvicorn app.main:app --reload --app-dir backend

# Swagger UI: http://localhost:8000/docs
```

### 프론트엔드

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
npm run build
npm run preview
```

### 환경변수

```bash
# backend/.env
UPSTAGE_API_KEY=<upstage-api-key>
DATABASE_URL=sqlite:///./receipt.db

# frontend/.env.local
VITE_API_BASE_URL=http://localhost:8000
```

---

## 아키텍처

### 요청 흐름

```
브라우저 (React)
  └─ Axios → FastAPI (/api/receipts/upload)
               ├─ 파일 저장: backend/uploads/
               ├─ ocr_service.py → langchain-upstage → Upstage Vision LLM
               │     └─ JSON 파싱 (date, store_name, items, total, category)
               └─ SQLAlchemy → receipt.db (receipts + receipt_items 테이블)
```

**핵심 제약**: Upstage API 키는 `ocr_service.py`에서만 사용. 프론트엔드에 절대 노출 금지.

### 백엔드 레이어

```
backend/app/
├── main.py          # FastAPI 앱 생성, 라우터 등록, CORS 설정
├── database.py      # SQLAlchemy 엔진, 세션 의존성 주입 (Depends)
├── models/          # ORM: Receipt, ReceiptItem (CASCADE 삭제 설정 필수)
├── schemas/         # Pydantic: 요청·응답 형식 분리 (Create/Update/Response)
├── routers/         # receipts.py / stats.py / categories.py
└── services/
    └── ocr_service.py   # langchain-upstage 호출, JSON 파싱, 카테고리 매핑
```

`ocr_service.py`가 전체 가치의 핵심. LLM 프롬프트에서 아래 JSON 스키마를 강제 출력:

```json
{
  "date": "YYYY-MM-DD",
  "store_name": "string",
  "items": [{ "name": "string", "quantity": 1, "price": 0 }],
  "total": 0,
  "category": "식료품 | 외식 | 쇼핑 | 교통 | 의료/건강 | 문화/여가 | 기타"
}
```

### 프론트엔드 레이어

```
frontend/src/
├── api/             # axiosClient.js (인터셉터), receipts.js, stats.js
├── components/      # common / receipt / stats 도메인별 분리
├── pages/           # 5개 화면 (Dashboard, Upload, List, Detail, Stats)
└── hooks/           # useReceipts, useStats — 데이터 페칭 커스텀 훅
```

### DB 스키마

**receipts**: `id` PK | `store_name` | `date` | `total_amount` | `category` | `image_path` | `raw_json` | `created_at` | `updated_at`

**receipt_items**: `id` PK | `receipt_id` FK→receipts(CASCADE) | `item_name` | `quantity` | `unit_price` | `total_price`

### API 엔드포인트

| Method | URL | 비고 |
|--------|-----|------|
| `POST` | `/api/receipts/upload` | `multipart/form-data`, 파일 + OCR + DB 저장 |
| `GET` | `/api/receipts` | `page`, `size`, `start_date`, `end_date`, `category`, `store_name` |
| `GET/PUT/DELETE` | `/api/receipts/{id}` | GET은 items 배열 포함 반환 |
| `GET` | `/api/stats/summary` | `period`(day/month/year), `start_date`, `end_date` |
| `GET` | `/api/categories` | 7개 카테고리 목록 |

---

## 개발 우선순위

**P0 (먼저 구현)**: OCR 서비스 → Upload API → CRUD API → 업로드 UI → 목록/상세 화면  
**P1 (그 다음)**: 통계 API → 3개 차트 컴포넌트 → 대시보드 → 필터·페이지네이션  
**P2 (마지막)**: 이미지 뷰어 확대 · PDF 지원 · 빈 상태 UI

전체 순서: `PRD_AI_영수증_지출관리.md` §11.2 (개발 우선순위 표) 참조.

---

## 제약사항

- 파일 업로드: 최대 **10MB**, MIME 검증 (`image/jpeg`, `image/png`, `application/pdf`)
- CORS: 개발 `localhost:5173`, 운영 Vercel 도메인만 허용
- `raw_json` 컬럼에 LLM 원본 출력 보존 (디버깅용)
- 영수증 삭제 시 `receipt_items` CASCADE 삭제 (소프트 삭제 미적용)

## Git 브랜치 전략

| 브랜치 | 역할 |
|--------|------|
| `main` | Vercel 자동 배포 트리거 |
| `develop` | 기능 통합 및 테스트 |
| `feature/*` | 기능 단위 개발 (예: `feature/ocr-service`) |
| `hotfix/*` | 운영 긴급 수정 |

## 디자인 시스템

폰트: `Noto Sans KR` (한국어 UI), `Inter` (숫자·영문)  
Primary: `blue-600` (#2563EB) — CTA 버튼, 활성 상태  
카테고리 배지 색상: 식료품 `green`, 외식 `orange`, 쇼핑 `purple`, 교통 `blue`, 의료 `red`, 문화 `yellow`, 기타 `gray`  
차트 색상은 배지 색상과 통일 (Recharts `fill` 속성에 동일 HEX 사용).

상세 레이아웃 와이어프레임 및 Tailwind 클래스 가이드: `PRD_AI_영수증_지출관리.md` §15 참조.
