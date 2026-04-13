# PRD: AI 영수증 지출 관리 시스템
## Product Requirements Document

| 항목 | 내용 |
|------|------|
| 문서명 | AI 영수증 지출 관리 시스템 PRD |
| 작성일 | 2026-04-12 |
| 버전 | v1.0.0 |
| 상태 | 검토 중 |
| 기반 문서 | 개요서_AI_영수증_지출관리.md v1.0.0 |

---

## 1. 제품 개요 (Product Overview)

### 1.1 제품 비전

> 영수증 한 장으로 시작하는 스마트 가계부 — 촬영만 하면 AI가 알아서 기록하고 분석한다.

### 1.2 문제 정의 (Problem Statement)

| 문제 | 현재 상황 | 영향 |
|------|-----------|------|
| 수기 가계부의 번거로움 | 매 거래마다 직접 입력 필요 | 지속성 저하, 기록 누락 |
| 기존 앱의 높은 피로감 | 항목·금액·카테고리 수동 분류 | 사용자 이탈률 증가 |
| 영수증 보관의 비효율 | 종이 영수증 분실·훼손 빈번 | 지출 내역 추적 불가 |

### 1.3 목표 사용자 (Target Users)

| 페르소나 | 특징 | 핵심 니즈 |
|----------|------|-----------|
| 직장인 A (28세) | 외식·쇼핑 지출 多, 시간 부족 | 빠른 기록, 자동화 |
| 자영업자 B (42세) | 사업 경비 영수증 관리 필요 | 카테고리 분류, 내보내기 |
| 가정주부 C (35세) | 생활비 절약 목표 | 소비 패턴 분석, 예산 관리 |

### 1.4 성공 지표 (Success Metrics)

| 지표 | 목표값 | 측정 방법 |
|------|--------|-----------|
| OCR 인식 정확도 | ≥ 90% | 샘플 영수증 100건 검증 |
| 업로드-저장 처리 시간 | ≤ 10초 | API 응답 시간 측정 |
| 사용자 만족도 | ≥ 4.0 / 5.0 | 베타 테스트 설문 |
| 월간 활성 사용자 유지율 | ≥ 60% | 4주차 재방문 비율 |

---

## 2. 범위 (Scope)

### 2.1 In-Scope (v1.0 포함)

- 영수증 이미지(JPG, PNG) 및 PDF 업로드
- Upstage Vision LLM 기반 OCR 분석 및 JSON 구조화
- SQLite DB 저장 및 CRUD
- 지출 내역 목록 조회 (필터·검색·페이지네이션)
- AI 추출 결과 수동 수정
- 월별·카테고리별·일별 통계 차트 (Recharts)
- React + FastAPI 웹 애플리케이션
- Vercel 프론트엔드 배포

### 2.2 Out-of-Scope (v1.0 제외)

- 회원가입 / 로그인 / 다중 사용자 지원
- 예산 설정 및 초과 알림
- 모바일 앱 (React Native / PWA)
- Excel / CSV / PDF 내보내기
- PostgreSQL 마이그레이션
- AI 월별 소비 리포트 자동 생성

---

## 3. 기능 요구사항 (Functional Requirements)

### FR-01. 영수증 업로드 및 OCR 분석

**우선순위:** Critical

| ID | 요구사항 | 수락 기준 |
|----|----------|-----------|
| FR-01-1 | 사용자는 JPG, PNG, PDF 파일을 업로드할 수 있어야 한다. | 3가지 포맷 모두 업로드 성공 |
| FR-01-2 | 드래그앤드롭으로 파일을 업로드할 수 있어야 한다. | 드래그앤드롭 시 파일 인식 및 미리보기 표시 |
| FR-01-3 | 업로드 후 AI 분석 진행 상태를 사용자에게 표시해야 한다. | 로딩 프로그레스바 또는 스피너 노출 |
| FR-01-4 | Upstage Vision LLM이 날짜, 상호명, 항목명, 수량, 금액, 합계를 추출해야 한다. | 6개 필드 모두 JSON으로 반환 |
| FR-01-5 | OCR 실패 시 사용자에게 오류 메시지를 표시해야 한다. | 오류 원인 포함 toast/alert 노출 |

**OCR 출력 JSON 스펙:**
```json
{
  "date": "YYYY-MM-DD",
  "store_name": "string",
  "items": [
    { "name": "string", "quantity": 1, "price": 0 }
  ],
  "total": 0,
  "category": "string"
}
```

---

### FR-02. 지출 내역 저장 및 조회

**우선순위:** Critical

| ID | 요구사항 | 수락 기준 |
|----|----------|-----------|
| FR-02-1 | OCR 결과는 자동으로 SQLite DB에 저장되어야 한다. | 업로드 완료 후 DB 레코드 생성 확인 |
| FR-02-2 | 전체 영수증 목록을 최신순으로 조회할 수 있어야 한다. | 목록 API 호출 시 created_at 내림차순 반환 |
| FR-02-3 | 날짜 범위로 영수증을 필터링할 수 있어야 한다. | 시작일~종료일 파라미터 적용 결과 검증 |
| FR-02-4 | 카테고리로 영수증을 필터링할 수 있어야 한다. | 선택 카테고리만 반환 확인 |
| FR-02-5 | 상호명 키워드로 검색할 수 있어야 한다. | 부분 일치 검색 결과 반환 |
| FR-02-6 | 목록은 페이지네이션을 지원해야 한다. | 페이지당 20건, 이전/다음 페이지 이동 가능 |

---

### FR-03. 지출 상세 조회 및 수동 수정

**우선순위:** High

