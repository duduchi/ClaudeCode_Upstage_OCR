"""
OCR 테스트 스크립트
실행 방법 (backend/ 디렉토리에서):

  # 특정 이미지 테스트
  python test_ocr.py ../images/02_1_starbucks.jpg

  # images/ 전체 일괄 테스트
  python test_ocr.py --all

  # 첫 번째 샘플 이미지 테스트 (인수 없음)
  python test_ocr.py
"""
import json
import os
import sys
import textwrap
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
IMAGES_DIR = Path(__file__).parent.parent / "images"

PROMPT_TEMPLATE = """아래는 영수증 OCR 텍스트입니다.
다음 JSON 형식으로만 출력하세요. 마크다운 코드블록 없이 JSON만 출력하세요.

OCR 텍스트:
{ocr_text}

출력 형식 (반드시 이 형식 그대로):
{{
  "date": "YYYY-MM-DD",
  "store_name": "상호명",
  "items": [{{"name": "상품명", "quantity": 1, "price": 0}}],
  "total": 0,
  "category": "식료품 | 외식 | 쇼핑 | 교통 | 의료/건강 | 문화/여가 | 기타 중 하나"
}}"""


# ─────────────────────────────────────────────
# 핵심 로직
# ─────────────────────────────────────────────

def ocr_to_text(image_path: str) -> str:
    """Step 1: 이미지 → OCR 텍스트 (Upstage Document Parse)."""
    from langchain_upstage import UpstageDocumentParseLoader

    loader = UpstageDocumentParseLoader(
        image_path,
        api_key=UPSTAGE_API_KEY,
        output_format="text",
        ocr="force",
    )
    docs = loader.load()
    return "\n".join(d.page_content for d in docs)


def text_to_json(ocr_text: str) -> dict:
    """Step 2: OCR 텍스트 → 구조화 JSON (ChatUpstage Solar LLM)."""
    from langchain_core.messages import HumanMessage
    from langchain_upstage import ChatUpstage

    chat = ChatUpstage(api_key=UPSTAGE_API_KEY)
    prompt = PROMPT_TEMPLATE.format(ocr_text=ocr_text[:1500])
    response = chat.invoke([HumanMessage(content=prompt)])
    raw = response.content.strip()

    # JSON 블록만 추출
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"JSON을 찾을 수 없음: {raw[:200]}")
    return json.loads(raw[start:end])


def run_ocr(image_path: Path) -> dict:
    """단일 이미지 전체 파이프라인 실행."""
    ocr_text = ocr_to_text(str(image_path))
    result = text_to_json(ocr_text)
    result["_ocr_text_preview"] = ocr_text[:300]
    return result


# ─────────────────────────────────────────────
# 출력 헬퍼
# ─────────────────────────────────────────────

def print_separator(char="─", width=60):
    print(char * width)


def print_result(image_name: str, result: dict):
    print_separator()
    print(f"  파일      : {image_name}")
    print(f"  상호명    : {result.get('store_name', '-')}")
    print(f"  날짜      : {result.get('date', '-')}")
    print(f"  합계      : {result.get('total', 0):,.0f}원")
    print(f"  카테고리  : {result.get('category', '-')}")

    items = result.get("items", [])
    print(f"  항목 수   : {len(items)}개")
    for item in items[:5]:
        name = item.get("name", "?")
        qty = item.get("quantity", 1)
        price = item.get("price", 0)
        print(f"    - {name} x{qty}  {price:,.0f}원")
    if len(items) > 5:
        print(f"    ... 외 {len(items) - 5}개")

    print("\n  [OCR 원문 미리보기]")
    preview = result.get("_ocr_text_preview", "")
    for line in textwrap.wrap(preview, width=56):
        print(f"  {line}")
    print_separator()


def print_summary(results: list[tuple[str, bool, str]]):
    """results: [(파일명, 성공여부, 오류메시지)]"""
    print_separator("═")
    print(f"  총 {len(results)}개 이미지 테스트 결과")
    print_separator("═")
    passed = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - passed
    for fname, ok, msg in results:
        status = "PASS" if ok else "FAIL"
        suffix = f"  ({msg})" if not ok else ""
        print(f"  [{status}] {fname}{suffix}")
    print_separator("─")
    print(f"  PASS: {passed}  FAIL: {failed}")
    print_separator("═")


# ─────────────────────────────────────────────
# 진입점
# ─────────────────────────────────────────────

def test_single(image_path: Path):
    print(f"\nOCR 테스트: {image_path.name}")
    print_separator()
    try:
        result = run_ocr(image_path)
        print_result(image_path.name, result)
        print(f"\n[PASS] {image_path.name}")
    except Exception as e:
        print(f"[FAIL] {e}")
        sys.exit(1)


def test_all():
    exts = ("*.jpg", "*.jpeg", "*.png", "*.pdf")
    images = []
    for ext in exts:
        images.extend(sorted(IMAGES_DIR.glob(ext)))

    if not images:
        print(f"[SKIP] {IMAGES_DIR} 에 이미지 없음")
        sys.exit(0)

    print(f"\n일괄 OCR 테스트 — {len(images)}개 이미지\n")
    summary = []

    for img in images:
        print(f"\n처리 중: {img.name} ...", end=" ", flush=True)
        try:
            result = run_ocr(img)
            print("완료")
            print_result(img.name, result)
            summary.append((img.name, True, ""))
        except Exception as e:
            print(f"실패: {e}")
            summary.append((img.name, False, str(e)[:60]))

    print()
    print_summary(summary)


if __name__ == "__main__":
    if not UPSTAGE_API_KEY:
        print("[ERROR] UPSTAGE_API_KEY가 .env에 없습니다.")
        sys.exit(1)

    args = sys.argv[1:]

    if "--all" in args:
        test_all()
    elif args:
        target = Path(args[0])
        if not target.exists():
            # images/ 디렉토리 기준으로 재시도
            target = IMAGES_DIR / args[0]
        if not target.exists():
            print(f"[ERROR] 파일을 찾을 수 없습니다: {args[0]}")
            sys.exit(1)
        test_single(target)
    else:
        # 인수 없으면 첫 번째 샘플 이미지 테스트
        samples = sorted(IMAGES_DIR.glob("*.jpg")) + sorted(IMAGES_DIR.glob("*.png"))
        if not samples:
            print(f"[ERROR] {IMAGES_DIR} 에 이미지가 없습니다.")
            sys.exit(1)
        test_single(samples[0])
