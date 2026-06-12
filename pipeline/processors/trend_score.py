import pandas as pd
import numpy as np
from typing import Any

class TrendScoreCalculator:
    """Calculate composite TrendScore (0-100) from cross-platform signals.

    Components:
    - BSR Momentum (35%): Is BSR improving or declining?
    - Google Trends Direction (30%): Is search interest rising?
    - Reddit Signal Strength (25%): Are people talking about it?
    - Velocity Adjustment (10%): How fast are things changing?
    """

    def calculate(self, keyword: str, bsr_df: pd.DataFrame,
                  trends_df: pd.DataFrame, reddit_signal: dict[str, Any]) -> dict:
        """Calculate composite TrendScore for a keyword/category."""
        components = {}

        # BSR Momentum (0-100)
        if not bsr_df.empty and "bsr" in bsr_df.columns:
            components["bsr_momentum"] = round(self._bsr_momentum(bsr_df), 1)
        else:
            components["bsr_momentum"] = 0

        # Google Trends direction (0-100)
        if not trends_df.empty:
            components["google_trends"] = round(self._google_trends_signal(trends_df), 1)
        else:
            components["google_trends"] = 0

        # Reddit signal (0-100)
        components["reddit_signal"] = self._reddit_to_score(reddit_signal)

        # Velocity adjustment (0-100)
        components["velocity"] = self._velocity_adjustment(bsr_df, trends_df)

        # Weighted composite
        weights = {"bsr_momentum": 0.35, "google_trends": 0.30,
                    "reddit_signal": 0.25, "velocity": 0.10}

        trend_score = sum(components[k] * weights[k] for k in weights)
        trend_score = round(min(max(trend_score, 0), 100))

        # Data quality
        sources_available = sum(1 for k in weights if components.get(k, 0) > 0)
        if sources_available >= 3:
            data_quality = "good"
        elif sources_available >= 1:
            data_quality = "partial"
        else:
            data_quality = "insufficient"

        return {
            "keyword": keyword,
            "trend_score": trend_score,
            "components": components,
            "data_quality": data_quality,
        }

    def _bsr_momentum(self, df: pd.DataFrame) -> float:
        """Calculate BSR momentum. Lower (improving) BSR = higher score.
        Uses linear regression slope normalized to 0-100 scale."""
        if len(df) < 14:
            return 50.0

        df = df.dropna(subset=["bsr"]).sort_values("timestamp")
        if len(df) < 14:
            return 50.0

        x = np.arange(len(df))
        y = df["bsr"].values
        slope, _ = np.polyfit(x, y, 1)

        # Normalize: a slope of -10/day (fast improvement) -> score 100
        # A slope of +10/day (fast decline) -> score 0
        normalized = 50 - (slope * 5)
        return float(np.clip(normalized, 0, 100))

    def _google_trends_signal(self, df: pd.DataFrame) -> float:
        """Extract trend direction from Google Trends data.
        Compares first half vs second half average."""
        if df.empty or len(df) < 4:
            return 50.0

        col = df.columns[0]  # Use first keyword column
        mid = len(df) // 2
        first_half = df.iloc[:mid][col].mean()
        second_half = df.iloc[mid:][col].mean()

        if first_half == 0:
            return 70.0 if second_half > 0 else 50.0

        change_pct = ((second_half - first_half) / first_half) * 100
        # Map change_pct to 0-100: +50% change -> score 100
        score = 50 + change_pct
        return float(np.clip(score, 0, 100))

    def _reddit_to_score(self, reddit_signal: dict) -> float:
        """Convert Reddit signal dict to 0-100 score."""
        if not reddit_signal:
            return 0

        strength_map = {"strong": 85, "moderate": 55, "weak": 25, "none": 0}
        base = strength_map.get(reddit_signal.get("signal_strength", "none"), 0)

        # Bonus for high engagement
        total_posts = reddit_signal.get("total_posts", 0)
        avg_score = reddit_signal.get("avg_score", 0)

        bonus = min(15, (total_posts / 10) + (avg_score / 100))
        return min(base + bonus, 100)

    def _velocity_adjustment(self, bsr_df: pd.DataFrame,
                              trends_df: pd.DataFrame) -> float:
        """Measure how fast things are changing. Recent acceleration = higher score."""
        if bsr_df.empty or len(bsr_df) < 30:
            return 0.0

        df = bsr_df.dropna(subset=["bsr"]).sort_values("timestamp")
        if len(df) < 30:
            return 0.0

        # Compare last 14 days slope vs last 30 days slope
        recent = df.tail(14)
        earlier = df.head(len(df) - 14)

        if len(recent) < 5 or len(earlier) < 5:
            return 0.0

        x_recent = np.arange(len(recent))
        slope_recent, _ = np.polyfit(x_recent, recent["bsr"].values, 1)
        x_earlier = np.arange(len(earlier))
        slope_earlier, _ = np.polyfit(x_earlier, earlier["bsr"].values, 1)

        # If recent improvement is accelerating vs earlier
        acceleration = slope_earlier - slope_recent  # positive = accelerating improvement
        score = 50 + (acceleration * 10)
        return float(np.clip(score, 0, 100))
