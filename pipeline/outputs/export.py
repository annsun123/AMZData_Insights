import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from pipeline.config import DATA_PROCESSED, DATA_EXPORTS

class DataExporter:
    """Export processed data to web-consumable formats."""

    def __init__(self):
        self.exports_dir = DATA_EXPORTS
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def export_trend_scores(self, scores: list[dict],
                            filename: str = "trend_scores.json") -> Path:
        """Export trend scores list to JSON for web consumption."""
        output_path = self.exports_dir / filename

        payload = {
            "generated_at": datetime.now().isoformat(),
            "scores": scores,
        }

        with open(output_path, "w") as f:
            json.dump(payload, f, indent=2, default=str)

        return output_path

    def export_category_summary(self, summary: dict,
                                filename: str = "category_summary.json") -> Path:
        """Export category-level summary statistics to JSON."""
        output_path = self.exports_dir / filename

        summary["generated_at"] = datetime.now().isoformat()

        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        return output_path

    def save_processed_parquet(self, df: pd.DataFrame,
                                filename: str) -> Path:
        """Save processed DataFrame to parquet."""
        output_path = DATA_PROCESSED / filename
        df.to_parquet(output_path)
        return output_path

    def export_all(self, scores: list[dict],
                   summary: dict, df: pd.DataFrame,
                   prefix: str = "pet_supplies") -> dict[str, Path]:
        """Run all exports and return path mapping."""
        return {
            "scores_json": self.export_trend_scores(scores, f"{prefix}_trend_scores.json"),
            "summary_json": self.export_category_summary(summary, f"{prefix}_summary.json"),
            "processed_parquet": self.save_processed_parquet(df, f"{prefix}_processed.parquet"),
        }
