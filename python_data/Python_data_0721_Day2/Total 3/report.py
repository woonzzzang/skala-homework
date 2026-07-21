from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import CONFIG, Config


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def load_sales(path: Path) -> pd.DataFrame:
    """리포트용 sales 데이터 로딩"""
    return pd.read_csv(path)


def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    """리포트 집계 전 최소 정제"""
    clean_df = df.copy()

    # 문자열 타입 혼입 방어
    # 변환 실패는 결측으로 만든 뒤 category 중앙값 처리
    clean_df["order_date"] = pd.to_datetime(clean_df["order_date"], errors="coerce")
    clean_df["quantity"] = pd.to_numeric(clean_df["quantity"], errors="coerce")
    clean_df["unit_price"] = pd.to_numeric(clean_df["unit_price"], errors="coerce")
    clean_df["discount"] = pd.to_numeric(clean_df["discount"], errors="coerce")

    clean_df["unit_price"] = clean_df.groupby("category", observed=True)[
        "unit_price"
    ].transform(lambda series: series.fillna(series.median()))
    clean_df["region"] = clean_df["region"].fillna("Unknown")
    clean_df = clean_df.dropna(subset=["order_date", "quantity", "unit_price"])
    clean_df["amount"] = (
        clean_df["quantity"] * clean_df["unit_price"] * (1 - clean_df["discount"])
    )
    clean_df["month"] = clean_df["order_date"].dt.to_period("M").astype(str)

    return clean_df


def aggregate(df: pd.DataFrame, top_n: int = 10) -> dict[str, object]:
    """데이터를 리포트에 넣을 값으로 변환"""
    by_category = (
        df.groupby("category", observed=True)
        .agg(
            amount=("amount", "sum"),
            order_count=("order_id", "count"),
            avg_order_amount=("amount", "mean"),
        )
        .sort_values("amount", ascending=False)
        .head(top_n)
        .round(1)
        .reset_index()
    )
    by_region = (
        df.groupby("region", observed=True)
        .agg(amount=("amount", "sum"), order_count=("order_id", "count"))
        .sort_values("amount", ascending=False)
        .round(1)
        .reset_index()
    )
    monthly = (
        df.groupby("month", observed=True)
        .agg(amount=("amount", "sum"), order_count=("order_id", "count"))
        .sort_index()
        .round(1)
        .reset_index()
    )

    fig = px.bar(
        by_category,
        x="category",
        y="amount",
        color="order_count",
        title="카테고리별 매출 TOP",
        labels={
            "category": "카테고리",
            "amount": "매출",
            "order_count": "주문 수",
        },
    )

    return {
        "kpi": {
            "총매출": int(df["amount"].sum()),
            "주문수": int(len(df)),
            "평균주문액": round(float(df["amount"].mean()), 1),
            "카테고리수": int(df["category"].nunique()),
            "지역수": int(df["region"].nunique()),
        },
        "by_category": by_category.to_dict("records"),
        "by_region": by_region.to_dict("records"),
        "monthly": monthly.to_dict("records"),
        "chart_html": fig.to_html(full_html=False, include_plotlyjs="cdn"),
    }


def render(data: dict[str, object], cfg: Config = CONFIG) -> Path:
    """Jinja2 템플릿 렌더링"""
    env = Environment(
        loader=FileSystemLoader(cfg.template_dir),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template(cfg.template_name)

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = template.render(
        title=cfg.title,
        generated_at=generated_at,
        **data,
    )

    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = cfg.output_dir / f"report_{stamp}.html"
    output_path.write_text(html, encoding="utf-8")

    return output_path


def run_once(cfg: Config = CONFIG) -> Path:
    """한 번 실행해 HTML 리포트 생성"""
    raw_df = load_sales(cfg.data_path)
    clean_df = clean_sales(raw_df)
    data = aggregate(clean_df, cfg.top_n)
    output_path = render(data, cfg)

    logger.info("리포트 생성: %s", output_path)
    return output_path


def main() -> int:
    output_path = run_once()

    assert output_path.exists()
    assert output_path.suffix == ".html"

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
