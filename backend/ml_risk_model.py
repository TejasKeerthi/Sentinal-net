"""
Risk scoring model for Sentinel-Net.
Trains a regression model from CSV data and predicts failure risk scores.
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional

try:
    import numpy as np
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error
    from sklearn.model_selection import train_test_split

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class RiskScoreModel:
    """Train and serve an ML model for failure risk scoring."""

    feature_names = ["commits_30d", "contributors_30d", "open_issues"]

    def __init__(self, dataset_path: Optional[Path] = None):
        self.dataset_path = dataset_path or (Path(__file__).resolve().parent / "data" / "risk_training_data.csv")
        self.model = None
        self.training_status: Dict[str, object] = {
            "enabled": False,
            "trained": False,
            "reason": "Model not initialized",
        }
        self._train()

    def _load_rows(self) -> List[Dict[str, int]]:
        rows: List[Dict[str, int]] = []
        with self.dataset_path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                rows.append(
                    {
                        "commits_30d": int(row["commits_30d"]),
                        "contributors_30d": int(row["contributors_30d"]),
                        "open_issues": int(row["open_issues"]),
                        "risk_score": int(row["risk_score"]),
                    }
                )
        return rows

    def _train(self) -> None:
        if not SKLEARN_AVAILABLE:
            self.training_status = {
                "enabled": False,
                "trained": False,
                "reason": "scikit-learn not installed",
            }
            return

        if not self.dataset_path.exists():
            self.training_status = {
                "enabled": False,
                "trained": False,
                "reason": f"Dataset not found at {self.dataset_path}",
            }
            return

        rows = self._load_rows()
        if len(rows) < 10:
            self.training_status = {
                "enabled": False,
                "trained": False,
                "reason": "Dataset has too few samples",
            }
            return

        x = np.array([[r["commits_30d"], r["contributors_30d"], r["open_issues"]] for r in rows], dtype=float)
        y = np.array([r["risk_score"] for r in rows], dtype=float)

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

        model = RandomForestRegressor(
            n_estimators=250,
            max_depth=10,
            min_samples_leaf=2,
            random_state=42,
        )
        model.fit(x_train, y_train)

        preds = model.predict(x_test)
        mae = float(mean_absolute_error(y_test, preds))

        self.model = model
        self.training_status = {
            "enabled": True,
            "trained": True,
            "samples": len(rows),
            "features": self.feature_names,
            "model": "RandomForestRegressor",
            "mae": round(mae, 2),
        }

    def predict_risk_score(self, commits_30d: int, contributors_30d: int, open_issues: int) -> int:
        if self.model is None:
            return self._fallback_risk_score(commits_30d, contributors_30d, open_issues)

        values = np.array([[commits_30d, contributors_30d, open_issues]], dtype=float)
        predicted = float(self.model.predict(values)[0])
        return int(max(0, min(100, round(predicted))))

    def _fallback_risk_score(self, commits: int, contributors: int, issues: int) -> int:
        score = 50
        score += min(issues // 5, 20)

        if commits == 0:
            score += 25
        elif commits < 5:
            score += 15

        if contributors > 20:
            score += 10

        return max(0, min(100, score))

    def get_status(self) -> Dict[str, object]:
        return dict(self.training_status)


_MODEL_INSTANCE: Optional[RiskScoreModel] = None


def get_risk_model() -> RiskScoreModel:
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        _MODEL_INSTANCE = RiskScoreModel()
    return _MODEL_INSTANCE
