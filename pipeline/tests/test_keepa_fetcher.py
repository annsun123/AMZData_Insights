import pytest
from pathlib import Path
import pandas as pd
from pipeline.fetchers.keepa_fetcher import KeepaFetcher


@pytest.fixture
def keepa():
    return KeepaFetcher()


def test_fetch_product_data_returns_dataframe(keepa):
    """Fetch a known ASIN and verify we get a DataFrame with expected columns."""
    # A well-known pet product ASIN
    asin = "B00BMYFQ7C"
    df = keepa.fetch_product(asin)

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    expected_cols = {"asin", "price", "bsr", "timestamp"}
    assert expected_cols.issubset(set(df.columns))
    assert (df["asin"] == asin).all()


def test_fetch_product_saves_to_file(keepa, tmp_path):
    """Verify raw data is saved to parquet."""
    asin = "B00BMYFQ7C"
    output_path = tmp_path / "test_output.parquet"

    keepa.fetch_and_save(asin, output_path)

    assert output_path.exists()
    df = pd.read_parquet(output_path)
    assert len(df) > 0


def test_fetch_multiple_asins(keepa):
    """Fetch multiple ASINs and verify deduplication."""
    asins = ["B00BMYFQ7C", "B0009YNTYI"]
    df = keepa.fetch_multiple(asins)

    assert df["asin"].nunique() == len(asins)


def test_empty_asins_returns_empty_dataframe(keepa):
    """Edge case: empty list should return empty DataFrame."""
    df = keepa.fetch_multiple([])
    assert df.empty
