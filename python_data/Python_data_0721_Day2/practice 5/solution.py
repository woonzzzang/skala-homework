from __future__ import annotations

import logging
import timeit
from pathlib import Path

import duckdb
import pandas as pd
import polars as pl


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parents[1] / "data" / "events_large.csv"
OUTPUT_DIR = BASE_DIR / "output"
BENCHMARK_PATH = OUTPUT_DIR / "benchmark.csv"
RESULT_PATH = OUTPUT_DIR / "engine_result.csv"

REPEAT = 3
NUMBER = 1

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def log_section(title: str) -> None:
    """실행 결과 구분"""
    logger.info("")
    logger.info("=" * 70)
    logger.info(title)
    logger.info("=" * 70)


def query_pandas() -> pd.DataFrame:
    """Pandas 기준선 집계"""
    df = pd.read_csv(DATA_PATH)

    # 공통 질의
    # amount > 0 이벤트만 event_type별 집계
    return (
        df.loc[df["amount"] > 0]
        .groupby("event_type", as_index=False)
        .agg(
            cnt=("amount", "count"),
            avg_amount=("amount", "mean"),
            total_amount=("amount", "sum"),
        )
        .sort_values("cnt", ascending=False)
        .reset_index(drop=True)
    )


def query_polars() -> pl.DataFrame:
    """Polars Lazy 집계"""
    return (
        pl.scan_csv(DATA_PATH)
        .filter(pl.col("amount") > 0)
        .group_by("event_type")
        .agg(
            [
                pl.len().alias("cnt"),
                pl.col("amount").mean().alias("avg_amount"),
                pl.col("amount").sum().alias("total_amount"),
            ]
        )
        .sort("cnt", descending=True)
        .collect()
    )


def query_duckdb() -> pd.DataFrame:
    """DuckDB SQL 파일 직접 조회"""
    return duckdb.sql(
        f"""
        SELECT
            event_type,
            COUNT(*) AS cnt,
            AVG(amount) AS avg_amount,
            SUM(amount) AS total_amount
        FROM '{DATA_PATH}'
        WHERE amount > 0
        GROUP BY event_type
        ORDER BY cnt DESC
        """
    ).df()


def normalize_result(df: pd.DataFrame) -> pd.DataFrame:
    """엔진별 결과 비교 전 정렬과 타입 통일"""
    normalized = df.copy()
    normalized["cnt"] = normalized["cnt"].astype("int64")

    return (
        normalized[["event_type", "cnt", "avg_amount", "total_amount"]]
        .sort_values("event_type")
        .reset_index(drop=True)
    )


def verify_results(
    pandas_result: pd.DataFrame,
    polars_result: pl.DataFrame,
    duckdb_result: pd.DataFrame,
) -> pd.DataFrame:
    """세 엔진 결과 일치 검증"""
    a = normalize_result(pandas_result)
    b = normalize_result(polars_result.to_pandas())
    c = normalize_result(duckdb_result)

    pd.testing.assert_frame_equal(a, b, check_dtype=False, atol=1e-6)
    pd.testing.assert_frame_equal(a, c, check_dtype=False, atol=1e-6)

    return a


def benchmark(name: str, func) -> dict[str, float | str]:
    """동일 반복 횟수로 실행 시간 측정"""
    times = timeit.repeat(func, repeat=REPEAT, number=NUMBER)
    times_ms = [round(value * 1000 / NUMBER, 2) for value in times]

    return {
        "engine": name,
        "best_ms": min(times_ms),
        "avg_ms": round(sum(times_ms) / len(times_ms), 2),
        "runs_ms": str(times_ms),
    }


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    log_section("공통 질의")
    logger.info("amount > 0 이벤트만 event_type별 cnt, avg_amount, total_amount 집계")

    pandas_result = query_pandas()
    polars_result = query_polars()
    duckdb_result = query_duckdb()
    verified = verify_results(pandas_result, polars_result, duckdb_result)

    log_section("세 엔진 결과 일치 검증")
    logger.info("assert_frame_equal 통과")
    logger.info("\n%s", verified)
    verified.to_csv(RESULT_PATH, index=False)

    benchmarks = pd.DataFrame(
        [
            benchmark("Pandas", query_pandas),
            benchmark("Polars", query_polars),
            benchmark("DuckDB", query_duckdb),
        ]
    ).sort_values("best_ms")
    pandas_time = benchmarks.loc[benchmarks["engine"] == "Pandas", "best_ms"].iloc[0]
    benchmarks["speedup_vs_pandas"] = (pandas_time / benchmarks["best_ms"]).round(2)

    log_section("벤치마크 결과")
    logger.info("repeat=%s, number=%s", REPEAT, NUMBER)
    logger.info("\n%s", benchmarks.to_string(index=False))

    benchmarks.to_csv(BENCHMARK_PATH, index=False)
    logger.info("벤치마크 저장: %s", BENCHMARK_PATH)

    assert not verified.empty
    assert set(benchmarks["engine"]) == {"Pandas", "Polars", "DuckDB"}

    log_section("성공 판정 기준 통과")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
