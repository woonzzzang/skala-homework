from __future__ import annotations

import asyncio
import json
import logging
import time
from pathlib import Path

import pandas as pd
from pydantic import ValidationError

from models import Product


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

TOTAL_ITEMS = 60
MAX_CONCURRENT = 10
MAX_RETRIES = 3
REQUEST_TIMEOUT = 3.0
MOCK_DELAY = 0.05
BACKOFF_BASE = 0.02

TRANSIENT_FAILURES = {7, 19, 41}
INVALID_PRICE_IDS = {6, 18, 33, 47}
CATEGORIES = [" FOOD ", "Book", "ELECTRONICS", "toy"]

RawProduct = dict[str, object]
InvalidRecord = dict[str, object]
Summary = dict[str, int | float | str]

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def log_section(title: str) -> None:
    """실행 결과를 보기 좋게 나누는 로그"""
    logger.info("")
    logger.info("=" * 60)
    logger.info(title)
    logger.info("=" * 60)


def make_mock_product(item_id: int) -> RawProduct:
    """외부 API 응답을 대신하는 mock 상품 데이터 생성"""
    price = round(1000 + item_id * 125.5, 2)

    if item_id in INVALID_PRICE_IDS:
        price = -price

    return {
        "id": item_id + 1,
        "name": f"product-{item_id + 1}",
        "category": CATEGORIES[item_id % len(CATEGORIES)],
        "price": price,
    }


async def fetch_product(item_id: int, attempt: int) -> RawProduct:
    """네트워크 요청을 흉내 내는 비동기 수집 함수"""
    await asyncio.sleep(MOCK_DELAY)

    if item_id in TRANSIENT_FAILURES and attempt == 0:
        raise RuntimeError("일시 실패 mock 데이터")

    return make_mock_product(item_id)


async def fetch_with_retry(item_id: int, sem: asyncio.Semaphore) -> RawProduct:
    """동시성 제한, 타임아웃, 지수 백오프 재시도 적용"""
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            async with sem:
                return await asyncio.wait_for(
                    fetch_product(item_id, attempt),
                    timeout=REQUEST_TIMEOUT,
                )
        except (asyncio.TimeoutError, RuntimeError, OSError) as error:
            last_error = error

            if attempt == MAX_RETRIES - 1:
                break

            wait = BACKOFF_BASE * (2**attempt)
            await asyncio.sleep(wait)

    raise RuntimeError(
        f"item_id={item_id} 재시도 {MAX_RETRIES}회 실패: {last_error}"
    ) from last_error


async def extract(
    ids: list[int], max_concurrent: int = MAX_CONCURRENT
) -> list[RawProduct]:
    """여러 상품 데이터를 비동기로 수집"""
    sem = asyncio.Semaphore(max_concurrent)
    tasks = [fetch_with_retry(item_id, sem) for item_id in ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return [result for result in results if not isinstance(result, BaseException)]


def serialize_errors(error: ValidationError) -> list[dict[str, object]]:
    """ValidationError를 JSON 저장 가능한 형태로 변환"""
    serialized = []

    for item in error.errors():
        clean_item = item.copy()
        if "ctx" in clean_item:
            clean_item["ctx"] = {
                key: str(value) for key, value in clean_item["ctx"].items()
            }
        serialized.append(clean_item)

    return serialized


def transform(raw: list[RawProduct]) -> tuple[list[Product], list[InvalidRecord]]:
    """Pydantic 검증으로 유효/무효 상품 데이터 분리"""
    valid = []
    invalid = []

    for row in raw:
        try:
            valid.append(Product.model_validate(row))
        except ValidationError as error:
            invalid.append(
                {
                    "data": row,
                    "errors": serialize_errors(error),
                }
            )

    return valid, invalid


def load(valid: list[Product], output_dir: str | Path = OUTPUT_DIR) -> pd.DataFrame:
    """유효 데이터를 DataFrame으로 만들고 CSV와 Parquet로 저장"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    records = [product.model_dump() for product in valid]
    df = pd.DataFrame(records, columns=["id", "name", "category", "price"])

    df.to_csv(output_path / "products.csv", index=False)
    df.to_parquet(output_path / "products.parquet", index=False)

    return df


def save_invalid(
    invalid: list[InvalidRecord], output_dir: str | Path = OUTPUT_DIR
) -> None:
    """무효 데이터를 별도 리포트로 저장"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with (output_path / "invalid_records.json").open("w", encoding="utf-8") as file:
        json.dump(invalid, file, ensure_ascii=False, indent=2)


async def run(
    ids: list[int],
    output_dir: str | Path = OUTPUT_DIR,
    max_concurrent: int = MAX_CONCURRENT,
) -> Summary:
    """Extract, Transform, Load 단계를 순서대로 조율"""
    start = time.perf_counter()

    raw = await extract(ids, max_concurrent=max_concurrent)
    valid, invalid = transform(raw)
    df = load(valid, output_dir=output_dir)
    save_invalid(invalid, output_dir=output_dir)

    elapsed = time.perf_counter() - start

    return {
        "total": len(raw),
        "valid": len(valid),
        "invalid": len(invalid),
        "rows_saved": len(df),
        "elapsed_seconds": round(elapsed, 2),
        "output_dir": str(Path(output_dir)),
    }


def log_summary(summary: Summary) -> None:
    """파이프라인 실행 요약 출력"""
    log_section("비동기 ETL 파이프라인 결과")
    logger.info("요약 딕셔너리: %s", summary)
    logger.info("전체 수집: %s건", summary["total"])
    logger.info("유효 데이터: %s건", summary["valid"])
    logger.info("무효 데이터: %s건", summary["invalid"])
    logger.info("저장 행 수: %s건", summary["rows_saved"])
    logger.info("처리 시간: %s초", summary["elapsed_seconds"])
    logger.info("출력 폴더: %s", summary["output_dir"])


def main() -> int:
    summary = asyncio.run(run(list(range(TOTAL_ITEMS))))

    assert summary["total"] == TOTAL_ITEMS
    assert summary["valid"] == TOTAL_ITEMS - len(INVALID_PRICE_IDS)
    assert summary["invalid"] == len(INVALID_PRICE_IDS)
    assert summary["rows_saved"] == summary["valid"]

    log_summary(summary)
    log_section("성공 판정 기준 통과")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
