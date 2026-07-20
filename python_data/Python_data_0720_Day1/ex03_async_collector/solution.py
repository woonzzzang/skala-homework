from __future__ import annotations

import asyncio
import json
import logging
import time
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEAD_LETTER_PATH = BASE_DIR / "dead_letter.json"

USE_REAL_HTTP = False
TOTAL_ITEMS = 60
MAX_CONCURRENT = 10
MAX_RETRIES = 3
REQUEST_TIMEOUT = 3.0
MOCK_DELAY = 0.20
BACKOFF_BASE = 0.05

TRANSIENT_FAILURES = {7, 19, 41}
PERMANENT_FAILURES = {13}

FetchResult = dict[str, object]
DeadLetter = dict[str, object]

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def log_section(title: str) -> None:
    """실행 결과를 구분해서 보기 위한 섹션 로그"""
    logger.info("")
    logger.info("=" * 60)
    logger.info(title)
    logger.info("=" * 60)


def estimate_sync_seconds() -> float:
    """동기 방식으로 60건을 순서대로 기다릴 때의 예상 시간"""
    return TOTAL_ITEMS * MOCK_DELAY


async def request_mock(item_id: int, attempt: int) -> FetchResult:
    """인터넷 없이 실행 가능한 모의 비동기 요청"""
    await asyncio.sleep(MOCK_DELAY)

    if item_id in PERMANENT_FAILURES:
        raise RuntimeError("반복 실패 mock 데이터")

    if item_id in TRANSIENT_FAILURES and attempt == 0:
        raise RuntimeError("일시 실패 mock 데이터")

    return {
        "id": item_id,
        "ok": True,
        "source": "mock",
        "attempt": attempt + 1,
    }


async def request_real_http(item_id: int, client) -> FetchResult:
    """USE_REAL_HTTP=True일 때만 사용하는 실제 HTTP 요청"""
    response = await client.get(f"https://httpbin.org/anything/{item_id}")
    response.raise_for_status()

    return {
        "id": item_id,
        "ok": True,
        "source": "http",
        "status_code": response.status_code,
    }


async def request_item(item_id: int, attempt: int, client=None) -> FetchResult:
    """설정에 따라 실제 HTTP 또는 mock 요청을 실행"""
    if USE_REAL_HTTP:
        return await request_real_http(item_id, client)
    return await request_mock(item_id, attempt)


async def fetch_with_retry(item_id: int, sem: asyncio.Semaphore, client=None) -> FetchResult:
    """타임아웃과 지수 백오프 재시도를 적용한 단일 수집 작업"""
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            async with sem:
                return await asyncio.wait_for(
                    request_item(item_id, attempt, client),
                    timeout=REQUEST_TIMEOUT,
                )
        except (asyncio.TimeoutError, RuntimeError, OSError) as error:
            last_error = error

            if attempt == MAX_RETRIES - 1:
                break

            wait = BACKOFF_BASE * (2 ** attempt)
            await asyncio.sleep(wait)

    raise RuntimeError(
        f"item_id={item_id} 재시도 {MAX_RETRIES}회 실패: {last_error}"
    ) from last_error


def split_results(
    item_ids: list[int],
    results: list[FetchResult | BaseException],
) -> tuple[list[FetchResult], list[DeadLetter]]:
    """성공 결과와 최종 실패 결과를 분리"""
    ok = []
    dead_letter = []

    for item_id, result in zip(item_ids, results):
        if isinstance(result, BaseException):
            dead_letter.append({"id": item_id, "error": str(result)})
        else:
            ok.append(result)

    return ok, dead_letter


async def collect_all(item_ids: list[int]) -> tuple[list[FetchResult], list[DeadLetter]]:
    """60건의 수집 작업을 동시에 예약하고 결과를 모음"""
    sem = asyncio.Semaphore(MAX_CONCURRENT)

    if USE_REAL_HTTP:
        import httpx

        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            tasks = [fetch_with_retry(item_id, sem, client) for item_id in item_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)
    else:
        tasks = [fetch_with_retry(item_id, sem) for item_id in item_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    return split_results(item_ids, results)


def save_dead_letter(dead_letter: list[DeadLetter]) -> None:
    """재시도 후에도 실패한 데이터를 별도 파일로 저장"""
    with DEAD_LETTER_PATH.open("w", encoding="utf-8") as file:
        json.dump(dead_letter, file, ensure_ascii=False, indent=2)


def log_dead_letter(dead_letter: list[DeadLetter]) -> None:
    """최종 실패 데이터를 표 형태로 출력"""
    logger.info("-- dead-letter --")
    logger.info("%-6s%s", "id", "error")

    for item in dead_letter:
        logger.info("%-6s%s", item["id"], item["error"])


async def async_main() -> int:
    item_ids = list(range(TOTAL_ITEMS))

    log_section("비동기 수집 시작")
    logger.info("전체 요청: %s건", TOTAL_ITEMS)
    logger.info("동시 요청 제한: %s개", MAX_CONCURRENT)
    logger.info("실행 모드: %s", "real http" if USE_REAL_HTTP else "mock")

    start = time.perf_counter()
    ok, dead_letter = await collect_all(item_ids)
    elapsed = time.perf_counter() - start

    save_dead_letter(dead_letter)

    log_section("수집 결과")
    logger.info("성공: %s건", len(ok))
    logger.info("실패: %s건", len(dead_letter))
    logger.info("처리 완료: %s건", len(ok) + len(dead_letter))
    logger.info("비동기 처리 시간: %.2f초", elapsed)
    logger.info("동기 예상 대기시간: %.2f초", estimate_sync_seconds())

    if dead_letter:
        log_dead_letter(dead_letter)

    assert len(ok) + len(dead_letter) == TOTAL_ITEMS
    assert len(ok) == TOTAL_ITEMS - len(PERMANENT_FAILURES)
    assert len(dead_letter) == len(PERMANENT_FAILURES)
    assert elapsed < estimate_sync_seconds()

    log_section("성공 판정 기준 통과")
    return 0


def main() -> int:
    return asyncio.run(async_main())


if __name__ == "__main__":
    raise SystemExit(main())
