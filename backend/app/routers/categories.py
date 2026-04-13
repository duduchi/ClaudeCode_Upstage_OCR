from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/categories", tags=["categories"])

CATEGORIES = [
    {"code": "식료품",   "color": "green"},
    {"code": "외식",     "color": "orange"},
    {"code": "쇼핑",     "color": "purple"},
    {"code": "교통",     "color": "blue"},
    {"code": "의료/건강", "color": "red"},
    {"code": "문화/여가", "color": "yellow"},
    {"code": "기타",     "color": "gray"},
]


class CategoryItem(BaseModel):
    code: str
    color: str


@router.get("", response_model=list[CategoryItem])
def list_categories():
    """
    지출 카테고리 목록 반환.

    - 총 7개 카테고리를 반환합니다.
    - `color`는 프론트엔드 배지 색상에 사용됩니다.
    """
    return CATEGORIES
