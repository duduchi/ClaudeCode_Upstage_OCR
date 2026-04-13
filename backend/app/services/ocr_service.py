"""
ocr_service.py — Upstage Vision LLM 기반 영수증 OCR 서비스

파이프라인:
    이미지/PDF 파일
        → UpstageDocumentParseLoader  (Step 1: OCR 텍스트 추출)
        → ChatUpstage / Solar LLM     (Step 2: JSON 구조화)
        → dict                        (date, store_name, items, total, category)
"""
import json
import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

UPSTAGE_API_KEY: str = os.getenv("UPSTAGE_API_KEY", "")

VALID_CATEGORIES = ["식료품", "외식", "쇼핑", "교통", "의료/건강", "문화/여가", "기타"]

# ---------------------------------------------------------------------------
# 프롬프트 템플릿
# ---------------------------------------------------------------------------
PROMPT_TEMPLATE = """\
아래는 영수증 OCR 텍스트입니다.
다음 JSON 형식으로만 출력하세요. 마크다운 코드블록 없이 순수 JSON만 출력하세요.

[OCR 텍스트]
{ocr_text}

[출력 형식 — 반드시 이 구조 그대로]
{{
  "date": "YYYY-MM-DD",
  "store_name": "상호명",
  "items": [
    {{"name": "상품명", "quantity": 1, "price": 0}}
  ],
  "total": 0,
  "category": "식료품 | 외식 | 쇼핑 | 교통 | 의료/건강 | 문화/여가 | 기타 중 하나"
}}

[규칙]
- date: YYYY-MM-DD 형식. 날짜를 인식할 수 없으면 오늘({today}) 사용.
- store_name: 영수증 상단의 상호명 또는 브랜드명.
- items[].name: 개별 상품·메뉴 이름.
- items[].quantity: 수량 (정수, 기본 1).
- items[].price: 해당 항목의 단가 (숫자만, 원 기호 제외).
- total: 최종 합계 금액 (숫자만).
- category: 위 7개 중 가장 적합한 하나만 선택.
"""


# ---------------------------------------------------------------------------
# 내부 함수
# ---------------------------------------------------------------------------

def _ocr_to_text(file_path: str) -> str:
    """Step 1: 이미지/PDF → OCR 텍스트 (Upstage Document Parse API)."""
    from langchain_upstage import UpstageDocumentParseLoader

    loader = UpstageDocumentParseLoader(
        file_path,
        api_key=UPSTAGE_API_KEY,
        output_format="text",
        ocr="force",
    )
    docs = loader.load()
    return "\n".join(d.page_content for d in docs)


def _text_to_json(ocr_text: str) -> dict:
    """Step 2: OCR 텍스트 → 구조화 JSON (ChatUpstage Solar LLM)."""
    from langchain_core.messages import HumanMessage
    from langchain_upstage import ChatUpstage

    chat = ChatUpstage(api_key=UPSTAGE_API_KEY)
    prompt = PROMPT_TEMPLATE.format(
        ocr_text=ocr_text[:2000],  # 토큰 절약을 위해 앞부분만 사용
        today=date.today().isoformat(),
    )
    response = chat.invoke([HumanMessage(content=prompt)])
    raw: str = response.content.strip()

    # 마크다운 코드블록이 포함되었을 경우 JSON 부분만 추출
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"LLM 응답에서 JSON을 추출할 수 없음: {raw[:300]}")

    parsed: dict = json.loads(raw[start:end])

    # 카테고리 정규화: 유효하지 않은 값이면 "기타"로 대체
    if parsed.get("category") not in VALID_CATEGORIES:
        parsed["category"] = "기타"

    return parsed


def _normalize_result(raw: dict) -> dict:
    """
    LLM 출력 dict를 DB 저장에 맞는 형태로 정규화.

    - items[].price → float 보장
    - total → float 보장
    - items 없으면 [] 기본값
    """
    items = []
    for item in raw.get("items", []):
        items.append({
            "name": str(item.get("name", "")),
            "quantity": int(item.get("quantity", 1)),
            "price": float(item.get("price", 0)),
        })

    return {
        "date": str(raw.get("date", date.today().isoformat())),
        "store_name": str(raw.get("store_name", "알 수 없는 상점")),
        "items": items,
        "total": float(raw.get("total", 0)),
        "category": raw.get("category", "기타"),
    }


# ---------------------------------------------------------------------------
# 공개 API
# ---------------------------------------------------------------------------

def run_ocr(file_path: str) -> dict:
    """
    영수증 파일 전체 OCR 파이프라인 실행.

    Args:
        file_path: 영수증 이미지(JPG/PNG) 또는 PDF의 절대·상대 경로.

    Returns:
        {
            "date":       "YYYY-MM-DD",
            "store_name": str,
            "items":      [{"name": str, "quantity": int, "price": float}],
            "total":      float,
            "category":   str,   # VALID_CATEGORIES 중 하나
            "_raw_text":  str,   # OCR 원본 텍스트 (raw_json 저장용)
        }

    Raises:
        EnvironmentError: UPSTAGE_API_KEY 미설정
        FileNotFoundError: 파일 경로 오류
        ValueError: OCR 결과 없음 또는 JSON 파싱 오류
        Exception: Upstage API 호출 실패
    """
    if not UPSTAGE_API_KEY:
        raise EnvironmentError("UPSTAGE_API_KEY가 환경변수에 설정되지 않았습니다.")

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

    # Step 1: OCR
    raw_text = _ocr_to_text(str(path))
    if not raw_text.strip():
        raise ValueError("OCR 결과가 비어 있습니다. 이미지 품질을 확인하세요.")

    # Step 2: JSON 구조화
    parsed = _text_to_json(raw_text)

    # Step 3: 정규화
    result = _normalize_result(parsed)
    result["_raw_text"] = raw_text

    return result
