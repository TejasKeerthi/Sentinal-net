"""
Risk scoring model for Sentinel-Net.
Trains an ensemble regressor and predicts failure risk scores.
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import numpy as np
    from sklearn.ensemble import (
        ExtraTreesRegressor,
        GradientBoostingRegressor,
        HistGradientBoostingRegressor,
        RandomForestRegressor,
        StackingRegressor,
    )
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import KFold, cross_val_score, train_test_split

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class RiskScoreModel:
    """Train and serve an ML model for failure risk scoring."""

    input_feature_names = ["commits_30d", "contributors_30d", "open_issues"]
    engineered_feature_names = [
        "commits_30d",
        "contributors_30d",
        "open_issues",
        "log_commits",
        "log_contributors",
        "log_issues",
        "issue_per_commit",
        "contributors_per_commit",
        "change_pressure",
        "issue_commit_gap",
        "sqrt_issues",
        "commit_stability",
    ]

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

    def _build_feature_vector(self, commits_30d: int, contributors_30d: int, open_issues: int) -> np.ndarray:
        commits = float(max(0, commits_30d))
        contributors = float(max(0, contributors_30d))
        issues = float(max(0, open_issues))
        commit_base = commits + 1.0

        issue_per_commit = issues / commit_base
        contributors_per_commit = contributors / commit_base
        change_pressure = (issues * (contributors + 1.0)) / commit_base
        issue_commit_gap = issues - (commits * 0.35)
        commit_stability = commits / (contributors + 1.0)

        return np.array(
            [
                commits,
                contributors,
                issues,
                np.log1p(commits),
                np.log1p(contributors),
                np.log1p(issues),
                issue_per_commit,
                contributors_per_commit,
                change_pressure,
                issue_commit_gap,
                np.sqrt(issues),
                commit_stability,
            ],
            dtype=float,
        )

    def _augment_rows(self, rows: List[Dict[str, int]], copies_per_row: int = 6) -> List[Dict[str, int]]:
        """Expand training rows with controlled perturbations for robustness."""
        rng = np.random.default_rng(42)
        augmented: List[Dict[str, int]] = list(rows)

        for row in rows:
            base_commits = row["commits_30d"]
            base_contributors = row["contributors_30d"]
            base_issues = row["open_issues"]
            base_risk = row["risk_score"]

            for _ in range(copies_per_row):
                commits = max(0, int(round(rng.normal(base_commits, max(2.0, base_commits * 0.10)))))
                contributors = max(0, int(round(rng.normal(base_contributors, max(1.0, base_contributors * 0.12)))))
                issues = max(0, int(round(rng.normal(base_issues, max(2.0, base_issues * 0.10)))))

                # Keep generated labels coherent with feature shifts.
                risk_delta = (
                    0.42 * (issues - base_issues)
                    - 0.18 * (commits - base_commits)
                    + 0.22 * (contributors - base_contributors)
                    + rng.normal(0, 1.4)
                )
                risk = int(max(0, min(100, round(base_risk + risk_delta))))

                augmented.append(
                    {
                        "commits_30d": commits,
                        "contributors_30d": contributors,
                        "open_issues": issues,
                        "risk_score": risk,
                    }
                )

        return augmented

    def _prepare_xy(self, rows: List[Dict[str, int]]) -> Tuple[np.ndarray, np.ndarray]:
        x = np.array(
            [
                self._build_feature_vector(
                    r["commits_30d"],
                    r["contributors_30d"],
                    r["open_issues"],
                )
                for r in rows
            ],
            dtype=float,
        )
        y = np.array([r["risk_score"] for r in rows], dtype=float)
        return x, y

    def _build_candidate_models(self):
        base_et = ExtraTreesRegressor(
            n_estimators=500,
            max_depth=28,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=-1,
        )
        base_rf = RandomForestRegressor(
            n_estimators=450,
            max_depth=22,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=-1,
        )
        base_gb = GradientBoostingRegressor(
            n_estimators=350,
            learning_rate=0.04,
            max_depth=4,
            random_state=42,
        )
        base_hgb = HistGradientBoostingRegressor(
            max_depth=8,
            learning_rate=0.05,
            max_iter=380,
            random_state=42,
        )

        stacked = StackingRegressor(
            estimators=[
                ("et", ExtraTreesRegressor(n_estimators=220, max_depth=20, random_state=42, n_jobs=-1)),
                ("rf", RandomForestRegressor(n_estimators=200, max_depth=18, random_state=42, n_jobs=-1)),
                ("hgb", HistGradientBoostingRegressor(max_depth=7, max_iter=300, random_state=42)),
            ],
            final_estimator=Ridge(alpha=0.6),
            passthrough=True,
            cv=5,
            n_jobs=-1,
        )

        return {
            "ExtraTrees": base_et,
            "RandomForest": base_rf,
            "GradientBoosting": base_gb,
            "HistGradientBoosting": base_hgb,
            "StackingEnsemble": stacked,
        }

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

        raw_rows = self._load_rows()
        if len(raw_rows) < 10:
            self.training_status = {
                "enabled": False,
                "trained": False,
                "reason": "Dataset has too few samples",
            }
            return

        training_rows = self._augment_rows(raw_rows, copies_per_row=6)
        x, y = self._prepare_xy(training_rows)

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
        cv = KFold(n_splits=5, shuffle=True, random_state=42)

        leaderboard: List[Dict[str, float]] = []
        best = {
            "name": "",
            "model": None,
            "score": float("inf"),
            "mae_holdout": float("inf"),
            "mae_cv": float("inf"),
            "r2": float("-inf"),
        }

        for name, model in self._build_candidate_models().items():
            cv_mae = float((-cross_val_score(model, x_train, y_train, cv=cv, scoring="neg_mean_absolute_error")).mean())
            model.fit(x_train, y_train)
            preds = model.predict(x_test)

            holdout_mae = float(mean_absolute_error(y_test, preds))
            holdout_r2 = float(r2_score(y_test, preds))
            blended_score = (0.70 * holdout_mae) + (0.30 * cv_mae)

            leaderboard.append(
                {
                    "model": name,
                    "mae_holdout": round(holdout_mae, 3),
                    "mae_cv": round(cv_mae, 3),
                    "r2_holdout": round(holdout_r2, 3),
                    "score": round(blended_score, 3),
                }
            )

            if blended_score < best["score"]:
                best = {
                    "name": name,
                    "model": model,
                    "score": blended_score,
                    "mae_holdout": holdout_mae,
                    "mae_cv": cv_mae,
                    "r2": holdout_r2,
                }

        leaderboard.sort(key=lambda item: item["score"])
        self.model = best["model"]
        self.training_status = {
            "enabled": True,
            "trained": True,
            "raw_samples": len(raw_rows),
            "augmented_samples": len(training_rows),
            "features": self.engineered_feature_names,
            "model": best["name"],
            "mae_holdout": round(float(best["mae_holdout"]), 3),
            "mae_cv": round(float(best["mae_cv"]), 3),
            "r2_holdout": round(float(best["r2"]), 3),
            "leaderboard": leaderboard[:3],
        }

    def predict_risk_details(self, commits_30d: int, contributors_30d: int, open_issues: int) -> Dict[str, float]:
        if self.model is None:
            score = self._fallback_risk_score(commits_30d, contributors_30d, open_issues)
            return {
                "risk_score": float(score),
                "confidence": 0.55,
                "uncertainty": 11.0,
            }

        values = np.array([self._build_feature_vector(commits_30d, contributors_30d, open_issues)], dtype=float)
        predicted = float(self.model.predict(values)[0])
        bounded_score = float(max(0, min(100, round(predicted))))

        base_uncertainty = float(self.training_status.get("mae_cv", 8.0))
        confidence = float(max(0.40, min(0.98, 1.0 - (base_uncertainty / 25.0))))

        return {
            "risk_score": bounded_score,
            "confidence": round(confidence, 3),
            "uncertainty": round(base_uncertainty, 3),
        }

    def predict_risk_score(self, commits_30d: int, contributors_30d: int, open_issues: int) -> int:
        details = self.predict_risk_details(commits_30d, contributors_30d, open_issues)
        return int(details["risk_score"])

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
