import json
import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Receipt, ReceiptItem
from app.schemas import (
    ReceiptDetailResponse,
    ReceiptListResponse,
    ReceiptUpdate,
    UploadResponse,
    OcrItemResult,
)
from app.services.ocr_service import run_ocr

router = APIRouter(prefix="/api/receipts", tags=["receipts"])

# uploads/ 디렉토리 — main.py 와 동일한 로직으로 결정
if os.getenv("VERCEL"):
    UPLOAD_DIR = Path("/tmp/uploads")
else:
    UPLOAD_DIR = Path(
        os.getenv(
            "UPLOAD_DIR",
            str(Path(__file__).parent.parent.parent / "uploads"),
        )
    )

# 허용 MIME 타입 및 최대 파일 크기
ALLOWED_MIME = {"image/jpeg", "image/png", "application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ---------------------------------------------------------------------------
# POST /api/receipts/upload
# ---------------------------------------------------------------------------

@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    영수증 이미지/PDF 업로드 및 OCR 분석.

    - **file**: JPG / PNG / PDF (최대 10 MB)
    - Upstage Document Parse → Solar LLM 2단계 파이프라인으로 자동 분석
    - 분석 결과는 즉시 DB에 저장되며 `receipt_id`를 반환합니다.
    """

    # ── 1. MIME 타입 검증 ──────────────────────────────────────────────────
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(
            status_code=415,
            detail=(
                f"지원하지 않는 파일 형식입니다: '{file.content_type}'. "
                "JPG, PNG, PDF만 허용됩니다."
            ),
        )

    # ── 2. 파일 내용 읽기 + 크기 검증 ────────────────────────────────────
    content: bytes = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"파일 크기({len(content) / 1024 / 1024:.1f} MB)가 10 MB를 초과합니다.",
        )

    # ── 3. 파일 디스크 저장 ───────────────────────────────────────────────
    suffix = Path(file.filename or "upload").suffix.lower() or ".jpg"
    unique_name = f"{uuid4().hex}{suffix}"
    file_path = UPLOAD_DIR / unique_name

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    try:
        file_path.write_bytes(content)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"파일 저장에 실패했습니다: {e}")

    # ── 4. OCR 분석 ───────────────────────────────────────────────────────
    try:
        ocr_result = run_ocr(str(file_path))
    except Exception as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=422,
            detail=f"OCR 분석에 실패했습니다: {e}",
        )

    # ── 5. DB 저장 (Receipt + ReceiptItem) ────────────────────────────────
    try:
        receipt = Receipt(
            store_name=ocr_result["store_name"],
            date=ocr_result["date"],
            total_amount=ocr_result["total"],
            category=ocr_result["category"],
            image_path=f"/uploads/{unique_name}",   # 프론트엔드 URL 경로
            raw_json=json.dumps(ocr_result, ensure_ascii=False),
        )
        db.add(receipt)
        db.flush()  # receipt.id 확보

        for item in ocr_result.get("items", []):
            qty = int(item.get("quantity", 1))
            unit_price = float(item.get("price", 0))
            db.add(ReceiptItem(
                receipt_id=receipt.id,
                item_name=item["name"],
                quantity=qty,
                unit_price=unit_price,
                total_price=unit_price * qty,
            ))

        db.commit()
        db.refresh(receipt)

    except Exception as e:
        db.rollback()
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"DB 저장에 실패했습니다: {e}")

    # ── 6. 응답 ───────────────────────────────────────────────────────────
    return UploadResponse(
        receipt_id=receipt.id,
        store_name=receipt.store_name,
        date=receipt.date,
        total=receipt.total_amount,
        category=receipt.category,
        items=[
            OcrItemResult(
                name=it["name"],
                quantity=int(it.get("quantity", 1)),
                price=float(it.get("price", 0)),
            )
            for it in ocr_result.get("items", [])
        ],
    )


# ---------------------------------------------------------------------------
# GET /api/receipts
# ---------------------------------------------------------------------------

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
    raise HTTPException(status_code=501, detail="목록 API 구현 예정 (2주차 Day3)")


# ---------------------------------------------------------------------------
# GET /api/receipts/{receipt_id}
# ---------------------------------------------------------------------------

@router.get("/{receipt_id}", response_model=ReceiptDetailResponse)
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    """
    영수증 상세 조회 (항목 포함).

    - 응답에 `items` 배열이 포함됩니다.
    """
    raise HTTPException(status_code=501, detail="상세 API 구현 예정 (2주차 Day3)")


# ---------------------------------------------------------------------------
# PUT /api/receipts/{receipt_id}
# ---------------------------------------------------------------------------

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
    raise HTTPException(status_code=501, detail="수정 API 구현 예정 (2주차 Day4)")


# ---------------------------------------------------------------------------
# DELETE /api/receipts/{receipt_id}
# ---------------------------------------------------------------------------

@router.delete("/{receipt_id}", status_code=204)
def delete_receipt(receipt_id: int, db: Session = Depends(get_db)):
    """
    영수증 삭제.

    - 영수증과 연결된 항목(receipt_items)이 CASCADE 삭제됩니다.
    - 업로드된 이미지 파일도 함께 삭제됩니다.
    """
    raise HTTPException(status_code=501, detail="삭제 API 구현 예정 (2주차 Day4)")
