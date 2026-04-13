from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# 카테고리
# ---------------------------------------------------------------------------

CATEGORY_VALUES = Literal[
    "식료품", "외식", "쇼핑", "교통", "의료/건강", "문화/여가", "기타"
]


# ---------------------------------------------------------------------------
# ReceiptItem 스키마
# ---------------------------------------------------------------------------

class ReceiptItemCreate(BaseModel):
    """영수증 항목 생성 요청."""

    item_name: str = Field(..., description="상품명")
    quantity: int = Field(default=1, ge=1, description="수량")
    unit_price: float = Field(..., ge=0, description="단가")
    total_price: float = Field(..., ge=0, description="소계 (수량 × 단가)")


class ReceiptItemResponse(BaseModel):
    """영수증 항목 응답."""

    id: int
    item_name: str
    quantity: int
    unit_price: float
    total_price: float

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Receipt 스키마
# ---------------------------------------------------------------------------

class ReceiptCreate(BaseModel):
    """영수증 생성 (내부 사용 — OCR 파싱 결과를 DB에 저장할 때)."""

    store_name: str = Field(..., description="상호명")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="구매 날짜 (YYYY-MM-DD)")
    total_amount: float = Field(..., ge=0, description="합계 금액")
    category: CATEGORY_VALUES | None = Field(None, description="지출 카테고리")
    image_path: str | None = Field(None, description="저장된 이미지 경로")
    raw_json: str | None = Field(None, description="LLM 원본 출력 JSON")
    items: list[ReceiptItemCreate] = Field(default_factory=list, description="항목 목록")


class ReceiptUpdate(BaseModel):
    """영수증 수정 요청 (PUT /api/receipts/{id})."""

    store_name: str | None = Field(None, description="상호명")
    date: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="구매 날짜")
    total_amount: float | None = Field(None, ge=0, description="합계 금액")
    category: CATEGORY_VALUES | None = Field(None, description="지출 카테고리")
    items: list[ReceiptItemCreate] | None = Field(None, description="항목 목록 (전체 교체)")


class ReceiptResponse(BaseModel):
    """영수증 기본 응답 (항목 미포함 — 목록 조회용)."""

    id: int
    store_name: str
    date: str
    total_amount: float
    category: str | None
    image_path: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReceiptDetailResponse(ReceiptResponse):
    """영수증 상세 응답 (항목 포함 — GET /api/receipts/{id})."""

    items: list[ReceiptItemResponse] = []


# ---------------------------------------------------------------------------
# 목록 조회 응답 (페이지네이션)
# ---------------------------------------------------------------------------

class ReceiptListResponse(BaseModel):
    """페이지네이션이 포함된 영수증 목록 응답."""

    items: list[ReceiptResponse]
    total: int = Field(..., description="전체 레코드 수")
    page: int = Field(..., description="현재 페이지 (1부터 시작)")
    size: int = Field(..., description="페이지당 항목 수")
    pages: int = Field(..., description="전체 페이지 수")


# ---------------------------------------------------------------------------
# 업로드 응답
# ---------------------------------------------------------------------------

class OcrItemResult(BaseModel):
    """OCR 파싱된 개별 항목."""

    name: str
    quantity: int = 1
    price: float


class UploadResponse(BaseModel):
    """POST /api/receipts/upload 응답."""

    receipt_id: int
    store_name: str
    date: str
    total: float
    category: str | None
    items: list[OcrItemResult]
    message: str = "영수증이 성공적으로 업로드되었습니다."
