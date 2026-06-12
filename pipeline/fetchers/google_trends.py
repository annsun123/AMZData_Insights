from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime

class GoogleTrendsFetcher:
    """Fetch Google Trends search volume data for pet-related terms."""

    def __init__(self):
        self.pytrends = TrendReq(hl="en-US", tz=300)

    def fetch_interest_over_time(self, keywords: list[str],
                                  timeframe: str = "today 12-m") -> pd.DataFrame:
        """Fetch search interest over time for given keywords.
        Returns DataFrame with date index and keyword columns."""
        if len(keywords) > 5:
            raise ValueError("Max 5 keywords per request for Google Trends")

        self.pytrends.build_payload(
            kw_list=keywords,
            timeframe=timeframe,
            geo="US",
            gprop="",
        )
        df = self.pytrends.interest_over_time()
        if df.empty:
            return pd.DataFrame()
        if "isPartial" in df.columns:
            df = df.drop(columns=["isPartial"])
        return df

    def fetch_multi_batch(self, keywords: list[str],
                          timeframe: str = "today 12-m") -> pd.DataFrame:
        """Fetch search interest for any number of keywords by batching in groups of 5."""
        results = []
        for i in range(0, len(keywords), 5):
            batch = keywords[i:i+5]
            df = self.fetch_interest_over_time(batch, timeframe)
            if not df.empty:
                results.append(df)
        if not results:
            return pd.DataFrame()
        return pd.concat(results, axis=1)

    def get_trend_direction(self, keyword: str,
                            timeframe: str = "today 3-m") -> dict:
        """Get simple trend direction for a keyword: rising, falling, or stable."""
        df = self.fetch_interest_over_time([keyword], timeframe)
        if df.empty or len(df) < 4:
            return {"keyword": keyword, "direction": "insufficient_data",
                    "change_pct": 0.0}

        first_half = df.iloc[:len(df)//2][keyword].mean()
        second_half = df.iloc[len(df)//2:][keyword].mean()

        if first_half == 0:
            return {"keyword": keyword, "direction": "rising" if second_half > 0 else "stable",
                    "change_pct": 100.0 if second_half > 0 else 0.0}

        change_pct = ((second_half - first_half) / first_half) * 100

        if change_pct > 15:
            direction = "rising"
        elif change_pct < -15:
            direction = "falling"
        else:
            direction = "stable"

        return {"keyword": keyword, "direction": direction,
                "change_pct": round(change_pct, 1)}
