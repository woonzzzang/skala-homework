from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Config:
    """분석 자동화 설정값"""

    data_path: Path = BASE_DIR.parents[1] / "data" / "sales_raw.csv"
    output_dir: Path = BASE_DIR / "output"
    template_dir: Path = BASE_DIR / "templates"
    template_name: str = "report.html"
    title: str = "일일 매출 자동 리포트"
    top_n: int = 10


CONFIG = Config()