| ID | 요구사항 | 수락 기준 |
|----|----------|-----------|
| FR-03-1 | 영수증 상세 페이지에서 원본 이미지를 썸네일로 볼 수 있어야 한다. | 이미지 로드 성공 확인 |
| FR-03-2 | 썸네일 클릭 시 원본 이미지를 확대 조회할 수 있어야 한다. | 모달/라이트박스로 원본 표시 |
| FR-03-3 | AI 추출 결과(상호명, 날짜, 항목, 금액)를 수동으로 수정할 수 있어야 한다. | 수정 저장 후 DB 반영 확인 |
| FR-03-4 | 항목 추가 및 삭제가 가능해야 한다. | 항목 추가/삭제 후 합계 자동 재계산 |
| FR-03-5 | 영수증 전체 삭제가 가능해야 한다. | 삭제 확인 다이얼로그 → DB 및 이미지 파일 삭제 |

---

### FR-04. 지출 통계 시각화

**우선순위:** High

| ID | 요구사항 | 수락 기준 |
|----|----------|-----------|
| FR-04-1 | 월별 지출 합계를 막대 차트(BarChart)로 표시해야 한다. | 최근 6개월 데이터 시각화 |
| FR-04-2 | 카테고리별 지출 비율을 파이 차트(PieChart)로 표시해야 한다. | 카테고리별 금액·비율(%) 표시 |
| FR-04-3 | 일별 지출 추이를 선 그래프(LineChart)로 표시해야 한다. | 선택 월의 일별 누적 지출 표시 |
| FR-04-4 | 통계 조회 기간을 사용자가 선택할 수 있어야 한다. | 기간 선택기(DateRangePicker)로 필터 적용 |
| FR-04-5 | 메인 대시보드에서 주요 통계 요약을 확인할 수 있어야 한다. | 이번 달 총 지출, 최다 지출 카테고리 표시 |

---

## 4. 비기능 요구사항 (Non-Functional Requirements)

### 4.1 성능 (Performance)

| 요구사항 | 목표 |
|----------|------|
| OCR 분석 포함 전체 처리 시간 | ≤ 10초 (네트워크 지연 제외) |
| 지출 목록 API 응답 시간 | ≤ 1초 |
| 통계 API 응답 시간 | ≤ 2초 |
| 프론트엔드 최초 로딩 시간 (FCP) | ≤ 3초 |

### 4.2 보안 (Security)

| 요구사항 | 상세 |
|----------|------|
| API Key 보호 | `UPSTAGE_API_KEY`는 서버 환경변수로만 관리, 클라이언트 노출 금지 |
| 파일 업로드 검증 | MIME 타입 및 확장자 화이트리스트 검증 (jpg, png, pdf만 허용) |
| 파일 크기 제한 | 업로드 파일 최대 10MB로 제한 |
| SQL Injection 방지 | SQLAlchemy ORM 또는 파라미터 바인딩 사용 |

### 4.3 가용성 및 배포 (Availability & Deployment)

| 요구사항 | 상세 |
|----------|------|
| 프론트엔드 가용성 | Vercel CDN 기반 99.9% SLA |
| 환경변수 관리 | Vercel Dashboard에서 `UPSTAGE_API_KEY` 등 관리 |
| CI/CD | `main` 브랜치 push → Vercel 자동 빌드·배포 |
| PR Preview | Pull Request 생성 시 Preview URL 자동 생성 |

### 4.4 유지보수성 (Maintainability)

