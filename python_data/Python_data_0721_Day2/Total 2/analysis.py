from __future__ import annotations

import json
import logging
from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import polars as pl
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parents[1] / "data" / "telco_churn.csv"
OUTPUT_DIR = BASE_DIR / "output"
MODEL_PATH = OUTPUT_DIR / "churn_model.joblib"
SUMMARY_PATH = OUTPUT_DIR / "analysis_summary.json"
BOX_CHART_PATH = OUTPUT_DIR / "churn_charges.html"
CONTRACT_CHART_PATH = OUTPUT_DIR / "contract_churn_rate.html"
CORR_CHART_PATH = OUTPUT_DIR / "numeric_correlation.html"

NUM_COLS = [
    "senior",
    "tenure_months",
    "monthly_charges",
    "total_charges",
    "num_services",
]
CAT_COLS = ["gender", "contract", "payment_method"]
TARGET_COL = "churn"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def log_section(title: str) -> None:
    """실행 결과 구분"""
    logger.info("")
    logger.info("=" * 70)
    logger.info(title)
    logger.info("=" * 70)


def load_data(path: Path = DATA_PATH) -> pl.DataFrame:
    """Polars로 Telco Churn 데이터 로딩"""
    return pl.read_csv(path)


def run_eda(df: pl.DataFrame) -> dict[str, object]:
    """Polars EDA 요약"""
    churn_counts = df.group_by(TARGET_COL).len().sort(TARGET_COL)
    churn_group_summary = df.group_by(TARGET_COL).agg(
        [
            pl.col("monthly_charges").mean().alias("mean_monthly_charges"),
            pl.col("tenure_months").mean().alias("mean_tenure_months"),
            pl.col("total_charges").mean().alias("mean_total_charges"),
            pl.len().alias("count"),
        ]
    )

    summary = {
        "shape": df.shape,
        "columns": df.columns,
        "missing": df.null_count().to_dicts()[0],
        "churn_counts": churn_counts.to_dicts(),
        "churn_group_summary": churn_group_summary.to_dicts(),
        "describe": df.describe().to_dicts(),
    }

    log_section("STEP 0. Polars EDA")
    logger.info("shape: %s", summary["shape"])
    logger.info("columns: %s", summary["columns"])
    logger.info("결측치: %s", summary["missing"])
    logger.info("이탈 비율:\n%s", churn_counts)
    logger.info("이탈 그룹별 요약:\n%s", churn_group_summary)

    return summary


def create_plotly_reports(df: pd.DataFrame) -> pd.DataFrame:
    """Plotly HTML 시각화 저장"""
    # 박스플롯
    # 평균만으로 놓치는 분포와 이상치 후보 확인
    box_fig = px.box(
        df,
        x=TARGET_COL,
        y="monthly_charges",
        color=TARGET_COL,
        title="Churn 여부별 월 요금 분포",
        labels={TARGET_COL: "이탈 여부", "monthly_charges": "월 요금"},
    )
    box_fig.write_html(BOX_CHART_PATH)

    contract_summary = (
        df.groupby("contract", observed=True)
        .agg(churn_rate=(TARGET_COL, "mean"), count=(TARGET_COL, "count"))
        .reset_index()
        .sort_values("churn_rate", ascending=False)
    )
    contract_summary["churn_rate_percent"] = (
        contract_summary["churn_rate"] * 100
    ).round(2)

    contract_fig = px.bar(
        contract_summary,
        x="contract",
        y="churn_rate_percent",
        color="count",
        title="계약 유형별 이탈률",
        labels={
            "contract": "계약 유형",
            "churn_rate_percent": "이탈률(%)",
            "count": "고객 수",
        },
    )
    contract_fig.write_html(CONTRACT_CHART_PATH)

    corr = df[NUM_COLS + [TARGET_COL]].corr().round(4)
    corr_fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="수치형 변수 상관관계",
    )
    corr_fig.write_html(CORR_CHART_PATH)

    log_section("STEP 2. Plotly HTML 저장")
    logger.info("월 요금 박스플롯: %s", BOX_CHART_PATH)
    logger.info("계약 유형별 이탈률: %s", CONTRACT_CHART_PATH)
    logger.info("수치형 상관관계: %s", CORR_CHART_PATH)

    return contract_summary


