import json
import pandas as pd
from pipeline.outputs.export import DataExporter

def test_export_trend_scores(tmp_path):
    exporter = DataExporter()
    exporter.exports_dir = tmp_path

    scores = [
        {"keyword": "dog treats", "trend_score": 78, "components": {}, "data_quality": "good"},
        {"keyword": "cat litter", "trend_score": 45, "components": {}, "data_quality": "partial"},
    ]

    path = exporter.export_trend_scores(scores, "test_scores.json")
    assert path.exists()

    with open(path) as f:
        data = json.load(f)

    assert len(data["scores"]) == 2
    assert data["scores"][0]["keyword"] == "dog treats"
    assert "generated_at" in data

def test_save_processed_parquet(tmp_path):
    from pipeline.config import DATA_PROCESSED
    exporter = DataExporter()
    exporter.exports_dir = tmp_path

    df = pd.DataFrame({"asin": ["X", "Y"], "bsr": [100, 200]})
    path = exporter.save_processed_parquet(df, "test.parquet")

    assert path.exists()
    loaded = pd.read_parquet(path)
    assert len(loaded) == 2
