"""
OCR 테스트 스크립트 — app.services.ocr_service 사용

실행 방법 (backend/ 디렉토리에서):

  # 특정 이미지 테스트
  python test_ocr.py ../images/02_1_starbucks.jpg

  # images/ 전체 일괄 테스트
  python test_ocr.py --all

  # 첫 번째 샘플 이미지 테스트 (인수 없음)
  python test_ocr.py
"""
import sys
import textwrap
from pathlib import Path

# backend/ 디렉토리를 sys.path에 추가 (app 패키지 임포트를 위해)
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ocr_service import run_ocr  # noqa: E402

IMAGES_DIR = Path(__file__).parent.parent / "images"


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

    raw_text = result.get("_raw_text", "")
    if raw_text:
        print("\n  [OCR 원문 미리보기]")
        for line in textwrap.wrap(raw_text[:300], width=56):
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
# 테스트 실행
# ─────────────────────────────────────────────

def test_single(image_path: Path):
    print(f"\nOCR 테스트: {image_path.name}")
    print_separator()
    try:
        result = run_ocr(str(image_path))
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
    summary: list[tuple[str, bool, str]] = []

    for img in images:
        print(f"\n처리 중: {img.name} ...", end=" ", flush=True)
        try:
            result = run_ocr(str(img))
            print("완료")
            print_result(img.name, result)
            summary.append((img.name, True, ""))
        except Exception as e:
            print(f"실패: {e}")
            summary.append((img.name, False, str(e)[:60]))

    print()
    print_summary(summary)


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--all" in args:
        test_all()
    elif args:
        target = Path(args[0])
        if not target.exists():
            target = IMAGES_DIR / args[0]
        if not target.exists():
            print(f"[ERROR] 파일을 찾을 수 없습니다: {args[0]}")
            sys.exit(1)
        test_single(target)
    else:
        samples = sorted(IMAGES_DIR.glob("*.jpg")) + sorted(IMAGES_DIR.glob("*.png"))
        if not samples:
            print(f"[ERROR] {IMAGES_DIR} 에 이미지가 없습니다.")
            sys.exit(1)
        test_single(samples[0])
