"""
Upstage API 연결 테스트 스크립트 (1주차 Day 4)
실행: python test_connection.py  (backend/ 디렉토리에서)
"""
import os
import sys
import json

from dotenv import load_dotenv

load_dotenv()

UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")

if not UPSTAGE_API_KEY:
    print("[FAIL] UPSTAGE_API_KEY가 .env에 없습니다.")
    sys.exit(1)

print(f"[OK] UPSTAGE_API_KEY 로드 완료: {UPSTAGE_API_KEY[:12]}...")


def test_chat_upstage():
    """ChatUpstage 텍스트 응답 테스트."""
    from langchain_upstage import ChatUpstage
    from langchain_core.messages import HumanMessage

    print("\n[TEST 1] ChatUpstage 텍스트 연결 테스트...")
    chat = ChatUpstage(api_key=UPSTAGE_API_KEY)
    response = chat.invoke([HumanMessage(content="안녕하세요. 한 문장으로 답하세요.")])
    print(f"  응답: {response.content[:80]}...")
    print("  [PASS]")


def test_document_parse():
    """UpstageDocumentParseLoader로 영수증 이미지 OCR 테스트."""
    from pathlib import Path
    from langchain_upstage import ChatUpstage, UpstageDocumentParseLoader
    from langchain_core.messages import HumanMessage

    image_dir = Path(__file__).parent.parent / "images"
    sample_images = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))

    if not sample_images:
        print("\n[SKIP] 샘플 이미지 없음 — OCR 테스트 건너뜀")
        return

    sample = sample_images[0]
    print(f"\n[TEST 2] Document Parse OCR 테스트 ({sample.name})")

    # Step 1: 이미지 -> 텍스트 파싱
    loader = UpstageDocumentParseLoader(
        str(sample),
        api_key=UPSTAGE_API_KEY,
        output_format="text",
        ocr="force",
    )
    docs = loader.load()
    parsed_text = "\n".join(d.page_content for d in docs)
    print(f"  OCR 원문 (앞 200자):\n  {parsed_text[:200]}")
    print("  [PASS] Document Parse 완료")

    # Step 2: 파싱된 텍스트 -> JSON 구조화
    print("\n[TEST 3] LLM 구조화 추출 테스트...")
    prompt = f"""아래는 영수증 OCR 텍스트입니다. 다음 JSON 형식으로만 출력하세요. 마크다운 없이 JSON만 출력하세요.

OCR 텍스트:
{parsed_text[:1000]}

출력 형식:
{{
  "date": "YYYY-MM-DD",
  "store_name": "상호명",
  "items": [{{"name": "상품명", "quantity": 1, "price": 0}}],
  "total": 0,
  "category": "식료품 | 외식 | 쇼핑 | 교통 | 의료/건강 | 문화/여가 | 기타 중 하나"
}}"""

    chat = ChatUpstage(api_key=UPSTAGE_API_KEY)
    response = chat.invoke([HumanMessage(content=prompt)])
    raw = response.content

    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        parsed = json.loads(raw[start:end])
        print(f"  상호명  : {parsed.get('store_name')}")
        print(f"  날짜    : {parsed.get('date')}")
        print(f"  합계    : {parsed.get('total')}")
        print(f"  카테고리: {parsed.get('category')}")
        print(f"  항목 수 : {len(parsed.get('items', []))}")
        print("  [PASS] 구조화 추출 완료")
    except Exception as e:
        print(f"  [WARN] JSON 파싱 실패 ({e}) — 원본: {raw[:200]}")


if __name__ == "__main__":
    try:
        test_chat_upstage()
        test_document_parse()
        print("\n=== 모든 연결 테스트 완료 ===")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
