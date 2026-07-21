from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parents[1] / "data" / "sales_raw.csv"
OUTPUT_DIR = BASE_DIR / "output"
CLEAN_PATH = OUTPUT_DIR / "sales_clean.csv"

# Pandas 3.x는 Copy-on-Write가 항상 활성화
# Pandas 2.x에서는 pd.options.mode.copy_on_write = True 권장

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def log_section(title: str) -> None:
    """실행 결과 구분"""
    logger.info("")
    logger.info("=" * 70)
    logger.info(title)
    logger.info("=" * 70)


def load_raw_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """raw CSV 로딩"""
    return pd.read_csv(path)


def diagnose(df: pd.DataFrame, title: str) -> None:
    """정제 전후 진단 출력"""
    log_section(title)
    logger.info("shape: %s", df.shape)
    logger.info("dtypes:\n%s", df.dtypes)
    logger.info("결측치:\n%s", df.isna().sum())
    logger.info("수치형 요약:\n%s", df.describe(include="all"))
    logger.info("샘플:\n%s", df.head())


def normalize_types(df: pd.DataFrame) -> pd.DataFrame:
    """숫자는 숫자, 날짜는 날짜, 범주는 category"""
    clean_df = df.copy()

    # 타입 변환 우선
    # 변환 실패 값은 NaN 처리 후 결측 처리 단계에서 보정
    clean_df["order_date"] = pd.to_datetime(clean_df["order_date"], errors="coerce")
    clean_df["quantity"] = pd.to_numeric(clean_df["quantity"], errors="coerce")
    clean_df["unit_price"] = pd.to_numeric(clean_df["unit_price"], errors="coerce")
    clean_df["discount"] = pd.to_numeric(clean_df["discount"], errors="coerce")
    clean_df["category"] = clean_df["category"].astype("category")

    return clean_df


def fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    """그룹별 중앙값과 Unknown으로 결측 처리"""
    clean_df = df.copy()

    # 가격 결측은 0이 아님
    # 같은 category 안의 중앙값으로 대치
    clean_df["unit_price"] = clean_df.groupby("category", observed=True)[
        "unit_price"
    ].transform(lambda series: series.fillna(series.median()))

    # region 결측은 임의 지역 추정 근거 부족
    # Unknown 범주로 보존
    clean_df["region"] = clean_df["region"].fillna("Unknown").astype("category")

    # 날짜나 수량은 핵심 계산 컬럼
    # 변환 실패가 생긴 경우만 보수적으로 제거
    clean_df = clean_df.dropna(subset=["order_date", "quantity", "unit_price"])

    return clean_df


def winsorize(
    series: pd.Series, k: float = 1.5, non_negative: bool = False
) -> tuple[pd.Series, dict[str, float]]:
    """IQR 기준 윈저라이징"""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr

    # 가격처럼 음수가 불가능한 컬럼 방어
    if non_negative:
        lower = max(0, lower)

    clipped = series.clip(lower=lower, upper=upper)

    return clipped, {
        "q1": round(float(q1), 2),
        "q3": round(float(q3), 2),
        "iqr": round(float(iqr), 2),
        "lower": round(float(lower), 2),
        "upper": round(float(upper), 2),
        "outlier_count": int((~series.between(lower, upper)).sum()),
        "before_max": round(float(series.max()), 2),
        "after_max": round(float(clipped.max()), 2),
    }


def clean_sales(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    """정제 전체 흐름"""
    clean_df = normalize_types(df)
    missing_after_type = clean_df.isna().sum().to_dict()
    clean_df = fill_missing(clean_df)

    # 극단 가격은 행 삭제 대신 상한/하한으로 제한
    # 멀쩡한 주문 정보 보존 목적
    clean_df["unit_price"], price_rule = winsorize(
        clean_df["unit_price"],
        non_negative=True,
    )

    clean_df["amount"] = (
        clean_df["quantity"] * clean_df["unit_price"] * (1 - clean_df["discount"])
    )

    # CoW와 체인 인덱싱 회피
    # 원본 DataFrame에 .loc로 명시적 수정
    high_value_line = clean_df["amount"].quantile(0.9)
    clean_df.loc[:, "is_high_value"] = clean_df["amount"] >= high_value_line

    summary = {
        "raw_rows": len(df),
        "clean_rows": len(clean_df),
        "missing_after_type": missing_after_type,
        "missing_after_clean": clean_df.isna().sum().to_dict(),
        "price_rule": price_rule,
    }

    return clean_df, summary


def summarize_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """groupby named aggregation"""
    return (
        df.groupby("category", observed=True)
        .agg(
            count=("amount", "count"),
            mean_amount=("amount", "mean"),
            median_price=("unit_price", "median"),
            total_amount=("amount", "sum"),
        )
        .round(2)
        .sort_values("total_amount", ascending=False)
        .reset_index()
    )


def make_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """category x region 매출 피벗"""
    return df.pivot_table(
        index="category",
        columns="region",
        values="amount",
        aggfunc="sum",
        fill_value=0,
        observed=True,
    ).round(2)


def merge_category_info(df: pd.DataFrame) -> pd.DataFrame:
    """키 기준 merge 예시"""
    category_info = pd.DataFrame(
        {
            "category": ["Beauty", "Electronics", "Fashion", "Food", "Home"],
            "category_group": [
                "Lifestyle",
                "Durable",
                "Lifestyle",
                "Daily",
                "Durable",
            ],
        }
    )

    before_rows = len(df)
    merged = df.merge(category_info, on="category", how="left")
    after_rows = len(merged)

    logger.info("merge 전후 행 수: %s -> %s", before_rows, after_rows)
    assert before_rows == after_rows

    return merged


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    raw_df = load_raw_data()
    diagnose(raw_df, "STEP 0. 정제 전 진단")

    clean_df, summary = clean_sales(raw_df)
    diagnose(clean_df, "STEP 1~3. 정제 후 진단")

    log_section("정제 요약")
    logger.info("행 수: %s -> %s", summary["raw_rows"], summary["clean_rows"])
    logger.info("타입 변환 후 결측:\n%s", summary["missing_after_type"])
    logger.info("최종 결측:\n%s", summary["missing_after_clean"])
    logger.info("unit_price IQR 윈저라이징:\n%s", summary["price_rule"])

    category_summary = summarize_by_category(clean_df)
    pivot = make_pivot(clean_df)
    merged = merge_category_info(clean_df)

    log_section("STEP 4. groupby.agg 결과")
    logger.info("\n%s", category_summary)

    log_section("STEP 5. pivot_table 결과")
    logger.info("\n%s", pivot)

    log_section("STEP 6. merge 결과")
    logger.info("\n%s", merged[["order_id", "category", "category_group"]].head())

    clean_df.to_csv(CLEAN_PATH, index=False)
    logger.info("정제 파일 저장: %s", CLEAN_PATH)

    assert clean_df.isna().sum().sum() == 0
    assert (clean_df["unit_price"] >= 0).all()
    assert (clean_df["amount"] >= 0).all()
    assert summary["price_rule"]["after_max"] <= summary["price_rule"]["upper"]
    assert not category_summary.empty
    assert not pivot.empty

    log_section("성공 판정 기준 통과")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