| 요구사항 | 상세 |
|----------|------|
| 브랜치 전략 | main / develop / feature/* / hotfix/* 4단계 전략 준수 |
| 백엔드 구조 | FastAPI 라우터 모듈화 (receipts, stats, categories) |
| 프론트엔드 구조 | React 컴포넌트 단위 분리, 페이지별 디렉토리 구성 |

---

## 5. API 명세 (API Specification)

### 5.1 엔드포인트 목록

| Method | URL | 설명 | 요청 Body | 응답 |
|--------|-----|------|-----------|------|
| `POST` | `/api/receipts/upload` | 영수증 업로드 및 OCR 분석 | `multipart/form-data` (file) | OCR JSON + receipt_id |
| `GET` | `/api/receipts` | 목록 조회 | Query: page, limit, category, start_date, end_date, keyword | receipts 배열 + pagination |
| `GET` | `/api/receipts/{id}` | 상세 조회 | - | receipt + items 배열 |
| `PUT` | `/api/receipts/{id}` | 영수증 수정 | JSON (store_name, date, category, items) | 수정된 receipt |
| `DELETE` | `/api/receipts/{id}` | 영수증 삭제 | - | `{ "success": true }` |
| `GET` | `/api/stats/summary` | 통계 데이터 | Query: start_date, end_date | 월별/카테고리별 집계 |
| `GET` | `/api/categories` | 카테고리 목록 | - | categories 배열 |

### 5.2 공통 응답 형식

**성공:**
```json
{
  "success": true,
  "data": { },
  "message": "string"
}
```

**실패:**
```json
{
  "success": false,
  "error": {
    "code": "UPLOAD_FAILED",
    "message": "파일 처리 중 오류가 발생했습니다."
  }
}
```

---

## 6. 데이터 모델 (Data Model)

### 6.1 receipts 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PK, AUTOINCREMENT | 영수증 고유 ID |
| store_name | TEXT | NOT NULL | 상호명 |
| date | DATE | NOT NULL | 구매 날짜 |
| total_amount | REAL | NOT NULL | 합계 금액 |
| category | TEXT | | 지출 카테고리 |
| image_path | TEXT | | 원본 이미지 저장 경로 |
| raw_json | TEXT | | LLM 출력 원본 JSON |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 레코드 생성 시각 |

### 6.2 receipt_items 테이블

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PK, AUTOINCREMENT | 항목 고유 ID |
| receipt_id | INTEGER | FK → receipts.id ON DELETE CASCADE | 영수증 참조 ID |
| item_name | TEXT | NOT NULL | 상품명 |
| quantity | INTEGER | DEFAULT 1 | 수량 |
| unit_price | REAL | NOT NULL | 단가 |
| total_price | REAL | NOT NULL | 소계 (수량 × 단가) |

### 6.3 카테고리 정의 (초기값)

| 코드 | 표시명 |
|------|--------|
| food | 식료품 |
| dining | 외식 |
| shopping | 쇼핑 |
| transport | 교통 |
| medical | 의료/건강 |
| culture | 문화/여가 |
| education | 교육 |
| etc | 기타 |

---

## 7. UI/UX 요구사항 (UI/UX Requirements)

### 7.1 화면 목록 및 주요 컴포넌트

| No. | 화면명 | Route | 주요 컴포넌트 |
|:---:|--------|-------|--------------|
| 1 | 메인 대시보드 | `/` | `SummaryCard`, `MonthlyBarChart`, `CategoryPieChart`, `RecentReceiptList` |
| 2 | 영수증 업로드 | `/upload` | `FileDropzone`, `UploadPreview`, `ProgressBar`, `AnalysisResult` |
| 3 | 지출 내역 목록 | `/receipts` | `FilterBar`, `ReceiptTable`, `Pagination` |
| 4 | 지출 상세/수정 | `/receipts/:id` | `ImageViewer`, `ReceiptForm`, `ItemEditor` |
| 5 | 통계 분석 | `/stats` | `DateRangePicker`, `MonthlyBarChart`, `CategoryPieChart`, `DailyLineChart` |

### 7.2 UX 원칙

- **즉각적 피드백**: 업로드, 저장, 삭제 모든 액션에 로딩 상태 표시
- **오류 가이드**: 실패 시 원인과 해결 방법을 함께 안내
- **반응형 레이아웃**: TailwindCSS 기반 모바일~데스크탑 대응
- **수정 용이성**: AI 추출 오류를 즉시 인라인 편집으로 수정 가능

### 7.3 파일 업로드 UX 흐름

```
파일 선택 or 드래그앤드롭
        ↓
미리보기 표시 + [분석 시작] 버튼
        ↓
AI 분석 중... (프로그레스바)
        ↓
분석 결과 화면 (추출 데이터 표시)
        ↓
[수정] or [저장] 선택
        ↓
저장 완료 → 지출 내역 목록으로 이동
```

---

## 8. 화면 디자인 및 스타일 가이드 (Design & Style Guide)

### 8.1 디자인 원칙

| 원칙 | 설명 |
|------|------|
| **Simple First** | 복잡한 기능도 단순한 UI로 표현 — 영수증 업로드는 버튼 하나로 시작 |
| **Data-Driven** | 숫자·차트 중심 레이아웃, 지출 데이터가 항상 주인공 |
| **Responsive** | 모바일(375px) → 태블릿(768px) → 데스크탑(1280px) 3단계 반응형 |
| **Accessible** | 색상 대비 WCAG AA 기준 준수, 키보드 내비게이션 지원 |

---

### 8.2 컬러 팔레트 (Color Palette)

#### Primary 컬러
| 용도 | 색상명 | HEX | TailwindCSS 클래스 |
|------|--------|-----|-------------------|
| 주요 액션 버튼, 강조 | Indigo 600 | `#4F46E5` | `bg-indigo-600` |
| 호버 상태 | Indigo 700 | `#4338CA` | `hover:bg-indigo-700` |
| 아이콘·링크 | Indigo 500 | `#6366F1` | `text-indigo-500` |
| 배경 틴트 | Indigo 50 | `#EEF2FF` | `bg-indigo-50` |

#### 시맨틱 컬러 (Semantic Colors)
| 용도 | 색상명 | HEX | TailwindCSS 클래스 |
|------|--------|-----|-------------------|
| 성공 / 저장 완료 | Green 500 | `#22C55E` | `text-green-500` |
| 경고 / 주의 | Amber 500 | `#F59E0B` | `text-amber-500` |
| 오류 / 삭제 | Red 500 | `#EF4444` | `text-red-500` |
| 정보 / 안내 | Blue 500 | `#3B82F6` | `text-blue-500` |

#### 차트 카테고리 컬러 (Recharts용)
| 카테고리 | HEX |
|----------|-----|
| 식료품 | `#6366F1` |
| 외식 | `#F59E0B` |
| 쇼핑 | `#EC4899` |
| 교통 | `#14B8A6` |
| 의료/건강 | `#22C55E` |
| 문화/여가 | `#8B5CF6` |
| 교육 | `#F97316` |
| 기타 | `#94A3B8` |

#### 뉴트럴 컬러 (Neutral Colors)
| 용도 | HEX | TailwindCSS 클래스 |
|------|-----|-------------------|
| 페이지 배경 | `#F8FAFC` | `bg-slate-50` |
| 카드 배경 | `#FFFFFF` | `bg-white` |
| 테두리 | `#E2E8F0` | `border-slate-200` |
| 보조 텍스트 | `#64748B` | `text-slate-500` |
| 기본 텍스트 | `#1E293B` | `text-slate-800` |

---

### 8.3 타이포그래피 (Typography)

| 구분 | 크기 | 굵기 | TailwindCSS 클래스 | 사용처 |
|------|------|------|-------------------|--------|
| Display | 30px | 700 | `text-3xl font-bold` | 페이지 타이틀 |
| Heading 1 | 24px | 700 | `text-2xl font-bold` | 섹션 제목 |
| Heading 2 | 18px | 600 | `text-lg font-semibold` | 카드 제목 |
| Body | 14px | 400 | `text-sm` | 본문, 테이블 내용 |
| Caption | 12px | 400 | `text-xs` | 보조 정보, 라벨 |
| 금액 강조 | 20px | 700 | `text-xl font-bold` | 합계 금액 표시 |

- **기본 폰트**: `Inter` (Google Fonts) — 숫자·영문 가독성 우수
- **한국어 폰트**: `Noto Sans KR` — 한글 영수증 데이터 표시

```html
<!-- index.html에 추가 -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
```

---

### 8.4 간격 및 레이아웃 시스템 (Spacing & Layout)

| 용도 | 값 | TailwindCSS 클래스 |
|------|----|--------------------|
| 카드 내부 패딩 | 24px | `p-6` |
| 섹션 간 간격 | 32px | `gap-8` |
| 인풋 패딩 | 8px 12px | `py-2 px-3` |
| 버튼 패딩 | 8px 16px | `py-2 px-4` |
| 페이지 최대 너비 | 1280px | `max-w-7xl mx-auto` |
| 사이드바 너비 | 256px | `w-64` |
| 콘텐츠 영역 | 사이드바 제외 | `flex-1` |

---

### 8.5 공통 컴포넌트 스타일

#### 버튼 (Button)
```
[Primary]   bg-indigo-600  text-white  rounded-lg  px-4 py-2  hover:bg-indigo-700
[Secondary] bg-white  text-slate-700  border border-slate-200  rounded-lg  hover:bg-slate-50
[Danger]    bg-red-500  text-white  rounded-lg  px-4 py-2  hover:bg-red-600
[Ghost]     text-indigo-600  hover:bg-indigo-50  rounded-lg  px-4 py-2
```

#### 카드 (Card)
```
bg-white  rounded-xl  border border-slate-200  shadow-sm  p-6
```

#### 인풋 (Input)
```
w-full  border border-slate-200  rounded-lg  px-3 py-2  text-sm
focus:outline-none  focus:ring-2  focus:ring-indigo-500  focus:border-transparent
```

#### 배지 (Badge) — 카테고리 표시용
```
[식료품]  bg-indigo-100  text-indigo-700  text-xs  px-2 py-1  rounded-full
[외식]    bg-amber-100   text-amber-700   text-xs  px-2 py-1  rounded-full
[기타]    bg-slate-100   text-slate-600   text-xs  px-2 py-1  rounded-full
```

#### 테이블 (Table)
```
헤더: bg-slate-50  text-slate-500  text-xs  font-medium  uppercase
행:   border-b border-slate-100  hover:bg-slate-50  text-sm
```

---

### 8.6 화면별 레이아웃 설계

#### 공통 레이아웃
```
┌──────────────────────────────────────────────────┐
│  Navbar  (h-16, bg-white, border-b)              │
├──────────┬───────────────────────────────────────┤
│          │                                       │
│ Sidebar  │  Main Content Area                    │
│  (w-64)  │  (flex-1, bg-slate-50, p-8)          │
│          │                                       │
│  - 대시보드│                                       │
│  - 업로드 │                                       │
│  - 내역  │                                       │
│  - 통계  │                                       │
│          │                                       │
└──────────┴───────────────────────────────────────┘
```

#### 1. 메인 대시보드 (`/`)
```
┌─────────────────────────────────────────────────────┐
│  이번달 총 지출    최다 카테고리   영수증 건수   평균/건  │
│  [SummaryCard x 4 — grid grid-cols-4 gap-4]         │
├────────────────────────┬────────────────────────────┤
│  월별 지출 막대 차트    │  카테고리별 파이 차트       │
│  (MonthlyBarChart)     │  (CategoryPieChart)        │
│  col-span-2            │  col-span-1               │
├────────────────────────┴────────────────────────────┤
│  최근 영수증 목록 (RecentReceiptList — 최근 5건)      │
└─────────────────────────────────────────────────────┘
```

#### 2. 영수증 업로드 (`/upload`)
```
┌─────────────────────────────────────────────────────┐
│  영수증 업로드                                        │
├──────────────────────┬──────────────────────────────┤
│  파일 드롭존          │  분석 결과 미리보기            │
│  (FileDropzone)      │  (AnalysisResult)            │
│                      │                              │
│  ┌──────────────┐   │  날짜: ________              │
│  │  이미지 드래그  │   │  상호명: ________            │
│  │  또는 클릭    │   │  카테고리: [선택]             │
│  └──────────────┘   │  항목 목록:                  │
│                      │  ┌──────┬──┬──────┐         │
│  JPG PNG PDF 지원    │  │ 상품명│수량│금액  │         │
│  최대 10MB           │  └──────┴──┴──────┘         │
│                      │  합계: ₩ 0                  │
│  [파일 선택 버튼]     │  [저장] [취소]               │
└──────────────────────┴──────────────────────────────┘
```

#### 3. 지출 내역 목록 (`/receipts`)
```
┌─────────────────────────────────────────────────────┐
│  [검색창]  [카테고리▼]  [날짜범위]  [초기화]           │
├─────────────────────────────────────────────────────┤
│  날짜  │  상호명  │  카테고리  │  항목수  │  금액  │ 관리 │
│──────────────────────────────────────────────────── │
│  ...   │  ...     │  [배지]   │  ...    │  ₩...  │ 🔍✏️🗑│
│  ...   │  ...     │  [배지]   │  ...    │  ₩...  │ 🔍✏️🗑│
├─────────────────────────────────────────────────────┤
│           [◀ 이전]  1  2  3  [다음 ▶]               │
└─────────────────────────────────────────────────────┘
```

#### 4. 지출 상세/수정 (`/receipts/:id`)
```
┌─────────────────────────────────────────────────────┐
│  ← 목록으로                      [수정] [삭제]       │
├──────────────────────┬──────────────────────────────┤
│  영수증 이미지         │  날짜: [____-__-__]           │
│  (ImageViewer)       │  상호명: [____________]       │
│                      │  카테고리: [선택▼]            │
│  [클릭시 원본 확대]    │                              │
│                      │  항목 목록                    │
│                      │  ┌──────┬──┬──────┬────┐    │
│                      │  │상품명 │수량│단가  │소계│    │
│                      │  ├──────┼──┼──────┼────┤    │
│                      │  │      │  │      │    │[X] │
│                      │  └──────┴──┴──────┴────┘    │
│                      │  [+ 항목 추가]               │
│                      │                              │
│                      │  합계: ₩ 0                  │
│                      │  [저장하기]                   │
└──────────────────────┴──────────────────────────────┘
```

#### 5. 통계 분석 (`/stats`)
```
┌─────────────────────────────────────────────────────┐
│  기간 선택: [시작일] ~ [종료일]  [조회]               │
├────────────────────────┬────────────────────────────┤
│  월별 지출 추이          │  카테고리별 비율            │
│  (MonthlyBarChart)     │  (CategoryPieChart)        │
│                        │  + 범례 목록               │
├────────────────────────┴────────────────────────────┤
│  일별 지출 선 그래프 (DailyLineChart — 전체 너비)      │
├─────────────────────────────────────────────────────┤
│  카테고리별 지출 요약 테이블                           │
│  카테고리 │ 건수 │ 합계 │ 비율(%)                    │
└─────────────────────────────────────────────────────┘
```

---

### 8.7 로딩 및 상태 표시

| 상태 | 컴포넌트 | 스타일 |
|------|----------|--------|
| OCR 분석 중 | `ProgressBar` + 텍스트 | `bg-indigo-600` 애니메이션 바 |
| 데이터 로딩 | `LoadingSpinner` | Indigo 색상 스피너, 화면 중앙 |
| 빈 목록 | Empty State 일러스트 | 영수증 아이콘 + 안내 텍스트 |
| 저장 성공 | Toast (green) | 우측 상단 슬라이드인, 3초 후 사라짐 |
| 오류 발생 | Toast (red) | 오류 메시지 + 닫기 버튼 |
| 삭제 확인 | Modal Dialog | 오버레이 + [취소] [삭제] 버튼 |

---

## 9. 기술 스택 (Tech Stack)

### 9.1 백엔드

| 기술 | 버전 | 역할 |
|------|------|------|
| Python | 3.11+ | 런타임 |
| FastAPI | 0.110+ | REST API 서버, 자동 Swagger 문서 |
| LangChain | 1.2+ | LLM 파이프라인 |
| langchain-upstage | 0.7+ | Upstage Vision LLM OCR |
| SQLite | 내장 | 데이터 저장 |
| SQLAlchemy | 2.0+ | ORM (SQL Injection 방지) |
| python-multipart | - | 파일 업로드 처리 |

### 9.2 프론트엔드

| 기술 | 버전 | 역할 |
|------|------|------|
| ReactJS | 18+ | UI 컴포넌트 |
| Vite | 5+ | 빌드 도구 |
| TailwindCSS | 3+ | 스타일링 |
| Recharts | 2+ | 통계 차트 |
| Axios | 1.6+ | HTTP 클라이언트 |
| React Router | 6+ | 클라이언트 라우팅 |

### 9.3 인프라

| 기술 | 역할 |
|------|------|
| Git | 버전 관리 |
| GitHub | 원격 저장소 |
| Vercel | 프론트엔드 CI/CD 배포 |

---

## 9. 개발 일정 (Milestones)

### 9.1 개발 우선순위 기준 (Priority Definition)

| 등급 | 기호 | 정의 | 미완성 시 영향 |
|------|------|------|---------------|
| Critical | `P0` | 서비스 핵심 기능 — 없으면 제품이 동작하지 않음 | 배포 불가 |
| High | `P1` | 주요 사용자 경험 — 없으면 불편하지만 동작은 가능 | 품질 저하 |
| Medium | `P2` | 완성도 향상 — 있으면 좋지만 v1.1로 이연 가능 | 기능 축소 |
| Low | `P3` | 부가 개선 — v2.0 로드맵으로 이연 가능 | 영향 없음 |

---

### 9.2 기능별 우선순위 목록

| 기능 | 우선순위 | 담당 영역 | 의존성 |
|------|----------|-----------|--------|
| DB 스키마 생성 (receipts, receipt_items) | `P0` | 백엔드 | 없음 |
| FastAPI 서버 기본 구조 | `P0` | 백엔드 | 없음 |
| Upstage OCR 연동 (`ocr_service.py`) | `P0` | 백엔드 | FastAPI 서버 |
| 영수증 업로드 API (`POST /api/receipts/upload`) | `P0` | 백엔드 | OCR 연동 |
| 영수증 CRUD API (GET/PUT/DELETE) | `P0` | 백엔드 | DB 스키마 |
| React 앱 기본 구조 + 라우팅 | `P0` | 프론트엔드 | 없음 |
| 파일 업로드 UI (FileDropzone) | `P0` | 프론트엔드 | React 앱 |
| OCR 분석 결과 표시 (AnalysisResult) | `P0` | 프론트엔드 | 업로드 API |
| 지출 내역 목록 화면 | `P0` | 프론트엔드 | GET API |
| 지출 상세 화면 + 수동 수정 | `P1` | 프론트엔드 | GET/PUT API |
| 통계 API (`GET /api/stats/summary`) | `P1` | 백엔드 | DB CRUD |
| 월별 막대 차트 (MonthlyBarChart) | `P1` | 프론트엔드 | 통계 API |
| 카테고리 파이 차트 (CategoryPieChart) | `P1` | 프론트엔드 | 통계 API |
| 일별 선 그래프 (DailyLineChart) | `P1` | 프론트엔드 | 통계 API |
| 메인 대시보드 (SummaryCard + 차트) | `P1` | 프론트엔드 | 통계 API |
| 검색·필터·페이지네이션 | `P1` | 풀스택 | 목록 API |
| 영수증 이미지 썸네일·원본 뷰어 | `P2` | 프론트엔드 | 업로드 API |
| Toast 알림 / Empty State | `P2` | 프론트엔드 | 없음 |
| 삭제 확인 다이얼로그 | `P2` | 프론트엔드 | DELETE API |
| CORS 설정 및 보안 헤더 | `P2` | 백엔드 | FastAPI 서버 |
| 반응형 모바일 레이아웃 | `P3` | 프론트엔드 | 모든 화면 |
| Vercel 환경변수 설정 및 배포 | `P0` | 인프라 | 프론트엔드 빌드 |

---

### 9.3 주차별 상세 일정

#### 1주차 — 환경 세팅 및 설계 확정

**목표:** 개발 환경 완성 + 설계 문서 확정으로 2주차 개발 즉시 착수 가능

| 일차 | 작업 | 우선순위 | 산출물 |
|------|------|----------|--------|
| Day 1 | Git 저장소 초기화, 브랜치 전략 설정 (`main/develop`) | `P0` | `.gitignore`, `README.md` |
| Day 1 | 프로젝트 디렉토리 구조 생성 (`backend/`, `frontend/`) | `P0` | 폴더 스캐폴딩 |
| Day 2 | Python 가상환경 + FastAPI 기본 앱 실행 확인 | `P0` | `main.py`, `requirements.txt` |
| Day 2 | React + Vite + TailwindCSS 프로젝트 초기화 | `P0` | `package.json`, `vite.config.js` |
| Day 3 | SQLite DB 스키마 설계 확정 및 테이블 생성 | `P0` | `database.py`, `models.py` |
| Day 3 | Pydantic 요청/응답 스키마 정의 | `P0` | `schemas.py` |
| Day 4 | Upstage API Key 발급 및 연결 테스트 | `P0` | `.env` 설정 확인 |
| Day 4 | API 명세 최종 확정 (엔드포인트·파라미터·응답 형식) | `P0` | API 명세서 |
| Day 5 | React Router 설정 + 페이지 컴포넌트 빈 파일 생성 | `P0` | `App.jsx`, `pages/` |
| Day 5 | Axios 인스턴스 설정 + 환경변수 연결 | `P0` | `axiosInstance.js` |

**완료 기준:** `uvicorn main:app` 실행 → Swagger UI 접속, `npm run dev` 실행 → React 앱 접속

---

#### 2주차 — 백엔드 MVP

**목표:** OCR 분석부터 DB 저장까지 전체 백엔드 파이프라인 완성

| 일차 | 작업 | 우선순위 | 산출물 |
|------|------|----------|--------|
| Day 1 | `ocr_service.py` — LangChain + Upstage Vision LLM 연동 | `P0` | OCR 서비스 함수 |
| Day 1 | 영수증 이미지 → JSON 구조화 출력 프롬프트 작성 및 테스트 | `P0` | 프롬프트 템플릿 |
| Day 2 | `POST /api/receipts/upload` — 파일 수신·OCR 처리·DB 저장 | `P0` | `routers/receipts.py` |
| Day 2 | 파일 업로드 MIME 타입 검증 + 10MB 제한 적용 | `P2` | 파일 검증 로직 |
| Day 3 | `GET /api/receipts` — 목록 조회 + 필터·검색·페이지네이션 | `P0` | 목록 API |
| Day 3 | `GET /api/receipts/{id}` — 상세 조회 (items 포함) | `P0` | 상세 API |
| Day 4 | `PUT /api/receipts/{id}` — 영수증 및 항목 수정 | `P0` | 수정 API |
| Day 4 | `DELETE /api/receipts/{id}` — 영수증 + 이미지 파일 삭제 | `P0` | 삭제 API |
| Day 5 | `GET /api/stats/summary` — 월별·카테고리별 집계 | `P1` | `routers/stats.py` |
| Day 5 | `GET /api/categories` — 카테고리 목록 반환 + CORS 설정 | `P1` | `routers/categories.py` |

**완료 기준:** Swagger UI에서 전체 7개 엔드포인트 호출 성공

---

#### 3주차 — 프론트엔드 MVP

**목표:** 영수증 업로드 → 분석 결과 확인 → 목록 조회 핵심 흐름 완성

| 일차 | 작업 | 우선순위 | 산출물 |
|------|------|----------|--------|
| Day 1 | `Navbar` + `Sidebar` 레이아웃 컴포넌트 구현 | `P1` | `layout/` 컴포넌트 |
| Day 1 | `receiptApi.js` — 영수증 API 호출 함수 작성 | `P0` | API 모듈 |
| Day 2 | `FileDropzone.jsx` — 드래그앤드롭 + 파일 선택 UI | `P0` | 업로드 컴포넌트 |
| Day 2 | `UploadPreview.jsx` — 파일 미리보기 + 진행바 | `P0` | 미리보기 컴포넌트 |
| Day 3 | `AnalysisResult.jsx` — OCR 결과 표시 + 저장 버튼 | `P0` | 결과 컴포넌트 |
| Day 3 | `UploadPage.jsx` — 업로드 전체 흐름 조립 | `P0` | 업로드 페이지 |
| Day 4 | `ReceiptTable.jsx` — 영수증 목록 테이블 | `P0` | 목록 컴포넌트 |
| Day 4 | `FilterBar.jsx` — 검색·카테고리·날짜 필터 | `P1` | 필터 컴포넌트 |
| Day 4 | `Pagination.jsx` — 페이지네이션 | `P1` | 페이지네이션 |
| Day 5 | `ReceiptList.jsx` — 목록 페이지 조립 + API 연동 | `P0` | 목록 페이지 |
| Day 5 | `LoadingSpinner.jsx` + Toast 알림 구현 | `P2` | 공통 컴포넌트 |

**완료 기준:** 영수증 업로드 → OCR 분석 → 목록 조회 E2E 흐름 브라우저에서 동작

---

#### 4주차 — 통계 화면 + 전체 연동 + UX 개선

**목표:** 통계 시각화 완성 + 상세/수정 화면 + 전체 화면 품질 개선

| 일차 | 작업 | 우선순위 | 산출물 |
|------|------|----------|--------|
| Day 1 | `statsApi.js` + `categoryApi.js` API 모듈 작성 | `P1` | API 모듈 |
| Day 1 | `MonthlyBarChart.jsx` — Recharts BarChart 구현 | `P1` | 차트 컴포넌트 |
| Day 2 | `CategoryPieChart.jsx` — Recharts PieChart + 범례 | `P1` | 차트 컴포넌트 |
| Day 2 | `DailyLineChart.jsx` — Recharts LineChart 구현 | `P1` | 차트 컴포넌트 |
| Day 3 | `StatsPage.jsx` — DateRangePicker + 차트 조립 | `P1` | 통계 페이지 |
| Day 3 | `SummaryCard.jsx` + `Dashboard.jsx` — 대시보드 조립 | `P1` | 대시보드 |
| Day 4 | `ImageViewer.jsx` — 썸네일 + 모달 원본 뷰어 | `P2` | 이미지 뷰어 |
| Day 4 | `ReceiptForm.jsx` + `ItemEditor.jsx` — 수정 폼 | `P1` | 수정 컴포넌트 |
| Day 4 | `ReceiptDetail.jsx` — 상세/수정 페이지 조립 | `P1` | 상세 페이지 |
| Day 5 | 삭제 확인 Modal + Empty State UI 구현 | `P2` | 공통 컴포넌트 |
| Day 5 | 전체 화면 반응형 점검 + TailwindCSS 스타일 정리 | `P3` | 스타일 개선 |

**완료 기준:** 5개 페이지 전체 기능 브라우저에서 오류 없이 동작

---

#### 5주차 — QA · 버그 수정 · 배포

**목표:** 서비스 품질 검증 및 Vercel 배포 완료

| 일차 | 작업 | 우선순위 | 산출물 |
|------|------|----------|--------|
| Day 1 | OCR 인식 정확도 검증 (샘플 영수증 20건 테스트) | `P0` | 테스트 결과 보고 |
| Day 1 | 파일 포맷별 업로드 테스트 (JPG/PNG/PDF) | `P0` | QA 체크리스트 |
| Day 2 | API 엔드포인트 전수 테스트 (정상·오류 케이스) | `P0` | 테스트 결과 |
| Day 2 | 프론트엔드 E2E 시나리오 테스트 (5개 화면) | `P0` | QA 체크리스트 |
| Day 3 | 발견 버그 수정 + 오류 메시지 UX 개선 | `P0` | 버그 수정 커밋 |
| Day 3 | 보안 점검 (API Key 노출 여부, 파일 검증 확인) | `P0` | 보안 체크리스트 |
| Day 4 | GitHub 저장소 정리 + Vercel 프로젝트 연동 | `P0` | Vercel 배포 URL |
| Day 4 | Vercel 환경변수 설정 (`UPSTAGE_API_KEY` 등) | `P0` | 운영 환경 설정 |
| Day 5 | 배포 후 스모크 테스트 (운영 환경 최종 검증) | `P0` | 배포 완료 확인 |
| Day 5 | `README.md` 작성 (실행 방법, 환경변수 설명) | `P2` | 문서화 완료 |

**완료 기준:** Vercel 배포 URL에서 전체 기능 정상 동작 확인

---

### 9.4 전체 일정 요약

```
Week 1  │░░░░░░░░░░│  환경 세팅 & 설계 확정
Week 2  │██████████│  백엔드 MVP (P0 API 전체)
Week 3  │██████████│  프론트엔드 MVP (핵심 흐름)
Week 4  │████████░░│  통계·상세·UX 개선 (P1~P2)
Week 5  │████████░░│  QA & 배포

█ P0/P1 작업   ░ P2/P3 작업
```

### 9.5 MVP 최소 범위 (일정 지연 시 P2·P3 이연)

> 아래 기능만 완성되면 v1.0 배포 가능

- `P0` 영수증 업로드 → OCR 분석 → DB 저장
- `P0` 지출 내역 목록 조회
- `P0` 영수증 수정 및 삭제
- `P1` 월별·카테고리별 통계 차트
- `P0` Vercel 배포

---

## 10. 리스크 관리 (Risk Management)

| 리스크 | 발생 가능성 | 영향도 | 대응 방안 |
|--------|------------|--------|-----------|
| Upstage API 인식률 저조 | 중 | 높음 | 수동 수정 UI 필수 제공, 프롬프트 튜닝 |
| 이미지 품질 불량 | 높음 | 중 | 업로드 전 해상도/크기 가이드 안내 |
| API 응답 지연 (10초 초과) | 중 | 중 | 타임아웃 설정, 사용자에게 진행 상태 표시 |
| SQLite 동시접속 한계 | 낮음 | 낮음 | v1.0은 단일 사용자 가정, v2에서 PostgreSQL 전환 |

---

## 11. 향후 확장 로드맵 (Future Roadmap)

| 버전 | 기능 |
|------|------|
| v1.1 | AI 카테고리 자동 분류 (LLM 기반 태깅) |
| v1.2 | Excel/CSV 내보내기, 월별 예산 설정 |
| v2.0 | JWT 다중 사용자, PostgreSQL, AI 소비 리포트 |
| v3.0 | 모바일 앱 (PWA), 은행 API 연동 |

---

## 12. 프로젝트 구조 (Project Structure)

```
claude_ocr_2th/                          # 프로젝트 루트
│
├── backend/                             # FastAPI 백엔드
│   ├── main.py                          # FastAPI 앱 진입점, CORS 설정
│   ├── database.py                      # SQLite 연결 및 세션 관리
│   ├── models.py                        # SQLAlchemy ORM 모델 (receipts, receipt_items)
│   ├── schemas.py                       # Pydantic 요청/응답 스키마
│   ├── requirements.txt                 # Python 패키지 의존성
│   │
│   ├── routers/                         # API 라우터 모듈
│   │   ├── receipts.py                  # 영수증 CRUD API (/api/receipts)
│   │   ├── stats.py                     # 통계 조회 API (/api/stats)
│   │   └── categories.py               # 카테고리 목록 API (/api/categories)
│   │
│   ├── services/                        # 비즈니스 로직 레이어
│   │   ├── ocr_service.py              # LangChain + Upstage OCR 연동
│   │   └── stats_service.py            # 통계 집계 로직
│   │
│   ├── uploads/                         # 업로드된 영수증 이미지 저장소
│   │   └── .gitkeep
│   │
│   └── receipts.db                      # SQLite DB 파일 (자동 생성)
│
├── frontend/                            # React 프론트엔드
│   ├── index.html                       # Vite HTML 진입점
│   ├── package.json                     # Node.js 패키지 의존성
│   ├── vite.config.js                   # Vite 빌드 설정
│   ├── tailwind.config.js               # TailwindCSS 설정
│   │
│   ├── public/                          # 정적 파일
│   │   └── favicon.ico
│   │
│   └── src/
│       ├── main.jsx                     # React 앱 진입점
│       ├── App.jsx                      # 라우터 설정 (React Router)
│       │
│       ├── pages/                       # 페이지 컴포넌트 (Route 단위)
│       │   ├── Dashboard.jsx            # 메인 대시보드 (/)
│       │   ├── UploadPage.jsx           # 영수증 업로드 (/upload)
│       │   ├── ReceiptList.jsx          # 지출 내역 목록 (/receipts)
│       │   ├── ReceiptDetail.jsx        # 지출 상세/수정 (/receipts/:id)
│       │   └── StatsPage.jsx           # 통계 분석 (/stats)
│       │
│       ├── components/                  # 재사용 UI 컴포넌트
│       │   ├── layout/
│       │   │   ├── Navbar.jsx           # 상단 네비게이션 바
│       │   │   └── Sidebar.jsx          # 사이드 메뉴
│       │   ├── upload/
│       │   │   ├── FileDropzone.jsx     # 드래그앤드롭 업로드 영역
│       │   │   ├── UploadPreview.jsx    # 파일 미리보기
│       │   │   └── AnalysisResult.jsx   # OCR 분석 결과 표시
│       │   ├── receipt/
│       │   │   ├── ReceiptTable.jsx     # 영수증 목록 테이블
│       │   │   ├── ReceiptForm.jsx      # 영수증 정보 수정 폼
│       │   │   ├── ItemEditor.jsx       # 항목 추가/수정/삭제
│       │   │   └── ImageViewer.jsx      # 원본 이미지 뷰어 (모달)
│       │   ├── charts/
│       │   │   ├── MonthlyBarChart.jsx  # 월별 지출 막대 차트
│       │   │   ├── CategoryPieChart.jsx # 카테고리별 파이 차트
│       │   │   └── DailyLineChart.jsx   # 일별 추이 선 그래프
│       │   └── common/
│       │       ├── FilterBar.jsx        # 검색/필터 바
│       │       ├── Pagination.jsx       # 페이지네이션
│       │       ├── SummaryCard.jsx      # 대시보드 요약 카드
│       │       └── LoadingSpinner.jsx   # 로딩 인디케이터
│       │
│       └── api/                         # Axios API 호출 모듈
│           ├── axiosInstance.js         # Axios 기본 설정 (baseURL, 인터셉터)
│           ├── receiptApi.js            # 영수증 관련 API 함수
│           ├── statsApi.js              # 통계 관련 API 함수
│           └── categoryApi.js           # 카테고리 API 함수
│
├── .env                                 # 환경변수 (UPSTAGE_API_KEY 등) — Git 제외
├── .gitignore                           # Git 제외 파일 목록
└── README.md                            # 프로젝트 설명 및 실행 가이드
```

### 12.1 핵심 파일 역할 요약

| 파일/디렉토리 | 설명 |
|--------------|------|
| `backend/services/ocr_service.py` | LangChain + Upstage Vision LLM 연동 핵심 로직 |
| `backend/routers/receipts.py` | 업로드·조회·수정·삭제 API 엔드포인트 |
| `frontend/src/pages/` | React Router와 매핑되는 화면 단위 컴포넌트 |
| `frontend/src/components/upload/` | 드래그앤드롭·OCR 결과 표시 UI |
| `frontend/src/components/charts/` | Recharts 기반 통계 시각화 컴포넌트 |
| `frontend/src/api/` | 백엔드와 통신하는 Axios API 모듈 |
| `.env` | API Key 등 민감 정보 — 절대 Git에 커밋하지 않음 |

---

*AI 영수증 지출 관리 시스템 PRD v1.0.0 — 2026-04-12*
