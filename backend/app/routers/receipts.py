from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ReceiptDetailResponse,
    ReceiptListResponse,
    ReceiptUpdate,
    UploadResponse,
)

router = APIRouter(prefix="/api/receipts", tags=["receipts"])


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    영수증 이미지/PDF 업로드 및 OCR 분석.

    - **file**: 영수증 이미지 (JPG/PNG) 또는 PDF (최대 10MB)
    - 업로드된 파일은 `backend/uploads/`에 저장됩니다.
    - Upstage Document Parse + Solar LLM이 자동으로 OCR 분석 후 DB에 저장합니다.
    """
    # 2주차 Day 1~2에서 구현 예정
    raise HTTPException(status_code=501, detail="OCR 서비스 구현 예정 (2주차)")


@router.get("", response_model=ReceiptListResponse)
def list_receipts(
    page: int = Query(default=1, ge=1, description="페이지 번호 (1부터)"),
    size: int = Query(default=20, ge=1, le=100, description="페이지당 항목 수"),
    start_date: str | None = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: str | None = Query(default=None, description="종료 날짜 (YYYY-MM-DD)"),
    category: str | None = Query(default=None, description="카테고리 필터"),
    store_name: str | None = Query(default=None, description="상호명 검색 (부분 일치)"),
    db: Session = Depends(get_db),
):
    """
    영수증 목록 조회 (페이지네이션 + 필터).

    - **page**: 페이지 번호 (기본값 1)
    - **size**: 페이지당 항목 수 (기본값 20, 최대 100)
    - **start_date / end_date**: 날짜 범위 필터
    - **category**: 카테고리 필터 (식료품, 외식, 쇼핑 등)
    - **store_name**: 상호명 부분 검색
    """
    raise HTTPException(status_code=501, detail="목록 API 구현 예정 (2주차)")


@router.get("/{receipt_id}", response_model=ReceiptDetailResponse)
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    """
    영수증 상세 조회 (항목 포함).

    - 응답에 `items` 배열이 포함됩니다.
    """
    raise HTTPException(status_code=501, detail="상세 API 구현 예정 (2주차)")


@router.put("/{receipt_id}", response_model=ReceiptDetailResponse)
def update_receipt(
    receipt_id: int,
    body: ReceiptUpdate,
    db: Session = Depends(get_db),
):
    """
    영수증 수정.

    - 수정할 필드만 포함해서 전송하면 됩니다 (Partial Update).
    - `items` 를 전달하면 기존 항목 전체를 교체합니다.
    """
    raise HTTPException(status_code=501, detail="수정 API 구현 예정 (2주차)")


@router.delete("/{receipt_id}", status_code=204)
def delete_receipt(receipt_id: int, db: Session = Depends(get_db)):
    """
    영수증 삭제.

    - 영수증과 연결된 항목(receipt_items)이 CASCADE 삭제됩니다.
    - 업로드된 이미지 파일도 함께 삭제됩니다.
    """
    raise HTTPException(status_code=501, detail="삭제 API 구현 예정 (2주차)")
