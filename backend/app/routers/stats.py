from typing import Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(prefix="/api/stats", tags=["stats"])


class CategoryStat(BaseModel):
    category: str
    total: float
    count: int


class DailyStat(BaseModel):
    date: str
    total: float
    count: int


class StatsSummaryResponse(BaseModel):
    period: str
    start_date: str
    end_date: str
    grand_total: float
    receipt_count: int
    by_category: list[CategoryStat]
    by_date: list[DailyStat]


@router.get("/summary", response_model=StatsSummaryResponse)
def get_stats_summary(
    period: Literal["day", "month", "year"] = Query(
        default="month", description="집계 단위 (day/month/year)"
    ),
    start_date: str | None = Query(default=None, description="시작 날짜 (YYYY-MM-DD)"),
    end_date: str | None = Query(default=None, description="종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """
    지출 통계 집계.

    - **period**: 집계 단위 — `day`(일별) / `month`(월별) / `year`(연별)
    - **start_date / end_date**: 조회 기간 (미입력 시 최근 1개월)
    - 응답에 카테고리별·날짜별 집계가 포함됩니다.
    """
    from fastapi import HTTPException
    raise HTTPException(status_code=501, detail="통계 API 구현 예정 (2주차)")