def run_statistics(df: pd.DataFrame) -> dict[str, object]:
    """t-test와 카이제곱 검정"""
    churn_yes = df.loc[df[TARGET_COL] == 1, "monthly_charges"]
    churn_no = df.loc[df[TARGET_COL] == 0, "monthly_charges"]
    t_stat, t_p = stats.ttest_ind(churn_yes, churn_no, equal_var=False)

    table = pd.crosstab(df["contract"], df[TARGET_COL])
    chi2, chi_p, dof, expected = stats.chi2_contingency(table)

    result = {
        "ttest": {
            "target": "monthly_charges",
            "t_statistic": round(float(t_stat), 4),
            "p_value": float(t_p),
            "interpretation": (
                "월 요금과 이탈 여부는 통계적으로 유의한 평균 차이를 보임"
                if t_p < 0.05
                else "월 요금과 이탈 여부의 평균 차이가 유의하다고 보기 어려움"
            ),
        },
        "chi_square": {
            "target": "contract x churn",
            "chi2": round(float(chi2), 4),
            "p_value": float(chi_p),
            "dof": int(dof),
            "interpretation": (
                "계약 유형과 이탈 여부는 통계적으로 유의한 연관을 보임"
                if chi_p < 0.05
                else "계약 유형과 이탈 여부의 연관이 유의하다고 보기 어려움"
            ),
        },
        "contract_table": table.to_dict(),
        "expected": pd.DataFrame(
            expected,
            index=table.index,
            columns=table.columns,
        )
        .round(2)
        .to_dict(),
    }

    log_section("STEP 3. 통계 검정")
    logger.info("t-test p-value: %.2e", t_p)
    logger.info("t-test 해석: %s", result["ttest"]["interpretation"])
    logger.info("chi-square p-value: %.2e", chi_p)
    logger.info("chi-square 해석: %s", result["chi_square"]["interpretation"])
    logger.info("주의: 통계 검정은 연관성 확인이며 인과관계 증명 아님")

    return result


def build_pipeline() -> Pipeline:
    """전처리와 RandomForest를 하나로 묶은 Pipeline"""
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, NUM_COLS),
            ("cat", categorical_pipeline, CAT_COLS),
        ]
    )

    return Pipeline(
        steps=[
            ("prep", preprocessor),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=300,
                    max_depth=5,
                    random_state=42,
                    class_weight="balanced",
                ),
            ),
        ]
    )


def train_model(df: pd.DataFrame) -> dict[str, object]:
    """Pipeline 학습, 평가, 저장"""
    X = df[NUM_COLS + CAT_COLS]
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipe = build_pipeline()
    pipe.fit(X_train, y_train)

    pred = pipe.predict(X_test)
    proba = pipe.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, proba)
    accuracy = accuracy_score(y_test, pred)
    f1 = f1_score(y_test, pred)
    report = classification_report(y_test, pred, output_dict=True)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    reloaded = joblib.load(MODEL_PATH)
    reloaded_auc = roc_auc_score(y_test, reloaded.predict_proba(X_test)[:, 1])

    result = {
        "roc_auc": round(float(auc), 4),
        "accuracy": round(float(accuracy), 4),
        "f1_score": round(float(f1), 4),
        "reloaded_roc_auc": round(float(reloaded_auc), 4),
        "classification_report": report,
        "model_path": str(MODEL_PATH),
    }

    log_section("STEP 7. ML Pipeline 평가")
    logger.info("ROC-AUC: %.4f", auc)
    logger.info("accuracy: %.4f", accuracy)
    logger.info("F1-score: %.4f", f1)
    logger.info("재로딩 후 ROC-AUC: %.4f", reloaded_auc)
    logger.info("모델 저장: %s", MODEL_PATH)

    return result


def save_summary(summary: dict[str, object]) -> None:
    """분석 요약 JSON 저장"""
    with SUMMARY_PATH.open("w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2, default=str)

    logger.info("분석 요약 저장: %s", SUMMARY_PATH)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df_pl = load_data()
    eda_summary = run_eda(df_pl)
    df_pd = df_pl.to_pandas()

    contract_summary = create_plotly_reports(df_pd)
    stat_result = run_statistics(df_pd)
    ml_result = train_model(df_pd)

    summary = {
        "eda": eda_summary,
        "contract_churn_rate": contract_summary.to_dict("records"),
        "statistics": stat_result,
        "ml": ml_result,
    }
    save_summary(summary)

    assert stat_result["ttest"]["p_value"] < 0.05
    assert stat_result["chi_square"]["p_value"] < 0.05
    assert ml_result["roc_auc"] > 0.5
    assert MODEL_PATH.exists()
    assert BOX_CHART_PATH.exists()
    assert CONTRACT_CHART_PATH.exists()
    assert CORR_CHART_PATH.exists()

    log_section("성공 판정 기준 통과")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
