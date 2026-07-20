import asyncio

import pandas as pd

from models import Product
from pipeline import INVALID_PRICE_IDS, extract, load, run, transform


def test_category_lowercase():
    valid, invalid = transform(
        [{"id": 1, "name": "A", "category": " FOOD ", "price": 1000}]
    )

    assert len(invalid) == 0
    assert valid[0].category == "food"


def test_negative_price_rejected():
    valid, invalid = transform(
        [{"id": 1, "name": "A", "category": "food", "price": -1000}]
    )

    assert len(valid) == 0
    assert len(invalid) == 1


def test_valid_invalid_counts_match():
    rows = [
        {"id": 1, "name": "A", "category": " FOOD ", "price": 1000},
        {"id": 2, "name": "B", "category": "BOOK", "price": -1000},
        {"id": 3, "name": "C", "category": "toy", "price": 2500},
    ]

    valid, invalid = transform(rows)

    assert len(valid) == 2
    assert len(invalid) == 1
    assert len(valid) + len(invalid) == len(rows)


def test_extract_collects_all_rows():
    ids = list(range(12))
    rows = asyncio.run(extract(ids, max_concurrent=4))

    assert len(rows) == len(ids)


def test_load_csv_and_parquet_round_trip(tmp_path):
    valid = [
        Product(id=1, name="A", category="food", price=1000),
        Product(id=2, name="B", category="book", price=2000),
    ]

    df = load(valid, output_dir=tmp_path)
    back = pd.read_parquet(tmp_path / "products.parquet")

    assert (tmp_path / "products.csv").exists()
    assert (tmp_path / "products.parquet").exists()
    pd.testing.assert_frame_equal(df, back)


def test_run_summary(tmp_path):
    ids = list(range(60))
    summary = asyncio.run(run(ids, output_dir=tmp_path))

    assert summary["total"] == len(ids)
    assert summary["valid"] == len(ids) - len(INVALID_PRICE_IDS)
    assert summary["invalid"] == len(INVALID_PRICE_IDS)
    assert summary["rows_saved"] == summary["valid"]
