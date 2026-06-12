import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pipeline.processors.trend_score import TrendScoreCalculator


@pytest.fixture
def calculator():
    return TrendScoreCalculator()


@pytest.fixture
def sample_bsr_data():
    """Simulated BSR data: improving (decreasing) rank over 90 days."""
    dates = pd.date_range(end=datetime.now(), periods=90, freq="D")
    bsr = list(range(5000, 4100, -10))  # BSR improving: 5000 → 4100
    return pd.DataFrame({"timestamp": dates, "bsr": bsr})


@pytest.fixture
def sample_trends_data():
    """Simulated Google Trends data: rising interest."""
    dates = pd.date_range(end=datetime.now(), periods=52, freq="W")
    # Generate values matching actual date count (may be 51 or 52)
    n = len(dates)
    values = [20 + i * 0.5 for i in range(n)]
    df = pd.DataFrame({"dog_treats": values}, index=dates)
    return df


def test_bsr_momentum_improving(calculator, sample_bsr_data):
    """BSR that improves (goes down) should have positive momentum score."""
    score = calculator._bsr_momentum(sample_bsr_data)
    assert score > 50  # improving BSR = high score
    assert score <= 100


def test_bsr_momentum_declining(calculator):
    """BSR that gets worse (goes up) should have low momentum score."""
    dates = pd.date_range(end=datetime.now(), periods=90, freq="D")
    bsr = list(range(1000, 1900, 10))  # BSR worsening: 1000 → 1900
    df = pd.DataFrame({"timestamp": dates, "bsr": bsr})
    score = calculator._bsr_momentum(df)
    assert score < 50


def test_google_trends_direction(calculator, sample_trends_data):
    """Rising Google Trends should produce positive direction score."""
    direction = calculator._google_trends_signal(sample_trends_data)
    assert direction > 50


def test_calculate_complete_score(calculator, sample_bsr_data, sample_trends_data):
    """Full TrendScore calculation returns dict with all components."""
    reddit_signal = {"signal_strength": "moderate", "total_posts": 35, "avg_score": 120.0}

    result = calculator.calculate(
        keyword="dog treats",
        bsr_df=sample_bsr_data,
        trends_df=sample_trends_data,
        reddit_signal=reddit_signal,
    )

    assert isinstance(result, dict)
    assert "trend_score" in result
    assert "components" in result
    assert 0 <= result["trend_score"] <= 100
    assert "bsr_momentum" in result["components"]
    assert "google_trends" in result["components"]
    assert "reddit_signal" in result["components"]


def test_calculate_missing_data_returns_partial(calculator):
    """When some data sources are missing, return partial score with flag."""
    result = calculator.calculate(
        keyword="unknown product",
        bsr_df=pd.DataFrame(),
        trends_df=pd.DataFrame(),
        reddit_signal={"signal_strength": "none"},
    )
    assert result["trend_score"] < 10  # near-zero: only velocity default contributes (50*0.10=5)
    assert result["data_quality"] == "insufficient"
