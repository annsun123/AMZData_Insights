import keepa
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from pipeline.config import KEEPA_API_KEY, DATA_RAW


class KeepaFetcher:
    """Fetch Amazon product data via Keepa API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or KEEPA_API_KEY
        if not self.api_key:
            raise ValueError("KEEPA_API_KEY not set. Set it in pipeline/.env")
        self.api = keepa.Keepa(self.api_key)

    def fetch_product(self, asin: str, days_back: int = 365) -> pd.DataFrame:
        """Fetch historical data for a single ASIN. Returns DataFrame with
        price, BSR, and timestamp columns."""
        products = self.api.query(
            [asin],
            stats=days_back,
            offers=0,
            history=True,
            rating=True,
        )
        if not products or len(products) == 0:
            return pd.DataFrame(columns=["asin", "price", "bsr", "timestamp"])

        product = products[0]
        history = product.get("data", {})

        rows = []
        if "CSV" in history:
            csv_data = history["CSV"]
            for row in csv_data:
                if row:
                    timestamp = keepa.keepa_time.keepa_minutes_to_datetime(row[0])
                    rows.append({
                        "asin": asin,
                        "timestamp": timestamp,
                        "price": row[-1] if "AMAZON" in str(history.get("csvType")) else None,
                        "bsr": row[-3] if len(row) >= 3 else None,
                    })

        df = pd.DataFrame(rows)
        if df.empty:
            return pd.DataFrame(columns=["asin", "price", "bsr", "timestamp"])

        return df.sort_values("timestamp")

    def fetch_and_save(self, asin: str, output_path: Path) -> pd.DataFrame:
        """Fetch and save raw data to parquet."""
        df = self.fetch_product(asin)
        df.to_parquet(output_path)
        return df

    def fetch_multiple(self, asins: list[str], days_back: int = 365) -> pd.DataFrame:
        """Fetch multiple ASINs, return combined DataFrame."""
        if not asins:
            return pd.DataFrame(columns=["asin", "price", "bsr", "timestamp"])

        frames = []
        for asin in asins:
            df = self.fetch_product(asin, days_back)
            if not df.empty:
                frames.append(df)

        if not frames:
            return pd.DataFrame(columns=["asin", "price", "bsr", "timestamp"])

        return pd.concat(frames, ignore_index=True)
