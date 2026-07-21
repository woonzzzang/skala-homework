from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import plotly.express as px
import seaborn as sns
from matplotlib import pyplot as plt


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parents[1] / "data"
OUTPUT_DIR = BASE_DIR / "output"
ASSET_DIR = BASE_DIR / "assets"

DATASETS = [
    DATA_DIR / "sales_raw.csv",
    DATA_DIR / "events_large.csv",
    DATA_DIR / "telco_churn.csv",
]
SUMMARY_PATH = OUTPUT_DIR / "data_quality_summary.csv"
COLUMN_PROFILE_PATH = OUTPUT_DIR / "column_profile.csv"
REPORT_PATH = OUTPUT_DIR / "advanced_report.md"
MISSING_CHART_PATH = ASSET_DIR / "missing_rate.png"
QUALITY_CHART_PATH = ASSET_DIR / "quality_score.html"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def log_section(title: str) -> None:
    """실행 결과 구분"""
    logger.info("")
    logger.info("=" * 70)
    logger.info(title)
    logger.info("=" * 70)


def iqr_outlier_count(series: pd.Series) -> int:
    """IQR 기준 이상치 후보 수"""
    numeric = pd.to_numeric(series, errors="coerce").dropna()

    if numeric.empty:
        return 0

    q1 = numeric.quantile(0.25)
    q3 = numeric.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    return int((~numeric.between(lower, upper)).sum())


def profile_dataset(path: Path) -> tuple[dict[str, object], list[dict[str, object]]]:
    """데이터셋 단위 품질 요약"""
    df = pd.read_csv(path)
    row_count = len(df)
    cell_count = row_count * len(df.columns)
    missing_count = int(df.isna().sum().sum())
    duplicate_count = int(df.duplicated().sum())
    numeric_cols = list(df.select_dtypes(include="number").columns)
    outlier_count = sum(iqr_outlier_count(df[col]) for col in numeric_cols)

    missing_rate = missing_count / cell_count if cell_count else 0
    duplicate_rate = duplicate_count / row_count if row_count else 0
    outlier_rate = outlier_count / (row_count * len(numeric_cols)) if numeric_cols else 0

    # 품질 점수
    # 결측, 중복, 이상치 후보를 감점 요소로 환산
    quality_score = max(
        0,
        100
        - missing_rate * 100 * 3
        - duplicate_rate * 100 * 2
        - outlier_rate * 100,
    )

    dataset_summary = {
        "dataset": path.name,
        "rows": row_count,
        "columns": len(df.columns),
        "missing_cells": missing_count,
        "missing_rate": round(missing_rate * 100, 3),
        "duplicate_rows": duplicate_count,
        "duplicate_rate": round(duplicate_rate * 100, 3),
        "numeric_columns": len(numeric_cols),
        "iqr_outlier_candidates": outlier_count,
        "iqr_outlier_rate": round(outlier_rate * 100, 3),
        "quality_score": round(quality_score, 2),
    }

    column_profile = []
    for col in df.columns:
        missing = int(df[col].isna().sum())
        unique = int(df[col].nunique(dropna=True))
        outliers = iqr_outlier_count(df[col]) if col in numeric_cols else 0
        column_profile.append(
            {
                "dataset": path.name,
                "column": col,
                "dtype": str(df[col].dtype),
                "missing_count": missing,
                "missing_rate": round(missing / row_count * 100, 3),
                "unique_count": unique,
                "iqr_outlier_candidates": outliers,
            }
        )

    return dataset_summary, column_profile


def create_charts(summary_df: pd.DataFrame) -> None:
    """품질 요약 시각화"""
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    sns.set_theme(style="whitegrid", font="AppleGothic")
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(
        data=summary_df,
        x="dataset",
        y="missing_rate",
        hue="dataset",
        legend=False,
        ax=ax,
    )
    ax.set_title("데이터셋별 결측률")
    ax.set_xlabel("데이터셋")
    ax.set_ylabel("결측률(%)")
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(MISSING_CHART_PATH, dpi=150)
    plt.close(fig)

    fig_quality = px.bar(
        summary_df.sort_values("quality_score", ascending=False),
        x="dataset",
        y="quality_score",
        color="iqr_outlier_rate",
        title="데이터셋별 품질 점수",
        labels={
            "dataset": "데이터셋",
            "quality_score": "품질 점수",
            "iqr_outlier_rate": "IQR 이상치 후보율(%)",
        },
    )
    fig_quality.write_html(QUALITY_CHART_PATH)


def make_markdown_table(df: pd.DataFrame) -> str:
    """간단한 Markdown 표 생성"""
    headers = list(df.columns)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in headers) + " |")

    return "\n".join(lines)


def write_report(summary_df: pd.DataFrame, column_df: pd.DataFrame) -> None:
    """Advanced 실습 리포트 작성"""
    worst_missing = column_df.sort_values("missing_rate", ascending=False).head(10)
    worst_outlier = column_df.sort_values(
        "iqr_outlier_candidates", ascending=False
    ).head(10)

    report = f"""# Advanced - 데이터 품질 감사 리포트

## 수행 목적

Day2 실습에서 다룬 정제, EDA, 시각화, 자동화 흐름을 확장해 공통 데이터 품질 감사 도구를 작성했습니다.

데이터셋별 결측률, 중복 행, 수치형 IQR 이상치 후보, 품질 점수를 자동 산출했습니다.

## 데이터셋 요약

{make_markdown_table(summary_df)}

## 결측률 상위 컬럼

{make_markdown_table(worst_missing)}

## IQR 이상치 후보 상위 컬럼

{make_markdown_table(worst_outlier)}

## 시각화

정적 결측률 차트:

![missing rate](../assets/missing_rate.png)

인터랙티브 품질 점수 차트:

[quality score](../assets/quality_score.html)

## 해석

결측률이 높은 컬럼은 정제 우선순위가 높고, IQR 이상치 후보가 많은 컬럼은 삭제보다 도메인 의미 확인이 먼저 필요합니다.

이번 Advanced 실습은 분석 시작 전 데이터 품질을 빠르게 점검하는 사전 QA 단계로 활용할 수 있습니다.
"""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    summaries = []
    columns = []

    for path in DATASETS:
        dataset_summary, column_profile = profile_dataset(path)
        summaries.append(dataset_summary)
        columns.extend(column_profile)

    summary_df = pd.DataFrame(summaries)
    column_df = pd.DataFrame(columns)

    summary_df.to_csv(SUMMARY_PATH, index=False)
    column_df.to_csv(COLUMN_PROFILE_PATH, index=False)
    create_charts(summary_df)
    write_report(summary_df, column_df)

    log_section("Advanced 데이터 품질 감사")
    logger.info("\n%s", summary_df.to_string(index=False))
    logger.info("요약 저장: %s", SUMMARY_PATH)
    logger.info("컬럼 프로필 저장: %s", COLUMN_PROFILE_PATH)
    logger.info("리포트 저장: %s", REPORT_PATH)

    assert SUMMARY_PATH.exists()
    assert COLUMN_PROFILE_PATH.exists()
    assert REPORT_PATH.exists()
    assert MISSING_CHART_PATH.exists()
    assert QUALITY_CHART_PATH.exists()

    log_section("성공 판정 기준 통과")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
